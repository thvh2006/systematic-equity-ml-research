import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url))),out=path.join(root,'deliverables');
await fs.mkdir(path.join(root,'outputs/previews'),{recursive:true});
const data=JSON.parse(await fs.readFile(path.join(root,'artifacts/foundation/results.json'),'utf8'));
const review=JSON.parse(await fs.readFile(path.join(root,'artifacts/foundation/review_case.json'),'utf8'));
const windows=JSON.parse(await fs.readFile(path.join(root,'artifacts/foundation/fit_receipts.json'),'utf8'));
const wb=Workbook.create(),names=['Overview','Execution Lab','Event Checks','Walk Forward','Fixture Ledger','Sources'];
const sh=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const numeric='#,##0.00;(#,##0.00);"-"',integer='#,##0';
const v=(s,c,x)=>{s.getRange(c).values=[[x]];s.getRange(c).format.font.color='#1756C0';};
const l=(s,c,x)=>s.getRange(c).values=[[x]];
const f=(s,c,x)=>{s.getRange(c).formulas=[['='+x]];s.getRange(c).format.font.color=x.includes('!')?'#238249':'#172133';};
for(const [n,s] of Object.entries(sh)){
 s.showGridLines=false;s.getRange('C1:Q540').format.font={name:'Arial',size:10,color:'#172133'};
 s.getRange('C:C').format.columnWidth=37;s.getRange('D:Q').format.columnWidth=15;s.getRange('C1:Q540').format.rowHeight=22;
 l(s,'C2',n);s.getRange('C2:Q2').format.font={name:'Arial',size:16,bold:true,color:'#172133'};
 s.mergeCells('C3:Q3');l(s,'C3','SYNTHETIC FIXTURE ONLY. Fictional assets. No investment-performance evidence.');s.getRange('C3:Q3').format={fill:'#FFF2D9',font:{name:'Arial',size:10,color:'#855B13'},rowHeight:27};
 s.getRange('D5:Q535').setNumberFormat(numeric);s.freezePanes.freezeRows(4);
}
const ex=sh['Execution Lab'];
[['Initial NAV',review.initial_nav],['Fee bps',review.fee_bps],['Slippage bps',review.slippage_bps],['Session-volume participation',review.participation]].forEach(([label,x],i)=>{l(ex,'C'+(5+i),label);v(ex,'D'+(5+i),x);});ex.getRange('D8').setNumberFormat('0.0%');
ex.mergeCells('F5:Q7');l(ex,'F5','First rebalance only, starting from cash. Edit blue NAV/fees/slippage/participation inputs. This sheet independently calculates whole-share buys, cash caps and transaction costs. Full research ledgers on other sheets are imported Python snapshots.');ex.getRange('F5:Q7').format.wrapText=true;
const headers=['Asset','Target weight','Raw open','Session volume','Volume cap','Target qty','Execution price','Filled qty','Executed value','Fee','Cash before','Cash after','Raw close','Marked position','Order status'];
ex.getRange('C12:Q12').values=[headers];ex.getRange('C12:Q12').format={fill:'#183553',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:34,wrapText:true};
for(const [i,a] of review.assets.entries()){
 const r=13+i;l(ex,'C'+r,a.asset);v(ex,'D'+r,a.target_weight);v(ex,'E'+r,a.raw_open);v(ex,'F'+r,a.volume);v(ex,'O'+r,a.raw_close);
 ex.getRange('D'+r).setNumberFormat('0.0%');ex.getRange(`F${r}:H${r}`).setNumberFormat(integer);ex.getRange('J'+r).setNumberFormat(integer);
 f(ex,'G'+r,`ROUNDDOWN(F${r}*$D$8,0)`);f(ex,'H'+r,`ROUNDDOWN($D$5*D${r}/E${r},0)`);f(ex,'I'+r,`E${r}*(1+$D$7/10000)`);
 f(ex,'M'+r,i?`N${r-1}`:'$D$5');f(ex,'J'+r,`MIN(G${r},H${r},ROUNDDOWN(M${r}/(I${r}*(1+$D$6/10000)),0))`);
 f(ex,'K'+r,`J${r}*I${r}`);f(ex,'L'+r,`K${r}*$D$6/10000`);f(ex,'N'+r,`M${r}-K${r}-L${r}`);f(ex,'P'+r,`J${r}*O${r}`);f(ex,'Q'+r,`IF(H${r}=0,"NO_ORDER",IF(J${r}=H${r},"FILLED","CAPPED"))`);
}
const end=12+review.assets.length;
[['Closing cash',23,`N${end}`],['Position market value',24,`SUM(P13:P${end})`],['Closing NAV',25,'D23+D24'],['Total fees',27,`SUM(L13:L${end})`]].forEach(([label,row,formula])=>{l(ex,'C'+row,label);f(ex,'D'+row,formula);});
ex.getRange('C25:D25').format.fill='#EAF0F6';ex.getRange('C25:D25').format.font.bold=true;
l(ex,'F22','Python baseline snapshot');l(ex,'H22','Difference to baseline');
for(const [r,x] of [[23,review.python_ledger.cash],[24,review.python_ledger.market_value],[25,review.python_ledger.nav],[27,review.python_ledger.fees]]){v(ex,'G'+r,x);f(ex,'H'+r,`D${r}-G${r}`);}
ex.mergeCells('F29:Q30');l(ex,'F29','Baseline differences should be zero. After editing a control, differences from the frozen Python baseline are expected. Slippage is already in execution price; do not deduct it again. Session volume is not opening-auction liquidity.');ex.getRange('F29:Q30').format.wrapText=true;
l(ex,'C29','Signal close: '+review.signal_date);l(ex,'C30','Fill open: '+review.fill_date);
const ev=sh['Event Checks'];l(ev,'C5','Initial cash');v(ev,'D5',100);l(ev,'C6','Buy price');v(ev,'D6',10);l(ev,'C7','Forward split factor');v(ev,'D7',2);l(ev,'C8','Cash dividend per new share');v(ev,'D8',1);
ev.getRange('C11:H11').values=[['Stage','Cash','Shares','Mark price','Dividend receivable','NAV']];ev.getRange('C11:H11').format={fill:'#183553',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
l(ev,'C12','Buy before events');f(ev,'D12','$D$5-ROUNDDOWN($D$5/$D$6,0)*$D$6');f(ev,'E12','ROUNDDOWN($D$5/$D$6,0)');f(ev,'F12','$D$6');f(ev,'G12','0');f(ev,'H12','D12+E12*F12+G12');
l(ev,'C13','2-for-1 split');f(ev,'D13','D12');f(ev,'E13','E12*$D$7');f(ev,'F13','F12/$D$7');f(ev,'G13','G12');f(ev,'H13','D13+E13*F13+G13');
l(ev,'C14','Ex-dividend, not yet paid');f(ev,'D14','D13');f(ev,'E14','E13');f(ev,'F14','F13-$D$8');f(ev,'G14','G13+E14*$D$8');f(ev,'H14','D14+E14*F14+G14');
l(ev,'C15','Dividend payment');f(ev,'D15','D14+G14');f(ev,'E15','E14');f(ev,'F15','F14');f(ev,'G15','0');f(ev,'H15','D15+E15*F15+G15');
ev.mergeCells('C18:J20');l(ev,'C18','Hand calculation:10 shares at10 become20 shares at5. A1-per-share dividend reduces mark to4 and creates a20 receivable. Payment moves20 into cash. NAV remains100 throughout. No fee or price movement in this golden case.');ev.getRange('C18:J20').format.wrapText=true;
const wf=sh['Walk Forward'];wf.getRange('C5:J5').values=[['Signal close','Next-session fill','Train start','Train end','Latest matured label','Train rows','Train dates','Time ordering']];wf.getRange('C5:J5').format={fill:'#183553',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:34,wrapText:true};
for(const [i,w] of windows.entries()){const r=i+6;wf.getRange(`C${r}:I${r}`).values=[[...['signal_date','fill_date','train_start','train_end','max_label_end'].map(k=>new Date(w[k]+'T00:00:00Z')),w.fit_rows,w.fit_dates]];wf.getRange(`C${r}:G${r}`).setNumberFormat('yyyy-mm-dd');wf.getRange(`H${r}:I${r}`).setNumberFormat(integer);f(wf,'J'+r,`IF(AND(G${r}<C${r},C${r}<D${r}),"PASS","FAIL")`);}
const ledger=sh['Fixture Ledger'],rows=data.results.ridge_alpha10__cost1.ledger;
ledger.getRange('C5:L5').values=[['Date','Cash','Marked holdings','Dividend receivable','NAV','Fees','Slippage in price','Traded notional','Cash identity diff','Run ID']];ledger.getRange('C5:L5').format={fill:'#183553',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:34,wrapText:true};
ledger.getRange(`C6:L${rows.length+5}`).values=rows.map(r=>[new Date(r.date+'T00:00:00Z'),r.cash,r.market_value,r.dividend_receivable,r.nav,r.fees,r.slippage_cost,r.traded_notional,r.cash_reconciliation,data.run_id]);ledger.getRange(`C6:C${rows.length+5}`).setNumberFormat('yyyy-mm-dd');ledger.getRange(`L6:L${rows.length+5}`).format.columnWidth=29;
const overview=sh.Overview;overview.mergeCells('C5:J6');l(overview,'C5','Foundation demo: investigate temporal leakage, corporate actions and cash accounting before importing a market-data snapshot. The real-research gate remains blocked.');overview.getRange('C5:J6').format.wrapText=true;
[['Fictional assets',data.data_audit.assets],['Synthetic sessions',data.data_audit.sessions],['Input rows',data.data_audit.rows],['Walk-forward ridge fits',data.walk_forward_fits],['Strategy/cost captures',Object.keys(data.results).length],['Research release','BLOCKED: approved market data absent']].forEach(([label,x],i)=>{l(overview,'C'+(8+i),label);l(overview,'D'+(8+i),x);});
l(overview,'C15','Use Execution Lab to change costs and NAV.');l(overview,'C16','Event Checks explains split and dividend economics.');l(overview,'C17','Walk Forward shows label maturity before each fit.');l(overview,'C18','Full ledger is a frozen Python snapshot, not Excel model training.');
const sampled=rows.filter((r,i)=>i===rows.length-1||rows[i+1].date.slice(0,7)!==r.date.slice(0,7));overview.getRange('C21:D21').values=[['Fixture month end','Synthetic NAV']];
overview.getRange(`C22:D${21+sampled.length}`).values=sampled.map(r=>[r.date,r.nav]);overview.getRange(`D22:D${21+sampled.length}`).setNumberFormat(numeric);
const chart=overview.charts.add('line',overview.getRange(`C21:D${21+sampled.length}`));chart.title='Synthetic NAV: accounting demonstration only';chart.setPosition('F20','M36');chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=12;chart.legend={position:'bottom',textStyle:{typeface:'Arial',fontSize:10}};chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:9}};chart.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
const sources=sh.Sources;sources.mergeCells('C5:J6');l(sources,'C5','Source: locally generated fixture, seed20261124. Data are not exchange prices. Full source/data/config hashes are recorded in artifacts/foundation/results.json.');sources.getRange('C5:J6').format.wrapText=true;
l(sources,'C8','Fixture SHA256');sources.mergeCells('D8:J8');l(sources,'D8',data.data_sha256);l(sources,'C9','Run ID');l(sources,'D9',data.run_id);
for(const [i,key] of data.research_gate.missing.entries()){l(sources,'C'+(12+i),key.replaceAll('_',' '));l(sources,'F'+(12+i),'NOT VERIFIED');}
sources.mergeCells('C22:J24');l(sources,'C22','Provider intake is pending. A direct Stooq CSV request failed DNS in this environment; the official historical-data page returned a JavaScript browser-verification notice. Adjustment, action and redistribution contracts were not verified. No provider market data is included in this release.');sources.getRange('C22:J24').format.wrapText=true;
sources.mergeCells('C26:J28');l(sources,'C26','Temporal reference: official scikit-learn TimeSeriesSplit documentation. This project implements its own date-group and label-maturity logic; ordinary row-wise time splitting alone does not protect a panel with overlapping forward labels. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html');sources.getRange('C26:J28').format.wrapText=true;
const checks=[];
function compareCase(name,c){
 wb.recalculate();const want=c.ledger,qty=Object.fromEntries(c.trades.map(t=>[t.asset,t.quantity]));
 for(const [cell,expected] of [['D23',want.cash],['D24',want.market_value],['D25',want.nav],['D27',want.fees],...review.assets.map((a,i)=>['J'+(13+i),qty[a.asset]??0])]){
  const got=ex.getRange(cell).values[0][0];if(typeof got!=='number'||Math.abs(got-expected)>1e-6)throw Error(`${name}:${cell} ${got} != ${expected}`);checks.push({case:name,cell,excel:got,python:expected,difference:got-expected});
 }
}
compareCase('baseline',{ledger:review.python_ledger,trades:review.python_trades});v(ex,'D6',30);compareCase('fee_plus20',review.counterfactuals.fee_plus20);v(ex,'D6',10);v(ex,'D5',200000);compareCase('nav_double',review.counterfactuals.nav_double);v(ex,'D5',100000);wb.recalculate();
for(let r=12;r<=15;r++){if(Math.abs(ev.getRange('H'+r).values[0][0]-100)>1e-8)throw Error('Golden event NAV failed');}
for(let r=6;r<windows.length+6;r++)if(wf.getRange('J'+r).values[0][0]!=='PASS')throw Error('Temporal worksheet failed');
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:700})).ndjson);
for(const [name,range] of [['Overview','C2:M38'],['Execution Lab','C2:Q30'],['Event Checks','C2:J21'],['Walk Forward','C2:J21'],['Fixture Ledger','C2:L20'],['Sources','C2:J29']]){const img=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(root,'outputs/previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await img.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'P2_Systematic_Equity_Foundation.xlsx'));
await fs.writeFile(path.join(root,'artifacts/foundation/excel_reconciliation.json'),JSON.stringify({status:'PASS_FIXTURE_ONLY',comparisons:checks.length,event_golden_nav_checks:4,temporal_window_checks:windows.length,checks},null,2));
console.log(JSON.stringify({sheets:names.length,execution_comparisons:checks.length,event_golden_checks:4,temporal_window_checks:windows.length}));
