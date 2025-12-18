(() => {
  function prefersReducedMotion() {
    return (
      typeof window !== "undefined" &&
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
  }

  function languageCode() {
    const lang = (document.documentElement.getAttribute("lang") || "").toLowerCase();
    if (lang.startsWith("fr")) return "fr";
    if (lang.startsWith("de")) return "de";
    return "en";
  }

  function comingSoonLabel(lang) {
    if (lang === "fr") return "PDF à venir";
    if (lang === "de") return "PDF folgt";
    return "PDF coming soon";
  }

  function downloadPdfLabel(lang) {
    if (lang === "fr") return "Télécharger le PDF";
    if (lang === "de") return "PDF herunterladen";
    return "Download PDF";
  }

  function extractTitleFromAriaLabel(ariaLabel) {
    const patterns = [
      /^Download PDF of (.+)$/i,
      /^Télécharger le PDF de (.+)$/i,
      /^PDF von (.+) herunterladen$/i,
    ];
    for (const pattern of patterns) {
      const match = ariaLabel.match(pattern);
      if (match) return match[1].trim();
    }
    return null;
  }

  function setDownloadLinkText(link, label) {
    const icon = link.querySelector("i");
    if (!icon) {
      link.textContent = label;
      return;
    }

    let node = icon.nextSibling;
    while (node) {
      const next = node.nextSibling;
      link.removeChild(node);
      node = next;
    }
    link.appendChild(document.createTextNode(` ${label}`));
  }

  function ensureDownloadLinksOpenNewTab(root) {
    const links = root.querySelectorAll?.("a.download-link") ?? [];
    const lang = languageCode();
    const labelComingSoon = comingSoonLabel(lang);
    const labelDownload = downloadPdfLabel(lang);

    for (const link of links) {
      const href = (link.getAttribute("href") || "").trim();

      const hasLink = !!href && !href.startsWith("#");

      const existingAria = (link.getAttribute("aria-label") || "").trim();
      const title = existingAria ? extractTitleFromAriaLabel(existingAria) : null;

      if (hasLink) {
        link.setAttribute("target", "_blank");

        const existingRel = (link.getAttribute("rel") || "").trim();
        const relParts = existingRel ? existingRel.split(/\s+/) : [];
        for (const needed of ["noopener", "noreferrer"]) {
          if (!relParts.includes(needed)) relParts.push(needed);
        }
        link.setAttribute("rel", relParts.join(" "));

        setDownloadLinkText(link, labelDownload);
        link.setAttribute("aria-label", title ? `${labelDownload}: ${title}` : labelDownload);
      } else {
        link.removeAttribute("target");
        link.removeAttribute("rel");
        setDownloadLinkText(link, labelComingSoon);
        link.setAttribute("aria-label", title ? `${labelComingSoon}: ${title}` : labelComingSoon);
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => ensureDownloadLinksOpenNewTab(document));
  } else {
    ensureDownloadLinksOpenNewTab(document);
  }

  function setupBookAudioButtons(root) {
    const buttons = root.querySelectorAll?.("a.book-audio-button") ?? [];
    if (!buttons.length) return;

    let activePlayer = null;

    function getOrCreatePlayer(bookMediaEl) {
      let player = bookMediaEl.querySelector?.("audio.book-audio-player");
      if (player) return player;

      player = document.createElement("audio");
      player.className = "book-audio-player";
      player.controls = true;
      player.preload = "none";
      player.setAttribute("playsinline", "");
      player.hidden = true;

      const actions = bookMediaEl.querySelector?.(".book-actions");
      if (actions && actions.parentElement === bookMediaEl) {
        actions.insertAdjacentElement("afterend", player);
      } else {
        bookMediaEl.appendChild(player);
      }

      return player;
    }

    for (const button of buttons) {
      button.addEventListener("click", (event) => {
        const href = (button.getAttribute("href") || "").trim();
        const bookMedia = button.closest?.(".book-media");

        if (!href || !bookMedia) return;

        event.preventDefault();

        const player = getOrCreatePlayer(bookMedia);
        const src = new URL(href, window.location.href).toString();

        if (activePlayer && activePlayer !== player) {
          activePlayer.pause();
          activePlayer.hidden = true;
        }

        activePlayer = player;
        player.hidden = false;

        if (player.src !== src) {
          player.src = src;
        }

        const shouldPlay = player.paused || player.ended;
        if (shouldPlay) {
          player.play().catch(() => {
            window.location.href = src;
          });
        } else {
          player.pause();
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setupBookAudioButtons(document));
  } else {
    setupBookAudioButtons(document);
  }

  function triggerGlobeTapAnimation(toggleEl) {
    if (prefersReducedMotion()) return;
    const icon = toggleEl.querySelector?.(".fa-globe");
    if (!icon) return;
    icon.classList.remove("globe-tap");
    // Force reflow so the animation can replay on rapid taps.
    void icon.offsetWidth;
    icon.classList.add("globe-tap");
    icon.addEventListener(
      "animationend",
      () => {
        icon.classList.remove("globe-tap");
      },
      { once: true }
    );
  }

  function triggerThemeTapAnimation(themeSwitchEl) {
    if (prefersReducedMotion()) return;
    const icon = themeSwitchEl.querySelector?.(".fa-adjust");
    if (!icon) return;
    icon.classList.remove("theme-tap");
    void icon.offsetWidth;
    icon.classList.add("theme-tap");
    icon.addEventListener(
      "animationend",
      () => {
        icon.classList.remove("theme-tap");
      },
      { once: true }
    );
  }

  // Animate header icons on tap/click (works on mobile too).
  document.addEventListener(
    "pointerdown",
    (event) => {
      const themeSwitch = event.target?.closest?.("#header-mobile .theme-switch");
      if (themeSwitch) triggerThemeTapAnimation(themeSwitch);

      const toggle = event.target?.closest?.(
        "#header-desktop .language-switch > span[role=\"button\"], #header-mobile .language-switch > span[role=\"button\"]"
      );
      if (toggle) triggerGlobeTapAnimation(toggle);
    },
    true
  );
})();
