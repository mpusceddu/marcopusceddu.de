'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const tz = 'Europe/Berlin';
  const fmt = (n, digits=1) => Number.isFinite(n) ? n.toLocaleString('de-DE',{maximumFractionDigits:digits,minimumFractionDigits:digits}) : '–';
  const {inPeriod, currentPriceIndex} = window.energyModel;
  const stamp = t => new Intl.DateTimeFormat('de-DE',{timeZone:tz,day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit',timeZoneName:'short'}).format(new Date(t*1000));
  const finite = v => typeof v === 'number' && Number.isFinite(v);
  const groups = [
    {label:'Wind',color:'#087b7c',names:['Wind offshore','Wind onshore']},
    {label:'Sonne',color:'#e8b53b',names:['Solar']},
    {label:'Wasser',color:'#588cb3',names:['Hydro Run-of-River','Hydro water reservoir']},
    {label:'Biomasse',color:'#72915d',names:['Biomass','Geothermal']},
    {label:'Kohle',color:'#49545f',names:['Fossil brown coal / lignite','Fossil hard coal']},
    {label:'Gas',color:'#ba815d',names:['Fossil gas','Fossil coal-derived gas']},
    {label:'Speicher',color:'#9a83ab',names:['Hydro pumped storage']},
    {label:'Weitere',color:'#a7ada7',names:['Fossil oil','Others','Waste','Nuclear']}
  ];
  const countries = {'Austria':'Österreich','Belgium':'Belgien','Czech Republic':'Tschechien','Denmark':'Dänemark','France':'Frankreich','Luxembourg':'Luxemburg','Netherlands':'Niederlande','Norway':'Norwegen','Poland':'Polen','Sweden':'Schweden','Switzerland':'Schweiz'};
  let data;
  const selected = () => $('period').value;
  function indices(dataset, period=selected()) {
    return dataset.unix_seconds.map((t,i)=>({t,i})).filter(({t})=>inPeriod(t,period,Date.now()/1000));
  }
  function rows(dataset, list, period=selected()) {
    return indices(dataset,period).map(({t,i})=>({t,values:list.map(s=>s.data[i])}));
  }
  function latest(dataset,list) {
    return rows(dataset,list,'today').filter(r=>r.t<=Date.now()/1000 && r.values.every(finite)).at(-1);
  }
  const el = (tag,attrs={},content='') => {
    const node=document.createElementNS('http://www.w3.org/2000/svg',tag);
    for(const [k,v] of Object.entries(attrs))node.setAttribute(k,v);
    node.textContent=content;return node;
  };
  function chart(target, records, series, unit, stacked=false) {
    const host=$(target), tableWasOpen=host.querySelector('details')?.open;host.replaceChildren();
    if(!records.some(r=>r.values.some(finite))){host.className='energy-empty';host.textContent='Für diesen Zeitraum liegen noch keine Daten vor.';return;}
    host.className='energy-chart-wrap';
    const w=Math.max(280,host.clientWidth||1000),h=310,l=52,r=16,top=28,b=50,inner=w-l-r,high=h-top-b;
    const all=records.flatMap(row=>stacked?[row.values.every(finite)?row.values.reduce((a,v)=>a+v,0):null]:row.values).filter(finite);
    let min=Math.min(0,...all),max=Math.max(1,...all);const margin=(max-min)*.08; if(min<0)min-=margin;max+=margin;
    if(unit==='%'){min=0;max=Math.max(100,max);}
    const first=records[0].t,last=records.at(-1).t,span=Math.max(900,last-first+(stacked?900:0));
    const x=t=>l+(t-first)/span*inner,y=v=>top+(max-v)/(max-min)*high;
    const svg=el('svg',{viewBox:`0 0 ${w} ${h}`,role:'img','aria-label':`${host.dataset.title}. Einheit: ${unit}. Genaue Werte in der Datentabelle.`,class:'energy-chart'});
    for(let j=0;j<=4;j++){const val=min+(max-min)*j/4;svg.append(el('line',{x1:l,x2:w-r,y1:y(val),y2:y(val),class:'grid'}),el('text',{x:l-10,y:y(val)+4,'text-anchor':'end'},fmt(val,0)));}
    svg.append(el('text',{x:l,y:17},unit),el('line',{x1:l,x2:w-r,y1:y(0),y2:y(0),class:'zero'}));
    [0,.5,1].forEach(f=>{const t=first+span*f;const label=new Intl.DateTimeFormat('de-DE',{timeZone:tz,...(selected()==='week'?{day:'2-digit',month:'2-digit'}:{hour:'2-digit',minute:'2-digit',timeZoneName:'short'})}).format(new Date(t*1000));svg.append(el('text',{x:x(t),y:h-12,'text-anchor':f===0?'start':f===1?'end':'middle'},label));});
    if(stacked){
      records.forEach((row,i)=>{if(!row.values.every(finite))return;let base=0;const next=records[i+1]?.t;const end=next&&next-row.t<=1800?next:row.t+900;const barWidth=Math.max(.4,(end-row.t)/span*inner-.2);
        row.values.forEach((v,j)=>{const bar=el('rect',{x:x(row.t),y:y(base+v),width:Math.min(barWidth,w-r-x(row.t)),height:Math.max(0,y(base)-y(base+v)),fill:series[j].color});bar.append(el('title',{},`${stamp(row.t)} · ${series[j].label}: ${fmt(v,2)} ${unit}`));svg.append(bar);base+=v;});
      });
    } else {
      series.forEach((s,j)=>{let path='',prev=null;records.forEach(row=>{const v=row.values[j];if(!finite(v)){prev=null;return;}const contiguous=prev!==null&&row.t-prev<=1800;path+=`${contiguous?'L':'M'}${x(row.t).toFixed(2)},${y(v).toFixed(2)} `;prev=row.t;});svg.append(el('path',{d:path,fill:'none',stroke:s.color,'stroke-width':2.5,'stroke-linejoin':'round'}));});
    }
    host.append(svg);
    const legend=document.createElement('div');legend.className='energy-legend';series.forEach(s=>{const item=document.createElement('span');item.style.setProperty('--swatch',s.color);item.textContent=s.label;legend.append(item);});host.append(legend);
    const detail=document.createElement('details'),summary=document.createElement('summary');detail.open=!!tableWasOpen;summary.textContent='Werte als Tabelle ansehen';detail.append(summary);
    const wrap=document.createElement('div');wrap.className='energy-table-wrap';wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label',host.dataset.title+' – Datentabelle');
    const table=document.createElement('table');table.className='energy-table';
    const caption=document.createElement('caption');caption.textContent=host.dataset.title+' · '+unit;table.append(caption);
    const head=document.createElement('thead'),tr=document.createElement('tr');['Zeit (Berlin)',...series.map(s=>s.label)].forEach(t=>{const th=document.createElement('th');th.scope='col';th.textContent=t;tr.append(th);});head.append(tr);table.append(head);
    const body=document.createElement('tbody');records.forEach(row=>{const tr=document.createElement('tr');[stamp(row.t),...row.values.map(v=>finite(v)?fmt(v,2):'Keine Daten')].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td);});body.append(tr);});table.append(body);wrap.append(table);detail.append(wrap);host.append(detail);
  }
  function render(){
    const p=data.power;const map=Object.fromEntries(p.production_types.map(s=>[s.name,s]));
    const excluded=new Set(['Hydro pumped storage consumption','Cross border electricity trading','Load','Residual load','Renewable share of load','Renewable share of generation']);
    const known=new Set(groups.flatMap(g=>g.names));
    const extra=p.production_types.filter(s=>!excluded.has(s.name)&&!known.has(s.name));
    const grouped=groups.map((g,idx)=>({name:g.label,data:p.unix_seconds.map((_,i)=>{const found=[...g.names.map(n=>map[n]).filter(Boolean),...(idx===groups.length-1?extra:[])];return found.length===0?0:found.every(s=>finite(s.data[i])&&s.data[i]>=0)?found.reduce((a,s)=>a+s.data[i],0)/1000:null;})}));
    chart('power-chart',rows(p,grouped),groups,'GW',true);
    window.energyMix.renderMix(rows(p,grouped),groups);
    const share=map['Renewable share of generation'];
    chart('share-chart',rows(p,share?[share]:[]),[{label:'Erneuerbare an der Erzeugung',color:'#087b7c'}],'%');
    const priceDataset=selected()==='tomorrow'?data.tomorrow:data.price;
    const priceRows=priceDataset.unix_seconds.map((t,i)=>({t,values:[finite(priceDataset.price[i])?priceDataset.price[i]/10:null]})).filter(r=>inPeriod(r.t,selected(),Date.now()/1000));
    chart('price-chart',priceRows,[{label:'Day-Ahead-Börsenpreis',color:'#087b7c'}],'ct/kWh');
    const flowSeries=data.flows.countries.filter(s=>s.name.toLowerCase()!=='sum');
    const flowRows=indices(data.flows).map(({t,i})=>({t,values:flowSeries.every(s=>finite(s.data[i]))?[flowSeries.reduce((a,s)=>a+Math.max(0,s.data[i]),0),-flowSeries.reduce((a,s)=>a+Math.min(0,s.data[i]),0)]:[null,null]}));
    chart('flow-chart',flowRows,[{label:'Import',color:'#087b7c'},{label:'Export',color:'#ba815d'}],'GW');
    const srow=share&&latest(p,[share]),grow=latest(p,grouped),frow=latest(data.flows,flowSeries);
    $('share-number').textContent=srow?fmt(srow.values[0])+' %':'Keine Daten';
    $('share-time').textContent=srow?'Intervallbeginn '+stamp(srow.t):'Heute noch keine vollständigen Daten';
    const currentPrice=currentPriceIndex(data.price.unix_seconds,Date.now()/1000);
    $('price-number').textContent=currentPrice>=0&&finite(data.price.price[currentPrice])?fmt(data.price.price[currentPrice]/10,2)+' ct/kWh':'Keine Daten';
    $('price-time').textContent=currentPrice>=0?'Intervallbeginn '+stamp(data.price.unix_seconds[currentPrice]):'Kein Preis für das aktuelle Intervall';
    const net=frow?frow.values.reduce((a,v)=>a+v,0):null;
    $('flow-number').textContent=finite(net)?fmt(Math.abs(net),2)+' GW':'Keine Daten';
    $('flow-label').textContent=finite(net)?(net>=0?'Importüberschuss':'Exportüberschuss'):'Stromfluss-Saldo';
    $('flow-time').textContent=frow?'Intervallbeginn '+stamp(frow.t):'Heute noch keine vollständigen Daten';
    $('power-time').textContent=grow?'Letzte vollständige Werte: '+stamp(grow.t):'Heute keine vollständigen Werte';
    const importGW=frow?frow.values.reduce((sum,v)=>sum+Math.max(0,v),0):null;
    const exportGW=frow?-frow.values.reduce((sum,v)=>sum+Math.min(0,v),0):null;
    $('import-number').textContent=finite(importGW)?fmt(importGW,2)+' GW':'Keine Daten';
    $('export-number').textContent=finite(exportGW)?fmt(exportGW,2)+' GW':'Keine Daten';
    $('flow-net-number').textContent=finite(net)?fmt(Math.abs(net),2)+' GW':'Keine Daten';
    $('flow-net-label').textContent=finite(net)?(net>0?'Importüberschuss':net<0?'Exportüberschuss':'Ausgeglichener Saldo'):'Saldo';
    $('flow-observation-time').textContent=frow?'Letzte vollständige Länderwerte · Intervallbeginn '+stamp(frow.t):'Heute noch keine vollständigen Länderwerte';
    const totals=window.energyModel.flowTotals(flowRows,Date.now()/1000);
    $('flow-period-total').textContent=totals?'Im gewählten Zeitraum erfasst: '+fmt(totals.importGWh)+' GWh Import · '+fmt(totals.exportGWh)+' GWh Export. '+stamp(totals.start)+' bis '+stamp(totals.end)+'. Nur vollständige Viertelstunden; keine Hochrechnung auf Datenlücken.':'Im gewählten Zeitraum fehlen vollständige Viertelstunden für eine Strommengenbilanz.';
    const countryList=$('flow-country-list');countryList.replaceChildren();
    if(frow){
      flowSeries.map((series,i)=>({name:countries[series.name]||series.name,value:frow.values[i]})).sort((a,b)=>Math.abs(b.value)-Math.abs(a.value)).forEach(country=>{
        const li=document.createElement('li'),name=document.createElement('span'),direction=document.createElement('span'),amount=document.createElement('strong');
        name.textContent=country.name;
        direction.className='flow-direction '+(country.value>0?'import':country.value<0?'export':'balanced');
        direction.textContent=country.value>0?'→ nach Deutschland':country.value<0?'← aus Deutschland':'Kein Nettofluss';
        amount.textContent=fmt(Math.abs(country.value),2)+' GW';
        li.append(name,direction,amount);countryList.append(li);
      });
    }else{const li=document.createElement('li');li.textContent='Noch keine vollständigen Länderwerte für heute.';countryList.append(li);}
    const newest=Math.min(grow?.t||0,frow?.t||0),stale=Date.now()/1000-newest>7200;
    const failed=Object.keys(data.fetch_errors||{}), labels={power:'Erzeugung',flows:'Stromflüsse',price:'Börsenpreise'};
    const fetchStale=Date.now()-Date.parse(data.fetched_at)>2*3600*1000;
    $('data-status').className='energy-status'+(stale||failed.length||fetchStale?' warning':'');
    $('data-status').textContent=(failed.length?'Abruf derzeit gestört: '+failed.map(k=>labels[k]||k).join(', ')+'. Letzter gültiger Stand bleibt sichtbar. ':stale?'Erzeugung oder Stromflüsse sind derzeit verzögert. ':'')+(fetchStale?'Der gespeicherte Datenstand ist älter als zwei Stunden. ':'')+'Letzter erfolgreicher Abruf: '+stamp(Date.parse(data.fetched_at)/1000)+'. Alle Zeiten Europe/Berlin.';
    $('generation-sections').hidden=selected()==='tomorrow';
    $('generation-sections-after').hidden=selected()==='tomorrow';
    $('period-description').textContent=selected()==='tomorrow'?'Morgen: nur bereits veröffentlichte Börsenpreise. Erzeugung und Stromflüsse werden nicht vorhergesagt.':selected()==='week'?'Sieben Kalendertage einschließlich heute. Der laufende Tag ist unvollständig.':'Heute: verfügbare Messwerte und veröffentlichte Börsenpreise. Der laufende Tag ist unvollständig.';
  }
  let loading=false;
  async function loadData(){
    if(loading)return;
    loading=true;
    try{
      const response=await fetch('/assets/data/strom-im-blick.json',{cache:'no-cache',signal:AbortSignal.timeout(15000)});
      if(!response.ok)throw Error(response.status);
      const next=await response.json();
      if(!next.power?.production_types||!next.flows?.countries||!next.price?.price||!next.tomorrow?.price)throw Error('Unvollständige Daten');
      const firstLoad=!data;
      data=next;render();$('period').disabled=false;
      // Initial asynchronous chart layout must not displace a requested section.
      if(firstLoad&&['#flow-title','#merit-title','#mix-title','#price-title','#household-title'].includes(location.hash)){
        requestAnimationFrame(()=>document.getElementById(location.hash.slice(1))?.scrollIntoView({block:'start',behavior:'instant'}));
      }
    }catch{
      if(data)render();
      $('data-status').textContent='Der Datenstand konnte nicht aktualisiert werden. '+(data?'Die zuletzt geladenen Werte bleiben sichtbar. ':'Bitte später erneut versuchen oder die Originalcharts öffnen.');
      $('data-status').className='energy-status warning';
    }finally{loading=false;}
  }
  $('period').addEventListener('change',render);
  document.querySelector('.energy-jump a[href="#mix-title"]').addEventListener('click',()=>{if(data&&selected()==='tomorrow'){$('period').value='today';render();}});
  let resizing;window.addEventListener('resize',()=>{clearTimeout(resizing);resizing=setTimeout(()=>{if(data)render();},120);});
  // Visitors only read our shared snapshot, never the Fraunhofer API directly.
  setInterval(()=>{if(!document.hidden)loadData();},5*60*1000);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)loadData();});
  loadData();
})();
