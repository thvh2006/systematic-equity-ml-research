#!/usr/bin/env python3
import importlib.util,inspect,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
def main():
 count=0;failed=[]
 for path in sorted((R/'tests').glob('test_*.py')):
  spec=importlib.util.spec_from_file_location(path.stem,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  for name,fn in inspect.getmembers(module,inspect.isfunction):
   if name.startswith('test_') and fn.__module__==module.__name__:
    count+=1
    try:fn();print('PASS',name)
    except Exception:failed.append(name);traceback.print_exc()
 print(f'{count-len(failed)}/{count} checks passed')
 if failed:raise SystemExit(1)
if __name__=='__main__':main()
