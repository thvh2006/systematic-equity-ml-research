#!/usr/bin/env python3
"""Reproduce synthetic foundation; no real-data promotion or external calls."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--node',default='node');a=p.parse_args()
 stages=[([sys.executable,'scripts/generate_fixture.py'],'fixture'),([sys.executable,'scripts/run_foundation.py','--fixture'],'foundation'),([sys.executable,'scripts/build_review_case.py'],'review'),([sys.executable,'scripts/run_checks.py'],'checks'),([a.node,'scripts/build_workbook.mjs'],'excel'),([a.node,'scripts/build_dashboard.mjs'],'html'),([sys.executable,'scripts/build_notebook.py'],'notebook')]
 for command,label in stages:
  print('BUILD',label,flush=True);subprocess.run(command,cwd=R,check=True)
 p=json.loads((R/'artifacts/foundation/results.json').read_text());assert p['research_gate']['status']=='BLOCKED'
 paths=[R/'deliverables/P2_Systematic_Equity_Foundation.xlsx',R/'deliverables/P2_Systematic_Equity_Foundation.html',R/'notebooks/01_foundation_walkthrough.ipynb']
 result={'run_id':p['run_id'],'status':'SYNTHETIC_FOUNDATION_ONLY','market_research_complete':False,'native_excel_verified':False,'browser_ui_verified':False,'jupyter_kernel_verified':False,'outputs':[{'path':str(x.relative_to(R)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'bytes':x.stat().st_size} for x in paths]}
 (R/'artifacts/foundation/build_manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: synthetic foundation built; real-data research remains gated.',flush=True)
if __name__=='__main__':main()
