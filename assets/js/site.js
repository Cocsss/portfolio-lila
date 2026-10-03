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
  /* Les vidéos vivent dans le bucket R2 « cd-videos », dossier Lila/.
     Pour les déplacer vers un bucket propre à lilanarinx.com plus tard,
     cette seule ligne est à changer. */
  const BASE_VIDEO = EN_LOCAL
    ? 'assets/video/'
    : 'https://videos.corentindeville.com/Lila/';
  const url = v => BASE_VIDEO + v.dataset.f + '.mp4' + (v.dataset.debut ? '#t=' + v.dataset.debut : '');

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
    /* threshold .06 était surfacique : un bloc de 3000 px devait montrer
       190 px, une vignette de 300 px seulement 18. threshold 0 + marge
       basse négative rend le déclenchement indépendant de la hauteur. */
    const oeil = new IntersectionObserver((entrees, obs) => {
      entrees
        .filter(e => e.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        .forEach((e, k) => {
          e.target.style.transitionDelay = Math.min(k * 60, 240) + 'ms';
          e.target.classList.add('vu');
          obs.unobserve(e.target);
        });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0 });
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
  /* l'arbitre vit dans le bloc ci-dessous ; la visionneuse doit pouvoir
     le rappeler quand elle se ferme, pour relancer la vidéo de la grille */
  let reArbitrer = null;

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
        if (rang < MAX_SIMULTANE + 1) charger(v);
        if (rang < MAX_SIMULTANE && !doux && clip.dataset.gele !== '1') {
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

    reArbitrer = arbitrer;   /* la visionneuse en a besoin à la fermeture */

    clips.forEach(clip => {
      const v = $('video', clip);
      if (!v) return;

      visibilite.set(clip, 0);
      vue.observe(clip);

      /* en mouvement réduit, on ne lance rien : on donne les contrôles */
      if (doux) { v.controls = true; clip.classList.add('clip--manuel'); }

      /* On doit pouvoir arrêter une animation qui tourne (WCAG 2.2.2).
         La vidéo est elle-même la commande : aucun bouton ajouté. */
      const basculer = () => {
        const gele = clip.dataset.gele === '1';
        clip.dataset.gele = gele ? '0' : '1';
        if (gele) { charger(v); v.play().catch(() => {}); } else v.pause();
      };

      /* Un clic sur la vidéo = en grand, avec le son. Plein écran natif :
         identique sur ordi et mobile (iOS Safari ne l'expose que sur
         l'élément <video> lui-même, via webkitEnterFullscreen). On rend
         les contrôles natifs le temps du plein écran, puis on coupe le
         son en sortant : dans la grille, tout reste muet. */
      let enPleinEcran = false;

      /* Ordre d'essai :
         1. requestFullscreen() sur la <video> — standard, ordi + Android.
            Safari macOS/iPadOS l'ont aussi (16.4+).
         2. sinon webkitEnterFullscreen() — iPhone uniquement. Il lève
            InvalidStateError tant que les métadonnées ne sont pas là :
            on attend loadedmetadata si besoin (en général déjà chargées,
            la vidéo visible a été préparée par l'arbitre). */
      const visionneuse = () => {
        /* repli maison : on rend au clip son état de grille, la
           visionneuse affiche sa propre copie de la vidéo */
        v.muted = true;
        if (!doux && !clip.classList.contains('clip--manuel')) v.controls = false;
        clip.dispatchEvent(new CustomEvent('clip:engrand', { bubbles: true }));
      };
      const natif = () => {
        /* iPhone : seule la méthode Apple existe, et elle lève
           InvalidStateError tant que les métadonnées ne sont pas là. */
        if (!v.webkitEnterFullscreen) { visionneuse(); return; }
        const go = () => { try { v.webkitEnterFullscreen(); enPleinEcran = true; } catch (_) { visionneuse(); } };
        if (v.readyState >= 1) go();
        else v.addEventListener('loadedmetadata', go, { once: true });
      };
      const entrer = () => {
        if (!document.fullscreenEnabled || !v.requestFullscreen) { natif(); return; }
        /* en cas de refus (politique de permissions, geste jugé absent),
           on ne laisse SURTOUT pas le clip avec son et contrôles : repli */
        v.requestFullscreen().then(() => { enPleinEcran = true; }).catch(natif);
      };
      const enGrand = () => {
        clip.dataset.gele = '0';
        charger(v);
        clips.forEach(autre => { const av = $('video', autre); if (av && av !== v) av.muted = true; });
        v.muted = false;
        v.controls = true;
        v.play().catch(() => {});
        entrer();
      };
      /* Retour à la grille : seulement pour LE clip qui était en grand
         (chaque clip écoute document, sans ce garde-fou les 10 autres
         relançaient leur lecture et le plafond de 2 sautait). */
      const retour = () => {
        if (!enPleinEcran) return;
        if (document.fullscreenElement === v || document.fullscreenElement === clip) return;
        enPleinEcran = false;
        v.muted = true;
        if (!doux && !clip.classList.contains('clip--manuel')) v.controls = false;
        arbitrer();
      };
      document.addEventListener('fullscreenchange', retour);
      v.addEventListener('webkitendfullscreen', retour);   /* iPhone */

      v.addEventListener('click', () => { if (!v.controls) enGrand(); });
      /* au clavier : Entrée ouvre en grand, Espace met en pause (WCAG 2.2.2) */
      v.addEventListener('keydown', ev => {
        if (v.controls) return;
        if (ev.key === 'Enter') { ev.preventDefault(); enGrand(); }
        if (ev.key === ' ')     { ev.preventDefault(); basculer(); }
      });

    });
  }

  /* ─────────────────────────────────────────────────────────────────
     5. Visionneuse (images)
     ───────────────────────────────────────────────────────────────── */
  const boite = $('.boite');
  if (!boite) return;
  const scene   = $('.boite__scene', boite);
  const legende = $('.boite__legende', boite);
  const fermer  = $('.boite__fermer', boite);
  const prec    = $('.boite__fleche--prec', boite);
  const suiv    = $('.boite__fleche--suiv', boite);

  let lot = [], i = 0, declencheur = null, glisse = false;

  async function peindre() {
    const el = lot[i];
    const img = new Image();
    img.src = el.dataset.plein;
    img.alt = el.dataset.alt || '';
    const source = $('img', el);
    if (source) { img.width = source.width; img.height = source.height; }
    try { await img.decode(); } catch (_) { /* on affiche quand même */ }
    if (lot[i] !== el || !boite.classList.contains('ouverte')) return;
    scene.replaceChildren(img);
    legende.textContent = (el.dataset.alt || '').replace(/, visuel \d+$/, '');
    prec.hidden = suiv.hidden = lot.length < 2;
    [i - 1, i + 1].forEach(k => {
      const v = lot[(k + lot.length) % lot.length];
      if (v) new Image().src = v.dataset.plein;
    });
  }

  function viderSiFerme(ev) {
    if (ev.target !== boite || ev.propertyName !== 'opacity') return;
    boite.removeEventListener('transitionend', viderSiFerme);
    if (!boite.classList.contains('ouverte')) scene.replaceChildren();
  }

  function ouvrir(el) {
    /* le conteneur de galerie s'appelle .collage dans le HTML généré */
    /* le lot, c'est la PRODUCTION (collage principal + sa « suite ») */
    lot = $$('.vignette[data-plein]',
             el.closest('.prod__medias') || el.closest('.collage') || document);
    if (!lot.length) return;
    i = Math.max(0, lot.indexOf(el));
    declencheur = el;
    glisse = false;
    boite.removeEventListener('transitionend', viderSiFerme);
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
    const vid = $('video', scene);
    if (vid) {
      vid.pause(); vid.removeAttribute('src'); vid.load();
      /* la vidéo de la grille avait été mise en pause à l'ouverture :
         sans ça elle restait figée, l'observateur ne refranchit aucun seuil */
      if (reArbitrer) reArbitrer();
    }
    boite.addEventListener('transitionend', viderSiFerme);
    if (declencheur) { declencheur.focus(); declencheur = null; }
  }

  /* Vidéo en grand (téléphone) : la visionneuse reçoit une copie de la
     vidéo, avec le son et les contrôles natifs. La vidéo de la grille
     est mise en pause ; l'arbitre la relance à la fermeture. */
  document.addEventListener('clip:engrand', ev => {
    const clip = ev.target, v = $('video', clip);
    if (!v) return;
    v.pause(); v.muted = true;
    const grand = document.createElement('video');
    grand.src = url(v);
    grand.controls = true; grand.playsInline = true; grand.setAttribute('playsinline', '');
    grand.preload = 'auto';
    grand.setAttribute('aria-label', v.getAttribute('aria-label') || 'Vidéo');
    lot = []; declencheur = v; glisse = false;
    boite.removeEventListener('transitionend', viderSiFerme);
    scene.replaceChildren(grand);
    legende.textContent = v.getAttribute('aria-label') || '';
    prec.hidden = suiv.hidden = true;
    boite.classList.add('ouverte');
    boite.setAttribute('aria-hidden', 'false');
    document.body.classList.add('bloque');
    grand.play().catch(() => {});   /* dans le geste du clic : le son passe */
  });

  const glisser = n => { if (!lot.length) return; i = (i + n + lot.length) % lot.length; peindre(); };

  $$('.vignette[data-plein]').forEach(el =>
    el.addEventListener('click', () => ouvrir(el))
  );

  fermer.addEventListener('click', clore);
  prec.addEventListener('click', () => glisser(-1));
  suiv.addEventListener('click', () => glisser(1));
  /* l'<img> absorbait le clic : la visionneuse restait ouverte */
  boite.addEventListener('click', e => {
    if (glisse) { glisse = false; return; }
    if (e.target.closest('.boite__barre, .boite__fleche, video')) return;
    clore();
  });

  addEventListener('keydown', e => {
    if (e.key === 'Escape' && nav.classList.contains('nav--ouverte')) { fermerMenu(true); return; }
    if (!boite.classList.contains('ouverte')) return;
    if (e.key === 'Escape')     { clore(); return; }
    if (e.key === 'ArrowLeft')  { glisser(-1); return; }
    if (e.key === 'ArrowRight') { glisser(1); return; }
    if (e.key === 'Tab') {
      /* vrai piège de focus : on tourne entre les commandes visibles */
      /* la vidéo en fait partie : sinon ses contrôles natifs étaient
         inatteignables au clavier, le piège ne tournant qu'entre les boutons */
      const cibles = [fermer, prec, suiv, $('video', scene)].filter(b => b && !b.hidden);
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
    /* en mode vidéo le lot est vide : ne pas armer « glisse », sinon le
       tap suivant hors de la vidéo ne fermait plus la visionneuse */
    if (Math.abs(d) > 48 && lot.length) { glisse = true; glisser(d < 0 ? 1 : -1); }
    x0 = null;
  }, { passive: true });
})();
