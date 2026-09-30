"""Verify published tables, language parity, and source/provenance alignment."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from export_english import FILES,translated_key

ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def verify(base,input_dir):
    summary=json.loads((base/'en/summary.json').read_text(encoding='utf-8'))
    digest=hashlib.sha256((input_dir/'bulk_input_original.vasp').read_bytes()).hexdigest()
    assert digest==summary['source_sha256']
    configs=read(input_dir/'configuration_sites.csv')
    assert Counter(int(r['nCr_cell']) for r in configs)=={2:13,4:17,6:15,8:16,10:14}
    hpc=read(ROOT/'provenance/hpc_selected_paths_en.csv')
    normalize=lambda s:{x.removeprefix('Cr_') for x in s.split(';')}
    assert {(r['nCr_cell'],r['group']):normalize(r['Cr_sites']) for r in configs}=={
        (r['nCr_cell'],r['group']):normalize(r['Cr_sites']) for r in hpc}
    assert summary['global_bond_types']==24 and summary['global_observed_path_types']==51
    assert summary['theoretical_path_types']==300 and summary['additional_angle_subtypes']==0
    assert len(read(base/'en/all_bonds.csv'))==11400
    assert len(read(base/'en/all_MOM_paths.csv'))==17100
    parity_count=0
    for path in (base/'zh').rglob('*.csv'):
        relative=path.relative_to(base/'zh');target=base/'en'/relative.parent/FILES[path.name]
        expected=[{translated_key(k):('bond' if k=='记录类型' and v=='单键' else v) for k,v in row.items()} for row in read(path)]
        assert read(target)==expected;parity_count+=1
    for row in configs:
        folder=base/'en'/(row['nCr_cell']+'Cr')/row['group']
        bonds=read(folder/'bonds.csv');paths=read(folder/'MOM_paths.csv')
        assert len(bonds)==152 and len(paths)==228
        assert sum(int(r['count']) for r in read(folder/'bond_types_and_counts.csv'))==152
        all_combos=read(folder/'all_MOM_combinations_including_zero.csv')
        assert len(all_combos)==300 and sum(int(r['count']) for r in all_combos)==228
        assert read(folder/'observed_MOM_types_and_counts.csv')==[r for r in all_combos if int(r['count'])>0]
        key=lambda r:(r['oxygen_index_1based'],tuple(sorted(((r['left_metal'],r['left_element_index_1based']),
            (r['right_metal'],r['right_element_index_1based'])))))
        assert len({key(p) for p in paths})==228
        assert (folder/'POSCAR_bulk_doped').read_bytes()==(base/'zh'/(row['nCr_cell']+'Cr')/row['group']/'POSCAR_bulk_doped').read_bytes()
    return {'status':'passed','bulk_sha256':digest,'configurations':75,'bonds':11400,'paths':17100,
            'bilingual_CSV_pairs_checked':parity_count,'bilingual_POSCAR_pairs_checked':75,
            'configuration_occupations_match_archived_HPC_manifest':True,
            'note':'geometry assertions run in count_doped.py; this check validates stored tables and parity'}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,default=ROOT/'results')
    parser.add_argument('--input-dir',type=Path,default=ROOT/'data')
    parser.add_argument('--report',type=Path)
    args=parser.parse_args();report=verify(args.results.resolve(),args.input_dir.resolve())
    text=json.dumps(report,indent=2);print(text)
    if args.report:args.report.write_text(text,encoding='utf-8')
