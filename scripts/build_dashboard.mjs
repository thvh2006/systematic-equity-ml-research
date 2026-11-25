import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';import vm from 'node:vm';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url))),dir=path.join(root,'artifacts/foundation');
const results=JSON.parse(await fs.readFile(path.join(dir,'results.json'),'utf8')),review=JSON.parse(await fs.readFile(path.join(dir,'review_case.json'),'utf8')),windows=JSON.parse(await fs.readFile(path.join(dir,'fit_receipts.json'),'utf8'));
let html=await fs.readFile(path.join(root,'dashboard/template.html'),'utf8');
const source=html.slice(html.indexOf('function executionLab'),html.indexOf('\nconst $='));const sandbox={};vm.createContext(sandbox);vm.runInContext(source,sandbox);let comparisons=0;
for(const [name,nav,fee,want] of [['baseline',100000,10,{ledger:review.python_ledger,trades:review.python_trades}],['fee_plus20',100000,30,review.counterfactuals.fee_plus20],['nav_double',200000,10,review.counterfactuals.nav_double]]){
 const got=sandbox.executionLab(review,nav,fee,5),quantities=Object.fromEntries(want.trades.map(t=>[t.asset,t.quantity]));
 for(const [k,w] of [['cash',want.ledger.cash],['market_value',want.ledger.market_value],['fees',want.ledger.fees],['nav',want.ledger.nav]]){if(Math.abs(got[k]-w)>1e-6)throw Error(name+':'+k);comparisons++;}
 for(const r of got.rows){if(r.quantity!==(quantities[r.asset]??0))throw Error('Quantity mismatch');comparisons++;}
}
const data=JSON.stringify({results,review,windows}).replaceAll('<','\\u003c');html=html.replace('/* DATA */','const DATA='+data+';');new vm.Script(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
await fs.writeFile(path.join(root,'deliverables/P2_Systematic_Equity_Foundation.html'),html);await fs.writeFile(path.join(dir,'dashboard_reconciliation.json'),JSON.stringify({status:'PASS_CALCULATION_AND_SYNTAX_ONLY',execution_comparisons:comparisons,browser_ui_verified:false,mode:'synthetic_fixture'},null,2));console.log(JSON.stringify({javascript_review_case_comparisons:comparisons,script_syntax:'PASS',ui:'NOT_VERIFIED'}));
