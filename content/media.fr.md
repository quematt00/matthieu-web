---
title: "Presse et médiation scientifique"
description: "Interventions, entretiens et écrits destinés à un public plus large."
layout: "page"
readingProgress:
  enable: true
---

<style>
.page.single .single-title {
  display: none;
}
.page.single {
  padding-top: 5rem;
  padding-bottom: 3rem;
}
h2, h3 {
  margin-top: 1.1rem;
}
hr.section-divider {
  border: 0;
  height: 1px;
  background: rgba(0, 0, 0, 0.08);
  margin: 2rem 0 1.5rem;
}
[data-theme='dark'] hr.section-divider {
  background: rgba(255, 255, 255, 0.12);
}

.page.single #content {
  --showcase-link: #2376b7;
  --showcase-link-hover: #ea517f;
  --showcase-meta: #000;
  --showcase-bullet: #4f82b9;
  --showcase-bullet-glow: rgba(79, 130, 185, 0.16);
}
[data-theme='dark'] .page.single #content {
  --showcase-link: #66b2ff;
  --showcase-link-hover: #cc5595;
  --showcase-meta: #b8d1ee;
  --showcase-bullet: #79b5ef;
  --showcase-bullet-glow: rgba(121, 181, 239, 0.2);
}
.page.single #content > ul {
  list-style: none;
  padding-left: 0;
  margin: 1.2rem 0 3rem;
}
.page.single #content > ul > li {
  --media-li-pad-y: 0.18rem;
  --media-li-line-height: 1.56;
  position: relative;
  margin: 0;
  padding: var(--media-li-pad-y) 0 var(--media-li-pad-y) 1.06rem;
  font-size: 1.08rem;
  line-height: var(--media-li-line-height);
  transition: transform 0.24s cubic-bezier(0.2, 0.75, 0.3, 1);
}
.page.single #content > ul > li::before {
  content: '';
  position: absolute;
  left: 0;
  top: calc(var(--media-li-pad-y) + (0.5em * var(--media-li-line-height)));
  width: 0.38rem;
  height: 0.38rem;
  border-radius: 999px;
  background: var(--showcase-bullet);
  opacity: 0.8;
  transform: translateY(-50%) scale(1);
  transition: transform 0.24s cubic-bezier(0.2, 0.75, 0.3, 1), opacity 0.24s ease, box-shadow 0.24s ease, filter 0.24s ease;
}
.page.single #content > ul > li::after {
  content: '';
  position: absolute;
  left: 0.19rem;
  top: calc(var(--media-li-pad-y) + (0.5em * var(--media-li-line-height)));
  width: 1.04rem;
  height: 1.04rem;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(79, 130, 185, 0.34) 0%, rgba(79, 130, 185, 0.14) 46%, rgba(79, 130, 185, 0) 78%);
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.58);
  transition: transform 0.32s cubic-bezier(0.18, 0.8, 0.22, 1), opacity 0.32s ease;
  pointer-events: none;
}
.page.single #content > ul > li:hover,
.page.single #content > ul > li:focus-within {
  transform: translateX(3px);
}
.page.single #content > ul > li:hover::before,
.page.single #content > ul > li:focus-within::before {
  opacity: 1;
  transform: translateY(-50%) scale(1.16);
  box-shadow: 0 0 0 0.14rem var(--showcase-bullet-glow);
  filter: saturate(112%);
}
.page.single #content > ul > li:hover::after,
.page.single #content > ul > li:focus-within::after {
  opacity: 0.96;
  transform: translate(-50%, -50%) scale(1.06);
}
.page.single #content > ul > li a {
  display: inline;
  font-size: inherit;
  line-height: inherit;
  font-weight: inherit;
  color: var(--showcase-link);
  letter-spacing: 0.002em;
  text-decoration: none !important;
  transition: color 0.2s ease;
}
.page.single #content > ul > li a:hover,
.page.single #content > ul > li a:focus-visible {
  color: var(--showcase-link-hover);
  text-decoration: none !important;
}
.page.single #content > ul > li em {
  display: inline;
  margin: 0;
  font-size: 1em;
  line-height: inherit;
  letter-spacing: 0;
  font-style: italic;
  font-weight: 400;
  color: var(--showcase-meta);
}
.page.single #content > ul > li strong {
  font-weight: 700;
}
[data-theme='dark'] .page.single #content > ul > li::after {
  background: radial-gradient(circle, rgba(121, 181, 239, 0.36) 0%, rgba(121, 181, 239, 0.15) 46%, rgba(121, 181, 239, 0) 78%);
}
@media (max-width: 640px) {
  .page.single #content > ul > li {
    --media-li-pad-y: 0.12rem;
    --media-li-line-height: 1.48;
    padding: var(--media-li-pad-y) 0 var(--media-li-pad-y) 0.94rem;
    font-size: 1.01rem;
    line-height: var(--media-li-line-height);
  }
  .page.single #content > ul > li::before {
    width: 0.34rem;
    height: 0.34rem;
  }
  .page.single #content > ul > li::after {
    left: 0.17rem;
    width: 0.9rem;
    height: 0.9rem;
  }
}
</style>

<h2>Presse et médiation scientifique</h2>

- **[Unser Mensch bei den Maschinen: Interview mit Matthieu Queloz](https://www.hauptstadt.be/a/philosophie-ki-queloz)**. *Hauptstadt: Neuer Berner Journalismus*, 4 avril 2026.
- **[Mechanistic Indicators of Understanding in Large Language Models](/fr/entries/mechanistic-indicators-of-understanding-in-large-language-models/)** a fait l’objet d’une présentation détaillée sur la chaîne *AI Explained* le 14 janvier 2026 : [https://youtu.be/wYs6HWZ2FdM?si=HOxvPU6NiWm4Hwjh&t=764](https://youtu.be/wYs6HWZ2FdM?si=HOxvPU6NiWm4Hwjh&t=764)
- **[Bernard Williams on Philosophy and History](/fr/books/bernard-williams-on-philosophy-and-history/)** a fait l’objet d’un article dans *Prospect Magazine* : [https://www.prospectmagazine.co.uk/culture/72871/bernard-williamss-reckoning-with-history](https://www.prospectmagazine.co.uk/culture/72871/bernard-williamss-reckoning-with-history)
- **Mechanistic Interpretability and How LLMs Understand**. *RSAM Podcast for Philosophy and Cognitive Science*. 10 janvier 2026. [https://open.spotify.com/episode/61XaYy42EGa8BjF5CnPjl3?si=a41c403438df4f8a](https://open.spotify.com/episode/61XaYy42EGa8BjF5CnPjl3?si=a41c403438df4f8a)
- **[Mechanistic Indicators of Understanding in Large Language Models](/fr/entries/mechanistic-indicators-of-understanding-in-large-language-models/)** a été analysé dans la série japonaise *Compass of the AI Era* le 18 juillet 2025 : [https://youtu.be/P06GXup5CcQ](https://youtu.be/P06GXup5CcQ)
- **Pragmatic Genealogy**. Podcast du *Moral Sciences Club*, University of Cambridge. [https://sms.cam.ac.uk/media/4728376](https://sms.cam.ac.uk/media/4728376)
- **Kein Sicherheitsnetz der Wahrheit: Warum Normativität für LLMs schwierig bleibt**. *meta(φ)* 13 (1): 51—89. 2025.
- **Richard Marshall interviews Matthieu Queloz**. *3:16 AM, End Times Series*. À paraître. [www.3-16am.co.uk](https://www.3-16am.co.uk/articles/.c/end-times-series)
- **Tracing Concepts to Needs**. *The Philosopher* 109 (3): 34—39. 2021. [https://philpapers.org/archive/QUETCT.pdf](https://philpapers.org/archive/QUETCT.pdf)
- **Ideas that Work**. *Aeon: A World of Ideas*, 24 juin 2021. [https://aeon.co/essays/our-most-abstract-concepts-emerged-as-solutions-to-our-needs](https://aeon.co/essays/our-most-abstract-concepts-emerged-as-solutions-to-our-needs)
- **Warum die liberale Demokratie laufend verteidigt werden muss**. *Schweizer Radio und Fernsehen* (SRF Kultur), 5 septembre 2015. https://www.srf.ch/kultur/gesellschaft-religion/gesellschaft-religion-warum-die-liberale-demokratie-laufend-verteidigt-werden-muss
- **Kolmogorov Axioms and Dutch Book Arguments**. Série d’introduction à la théorie de la rationalité, partie V. *Science Communication Blog*, tenu par des étudiants de l’Université de Bâle. 2013.
- **Updating Degrees of Belief**. Série d’introduction à la théorie de la rationalité, partie IV. *Science Communication Blog*, tenu par des étudiants de l’Université de Bâle. 2013.
- **The Base Rate Fallacy**. Série d’introduction à la théorie de la rationalité, partie III. *Science Communication Blog*, tenu par des étudiants de l’Université de Bâle. 2013.
- **Bayes’s Theorem**. Série d’introduction à la théorie de la rationalité, partie II. *Science Communication Blog*, tenu par des étudiants de l’Université de Bâle. 2013.
- **Subjective and Objective Probabilities**. Série d’introduction à la théorie de la rationalité, partie I. *Science Communication Blog*, tenu par des étudiants de l’Université de Bâle. 2013.
- **Problem und Chance zugleich**. *Basler Zeitung*, 4 mai 2011.
- **Momentaufnahme der Kunst im Wandel**. *Basler Zeitung*, 11 mars 2011.
- **Kunst auf Wanderschaft**. *Basler Zeitung*, 9 mars 2011. Avec Andrea Fopp.
- **Kaleidoskop der Elemente**. *Basler Zeitung*, 17 février 2011.
- **Hymne an die Solidarität**. *Basler Zeitung*, 10 mars 2011.
- **Arche Noah der Universalmaschinen**. *Basler Zeitung*, 2 mars 2011.
- **Woher weisst du, dass der Wurm drin ist?** *Basler Zeitung*, 20 janvier 2011.
- **Ein Spiegelkabinett der Urängste**. *Basler Zeitung*, 20 janvier 2011.
- **Ein Casting für Caesar und Napoleon**. *Basler Zeitung*, 11 janvier 2011.
- **Nostalgische Lautmalerei**. *Basler Zeitung*, 28 décembre 2010.
- **Ästhetik des Urbanen**. *Basler Zeitung*, 21 décembre 2010.
