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
  function marketContext(power, prices, nowSeconds) {
    // Comparing different delivery intervals would falsely link production
    // with a price that was set for another time. Match exact interval starts.
    if (!power?.production_types || !prices?.price || prices.unit?.replaceAll(' ', '').toLowerCase() !== 'eur/mwh') return null;
    const series = Object.fromEntries(power.production_types.map(s => [s.name, s.data]));
    const required = ['Load','Wind onshore','Wind offshore','Solar','Hydro Run-of-River'];
    if (required.some(name => !series[name])) return null;
    const priceMap = new Map(prices.unix_seconds.map((t,i) => [t, prices.price[i]]));
    for (let i=power.unix_seconds.length-1;i>=0;i--) {
      const timestamp = power.unix_seconds[i];
      if (timestamp+900 > nowSeconds || timestamp < nowSeconds-7*86400) continue;
      const values = required.map(name => series[name][i]), price = priceMap.get(timestamp);
      if (values.some(v => typeof v !== 'number' || !Number.isFinite(v) || v<0) || typeof price !== 'number' || !Number.isFinite(price)) continue;
      const [load, windOn, windOff, solar, hydro] = values;
      return {timestamp, loadGW:load/1000, windGW:(windOn+windOff)/1000, solarGW:solar/1000, hydroGW:hydro/1000,
        cheapGW:(windOn+windOff+solar+hydro)/1000, marketPriceCt:price/10, delayed:nowSeconds-timestamp>7200};
    }
    return null;
  }
  const model = Object.freeze({dayKey, shiftDay, inPeriod, currentPriceIndex, generationMix, meritOrder, marketContext});
  if (typeof module !== 'undefined' && module.exports) module.exports = model;
  else window.energyModel = model;
})();
