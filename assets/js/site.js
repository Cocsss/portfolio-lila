/* ═══════════════════════════════════════════════════════════════════
   Lila Narinx — portfolio
   Vanilla, zéro dépendance.
   ═══════════════════════════════════════════════════════════════════ */
(() => {
  'use strict';

  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const doux = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ─────────────────────────────────────────────────────────────────
     1. Où vivent les vidéos
     En local  → assets/video/        En ligne → le bucket R2
     La bascule est automatique : rien à changer à la mise en ligne.
     ───────────────────────────────────────────────────────────────── */
  const EN_LOCAL = ['localhost', '127.0.0.1', ''].includes(location.hostname);
  const BASE_VIDEO = EN_LOCAL ? 'assets/video/' : 'https://videos.lilanarinx.com/';

  $$('video[data-f]').forEach(v => {
    const src = document.createElement('source');
    src.src = BASE_VIDEO + v.dataset.f + '.mp4';
    src.type = 'video/mp4';
    v.appendChild(src);
  });

  /* ─────────────────────────────────────────────────────────────────
     2. Barre de navigation
     ───────────────────────────────────────────────────────────────── */
  const nav = $('.nav');
  const posee = () => nav.classList.toggle('nav--pose', scrollY > 40);
  posee();
  addEventListener('scroll', posee, { passive: true });

  const bascule = $('.nav__bascule');
  if (bascule) {
    bascule.addEventListener('click', () => {
      const ouvert = nav.classList.toggle('nav--ouverte');
      bascule.setAttribute('aria-expanded', String(ouvert));
      bascule.setAttribute('aria-label', ouvert ? 'Fermer le menu' : 'Ouvrir le menu');
    });
    /* un clic dans le menu le referme */
    $$('.nav__liens a').forEach(a => a.addEventListener('click', () => {
      nav.classList.remove('nav--ouverte');
      bascule.setAttribute('aria-expanded', 'false');
    }));
  }

  /* ─────────────────────────────────────────────────────────────────
     3. Apparition au défilement
     ───────────────────────────────────────────────────────────────── */
  const montants = $$('.monte');
  if (doux) {
    montants.forEach(el => el.classList.add('vu'));
  } else {
    const oeil = new IntersectionObserver((entrees, obs) => {
      entrees.forEach(e => {
        if (!e.isIntersecting) return;
        e.target.classList.add('vu');
        obs.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .06 });
    montants.forEach(el => oeil.observe(el));
    /* filet de sécurité : quoi qu'il arrive (saut d'ancre, observer capricieux),
       tout est visible 1,2 s après le chargement */
    addEventListener('load', () => setTimeout(() => montants.forEach(el => el.classList.add('vu')), 1200));
  }

  /* ─────────────────────────────────────────────────────────────────
     4. Vidéos — elles se lancent seules, muettes, en boucle.
        Aucun bouton de lecture : seul le son se demande.
     ───────────────────────────────────────────────────────────────── */
  const clips = $$('.clip');

  const mmss = s => {
    if (!isFinite(s)) return '';
    const m = Math.floor(s / 60), r = Math.round(s % 60);
    return `${m}:${String(r).padStart(2, '0')}`;
  };

  if (clips.length) {
    /* on ne charge et ne joue que ce qui est à l'écran */
    const vue = new IntersectionObserver(entrees => {
      entrees.forEach(e => {
        const v = $('video', e.target);
        if (!v) return;
        if (e.isIntersecting) {
          if (v.preload === 'none') { v.preload = 'auto'; v.load(); }
          if (!doux) v.play().catch(() => {});
        } else {
          v.pause();
          if (!v.muted) { v.muted = true; v.dispatchEvent(new Event('volumechange')); }
        }
      });
    }, { threshold: .2 });

    clips.forEach(clip => {
      const v = $('video', clip);
      const son = $('.clip__son', clip);
      const duree = $('.clip__duree', clip);
      if (!v) return;

      vue.observe(clip);

      if (duree) {
        v.addEventListener('loadedmetadata', () => { duree.textContent = mmss(v.duration); });
      }

      if (son) {
        const dessine = () => {
          son.innerHTML = v.muted
            ? '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 9v6h4l5 5V4L7 9H3zm13.6 3L19 14.4 20.4 13 18 10.6 20.4 8.2 19 6.8 16.6 9.2 14.2 6.8 12.8 8.2 15.2 10.6 12.8 13z"/></svg>'
            : '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 9v6h4l5 5V4L7 9H3zm11.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM12 2v2.1a7.5 7.5 0 0 1 0 15.8V22a9.5 9.5 0 0 0 0-20z"/></svg>';
          son.setAttribute('aria-label', v.muted ? 'Activer le son' : 'Couper le son');
          son.setAttribute('aria-pressed', String(!v.muted));
        };
        dessine();
        son.addEventListener('click', ev => {
          ev.stopPropagation();
          /* une seule vidéo sonore à la fois */
          if (v.muted) {
            clips.forEach(autre => {
              const av = $('video', autre);
              if (av && av !== v && !av.muted) { av.muted = true; av.dispatchEvent(new Event('volumechange')); }
            });
          }
          v.muted = !v.muted;
          v.play().catch(() => {});
          dessine();
        });
        v.addEventListener('volumechange', dessine);
      }
    });
  }

  /* ─────────────────────────────────────────────────────────────────
     5. Lightbox (images uniquement)
     ───────────────────────────────────────────────────────────────── */
  const boite = $('.boite');
  if (!boite) return;
  const scene   = $('.boite__scene', boite);
  const compte  = $('.boite__compte', boite);
  const legende = $('.boite__legende', boite);
  const fermer  = $('.boite__fermer', boite);
  const prec    = $('.boite__fleche--prec', boite);
  const suiv    = $('.boite__fleche--suiv', boite);

  let lot = [], i = 0, declencheur = null;

  function peindre() {
    const el = lot[i];
    scene.innerHTML = '';
    const img = new Image();
    img.src = el.dataset.plein;
    img.alt = el.dataset.alt || '';
    scene.appendChild(img);
    compte.textContent = `${String(i + 1).padStart(2, '0')} / ${String(lot.length).padStart(2, '0')}`;
    legende.textContent = (el.dataset.alt || '').replace(/, visuel \d+$/, '');
    prec.hidden = suiv.hidden = lot.length < 2;
    [i - 1, i + 1].forEach(k => {
      const v = lot[(k + lot.length) % lot.length];
      if (v) new Image().src = v.dataset.plein;
    });
  }

  function ouvrir(el) {
    lot = $$('.vignette[data-plein]', el.closest('.galerie'));
    i = lot.indexOf(el);
    declencheur = el;
    boite.classList.add('ouverte');
    boite.setAttribute('aria-hidden', 'false');
    document.body.classList.add('bloque');
    peindre();
    fermer.focus();
  }

  function clore() {
    boite.classList.remove('ouverte');
    boite.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('bloque');
    scene.innerHTML = '';
    if (declencheur) { declencheur.focus(); declencheur = null; }
  }

  const glisser = n => { i = (i + n + lot.length) % lot.length; peindre(); };

  $$('.vignette[data-plein]').forEach(el =>
    el.addEventListener('click', () => ouvrir(el))
  );

  fermer.addEventListener('click', clore);
  prec.addEventListener('click', () => glisser(-1));
  suiv.addEventListener('click', () => glisser(1));
  boite.addEventListener('click', e => { if (e.target === boite || e.target === scene) clore(); });

  addEventListener('keydown', e => {
    if (!boite.classList.contains('ouverte')) return;
    if (e.key === 'Escape')     clore();
    if (e.key === 'ArrowLeft')  glisser(-1);
    if (e.key === 'ArrowRight') glisser(1);
    if (e.key === 'Tab')      { e.preventDefault(); fermer.focus(); }
  });

  let x0 = null;
  scene.addEventListener('touchstart', e => { x0 = e.changedTouches[0].clientX; }, { passive: true });
  scene.addEventListener('touchend', e => {
    if (x0 === null) return;
    const d = e.changedTouches[0].clientX - x0;
    if (Math.abs(d) > 48) glisser(d < 0 ? 1 : -1);
    x0 = null;
  }, { passive: true });
})();
