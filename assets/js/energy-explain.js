'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const fmt = (n,digits=1) => n.toLocaleString('de-DE',{minimumFractionDigits:digits,maximumFractionDigits:digits});
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
    $('demand-output').textContent=demand+' GW';$('renewables-output').textContent=renewables+' GW';
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
      const offered=document.createElement('span');offered.textContent=fmt(offer.capacity,0)+' GW angeboten';
      const accepted=document.createElement('span');accepted.textContent=fmt(offer.accepted,0)+' GW erhalten Zuschlag';
      const badge=document.createElement('span');badge.className='merit-badge';badge.textContent=result.marginal?.label===offer.label?'Bestimmt den Modellpreis':offer.accepted>0?'Erhält denselben Modellpreis':'Kein Zuschlag';
      item.append(name,price,offered,accepted,badge);host.append(item);
    });
    $('merit-price').textContent=result.price===null?'Nicht gedeckt':fmt(result.price,0)+' ct/kWh';
    $('merit-result').textContent=result.price===null?`Im Modell fehlen ${fmt(result.unmet,0)} GW Angebot. Für diese Nachfrage lässt sich hier kein Marktpreis bestimmen.`:`${result.marginal?.label||'Kein Angebot'} deckt den letzten benötigten Teil der Nachfrage. Alle bezuschlagten Mengen erhalten im Modell ${fmt(result.price,0)} ct/kWh.`;
  }
  $('merit-demand').addEventListener('input',renderMerit);
  $('merit-renewables').addEventListener('input',renderMerit);
  renderMerit();
  window.energyExplain=Object.freeze({renderMix});
})();
