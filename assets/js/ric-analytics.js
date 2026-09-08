(() => {
  'use strict';
  const VERSION = '1.0.0';
  const CONFIG_URL = 'https://ricmurtapsicologia.github.io/RPD/assets/analytics-config.json';
  const meta = (name) => document.querySelector(`meta[name="${name}"]`)?.content || '';
  let PAGE_ID = meta('ric-analytics-page') || location.pathname.replace(/^\/+|\/+$/g, '') || 'home';
  const PRIVACY = meta('ric-analytics-privacy') || 'health';
  if (PAGE_ID === 'monitoramento') {
    const instrument = new URLSearchParams(location.search).get('instrument') || '';
    if (new Set(['humor','ansiedade','autoestima']).has(instrument)) PAGE_ID = `monitoramento-${instrument}`;
  }
  const allowedEvents = new Set([
    'page_view','engaged_30s','cta_click','download','media_load','media_start',
    'funnel_start','funnel_step','funnel_complete','technical_error'
  ]);
  const safeKeys = new Set(['action','target','step','media','status']);
  const safe = (value) => String(value ?? '').replace(/[^a-zA-Z0-9_.:-]/g, '_').slice(0, 64);
  const safeMeta = (input = {}) => {
    const out = {};
    for (const [key, value] of Object.entries(input)) {
      if (safeKeys.has(key) && value !== undefined && value !== null) out[key] = safe(value);
    }
    return out;
  };
  const randomId = () => {
    try { return crypto.randomUUID(); } catch (_) { return `${Date.now()}-${Math.random().toString(36).slice(2)}`; }
  };
  let sessionId = '';
  if (PRIVACY === 'public') {
    try {
      sessionId = sessionStorage.getItem('ric_a_sid') || randomId();
      sessionStorage.setItem('ric_a_sid', sessionId);
    } catch (_) { sessionId = randomId(); }
  }

  const configPromise = (async () => {
    if (navigator.doNotTrack === '1') return null;
    try {
      const response = await fetch(CONFIG_URL, {
        cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer'
      });
      if (!response.ok) return null;
      const config = await response.json();
      if (config?.enabled !== true) return null;
      if (typeof config.endpoint !== 'string' || !config.endpoint.startsWith('https://')) return null;
      return config;
    } catch (_) { return null; }
  })();

  async function track(event, details = {}) {
    if (!allowedEvents.has(event)) return false;
    if (PRIVACY === 'clinical' && event !== 'technical_error') return false;
    const config = await configPromise;
    if (!config) return false;
    const payload = {
      v: VERSION,
      ts: Date.now(),
      page: safe(PAGE_ID),
      path: PRIVACY === 'public' ? location.pathname.slice(0, 160) : '',
      event,
      privacy: safe(PRIVACY),
      session: PRIVACY === 'public' ? sessionId : '',
      meta: safeMeta(details)
    };
    try {
      await fetch(config.endpoint, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-store',
        credentials: 'omit',
        referrerPolicy: 'no-referrer',
        keepalive: true,
        headers: {'Content-Type': 'text/plain;charset=UTF-8'},
        body: JSON.stringify(payload)
      });
      return true;
    } catch (_) { return false; }
  }

  window.RICAnalytics = Object.freeze({ track, version: VERSION });

  const onReady = () => {
    track('page_view');
    setTimeout(() => {
      if (document.visibilityState === 'visible') track('engaged_30s');
    }, 30000);

    const startedForms = new WeakSet();
    document.addEventListener('focusin', (event) => {
      const form = event.target?.closest?.('form');
      if (form && !startedForms.has(form)) {
        startedForms.add(form);
        track('funnel_start', {target: form.id || 'form'});
      }
    }, {passive: true});

    document.addEventListener('click', (event) => {
      const el = event.target?.closest?.('a,button');
      if (!el) return;
      const step = el.closest?.('[data-step]')?.getAttribute('data-step');
      if (el.matches('.next,[data-next]')) track('funnel_step', {step: step || 'next'});
      if (el.id === 'loadVideo' || el.matches('[data-load-video]')) track('media_load', {media: 'video'});
      if (el.matches('a[download]')) track('download', {target: 'file'});
      const explicit = el.getAttribute('data-ric-event');
      if (explicit && allowedEvents.has(explicit)) track(explicit, {target: el.getAttribute('data-ric-target') || el.id || 'cta'});
    }, {passive: true});

    document.addEventListener('play', (event) => {
      const media = event.target;
      if (media?.matches?.('audio,video')) track('media_start', {media: media.tagName.toLowerCase()});
    }, true);

    document.addEventListener('submit', (event) => {
      const form = event.target;
      if (form?.matches?.('form')) track('funnel_complete', {target: form.id || 'form'});
    }, true);

    window.addEventListener('error', () => {
      if (PRIVACY === 'clinical') track('technical_error', {status: 'script_error'});
    });
    window.addEventListener('unhandledrejection', () => {
      if (PRIVACY === 'clinical') track('technical_error', {status: 'unhandled_rejection'});
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', onReady, {once: true});
  else onReady();
})();
