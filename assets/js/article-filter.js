(() => {
  const filter = document.querySelector('[data-article-filter]');
  const list = document.querySelector('#article-list');
  if (!filter || !list) return;

  const buttons = [...filter.querySelectorAll('[data-topic]')];
  const cards = [...list.querySelectorAll('[data-topics]')];
  const status = filter.querySelector('[role="status"]');
  if (!buttons.length || !cards.length || !status) return;

  const currentTopic = () => {
    const value = new URLSearchParams(location.hash.slice(1)).get('thema');
    return buttons.some(button => button.dataset.topic === value) ? value : 'alle';
  };

  const showTopic = topic => {
    let count = 0;
    for (const card of cards) {
      card.hidden = topic !== 'alle' && !card.dataset.topics.split(' ').includes(topic);
      if (!card.hidden) count += 1;
    }
    for (const button of buttons) {
      button.setAttribute('aria-pressed', String(button.dataset.topic === topic));
    }
    const selected = buttons.find(button => button.dataset.topic === topic);
    const label = selected.firstChild.textContent.trim();
    status.textContent = `${count} ${count === 1 ? 'Beitrag' : 'Beiträge'}${topic === 'alle' ? ' insgesamt' : ` · ${label}`}`;
  };

  for (const button of buttons) {
    button.addEventListener('click', () => {
      const topic = button.dataset.topic;
      if (topic === currentTopic()) return;
      const url = new URL(location.href);
      url.hash = topic === 'alle' ? '' : `thema=${topic}`;
      history.pushState(null, '', url);
      showTopic(topic);
    });
  }
  window.addEventListener('popstate', () => showTopic(currentTopic()));
  window.addEventListener('hashchange', () => showTopic(currentTopic()));
  showTopic(currentTopic());
  filter.hidden = false;
})();
