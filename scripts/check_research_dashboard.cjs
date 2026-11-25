// Execute dashboard logic with a DOM harness. Browser review is separate.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),page=fs.readFileSync(path.join(root,'index.html'),'utf8');
class Element{constructor(id){this.id=id;this.children=[];this.value=({capital:'100000',fee:'1',slip:'5',chartType:'nav'})[id]||'';this.attributes={};this.listeners={};this.hidden=false;this.textContent='';this.html=''}append(x){this.children.push(x);if(!this.value)this.value=x.value}setAttribute(k,v){this.attributes[k]=v}addEventListener(k,f){this.listeners[k]=f}set innerHTML(x){this.html=x;if(x==='')this.children=[]}get innerHTML(){return this.html}}
const elements={},document={getElementById(id){return elements[id]??=new Element(id)},createElement(){return new Element('new')}};
const context={document,location:{pathname:'/index.html'}};vm.createContext(context);vm.runInContext(page.match(/<script>([\s\S]*?)<\/script>/)[1],context);
assert.equal(elements.navigation.children.length,8);assert.equal(elements.strategy.children.length,5);
for(const view of elements.navigation.children){view.listeners.click();assert.equal(view.attributes['aria-selected'],'true')}
for(const option of elements.strategy.children){elements.strategy.value=option.value;for(const type of ['nav','drawdown']){elements.chartType.value=type;vm.runInContext('backtest()',context);assert.ok(elements.navChart.innerHTML.includes('<polyline'));assert.ok(!elements.navChart.innerHTML.includes('NaN'));assert.ok(elements.navDetail.textContent.includes(option.value));assert.ok(elements.holdings.innerHTML.includes('Cash'))}}
const v=JSON.parse(fs.readFileSync(path.join(root,'artifacts/research/review_case.json')));
for(const [name,nav,fee,expected] of [['base',v.initial_nav,v.fee_bps,v.python_ledger],['fee_plus20',v.initial_nav,v.fee_bps+20,v.counterfactuals.fee_plus20.ledger],['nav_double',2*v.initial_nav,v.fee_bps,v.counterfactuals.nav_double.ledger]]){
 elements.capital.value=String(nav);elements.fee.value=String(fee);vm.runInContext('lab()',context);
 let cash=nav,mv=0;for(const a of v.assets){const px=a.raw_open*(1+v.slippage_bps/1e4),q=Math.min(Math.floor(nav*a.target_weight/a.raw_open),Math.floor(a.volume*v.participation),Math.floor(Math.max(0,cash)/(px*(1+fee/1e4))));cash-=q*px*(1+fee/1e4);mv+=q*a.raw_close}
 assert.ok(Math.abs(cash-expected.cash)<1e-7);assert.ok(Math.abs(cash+mv-expected.nav)<1e-7);assert.ok(elements.labSummary.textContent.includes((cash+mv).toLocaleString('en-US',{maximumFractionDigits:2})));
}
elements.capital.value='-1';vm.runInContext('lab()',context);assert.ok(elements.labSummary.textContent.includes('positive capital'));
console.log(JSON.stringify({navigation_views:8,saved_strategy_chart_combinations:10,independent_rebalance_scenarios:3,invalid_input_rejected:true,browser_render_verified:false}));
