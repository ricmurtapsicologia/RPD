(() => {
  'use strict';

  const VERSION = '1.1.1';
  const CONFIG_URL = 'https://ricmurtapsicologia.github.io/RPD/assets/analytics-config.json';
  const DEFAULT_GA_ID = 'G-N1GEBDNZ8B';
  const CONSENT_KEY = 'ric_analytics_consent';
  const meta = (name) => document.querySelector(`meta[name="${name}"]`)?.content || '';
  const safe = (value) => String(value ?? '').replace(/[^a-zA-Z0-9_.:-]/g, '_').slice(0, 64);

  let PAGE_ID = meta('ric-analytics-page') || location.pathname.replace(/^\/+|\/+$/g, '') || 'home';
  const PRIVACY = meta('ric-analytics-privacy') || 'health';
  const GA_ID = meta('ric-analytics-ga') || DEFAULT_GA_ID;
  const DNT = navigator.doNotTrack === '1';

  if (PAGE_ID === 'monitoramento') {
    const instrument = new URLSearchParams(location.search).get('instrument') || '';
    if (new Set(['humor', 'ansiedade', 'autoestima']).has(instrument)) PAGE_ID = `monitoramento-${instrument}`;
  }

  const allowedEvents = new Set([
    'page_view', 'engaged_30s', 'cta_click', 'download', 'media_load', 'media_start',
    'funnel_start', 'funnel_step', 'funnel_complete', 'auth_success', 'technical_error'
  ]);
  const safeKeys = new Set(['action', 'target', 'step', 'media', 'status']);
  const safeMeta = (input = {}) => {
    const out = {};
    for (const [key, value] of Object.entries(input)) {
      if (safeKeys.has(key) && value !== undefined && value !== null) out[key] = safe(value);
    }
    return out;
  };

  const randomId = () => {
    try { return crypto.randomUUID(); }
    catch (_) { return `${Date.now()}-${Math.random().toString(36).slice(2)}`; }
  };

  let sessionId = '';
  if (PRIVACY === 'public') {
    try {
      sessionId = sessionStorage.getItem('ric_a_sid') || randomId();
      sessionStorage.setItem('ric_a_sid', sessionId);
    } catch (_) { sessionId = randomId(); }
  }

  const consent = () => {
    if (PRIVACY !== 'public' || DNT) return 'denied';
    try { return localStorage.getItem(CONSENT_KEY) || 'unknown'; }
    catch (_) { return 'unknown'; }
  };

  const externalGaScript = document.querySelector('script[src*="googletagmanager.com/gtag/js?id="]');
  let gaReady = false;
  let gaPageViewOwned = false;
  let pageViewSent = false;

  if (PRIVACY === 'public' && consent() !== 'granted') {
    window[`ga-disable-${GA_ID}`] = true;
  }

  function initGa4() {
    if (PRIVACY !== 'public' || DNT || consent() !== 'granted' || !/^G-[A-Z0-9]+$/.test(GA_ID)) return false;
    window[`ga-disable-${GA_ID}`] = false;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

    if (!externalGaScript) {
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(GA_ID)}`;
      script.dataset.ricAnalyticsGa = VERSION;
      document.head.appendChild(script);
      window.gtag('js', new Date());
      window.gtag('config', GA_ID, {
        anonymize_ip: true,
        allow_google_signals: false,
        allow_ad_personalization_signals: false,
        send_page_view: false
      });
      gaPageViewOwned = true;
    }

    gaReady = true;
    return true;
  }

  function gaEvent(event, details = {}) {
    if (!gaReady || consent() !== 'granted' || PRIVACY !== 'public' || typeof window.gtag !== 'function') return false;
    if (event === 'page_view' && (!gaPageViewOwned || pageViewSent)) return false;
    const params = {
      ric_page: safe(PAGE_ID),
      page_path: location.pathname.slice(0, 160),
      ...safeMeta(details)
    };
    if (event === 'page_view') {
      params.page_title = document.title.slice(0, 120);
      params.page_location = `${location.origin}${location.pathname}`.slice(0, 300);
      pageViewSent = true;
    }
    try {
      window.gtag('event', event, params);
      return true;
    } catch (_) { return false; }
  }

  function showConsent() {
    if (PRIVACY !== 'public' || DNT || consent() !== 'unknown' || document.getElementById('ric-analytics-consent')) return;
    const box = document.createElement('aside');
    box.id = 'ric-analytics-consent';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-label', 'Preferência de estatísticas de uso');
    box.style.cssText = 'position:fixed;left:12px;right:12px;bottom:12px;z-index:2147483646;max-width:760px;margin:auto;padding:14px 16px;border-radius:14px;background:#0b1220;color:#f8fafc;border:1px solid rgba(255,255,255,.18);box-shadow:0 12px 35px rgba(0,0,0,.38);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif';
    box.innerHTML = '<div style="font-weight:700;margin-bottom:5px">Estatísticas de uso</div><div style="opacity:.9;margin-bottom:10px">Podemos registrar visitas e interações de forma agregada para melhorar este ambiente. Não enviamos nome, CPF, número BM, respostas ou conteúdo clínico ao Google Analytics.</div><div style="display:flex;gap:8px;flex-wrap:wrap"><button type="button" data-ric-consent="deny" style="padding:8px 12px;border-radius:9px;border:1px solid #64748b;background:transparent;color:#fff;cursor:pointer">Agora não</button><button type="button" data-ric-consent="grant" style="padding:8px 12px;border-radius:9px;border:0;background:#ff7f0e;color:#111827;font-weight:700;cursor:pointer">Permitir estatísticas</button></div>';
    document.body.appendChild(box);
    box.addEventListener('click', (event) => {
      const button = event.target.closest('[data-ric-consent]');
      if (!button) return;
      const grant = button.dataset.ricConsent === 'grant';
      try { localStorage.setItem(CONSENT_KEY, grant ? 'granted' : 'denied'); } catch (_) {}
      box.remove();
      if (grant) {
        initGa4();
        if (gaPageViewOwned) gaEvent('page_view');
        reportAuthenticatedSession();
      } else {
        window[`ga-disable-${GA_ID}`] = true;
      }
    });
  }

  const configPromise = (async () => {
    if (DNT) return null;
    try {
      const response = await fetch(CONFIG_URL, {cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer'});
      if (!response.ok) return null;
      const config = await response.json();
      if (config?.enabled !== true) return null;
      if (typeof config.endpoint !== 'string' || !config.endpoint.startsWith('https://')) return null;
      return config;
    } catch (_) { return null; }
  })();

  async function ownCollector(event, details = {}) {
    if (!allowedEvents.has(event)) return false;
    if (PRIVACY === 'clinical' && event !== 'technical_error') return false;
    const config = await configPromise;
    if (!config) return false;
    const payload = {
      v: VERSION, ts: Date.now(), page: safe(PAGE_ID),
      path: PRIVACY === 'public' ? location.pathname.slice(0, 160) : '',
      event, privacy: safe(PRIVACY),
      session: PRIVACY === 'public' ? sessionId : '',
      meta: safeMeta(details)
    };
    try {
      await fetch(config.endpoint, {
        method: 'POST', mode: 'cors', cache: 'no-store', credentials: 'omit',
        referrerPolicy: 'no-referrer', keepalive: true,
        headers: {'Content-Type': 'text/plain;charset=UTF-8'}, body: JSON.stringify(payload)
      });
      return true;
    } catch (_) { return false; }
  }

  async function track(event, details = {}) {
    if (!allowedEvents.has(event)) return false;
    if (PRIVACY === 'clinical' && event !== 'technical_error') return false;
    const own = ownCollector(event, details);
    gaEvent(event, details);
    return own;
  }

  function validAuthSession(key) {
    try {
      const data = JSON.parse(sessionStorage.getItem(key) || 'null');
      return Boolean(data && data.authenticated === true && Date.now() < Number(data.expiresAt || 0));
    } catch (_) { return false; }
  }

  function reportAuthenticatedSession() {
    if (PRIVACY !== 'public' || consent() !== 'granted') return;
    const keys = PAGE_ID === 'cats-pouso-alegre' ? ['cats_pa_auth_v1'] : ['curso_ats_auth_v3'];
    if (!keys.some(validAuthSession)) return;
    const onceKey = `ric_auth_${PAGE_ID}`;
    try {
      if (sessionStorage.getItem(onceKey) === '1') return;
      sessionStorage.setItem(onceKey, '1');
    } catch (_) {}
    track('auth_success', {status: 'authenticated'});
  }

  window.RICAnalytics = Object.freeze({track, version: VERSION, page: PAGE_ID, privacy: PRIVACY});

  const onReady = () => {
    if (consent() === 'granted') initGa4();
    else showConsent();
    track('page_view');
    reportAuthenticatedSession();
    window.addEventListener('cats:authenticated', reportAuthenticatedSession);

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
