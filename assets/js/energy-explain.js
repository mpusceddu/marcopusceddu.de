'use strict';
(() => {
  const $=id=>document.getElementById(id);
  const fmt=(n,digits=1)=>n.toLocaleString('de-DE',{minimumFractionDigits:digits,maximumFractionDigits:digits});
  function renderMerit(){
    const demand=Number($('merit-demand').value),renewables=Number($('merit-renewables').value);
    $('demand-output').textContent=fmt(demand)+' GW';$('renewables-output').textContent=fmt(renewables)+' GW';
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
  $('merit-demand').addEventListener('input',renderMerit);
  $('merit-renewables').addEventListener('input',renderMerit);
  renderMerit();
})();
