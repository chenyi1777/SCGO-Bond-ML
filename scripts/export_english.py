"""Translate result filenames and schema, preserving all numerical values."""
import argparse
import csv
import json
import shutil
from pathlib import Path

FILES={
 '各浓度统计汇总.csv':'concentration_summary.csv','跨浓度各类别计数.csv':'cross_concentration_type_counts.csv',
 '全部构型单键明细.csv':'all_bonds.csv','全部构型M-O-M路径明细.csv':'all_MOM_paths.csv',
 '新bulk位点映射.csv':'bulk_site_map.csv','逐构型统计汇总.csv':'configuration_summary.csv',
 '单键种类与数量.csv':'bond_types_and_counts.csv','单键明细.csv':'bonds.csv',
 '全部M-O-M组合_含零.csv':'all_MOM_combinations_including_zero.csv',
 '实际M-O-M种类与数量.csv':'observed_MOM_types_and_counts.csv','M-O-M路径明细.csv':'MOM_paths.csv'}
COLUMNS={
 '晶胞Cr数':'nCr_cell','构型':'configuration','构型数':'configuration_count',
 '单键种类并集':'bond_type_union_count','M-O-M种类并集':'MOM_type_union_count',
 '单键种类数':'bond_type_count','单键数量':'bond_count','M-O-M种类数':'MOM_type_count',
 'M-O-M路径数量':'MOM_path_count','每构型单键种类最少':'min_bond_types_per_configuration',
 '每构型单键种类最多':'max_bond_types_per_configuration','每构型路径种类最少':'min_path_types_per_configuration',
 '每构型路径种类最多':'max_path_types_per_configuration','全部构型单键总数':'total_bonds_all_configurations',
 '全部构型路径总数':'total_paths_all_configurations','金属元素':'metal','元素内编号':'element_local_index_1based',
 '新bulk_Ga编号':'bulk_Ga_index_1based','POSCAR全局编号':'POSCAR_global_index_1based',
 '新bulk_Cr占位Ga编号':'Cr_occupied_bulk_Ga_indices_1based','位点标签':'site_label',
 'O编号':'oxygen_index_1based','键长_A':'distance_A','键类别':'bond_type','周期镜像':'periodic_image_shift',
 '代表键长_A':'representative_distance_A','分类下限_含_A':'lower_bound_inclusive_A',
 '分类上限_不含_A':'upper_bound_exclusive_A','数量':'count','路径类型':'path_family',
 '左金属元素':'left_metal','左元素内编号':'left_element_index_1based','左位点标签':'left_site_label',
 '左键类别':'left_bond_type','左键长_A':'left_distance_A','右金属元素':'right_metal',
 '右元素内编号':'right_element_index_1based','右位点标签':'right_site_label','右键类别':'right_bond_type',
 '右键长_A':'right_distance_A','角度_度':'angle_deg','角度子类':'angle_subtype',
 '左键代表长度_A':'left_representative_distance_A','右键代表长度_A':'right_representative_distance_A',
 '平均角度_度':'mean_angle_deg','记录类型':'record_type','类别':'type_id'}
for n in (2,4,6,8,10):COLUMNS[f'{n}Cr数量']=f'count_{n}Cr'
for family in ('Sr-O','Ga-O','Cr-O','Sr-O-Sr','Sr-O-Ga','Sr-O-Cr','Ga-O-Ga','Ga-O-Cr','Cr-O-Cr'):
    COLUMNS[family+'种类数']=family.replace('-','_')+'_type_count'
    COLUMNS[family+'数量']=family.replace('-','_')+'_count'

def translated_key(key):
    if key in COLUMNS:return COLUMNS[key]
    if key.isascii():return key
    raise ValueError('Untranslated header: '+key)

def translate_json(value):
    if isinstance(value,dict):return {translated_key(k):translate_json(v) for k,v in value.items()}
    if isinstance(value,list):return [translate_json(v) for v in value]
    return value

def export(source,destination):
    source,destination=Path(source),Path(destination)
    count=0
    for path in sorted(source.rglob('*')):
        if not path.is_file():continue
        relative=path.relative_to(source)
        target=destination/relative.parent/FILES.get(path.name,path.name)
        target.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.csv':
            with path.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f);columns=reader.fieldnames;rows=list(reader)
            with target.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=[translated_key(k) for k in columns]);writer.writeheader()
                for row in rows:
                    writer.writerow({translated_key(k):('bond' if k=='记录类型' and v=='单键' else v) for k,v in row.items()})
        elif path.suffix=='.json':
            target.write_text(json.dumps(translate_json(json.loads(path.read_text(encoding='utf-8'))),indent=2),encoding='utf-8')
        else:shutil.copyfile(path,target)
        count+=1
    # Do not write outside the selected results tree when used for a temporary reproduction.
    dictionary=destination.parent/'column_dictionary.csv'
    with dictionary.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['中文字段','English_field'])
        writer.writerows(sorted(COLUMNS.items()))
    return count

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('destination',type=Path)
    args=parser.parse_args();print('Exported',export(args.source,args.destination),'files')
