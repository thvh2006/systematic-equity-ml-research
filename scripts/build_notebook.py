#!/usr/bin/env python3
"""Create notebook with captured plain-Python cell execution, not a kernel claim."""
import contextlib,io,json,os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 cells=[];scope={'__name__':'__main__'};count=0
 def md(text):cells.append(dict(cell_type='markdown',metadata={},source=text.splitlines(True)))
 def code(source):
  nonlocal count
  count+=1;out=io.StringIO()
  with contextlib.redirect_stdout(out):exec(compile(source,f'notebook_cell_{count}','exec'),scope)
  cells.append(dict(cell_type='code',metadata={},source=source.splitlines(True),execution_count=count,outputs=[dict(output_type='stream',name='stdout',text=out.getvalue().splitlines(True))]))
 os.chdir(R)
 md('# P2 · Systematic Equity & ML — foundation review\n\n**SYNTHETIC FIXTURE ONLY.** No market performance, alpha or investment findings. All code cells below were executed sequentially using plain Python 3.12; native Jupyter kernel execution remains unverified. Open from the project root. The full reproducible source is in the project ZIP.')
 code("from pathlib import Path\nimport json,csv,sys\nR=Path.cwd()\nassert (R/'src/equity_research').is_dir(), 'Start Jupyter from the project root'\nsys.path.insert(0,str(R/'src'))\np=json.loads((R/'artifacts/foundation/results.json').read_text())\nassert p['status']=='SYNTHETIC_FOUNDATION_ONLY'\nprint(p['run_id'],p['status'])\nprint('Release gate:',p['research_gate'])")
 md('## Data contract and events\nRaw prices and separate action records are fictional. The weekday calendar is not an exchange calendar. Integer forward splits are supported; reverse/fractional splits need a cash-in-lieu policy before use.')
 code("from equity_research.data import load_market,validate_market\nrows=load_market(R/'data/sample/synthetic_market.csv')\nprint(json.dumps(validate_market(rows),indent=2))\nprint('No real-market snapshot has been imported.')")
 md('## Label availability\nThe signal follows the close; the illustrative target runs from next-session open to the open 21 sessions later. Incomplete labels remain null. A training observation must have a matured outcome before the signal, with a further session gap.')
 code("from equity_research.features import build_panel\nfeatures,labels=build_panel(rows,horizon=21)\nprint('Feature rows:',len(features))\nprint('Label statuses:',p['label_status_counts'])\nassert all(l['target'] is None for l in labels if l['status']!='MATURED')\nprint('Unmatured targets remain null: PASS')")
 code("fits=json.loads((R/'artifacts/foundation/fit_receipts.json').read_text())\nassert all(w['max_label_end']<w['signal_date']<w['fill_date'] for w in fits)\nfor w in fits: print(w['signal_date'],w['max_label_end'],w['fill_date'],w['fit_rows'])\nprint('All temporal window checks: PASS')")
 md('## Ridge and train-only transforms\nAlpha 10 is fixed for this engineering fixture. It is not selected using a financial holdout. Dates receive equal total training weight; correlated ETF rows are not independent time observations.')
 code("first=fits[0]\nfor key in ['alpha','fit_rows','fit_dates','mean','scale','coef','intercept']:\n print(key,first[key])\nprint('No locked financial test was evaluated.')")
 md('## Execution accounting\nWhole shares; cash and volume caps; explicit commissions; slippage in execution price. The session-volume cap is a coarse constraint and does not establish opening-auction liquidity. The editable Excel and HTML labs independently reproduce the first cash rebalance only.')
 code("review=json.loads((R/'artifacts/foundation/review_case.json').read_text())\nprint(json.dumps(review['python_ledger'],indent=2))\nprint('Trades:',len(review['python_trades']))\nprint('Maximum cash reconciliation difference:',max(x['max_cash_difference'] for x in p['results'].values()))")
 md('## Hand calculation and adverse events\n100 cash buys 10 shares at 10. A 2-for-1 split gives 20 shares at 5. A dividend of 1 per post-split share with price 4 produces 80 marked value plus 20 receivable; payment moves receivable to cash. NAV stays 100. Separate tests cover suspension, delisting recovery and cash-limited costs.')
 code("import importlib.util\nspec=importlib.util.spec_from_file_location('economics',R/'tests/test_economics.py')\nm=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\nm.test_hand_calculated_split_dividend_receivable_and_payment_preserve_nav()\nm.test_delisting_settles_at_recovery_and_closes_position()\nm.test_suspended_asset_is_not_filled_and_order_expires()\nprint('Split/dividend, delisting and suspended-order checks: PASS')")
 md('## Research acceptance gate and next case\nPreferred, conditional case: monthly US equity-sector ETF rotation. Candidate universe XLB/XLE/XLF/XLI/XLK/XLP/XLU/XLV/XLY has NOT been fully verified or frozen. Issuer NAV is not an executable market price. Before fitting real models, approve raw OHLCV/actions/calendar/usage rights, verify each fund and benchmark, freeze coverage and the trial budget, then separate development and locked test dates. Read docs/RESEARCH_CHARTER.md and docs/DATA_FEASIBILITY.md. Academic report remains an outline only.')
 code("for filename in ['excel_reconciliation.json','dashboard_reconciliation.json']:\n d=json.loads((R/'artifacts/foundation'/filename).read_text())\n print(filename,{k:v for k,v in d.items() if k!='checks'})\nassert p['research_gate']['status']=='BLOCKED'\nprint('No financial research result is claimed.')")
 for i,cell in enumerate(cells):cell['id']=f'foundation-{i+1:03d}'
 nb=dict(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]},'execution_validation':'Sequential plain Python harness; not native Jupyter kernel'},nbformat=4,nbformat_minor=5)
 (R/'notebooks').mkdir(exist_ok=True);path=R/'notebooks/01_foundation_walkthrough.ipynb';path.write_text(json.dumps(nb,indent=2)+'\n')
 print(json.dumps({'code_cells_executed':count,'execution':'plain_python_sequential','native_kernel_verified':False}))
if __name__=='__main__':main()
