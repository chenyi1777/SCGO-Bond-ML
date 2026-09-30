"""Reproduce the accepted counting workflow and both language versions."""
import argparse
import subprocess
import sys
from pathlib import Path
from export_english import export

ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,default=ROOT/'data')
    parser.add_argument('--output',type=Path,default=ROOT/'results')
    args=parser.parse_args();output=args.output.resolve()
    subprocess.run([sys.executable,str(ROOT/'scripts/count_doped.py'),
                    '--input-dir',str(args.input_dir.resolve()),'--output',str(output/'zh')],check=True)
    count=export(output/'zh',output/'en')
    print(f'Completed: {output}; English mirror contains {count} files.')
if __name__=='__main__':main()
