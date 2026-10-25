'use strict';
(() => {
  const $=id=>document.getElementById(id);
  const fmt=(n,digits=1)=>n.toLocaleString('de-DE',{minimumFractionDigits:digits,maximumFractionDigits:digits});
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
  window.energyMix=Object.freeze({renderMix});
})();
