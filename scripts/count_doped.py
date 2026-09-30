"""Count 75 inherited occupations using only the newly supplied bulk geometry."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations_with_replacement, product
from pathlib import Path
import numpy as np
import scgo_one_case as core

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / 'results' / 'zh'
INPUTS = REPO / 'data'
LEVELS = (2, 4, 6, 8, 10)

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def save(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    source = INPUTS/'bulk_input_original.vasp'
    _, lattice, atoms = core.read_poscar(source)
    assert {e:len(v) for e,v in atoms.items()} == {'Sr':2,'Ga':24,'O':38}
    lines = source.read_text(encoding='utf-8').splitlines()
    labels = [lines[10+i].split()[3] for i in range(24)]
    assert len(set(labels)) == 24
    lookup = {label:i+1 for i,label in enumerate(labels)}
    save(ROOT/'新bulk位点映射.csv',[{'新bulk_Ga编号':i+1,'POSCAR全局编号':i+3,
                                  '位点标签':label} for i,label in enumerate(labels)])
    samples = read(INPUTS/'configuration_sites.csv')
    assert Counter(int(s['nCr_cell']) for s in samples) == {2:13,4:17,6:15,8:16,10:14}
    selected = {}
    catalogs = []
    cutoffs = {}
    expanded_shifts = np.array(list(product(range(-2,3),repeat=3)))
    multi_images = []
    for metal,limit in [('Sr',5.0),('Ga',4.0)]:
        pairs = core.shortest_pair_vectors(atoms,lattice,metal)
        cutoff,lo,hi = core.suggest_cutoff(pairs,limit)
        cutoffs[metal] = {'cutoff_A':cutoff,'gap_lower_A':lo,'gap_upper_A':hi}
        selected[metal],classes = core.classify_bonds(pairs,metal,cutoff,1e-5)
        catalogs.extend(classes)
        for p in pairs:
            delta = atoms[metal][p['metal_index']-1]-atoms['O'][p['O_index']-1]
            ds = np.linalg.norm((delta+expanded_shifts)@lattice,axis=1)
            assert abs(ds.min()-p['distance_A']) < 1e-10
            if (ds<cutoff).sum()>1:
                multi_images.append([metal,p['metal_index'],p['O_index'],int((ds<cutoff).sum())])
    catalogs += [{**r,'metal':'Cr','bond_type':r['bond_type'].replace('Ga_','Cr_')}
                 for r in catalogs if r['metal']=='Ga']
    catalog_lookup = {r['bond_type']:r for r in catalogs}
    assert len(catalogs)==24
    cases = []
    all_paths = []
    max_poscar_error = 0.0
    for sample in samples:
        n = int(sample['nCr_cell'])
        site_labels = [s.removeprefix('Cr_') for s in sample['Cr_sites'].split(';')]
        chosen = sorted(lookup[label] for label in site_labels)
        assert len(chosen)==len(set(chosen))==n
        remaining = [i for i in range(1,25) if i not in chosen]
        folder = ROOT/f'{n}Cr'/sample['group']
        folder.mkdir(parents=True,exist_ok=True)
        blocks = [atoms['Sr'],atoms['Ga'][np.array(remaining)-1],
                  atoms['Ga'][np.array(chosen)-1],atoms['O']]
        poscar = [f'New bulk Sr2 Ga{24-n} Cr{n} O38 {sample["group"]}','1.0']
        poscar += [' '.join(f'{v:.16f}' for v in row) for row in lattice]
        poscar += ['Sr Ga Cr O',f'2 {24-n} {n} 38','Direct']
        poscar += [' '.join(f'{v:.16f}' for v in row) for block in blocks for row in block]
        (folder/'POSCAR_bulk_doped').write_text('\n'.join(poscar)+'\n',encoding='utf-8')
        _,check_lat,check_atoms = core.read_poscar(folder/'POSCAR_bulk_doped')
        assert np.allclose(check_lat,lattice,rtol=0,atol=1e-12)
        for element,block in zip(('Sr','Ga','Cr','O'),blocks):
            assert check_atoms[element].shape==block.shape
            error = float(np.max(np.abs((check_atoms[element]-block)@lattice)))
            max_poscar_error=max(max_poscar_error,error)
            assert error<1e-12
        ranks = {'Ga':{old:i+1 for i,old in enumerate(remaining)},
                 'Cr':{old:i+1 for i,old in enumerate(chosen)}}
        bonds = [{**r,'site_label':'','bulk_Ga_index':''} for r in selected['Sr']]
        for p in selected['Ga']:
            old=p['metal_index']; metal='Cr' if old in chosen else 'Ga'
            bonds.append({**p,'metal':metal,'metal_index':ranks[metal][old],
                          'bond_type':p['bond_type'].replace('Ga_',metal+'_'),
                          'site_label':labels[old-1],'bulk_Ga_index':old})
        # Independently recompute the generated structure's metal–O distances.
        for metal in ('Sr','Ga','Cr'):
            cutoff=cutoffs['Sr' if metal=='Sr' else 'Ga']['cutoff_A']
            check=core.shortest_pair_vectors(check_atoms,check_lat,metal)
            observed={(r['metal_index'],r['O_index']):r['distance_A'] for r in check if r['distance_A']<cutoff}
            expected={(r['metal_index'],r['O_index']):r['distance_A'] for r in bonds if r['metal']==metal}
            assert observed.keys()==expected.keys()
            assert all(abs(observed[k]-expected[k])<1e-10 for k in observed)
        paths,by_o = core.enumerate_paths(bonds)
        assert len(bonds)==152 and len(paths)==228
        assert len(paths)==sum(len(v)*(len(v)-1)//2 for v in by_o.values())
        assert len({(p['O_index'],p['left_metal'],p['left_index'],p['right_metal'],p['right_index']) for p in paths})==len(paths)
        site_by_atom={(b['metal'],b['metal_index']):b['site_label'] for b in bonds}
        for p in paths:
            p['left_site_label']=site_by_atom[p['left_metal'],p['left_index']]
            p['right_site_label']=site_by_atom[p['right_metal'],p['right_index']]
        cases.append({'n':n,'group':sample['group'],'folder':folder,'chosen':chosen,'bonds':bonds,'paths':paths})
        all_paths.extend(paths)
    core.split_repeated_length_types(all_paths,0.01)
    def key(p):
        return (p['family'],p['left_type'],p['right_type'],p['angle_type'])
    observed=defaultdict(list)
    for p in all_paths: observed[key(p)].append(p)
    theoretical=[]
    for a,b in combinations_with_replacement(core.METALS,2):
        aa=[r['bond_type'] for r in catalogs if r['metal']==a]
        bb=[r['bond_type'] for r in catalogs if r['metal']==b]
        for left,right in (combinations_with_replacement(aa,2) if a==b else product(aa,bb)):
            matching=[k for k in observed if k[:3]==(f'{a}-O-{b}',left,right)]
            theoretical.extend(matching or [(f'{a}-O-{b}',left,right,'')])
    def type_row(k,members):
        return {'路径类型':k[0],'左键类别':k[1],'左键代表长度_A':catalog_lookup[k[1]]['representative_A'],
                '右键类别':k[2],'右键代表长度_A':catalog_lookup[k[2]]['representative_A'],
                '角度子类':k[3],'平均角度_度':float(np.mean([p['angle_deg'] for p in members])) if members else '',
                '数量':len(members)}
    summaries=[]; all_bond_rows=[]; all_path_rows=[]
    cross_bonds=Counter(); cross_paths=Counter()
    for case in cases:
        n=case['n']; folder=case['folder']; group=case['group']
        counts=Counter(b['bond_type'] for b in case['bonds'])
        br=[{'金属元素':r['metal'],'键类别':r['bond_type'],'代表键长_A':r['representative_A'],
             '分类下限_含_A':r['lower_inclusive_A'],'分类上限_不含_A':r['upper_exclusive_A'],
             '数量':counts[r['bond_type']]} for r in catalogs]
        save(folder/'单键种类与数量.csv',br)
        bond_rows=[{'金属元素':b['metal'],'元素内编号':b['metal_index'],'新bulk_Ga编号':b['bulk_Ga_index'],
                    '位点标签':b['site_label'],'O编号':b['O_index'],'键长_A':b['distance_A'],
                    '键类别':b['bond_type'],'周期镜像':str(b['image'])} for b in case['bonds']]
        save(folder/'单键明细.csv',bond_rows)
        grouped=defaultdict(list)
        for p in case['paths']: grouped[key(p)].append(p)
        combinations=[type_row(k,grouped[k]) for k in theoretical]
        save(folder/'全部M-O-M组合_含零.csv',combinations)
        save(folder/'实际M-O-M种类与数量.csv',[r for r in combinations if r['数量']])
        path_rows=[{'路径类型':p['family'],'O编号':p['O_index'],
                    '左金属元素':p['left_metal'],'左元素内编号':p['left_index'],'左位点标签':p['left_site_label'],
                    '左键类别':p['left_type'],'左键长_A':p['left_distance_A'],
                    '右金属元素':p['right_metal'],'右元素内编号':p['right_index'],'右位点标签':p['right_site_label'],
                    '右键类别':p['right_type'],'右键长_A':p['right_distance_A'],
                    '角度_度':p['angle_deg'],'角度子类':p['angle_type']} for p in case['paths']]
        save(folder/'M-O-M路径明细.csv',path_rows)
        meta={'晶胞Cr数':n,'构型':group}
        all_bond_rows += [{**meta,**r} for r in bond_rows]
        all_path_rows += [{**meta,**r} for r in path_rows]
        summary={**meta,'单键种类数':sum(v>0 for v in counts.values()),'单键数量':len(bond_rows),
                 'M-O-M种类数':sum(bool(v) for v in grouped.values()),'M-O-M路径数量':len(path_rows)}
        for metal in core.METALS:
            summary[f'{metal}-O种类数']=sum(counts[r['bond_type']]>0 for r in catalogs if r['metal']==metal)
            summary[f'{metal}-O数量']=sum(b['metal']==metal for b in case['bonds'])
        for a,b in combinations_with_replacement(core.METALS,2):
            family=f'{a}-O-{b}'
            summary[family+'种类数']=sum(k[0]==family and bool(v) for k,v in grouped.items())
            summary[family+'数量']=sum(p['family']==family for p in case['paths'])
        summary['新bulk_Cr占位Ga编号']=';'.join(map(str,case['chosen']))
        summaries.append(summary)
        cross_bonds.update({(n,k):v for k,v in counts.items()})
        cross_paths.update({(n,k):len(v) for k,v in grouped.items()})
    save(ROOT/'逐构型统计汇总.csv',summaries)
    save(ROOT/'全部构型单键明细.csv',all_bond_rows)
    save(ROOT/'全部构型M-O-M路径明细.csv',all_path_rows)
    cross=[]
    for r in catalogs:
        cross.append({'记录类型':'单键','类别':r['bond_type'],'左键长_A':r['representative_A'],'右键长_A':'',
                      **{f'{n}Cr数量':cross_bonds[n,r['bond_type']] for n in LEVELS}})
    for k in sorted(observed):
        cross.append({'记录类型':'M-O-M','类别':'__'.join(k),'左键长_A':catalog_lookup[k[1]]['representative_A'],
                      '右键长_A':catalog_lookup[k[2]]['representative_A'],
                      **{f'{n}Cr数量':cross_paths[n,k] for n in LEVELS}})
    save(ROOT/'跨浓度各类别计数.csv',cross)
    levels=[]
    for n in LEVELS:
        subset=[r for r in summaries if r['晶胞Cr数']==n]
        levels.append({'晶胞Cr数':n,'构型数':len(subset),
                       '单键种类并集':sum(cross_bonds[n,r['bond_type']]>0 for r in catalogs),
                       'M-O-M种类并集':sum(cross_paths[n,k]>0 for k in observed),
                       '每构型单键种类最少':min(r['单键种类数'] for r in subset),
                       '每构型单键种类最多':max(r['单键种类数'] for r in subset),
                       '每构型路径种类最少':min(r['M-O-M种类数'] for r in subset),
                       '每构型路径种类最多':max(r['M-O-M种类数'] for r in subset),
                       '全部构型单键总数':len(subset)*152,'全部构型路径总数':len(subset)*228})
    save(ROOT/'各浓度统计汇总.csv',levels)
    report={'samples':len(cases),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'cutoffs':cutoffs,'global_bond_types':len(catalogs),'global_observed_path_types':len(observed),
            'theoretical_path_types':len(theoretical),'additional_angle_subtypes':sum(bool(k[3]) for k in observed),
            'max_generated_poscar_coordinate_error_A':max_poscar_error,
            'multi_image_index_pairs':multi_images,'levels':levels,
            'verification':'75 generated structures independently checked against new bulk distances; all assertions passed'}
    (ROOT/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=INPUTS)
    parser.add_argument('--output', type=Path, default=ROOT)
    args = parser.parse_args()
    INPUTS = args.input_dir.resolve()
    ROOT = args.output.resolve()
    main()
