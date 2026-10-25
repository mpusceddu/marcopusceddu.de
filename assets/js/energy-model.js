'use strict';
// Calendar arithmetic must use German dates, including 23/25-hour DST days.
(() => {
  const dayKey = seconds => new Intl.DateTimeFormat('sv-SE', {timeZone:'Europe/Berlin'}).format(new Date(seconds * 1000));
  function shiftDay(key, offset) {
    const date = new Date(key + 'T12:00:00Z');
    date.setUTCDate(date.getUTCDate() + offset);
    return date.toISOString().slice(0, 10);
  }
  function inPeriod(seconds, period, nowSeconds) {
    const today = dayKey(nowSeconds), date = dayKey(seconds);
    if (period === 'week') return date >= shiftDay(today, -6) && date <= today;
    return date === (period === 'tomorrow' ? shiftDay(today, 1) : today);
  }
  function currentPriceIndex(timestamps, nowSeconds) {
    // Current German Day-Ahead delivery periods are 15 minutes long. A gap
    // in the source must never make the preceding price apply for longer.
    return timestamps.findIndex(t => t <= nowSeconds && nowSeconds < t + 900);
  }
  function generationMix(records, nowSeconds) {
    const valid = records.filter(r => r.t + 900 <= nowSeconds && r.values.length && r.values.every(v => typeof v === 'number' && Number.isFinite(v) && v >= 0));
    const energy = valid.length ? valid[0].values.map((_, i) => valid.reduce((sum, row) => sum + row.values[i] * .25, 0)) : [];
    const total = energy.reduce((sum, value) => sum + value, 0);
    return {energy, total, shares: energy.map(value => total > 0 ? value / total * 100 : null), intervals: valid.length, start: valid[0]?.t, end: valid.at(-1)?.t + 900};
  }
  function meritOrder(offers, demand) {
    if (!Number.isFinite(demand) || demand < 0 || offers.some(o => !Number.isFinite(o.capacity) || o.capacity < 0 || !Number.isFinite(o.price))) throw Error('Invalid model inputs');
    let remaining = demand, marginal = null;
    const cleared = [...offers].sort((a,b) => a.price-b.price).map(offer => {
      const accepted = Math.min(offer.capacity, remaining);
      remaining -= accepted;
      if (accepted > 0) marginal = offer;
      return {...offer, accepted};
    });
    return {offers:cleared, unmet:remaining, marginal:remaining > 0 ? null : marginal, price:remaining > 0 ? null : marginal?.price ?? 0};
  }
  function flowTotals(records, nowSeconds) {
    const valid=records.filter(row=>row.t+900<=nowSeconds&&row.values.length===2&&row.values.every(v=>typeof v==='number'&&Number.isFinite(v)&&v>=0));
    if(!valid.length)return null;
    const importGWh=valid.reduce((sum,row)=>sum+row.values[0]*.25,0);
    const exportGWh=valid.reduce((sum,row)=>sum+row.values[1]*.25,0);
    return {importGWh,exportGWh,netGWh:importGWh-exportGWh,intervals:valid.length,start:valid[0].t,end:valid.at(-1).t+900};
  }
  const model = Object.freeze({dayKey, shiftDay, inPeriod, currentPriceIndex, generationMix, meritOrder, flowTotals});
  if (typeof module !== 'undefined' && module.exports) module.exports = model;
  else window.energyModel = model;
})();
