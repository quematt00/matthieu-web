---
title: "Media"
description: "Talks, interviews, and public-facing writing."
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

<h2>{{< i18n "section_media" >}}</h2>

- **[Mechanistic Indicators of Understanding in Large Language Models](/entries/mechanistic-indicators-of-understanding-in-large-language-models/)** was featured in the hugely popular video series *AI Explained* on January 14, 2026: [https://youtu.be/wYs6HWZ2FdM?si=HOxvPU6NiWm4Hwjh&t=764](https://youtu.be/wYs6HWZ2FdM?si=HOxvPU6NiWm4Hwjh&t=764)
- **Mechanistic Interpretability and How LLMs Understand**. *RSAM Podcast for Philosophy and Cognitive Science*. January 10, 2026. [https://open.spotify.com/episode/61XaYy42EGa8BjF5CnPjl3?si=a41c403438df4f8a](https://open.spotify.com/episode/61XaYy42EGa8BjF5CnPjl3?si=a41c403438df4f8a)
- **[Mechanistic Indicators of Understanding in Large Language Models](/entries/mechanistic-indicators-of-understanding-in-large-language-models/)** was featured in the Japanese paper commentary series *Compass of the AI Era* on July 18, 2025: [https://youtu.be/P06GXup5CcQ](https://youtu.be/P06GXup5CcQ)
- **Pragmatic Genealogy**. Podcast of the *Moral Sciences Club*, University of Cambridge. [https://sms.cam.ac.uk/media/4728376](https://sms.cam.ac.uk/media/4728376)
- **Kein Sicherheitsnetz der Wahrheit: Warum Normativität für LLMs schwierig bleibt**. *meta(φ)* 13 (1): 51—89. 2025.
- **Richard Marshall interviews Matthieu Queloz**. *3:16 AM, End Times Series*. Forthcoming. [www.3-16am.co.uk](https://www.3-16am.co.uk/articles/.c/end-times-series)
- **Tracing Concepts to Needs**. *The Philosopher* 109 (3): 34—39. 2021. [https://philpapers.org/archive/QUETCT.pdf](https://philpapers.org/archive/QUETCT.pdf)
- **Ideas that Work**. *Aeon: A World of Ideas*, June 24, 2021. [https://aeon.co/essays/our-most-abstract-concepts-emerged-as-solutions-to-our-needs](https://aeon.co/essays/our-most-abstract-concepts-emerged-as-solutions-to-our-needs)
- **Warum die liberale Demokratie laufend verteidigt werden muss**. *Schweizer Radio und Fernsehen* (SRF Kultur), September 5, 2015. https://www.srf.ch/kultur/gesellschaft-religion/gesellschaft-religion-warum-die-liberale-demokratie-laufend-verteidigt-werden-muss
- **Kolmogorov Axioms and Dutch Book Arguments**. Introductory Series on the Theory of Rationality, Part V. *Science Communication Blog* run by students of the University of Basel. 2013.
- **Updating Degrees of Belief**. Introductory Series on the Theory of Rationality, Part IV. *Science Communication Blog* run by students of the University of Basel. 2013.
- **The Base Rate Fallacy**. Introductory Series on the Theory of Rationality, Part III. *Science Communication Blog* run by students of the University of Basel. 2013.
- **Bayes’s Theorem**. Introductory Series on the Theory of Rationality, Part II. *Science Communication Blog* run by students of the University of Basel. 2013.
- **Subjective and Objective Probabilities**. Introductory Series on the Theory of Rationality, Part I. *Science Communication Blog* run by students of the University of Basel. 2013.
- **Problem und Chance zugleich**. *Basler Zeitung*, May 4, 2011.
- **Momentaufnahme der Kunst im Wandel**. *Basler Zeitung*, March 11, 2011.
- **Kunst auf Wanderschaft**. *Basler Zeitung*, March 9, 2011. With Andrea Fopp.
- **Kaleidoskop der Elemente**. *Basler Zeitung*, February 17, 2011.
- **Hymne an die Solidarität**. *Basler Zeitung*, March 10, 2011.
- **Arche Noah der Universalmaschinen**. *Basler Zeitung*, March 2, 2011.
- **Woher weisst du, dass der Wurm drin ist?** *Basler Zeitung*, January 20, 2011.
- **Ein Spiegelkabinett der Urängste**. *Basler Zeitung*, January 20, 2011.
- **Ein Casting für Caesar und Napoleon**. *Basler Zeitung*, January 11, 2011.
- **Nostalgische Lautmalerei**. *Basler Zeitung*, December 28, 2010.
- **Ästhetik des Urbanen**. *Basler Zeitung*, December 21, 2010.
