const {test}=require('node:test');
const assert=require('node:assert/strict');
const {dayKey,shiftDay,inPeriod,currentPriceIndex}=require('../assets/js/energy-model.js');
const t=s=>Date.parse(s)/1000;

test('German calendar remains correct on a 25-hour day',()=>{
  const now=t('2026-10-25T00:15:00+02:00');
  assert.equal(dayKey(now),'2026-10-25');
  assert.equal(shiftDay(dayKey(now),1),'2026-10-26');
  assert.equal(inPeriod(t('2026-10-25T23:45:00+01:00'),'today',now),true);
  assert.equal(inPeriod(t('2026-10-26T00:00:00+01:00'),'tomorrow',now),true);
});
test('seven calendar days exclude both older and future observations',()=>{
  const now=t('2026-10-25T17:00:00+01:00');
  assert.equal(inPeriod(t('2026-10-19T00:00:00+02:00'),'week',now),true);
  assert.equal(inPeriod(t('2026-10-18T23:45:00+02:00'),'week',now),false);
  assert.equal(inPeriod(t('2026-10-26T00:00:00+01:00'),'week',now),false);
});
test('calendar arithmetic also handles spring DST and year boundaries',()=>{
  assert.equal(shiftDay('2026-03-29',1),'2026-03-30');
  assert.equal(shiftDay('2026-12-31',1),'2027-01-01');
  assert.equal(shiftDay('2027-01-01',-6),'2026-12-26');
});
test('price gaps do not extend the preceding delivery period',()=>{
  assert.equal(currentPriceIndex([1000,2800],2000),-1);
  assert.equal(currentPriceIndex([1000,1900],1900),1);
  assert.equal(currentPriceIndex([1000,1900],2800),-1);
});

const {generationMix,meritOrder}=require('../assets/js/energy-model.js');
test('generation shares integrate power as energy without bridging missing intervals',()=>{
  const result=generationMix([{t:0,values:[1,3]},{t:1800,values:[3,1]}],2700);
  assert.equal(result.total,2);
  assert.deepEqual(result.energy,[1,1]);
  assert.deepEqual(result.shares,[50,50]);
  assert.equal(result.intervals,2);
});
test('missing or unfinished intervals cannot distort the generation mix',()=>{
  const result=generationMix([{t:0,values:[1,3]},{t:900,values:[null,2]},{t:1800,values:[100,0]}],2000);
  assert.equal(result.total,1);
  assert.deepEqual(result.shares,[25,75]);
  assert.equal(generationMix([{t:0,values:[0,0]}],900).total,0);
});
test('the marginal accepted offer sets one price, not an average of bids',()=>{
  const offers=[{label:'A',capacity:35,price:0},{label:'B',capacity:20,price:6},{label:'C',capacity:20,price:12}];
  const result=meritOrder(offers,65);
  assert.equal(result.price,12);
  assert.equal(result.marginal.label,'C');
  assert.deepEqual(result.offers.map(o=>o.accepted),[35,20,10]);
  assert.equal(meritOrder(offers,55).price,6);
});
test('more cheap supply can lower price, while a shortage has no clearing price in this model',()=>{
  assert.equal(meritOrder([{capacity:60,price:0},{capacity:20,price:6}],55).price,0);
  assert.equal(meritOrder([{capacity:10,price:0},{capacity:20,price:6}],40).price,null);
  assert.equal(meritOrder([{capacity:10,price:0},{capacity:20,price:6}],40).unmet,10);
});
test('merit order sorts bids, supports negative prices, and rejects invalid assumptions',()=>{
  const offers=[{capacity:10,price:6},{capacity:20,price:-2}];
  assert.equal(meritOrder(offers,10).price,-2);
  assert.equal(offers[0].price,6);
  assert.throws(()=>meritOrder([{capacity:-1,price:0}],5));
});

const {marketContext}=require('../assets/js/energy-model.js');
const contextFixture=()=>({
  power:{unix_seconds:[1000,1900,2800],production_types:[
    {name:'Load',data:[5000,6000,7000]},
    {name:'Wind onshore',data:[1000,2000,3000]},
    {name:'Wind offshore',data:[500,500,500]},
    {name:'Solar',data:[200,200,200]},
    {name:'Hydro Run-of-River',data:[50,50,50]}]},
  prices:{unix_seconds:[1000,1900],price:[60,80],unit:'EUR / MWh'}
});
test('market context uses the latest exactly matching completed delivery interval',()=>{
  const {power,prices}=contextFixture();const result=marketContext(power,prices,4000);
  assert.equal(result.timestamp,1900);
  assert.equal(result.marketPriceCt,8);
  assert.equal(result.loadGW,6);
  assert.equal(result.cheapGW,2.75);
  assert.equal(marketContext(power,{...prices,unix_seconds:[1000,1901]},4000).timestamp,1000);
});
test('context skips future, unfinished and incomplete production periods',()=>{
  const {power,prices}=contextFixture();
  assert.equal(marketContext(power,prices,2700).timestamp,1000);
  power.production_types[0].data[1]=null;
  assert.equal(marketContext(power,prices,4000).timestamp,1000);
  power.production_types[0].data[0]=NaN;
  assert.equal(marketContext(power,prices,4000),null);
});
test('observed negative and zero prices and zero renewable production remain valid',()=>{
  const {power,prices}=contextFixture();
  for(const series of power.production_types)series.data[1]=0;
  prices.price[1]=-10;
  const result=marketContext(power,prices,4000);
  assert.equal(result.marketPriceCt,-1);
  assert.equal(result.cheapGW,0);
  assert.equal(result.loadGW,0);
  prices.price[1]=0;
  assert.equal(marketContext(power,prices,4000).marketPriceCt,0);
});
test('incompatible units or missing required source series have no market context',()=>{
  const {power,prices}=contextFixture();
  assert.equal(marketContext(power,{...prices,unit:'ct/kWh'},4000),null);
  power.production_types.pop();
  assert.equal(marketContext(power,prices,4000),null);
});
test('old context is marked delayed and expires after seven days',()=>{
  const {power,prices}=contextFixture();
  assert.equal(marketContext(power,prices,10000).delayed,true);
  assert.equal(marketContext(power,prices,700000),null);
});
