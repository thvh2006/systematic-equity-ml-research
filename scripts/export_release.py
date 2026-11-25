#!/usr/bin/env python3
"""Export reviewed source/derived evidence only; exclude private feeds and caches."""
import argparse,hashlib,json,re,shutil,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def candidates():
 for p in sorted(R.rglob('*')):
  rel=p.relative_to(R)
  if not p.is_file() or any(x in {'.git','.venv','node_modules','__pycache__','private','outputs'} for x in rel.parts):continue
  if 'private' in p.name or p.name.endswith(('.pyc','.inspect.ndjson','.zip')):continue
  if rel.parts[:2]==('artifacts','foundation') or 'Foundation' in p.name or p.name=='01_foundation_walkthrough.ipynb':continue
  yield p
def main():
 arg=argparse.ArgumentParser(description=__doc__);arg.add_argument('destination',type=Path);arg.add_argument('--zip',dest='zip_path',type=Path);a=arg.parse_args()
 if a.destination.exists():raise SystemExit('Export destination already exists; choose a fresh path')
 files=[p for p in candidates() if p.name!='release_manifest.json'];hashfiles=[p for p in files if p.name!='release_review.json']
 for p in files:
  if p.suffix in {'.py','.json','.md','.html','.yml','.toml','.txt','.cjs'}:
   text=p.read_text();patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}']
   if any(re.search(x,text) for x in patterns):raise SystemExit('Credential-like material detected in '+str(p.relative_to(R)))
 manifest={'version':'0.3.0','scope':'Original source and derived retrospective research; raw provider records excluded','mutable_review_receipt':'artifacts/research/release_review.json is excluded from hashes so post-publication UI/CI observations can be appended','files':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in hashfiles]}
 (R/'release_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(R/'release_manifest.json')
 for p in files:
  q=a.destination/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 assert not list(a.destination.rglob('private'))
 if a.zip_path:
  with zipfile.ZipFile(a.zip_path,'w',zipfile.ZIP_DEFLATED) as z:
   for p in sorted(a.destination.rglob('*')):
    if p.is_file():z.write(p,'systematic-equity-ml-research/'+str(p.relative_to(a.destination)))
  with zipfile.ZipFile(a.zip_path) as z:assert z.testzip() is None
 print(json.dumps({'exported_files':len(files),'hashed_files':len(hashfiles),'destination':str(a.destination),'total_bytes':sum(p.stat().st_size for p in files),'private_source_files':0,'credential_pattern_hits':0}))
if __name__=='__main__':main()
