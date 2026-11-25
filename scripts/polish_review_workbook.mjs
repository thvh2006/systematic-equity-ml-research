import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'deliverables/P2_Systematic_Equity_Research.xlsx')));
const out=path.join(root,'outputs/polish');await fs.mkdir(out,{recursive:true});
if(process.argv.includes('--inspect')){
 console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:3000})).ndjson);
 for(const [sheetName,range] of [['Comparison','A1:J9'],['Execution Lab','A1:M24']]){const b=await wb.render({sheetName,range,scale:1.3});await fs.writeFile(path.join(out,sheetName.replaceAll(' ','_')+'_before.png'),new Uint8Array(await b.arrayBuffer()));}
 process.exit(0);
}
const b=JSON.parse(await fs.readFile(path.join(root,'artifacts/research/public_bundle.json'),'utf8'));
const analysis=b.analysis,comp=wb.worksheets.getItem('Comparison'),lab=wb.worksheets.getItem('Execution Lab');
const money='#,##0.00;(#,##0.00);"-"',pct='0.00%;(0.00%);"-"';
const names=Object.keys(b.results);
const band=(s,r)=>{s.getRange(r).format={fill:'#17374B',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:27,wrapText:true};};
comp.getRange('A1:J75').format.font={name:'Arial',size:11,color:'#163346'};
comp.getRange('A1:A75').format.columnWidth=31;comp.getRange('B1:J75').format.columnWidth=17;comp.getRange('A1:J75').format.rowHeight=23;
comp.getRange('A1:J1').values=[['Policy','Net CAGR','Total return','Volatility','Sharpe*','Max drawdown','Turnover / year','Fees ($)','Slippage ($)','Final NAV ($)']];band(comp,'A1:J1');comp.getRange('A1:J1').format.rowHeight=38;
comp.getRange('B2:D6').setNumberFormat(pct);comp.getRange('F2:F6').setNumberFormat(pct);comp.getRange('E2:E6').setNumberFormat('0.000');comp.getRange('G2:G6').setNumberFormat('0.00"x"');comp.getRange('H2:J6').setNumberFormat(money);
comp.getRange('A8').values=[['Post-study relative review. Separate from the frozen model-selection decision.']];
comp.getRange('A10:B10').values=[['Review control','Selection']];band(comp,'A10:B10');
comp.getRange('A11:B12').values=[['Selected policy','stumps_24'],['Comparator','momentum_63']];
comp.getRange('B11').dataValidation={rule:{type:'list',values:['stumps_24']}};
comp.getRange('B12').dataValidation={rule:{type:'list',values:['momentum_63','equal_weight']}};comp.getRange('B11:B12').format.font.color='#0000FF';comp.getRange('B11:B12').format.fill='#FFF4D7';
comp.getRange('A15:B15').values=[['Comparative bridge ($)','Calculated difference']];band(comp,'A15:B15');
comp.getRange('A16:A22').values=[['Zero-cost final NAV gap'],['Differential friction effect'],['Net final NAV gap'],['Fund contribution sum'],['Contribution residual'],['ML average equity exposure'],['Comparator equity exposure']];
comp.getRange('B16').formulas=[["=INDEX('Costs'!$J$2:$J$16,MATCH(B11&\"__cost0\",'Costs'!$A$2:$A$16,0))-INDEX('Costs'!$J$2:$J$16,MATCH(B12&\"__cost0\",'Costs'!$A$2:$A$16,0))"]];
comp.getRange('B18').formulas=[['=INDEX($J$2:$J$6,MATCH(B11,$A$2:$A$6,0))-INDEX($J$2:$J$6,MATCH(B12,$A$2:$A$6,0))']];
comp.getRange('B17').formulas=[['=B18-B16']];comp.getRange('B19').formulas=[['=SUM(H16:H24)']];comp.getRange('B20').formulas=[['=ROUND(B19-B18,8)']];
// Saved exposure descriptions are inputs; the bridge does not treat exposure as causal alpha.
comp.getRange('L10:M12').values=[['Policy','Mean equity exposure'],...['stumps_24','momentum_63'].map(n=>[n,analysis.strategies[n].exposures.reduce((s,x)=>s+Object.values(x.weights).reduce((s,v)=>s+v,0),0)/analysis.strategies[n].exposures.length])];
comp.getRange('L13:M13').values=[['equal_weight',analysis.strategies.equal_weight.exposures.reduce((s,x)=>s+Object.values(x.weights).reduce((s,v)=>s+v,0),0)/analysis.strategies.equal_weight.exposures.length]];
comp.getRange('B21').formulas=[['=INDEX($M$11:$M$13,MATCH(B11,$L$11:$L$13,0))']];comp.getRange('B22').formulas=[['=INDEX($M$11:$M$13,MATCH(B12,$L$11:$L$13,0))']];
comp.getRange('B16:B20').setNumberFormat(money);comp.getRange('B21:B22').setNumberFormat(pct);
comp.getRange('A25').values=[['Gap = ML minus comparator; friction effect includes sizing and compounding.']];
comp.getRange('A26').values=[['Fund differences reconcile dollars; they are not a Brinson/causal skill decomposition.']];
comp.getRange('E15:H15').values=[['Fund','ML P&L ($)','Comparator P&L ($)','Difference ($)']];band(comp,'E15:H15');
for(let i=0;i<9;i++){let row=16+i;comp.getRange(`E${row}`).values=[[b.config.universe[i]]];comp.getRange(`F${row}:H${row}`).formulas=[[
 `=SUMIFS('Attribution'!$C$2:$C$38,'Attribution'!$A$2:$A$38,$B$11,'Attribution'!$B$2:$B$38,E${row})`,
 `=SUMIFS('Attribution'!$C$2:$C$38,'Attribution'!$A$2:$A$38,$B$12,'Attribution'!$B$2:$B$38,E${row})`,`=F${row}-G${row}`]];}
comp.getRange('F16:H24').setNumberFormat(money);comp.getRange('E1:E75').format.columnWidth=20;comp.getRange('F15:H24').format.columnWidth=24;
comp.getRange('B20').conditionalFormats.add('cellIs',{operator:'notBetween',formula:[-0.000001,0.000001],format:{fill:'#FDE2E2',font:{color:'#9B1C1C',bold:true}}});
comp.getRange('A30:D30').values=[['Month','ML wealth','Comparator wealth','Relative wealth']];band(comp,'A30:D30');
comp.getRange('A31:D31').values=[['Start',100000,100000,0]];
for(let i=0;i<36;i++){const r=32+i,m=i+2;comp.getRange(`A${r}`).formulas=[[`='Monthly'!A${m}`]];comp.getRange(`B${r}:D${r}`).formulas=[[
 `=${'B'+(r-1)}*(1+INDEX('Monthly'!$B$2:$F$37,${i+1},MATCH($B$11,'Monthly'!$B$1:$F$1,0)))`,
 `=${'C'+(r-1)}*(1+INDEX('Monthly'!$B$2:$F$37,${i+1},MATCH($B$12,'Monthly'!$B$1:$F$1,0)))`,`=B${r}/C${r}-1`]];}
comp.getRange('B31:C67').setNumberFormat(money);comp.getRange('D31:D67').setNumberFormat(pct);
comp.deleteAllDrawings();const ch=comp.charts.add('line',comp.getRange('A30:A67'));ch.title='Relative wealth: ML / comparator - 1';ch.setPosition('F30','L47');
const se=ch.series.add('Relative wealth');se.categoryFormula="'Comparison'!$A$31:$A$67";se.formula="'Comparison'!$D$31:$D$67";se.line={fill:'#087E8B',width:2};ch.hasLegend=false;ch.xAxis={tickLabelInterval:6,tickLabelPosition:'low',majorGridlines:null,minorGridlines:null};ch.yAxis={numberFormatCode:'0.0%'};
// Display a valid scenario state rather than treating missing inputs as zeros.
lab.getRange('A1:M35').format.font={name:'Arial',size:11,color:'#163346'};lab.getRange('A1:M35').format.rowHeight=25;lab.getRange('A1:A35').format.columnWidth=32;lab.getRange('B1:M35').format.columnWidth=17;band(lab,'A7:M7');lab.getRange('A7:M7').format.rowHeight=38;
lab.getRange('B2:B5').format.font.color='#0000FF';lab.getRange('B2:B5').format.fill='#FFF4D7';lab.getRange('B8:B16').setNumberFormat(pct);lab.getRange('C8:D16').setNumberFormat(money);lab.getRange('E8:G16').setNumberFormat('#,##0');lab.getRange('H8:M16').setNumberFormat(money);lab.getRange('J8:J16').setNumberFormat('#,##0');lab.getRange('B19:B21').setNumberFormat(money);
lab.getRange('A21').values=[['Scenario minus saved default']];lab.getRange('A23').values=[['Saved default is fixed. Changing blue drivers creates an independent scenario.']];
lab.getRange('D2').values=[['Input status']];lab.getRange('E2').formulas=[['=IF(AND(COUNT(B2:B5)=4,B2>0,B3>=0,B4>=0,B5>0,B5<=1),"Valid scenario","Missing or invalid driver")']];
lab.getRange('D4').values=[['Raw scenario NAV']];lab.getRange('E4').formulas=[['=L16+SUM(M8:M16)']];lab.getRange('E4').setNumberFormat(money);lab.getRange('B19').formulas=[['=IF(E2="Valid scenario",E4,"Unavailable")']];lab.getRange('B21').formulas=[['=IF(ISNUMBER(B19),B19-B20,"Unavailable")']];
lab.getRange('B5').dataValidation={rule:{type:'decimal',operator:'between',formula1:0.000001,formula2:1}};
const needsTable=lab.getRange('A27').values[0][0]!=='Fee/slippage sensitivity';lab.getRange('A27').values=[['Fee/slippage sensitivity']];lab.getRange('A28').values=[['Fee across; slippage down (bp)']];lab.getRange('B29').formulas=[['=E4']];lab.getRange('C29:F29').values=[[0,1,10,21]];lab.getRange('B30:B32').values=[[0],[5],[10]];
if(needsTable)lab.dataTables.add('B29:F32',{rowInput:'B3',columnInput:'B4'});lab.getRange('B29').setNumberFormat(';;;');lab.getRange('D31').format.fill='#E9EFF2';lab.getRange('C30:F32').setNumberFormat(money);lab.getRange('C29:F29').format.font.bold=true;lab.getRange('B30:B32').format.font.bold=true;
wb.worksheets.getItem('Read Me').getRange('A11:B13').values=[['Release 0.4','Comparison now includes a formula-driven comparator, relative wealth and fund bridge.'],['Sensitivity','Execution Lab fee/slippage grid is a native two-input What-If Data Table.'],['Scope','Post-study review only; original model selection, source/config and test retained.']];
wb.recalculate();
const v=b.review;const get=(s,r)=>s.getRange(r).values[0][0];
function close(x,y,label){if(typeof x!=='number'||Math.abs(x-y)>1e-6)throw Error(label+': '+x+' != '+y);}
close(get(lab,'B19'),v.python_ledger.nav,'default NAV');close(get(lab,'D31'),v.python_ledger.nav,'native table base');
for(const n of ['momentum_63','equal_weight']){comp.getRange('B12').values=[[n]];close(get(comp,'B18'),b.results.stumps_24.metrics.final_nav-b.results[n].metrics.final_nav,'net gap');close(get(comp,'B20'),0,'contribution bridge');close(get(comp,'D67'),b.results.stumps_24.metrics.final_nav/b.results[n].metrics.final_nav-1,'relative wealth');}
comp.getRange('B12').values=[['momentum_63']];lab.getRange('B3').values=[[21]];close(get(lab,'B19'),v.counterfactuals.fee_plus20.ledger.nav,'fee counterfactual');lab.getRange('B3').values=[[1]];lab.getRange('B2').values=[[200000]];close(get(lab,'B19'),v.counterfactuals.nav_double.ledger.nav,'capital counterfactual');lab.getRange('B2').values=[[null]];if(get(lab,'B19')!=='Unavailable')throw Error('Blank capital not blocked');lab.getRange('B2').values=[[100000]];wb.recalculate();
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Formula errors'})).ndjson);
for(const [sheetName,range] of [['Comparison','A10:J26'],['Comparison','A30:L48'],['Execution Lab','A1:M23'],['Execution Lab','A27:F34']]){const preview=await wb.render({sheetName,range,scale:1.4});await fs.writeFile(path.join(out,sheetName.replaceAll(' ','_')+'_'+range.replace(':','-')+'.png'),new Uint8Array(await preview.arrayBuffer()));}
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'deliverables/P2_Systematic_Equity_Research.xlsx'));
console.log(JSON.stringify({sheets:19,comparator_checks:2,scenario_checks:3,native_sensitivity_base:get(lab,'D31'),default_nav:get(lab,'B19')}));
