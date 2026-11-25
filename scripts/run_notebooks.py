#!/usr/bin/env python3
"""Execute the eight saved-result notebooks sequentially without a Jupyter service."""
import argparse,contextlib,io,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
NAMES=['01_market_data_and_universe_audit','02_hypotheses_labels_and_features','03_baseline_strategy_research','04_temporal_ml_validation','05_portfolio_and_execution','06_robustness_and_multiple_testing','07_locked_test_and_attribution','08_forward_paper_monitor']
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-outputs',action='store_true');arg=p.parse_args();total=0;previous=os.getcwd();os.chdir(R)
 try:
  for name in NAMES:
   path=R/'notebooks'/f'{name}.ipynb';nb=json.loads(path.read_text());ns={};count=0
   for cell in nb['cells']:
    if cell['cell_type']!='code':continue
    stream=io.StringIO();count+=1
    with contextlib.redirect_stdout(stream):exec(compile(''.join(cell['source']),str(path),'exec'),ns)
    if arg.write_outputs:cell.update(execution_count=count,outputs=[{'output_type':'stream','name':'stdout','text':stream.getvalue().splitlines(True)}])
   if arg.write_outputs:
    nb['metadata']['execution_method']='Sequential Python executor; native Jupyter kernel not used';path.write_text(json.dumps(nb,indent=2)+'\n')
   total+=count;print(f'PASS {name}: {count} code cells')
 finally:os.chdir(previous)
 print(json.dumps({'notebooks':len(NAMES),'code_cells':total,'native_jupyter_kernel':False,'all_passed':True}))
if __name__=='__main__':main()
