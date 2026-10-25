'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const fmt = (n,digits=1) => n.toLocaleString('de-DE',{minimumFractionDigits:digits,maximumFractionDigits:digits});
  const time = t => new Intl.DateTimeFormat('de-DE',{timeZone:'Europe/Berlin',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit',timeZoneName:'short'}).format(new Date(t*1000));
  let context=null, appliedContext=null, manualScenario=false;
  function applyContext(){
    if(!context)return;
    for(const [id,value] of [['merit-demand',context.loadGW],['merit-renewables',context.cheapGW]]){
      const control=$(id),rounded=Math.round(value*10)/10;
      control.max=String(Math.max(150,Math.ceil(rounded/10)*10));
      control.value=String(rounded);
    }
    appliedContext=context;manualScenario=false;renderMerit();
  }
  function updateContext(data){
    context=data?window.energyModel.marketContext(data.power,data.price,Date.now()/1000):null;
    $('merit-use-data').disabled=!context;
    $('observed-price').textContent=context?fmt(context.marketPriceCt,2)+' ct/kWh':'Keine gemeinsamen Daten';
    $('observed-load').textContent=context?fmt(context.loadGW)+' GW':'–';
    $('observed-cheap').textContent=context?fmt(context.cheapGW)+' GW':'–';
    $('context-time').textContent=context?(context.delayed?'Daten verzögert · ':'')+'Gemeinsames Lieferintervall: '+time(context.timestamp)+' bis '+time(context.timestamp+900):'Für die letzten sieben Tage fehlen vollständige, zeitgleiche Werte für Last, Erzeugung und Preis. Das Erklärmodell lässt sich weiterhin bedienen.';
    $('context-time').classList.toggle('warning',!!context?.delayed);
    $('context-breakdown').textContent=context?`Wind ${fmt(context.windGW)} GW · Sonne ${fmt(context.solarGW)} GW · Laufwasser ${fmt(context.hydroGW)} GW. Beobachtete Werte aus demselben abgeschlossenen Viertelstundenintervall; unabhängig von der Zeitraumwahl oben.`:'';
    if(context&&!manualScenario)applyContext();else renderMerit();
  }
  function renderMix(records, groups) {
    const host=$('generation-mix');host.replaceChildren();
    const mix=window.energyModel.generationMix(records,Date.now()/1000);
    if(!mix.total){host.className='energy-empty';host.textContent='Für den gewählten Zeitraum liegen noch keine vollständigen Erzeugungsintervalle vor.';return;}
    host.className='generation-mix';
    const bar=document.createElement('div');bar.className='mix-strip';bar.setAttribute('aria-hidden','true');
    const list=document.createElement('ul');list.className='mix-list';
    groups.forEach((group,i)=>{
      const segment=document.createElement('span');segment.style.background=group.color;segment.style.flexGrow=mix.energy[i];bar.append(segment);
      const item=document.createElement('li');item.style.setProperty('--swatch',group.color);
      const name=document.createElement('span');name.className='mix-name';name.textContent=group.label;
      const share=document.createElement('strong');share.textContent=fmt(mix.shares[i])+' %';
      const value=document.createElement('span');value.className='mix-amount';value.textContent=fmt(mix.energy[i])+' GWh';
      item.append(name,share,value);list.append(item);
    });
    const summary=document.createElement('p');summary.className='energy-description';
    const time=t=>new Intl.DateTimeFormat('de-DE',{timeZone:'Europe/Berlin',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit',timeZoneName:'short'}).format(new Date(t*1000));
    summary.textContent=`Erfasste Erzeugung: ${fmt(mix.total)} GWh · ${time(mix.start)} bis ${time(mix.end)}. Nur vollständige Viertelstunden mit vollständigen Gruppenwerten; keine Hochrechnung auf fehlende Zeiten. Prozentanteile können durch Rundung abweichen.`;
    host.append(bar,list,summary);
  }
  function renderMerit(){
    const demand=Number($('merit-demand').value),renewables=Number($('merit-renewables').value);
    $('demand-output').textContent=fmt(demand)+' GW';$('renewables-output').textContent=fmt(renewables)+' GW';
    $('model-scenario').textContent=appliedContext?(manualScenario?'Dein verändertes Szenario · Ausgangsdaten: ':'Modell mit übernommenen Messwerten: ')+time(appliedContext.timestamp)+(manualScenario?'':'. Mengen auf 0,1 GW gerundet.'):(manualScenario?'Dein frei gewähltes Szenario':'Erklärmodell mit Beispielmengen; noch keine Messwerte übernommen.');
    const offers=[
      {label:'Wind, Sonne, Laufwasser',capacity:renewables,price:0,color:'#087b7c'},
      {label:'Angebot B',capacity:20,price:6,color:'#72915d'},
      {label:'Angebot C',capacity:20,price:12,color:'#ba815d'},
      {label:'Angebot D',capacity:20,price:20,color:'#49545f'}
    ];
    const result=window.energyModel.meritOrder(offers,demand),host=$('merit-offers');host.replaceChildren();
    result.offers.forEach(offer=>{
      const item=document.createElement('div');item.className='merit-offer'+(result.marginal?.label===offer.label?' marginal':'')+(offer.accepted===0?' unused':'');
      item.style.setProperty('--offer',offer.color);
      const name=document.createElement('strong');name.textContent=offer.label;
      const price=document.createElement('span');price.className='merit-offer-price';price.textContent=fmt(offer.price,0)+' ct/kWh';
      const offered=document.createElement('span');offered.textContent=fmt(offer.capacity)+' GW im Modell angeboten';
      const accepted=document.createElement('span');accepted.textContent=fmt(offer.accepted)+' GW im Modell bezuschlagt';
      const badge=document.createElement('span');badge.className='merit-badge';badge.textContent=result.marginal?.label===offer.label?'Bestimmt den Modellpreis':offer.accepted>0?'Erhält denselben Modellpreis':'Kein Zuschlag';
      item.append(name,price,offered,accepted,badge);host.append(item);
    });
    $('merit-price').textContent=demand===0?'Keine Nachfrage':result.price===null?'Nicht gedeckt':fmt(result.price,0)+' ct/kWh';
    $('merit-result').textContent=demand===0?'Bei 0 GW Nachfrage wird im Modell kein Angebot benötigt.':result.price===null?`Im Modell fehlen ${fmt(result.unmet)} GW Angebot. Für diese Nachfrage lässt sich hier kein Marktpreis bestimmen.`:`${result.marginal?.label||'Kein Angebot'} deckt den letzten benötigten Teil der Nachfrage. Alle bezuschlagten Mengen erhalten im Modell ${fmt(result.price,0)} ct/kWh.`;
  }
  const changed=()=>{manualScenario=true;renderMerit();};
  $('merit-demand').addEventListener('input',changed);
  $('merit-renewables').addEventListener('input',changed);
  $('merit-use-data').addEventListener('click',applyContext);
  renderMerit();
  window.energyExplain=Object.freeze({renderMix,updateContext});
})();
