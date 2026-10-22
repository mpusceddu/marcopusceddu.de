/* Progressive enhancement: all links remain visible without JavaScript. */
(() => {
  const header = document.querySelector('.site-header');
  const nav = header?.querySelector('nav');
  if (!nav) return;
  const mobile = window.matchMedia('(max-width: 900px)');
  nav.id = nav.id || 'site-navigation';
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'menu-toggle';
  button.setAttribute('aria-controls', nav.id);
  button.setAttribute('aria-expanded', 'false');
  button.innerHTML = '<span class="menu-icon" aria-hidden="true">☰</span><span>Menü</span>';
  header.insertBefore(button, nav);
  header.classList.add('has-menu');
  const setOpen = (open, restoreFocus = false) => {
    button.setAttribute('aria-expanded', String(open));
    header.classList.toggle('menu-open', open);
    button.firstElementChild.textContent = open ? '×' : '☰';
    if (restoreFocus) button.focus();
  };
  button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
  header.addEventListener('keydown', event => {
    if (event.key === 'Escape' && mobile.matches && button.getAttribute('aria-expanded') === 'true') {
      setOpen(false, true);
    }
  });
  nav.addEventListener('click', event => {
    if (mobile.matches && event.target.closest('a')) setOpen(false, true);
  });
  mobile.addEventListener('change', () => {
    const focusInNav = nav.contains(document.activeElement);
    const focusOnButton = document.activeElement === button;
    setOpen(false, mobile.matches && focusInNav);
    if (!mobile.matches && focusOnButton) nav.querySelector('a')?.focus();
  });
})();
