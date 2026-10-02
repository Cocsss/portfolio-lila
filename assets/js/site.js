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
  const url = v => BASE_VIDEO + v.dataset.f + '.mp4';

  /* ─────────────────────────────────────────────────────────────────
     2. Barre de navigation
     ───────────────────────────────────────────────────────────────── */
  const nav = $('.nav');
  let attente = false;
  const posee = () => { nav.classList.toggle('nav--pose', scrollY > 40); attente = false; };
  posee();
  addEventListener('scroll', () => {
    if (!attente) { attente = true; requestAnimationFrame(posee); }
  }, { passive: true });

  const bascule = $('.nav__bascule');
  const fermerMenu = (rendreFocus) => {
    if (!nav.classList.contains('nav--ouverte')) return;
    nav.classList.remove('nav--ouverte');
    bascule.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('bloque');
    if (rendreFocus) bascule.focus();
  };
  if (bascule) {
    bascule.addEventListener('click', () => {
      const ouvert = nav.classList.toggle('nav--ouverte');
      bascule.setAttribute('aria-expanded', String(ouvert));
      document.body.classList.toggle('bloque', ouvert);
      if (ouvert) requestAnimationFrame(() => { const a = $('.nav__liens a', nav); if (a) a.focus(); });
      else bascule.focus();
    });
    $$('.nav__liens a').forEach(a => a.addEventListener('click', () => fermerMenu(false)));
  }

  /* ─────────────────────────────────────────────────────────────────
     3. Apparition au défilement
     ───────────────────────────────────────────────────────────────── */
  const montants = $$('.monte');
  if (doux) {
    montants.forEach(el => el.classList.add('vu'));
  } else if (montants.length) {
    const oeil = new IntersectionObserver((entrees, obs) => {
      entrees.forEach(e => {
        if (!e.isIntersecting) return;
        e.target.classList.add('vu');
        obs.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .06 });
    montants.forEach(el => oeil.observe(el));

    /* Filet : uniquement si l'observateur n'a RIEN produit (navigateur
       capricieux). On révèle alors sans animer, pour ne pas supprimer
       l'effet sur tout le reste de la page. */
    addEventListener('load', () => setTimeout(() => {
      if (document.querySelector('.monte.vu')) return;
      oeil.disconnect();
      montants.forEach(el => { el.style.transition = 'none'; el.classList.add('vu'); });
    }, 1200));
  }

  /* ─────────────────────────────────────────────────────────────────
     4. Vidéos
        Elles se lancent seules, muettes, en boucle — mais JAMAIS plus
        de deux à la fois (chaque lecture mobilise un décodeur et du
        réseau). Loin de l'écran, on rend la source pour libérer la
        mémoire. En « mouvement réduit », ou si le navigateur refuse la
        lecture auto, on rend les contrôles natifs : le contenu reste
        joignable.
     ───────────────────────────────────────────────────────────────── */
  const clips = $$('.clip');
  const MAX_SIMULTANE = 2;

  const mmss = s => {
    if (!isFinite(s)) return '';
    const m = Math.floor(s / 60), r = Math.round(s % 60);
    return `${m}:${String(r).padStart(2, '0')}`;
  };

  function charger(v) {
    if (v.querySelector('source')) return;
    const src = document.createElement('source');
    src.src = url(v);
    src.type = 'video/mp4';
    v.appendChild(src);
    v.preload = 'metadata';
    v.load();
  }

  function decharger(v) {
    if (!v.querySelector('source')) return;
    v.pause();
    v.replaceChildren();          /* retire le <source> → libère le tampon */
    v.removeAttribute('src');
    v.load();                     /* repose l'image d'attente */
    v.preload = 'none';
  }

  if (clips.length) {
    const visibilite = new Map();   /* clip → part visible */

    const arbitrer = () => {
      const classes = [...visibilite.entries()]
        .filter(([, r]) => r > 0)
        .sort((a, b) => b[1] - a[1]);

      classes.forEach(([clip], rang) => {
        const v = $('video', clip);
        if (!v) return;
        charger(v);
        if (rang < MAX_SIMULTANE && !doux) {
          v.play().catch(() => { v.controls = true; clip.classList.add('clip--manuel'); });
        } else {
          v.pause();
          if (!v.muted) v.muted = true;
        }
      });

      /* au-delà de deux écrans, on rend la mémoire */
      visibilite.forEach((r, clip) => {
        if (r > 0) return;
        const v = $('video', clip);
        if (!v) return;
        const d = clip.getBoundingClientRect();
        if (d.bottom < -innerHeight || d.top > innerHeight * 2) decharger(v);
        else v.pause();
      });
    };

    const vue = new IntersectionObserver(entrees => {
      entrees.forEach(e => visibilite.set(e.target, e.isIntersecting ? e.intersectionRatio : 0));
      arbitrer();
    }, { threshold: [0, .25, .5, .75, 1], rootMargin: '200px 0px' });

    clips.forEach(clip => {
      const v = $('video', clip);
      const son = $('.clip__son', clip);
      const duree = $('.clip__duree', clip);
      if (!v) return;

      visibilite.set(clip, 0);
      vue.observe(clip);

      /* en mouvement réduit, on ne lance rien : on donne les contrôles */
      if (doux) { v.controls = true; clip.classList.add('clip--manuel'); }

      if (duree) {
        v.addEventListener('loadedmetadata', () => { duree.textContent = mmss(v.duration); });
      }

      if (son) {
        const dessine = () => {
          son.classList.toggle('clip__son--muet', v.muted);
          son.setAttribute('aria-pressed', String(!v.muted));
        };
        son.setAttribute('aria-label', 'Son : ' + (v.getAttribute('aria-label') || 'vidéo'));
        dessine();
        son.addEventListener('click', ev => {
          ev.stopPropagation();
          if (v.muted) {                      /* une seule vidéo sonore à la fois */
            clips.forEach(autre => {
              const av = $('video', autre);
              if (av && av !== v) av.muted = true;
            });
          }
          v.muted = !v.muted;                 /* volumechange déclenchera le redessin */
          v.play().catch(() => {});
        });
        v.addEventListener('volumechange', dessine);
      }
    });
  }

  /* ─────────────────────────────────────────────────────────────────
     5. Visionneuse (images)
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

  async function peindre() {
    const el = lot[i];
    const img = new Image();
    img.src = el.dataset.plein;
    img.alt = el.dataset.alt || '';
    const source = $('img', el);
    if (source) { img.width = source.width; img.height = source.height; }
    try { await img.decode(); } catch (_) { /* on affiche quand même */ }
    if (lot[i] !== el) return;             /* on est déjà passé à la suivante */
    scene.replaceChildren(img);
    compte.textContent = `${String(i + 1).padStart(2, '0')} / ${String(lot.length).padStart(2, '0')}`;
    legende.textContent = (el.dataset.alt || '').replace(/, visuel \d+$/, '');
    prec.hidden = suiv.hidden = lot.length < 2;
    [i - 1, i + 1].forEach(k => {
      const v = lot[(k + lot.length) % lot.length];
      if (v) new Image().src = v.dataset.plein;
    });
  }

  function ouvrir(el) {
    /* le conteneur de galerie s'appelle .collage dans le HTML généré */
    lot = $$('.vignette[data-plein]', el.closest('.collage') || document);
    if (!lot.length) return;
    i = Math.max(0, lot.indexOf(el));
    declencheur = el;
    boite.classList.add('ouverte');
    boite.setAttribute('aria-hidden', 'false');
    document.body.classList.add('bloque');
    peindre();
    requestAnimationFrame(() => fermer.focus());
  }

  function clore() {
    boite.classList.remove('ouverte');
    boite.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('bloque');
    scene.replaceChildren();
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
    if (e.key === 'Escape' && nav.classList.contains('nav--ouverte')) { fermerMenu(true); return; }
    if (!boite.classList.contains('ouverte')) return;
    if (e.key === 'Escape')     { clore(); return; }
    if (e.key === 'ArrowLeft')  { glisser(-1); return; }
    if (e.key === 'ArrowRight') { glisser(1); return; }
    if (e.key === 'Tab') {
      /* vrai piège de focus : on tourne entre les commandes visibles */
      const cibles = [fermer, prec, suiv].filter(b => !b.hidden);
      const k = cibles.indexOf(document.activeElement);
      const vers = e.shiftKey
        ? cibles[(k - 1 + cibles.length) % cibles.length]
        : cibles[(k + 1) % cibles.length];
      e.preventDefault();
      vers.focus();
    }
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
