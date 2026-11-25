#!/usr/bin/env python3
"""Publish the saved-evidence explorer with post-study review, without fitting."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 t=(R/'dashboard/research.html').read_text()
 for marker,name in [('__BUNDLE__','artifacts/research/public_bundle.json'),('__POLISH__','artifacts/review/polish.json')]:
  data=json.loads((R/name).read_text());t=t.replace(marker,json.dumps(data,separators=(',',':')).replace('</','<\\/'))
 for name in ['index.html','deliverables/P2_Systematic_Equity_Research.html']:(R/name).write_text(t)
 print(json.dumps({'version':'0.4.0','views':9,'bytes':len(t.encode()),'model_refitted':False}))
if __name__=='__main__':main()
