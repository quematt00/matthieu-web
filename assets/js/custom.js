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
      const explicitLabel = (link.dataset.downloadLabel || "").trim();
      const explicitTitle = (link.dataset.downloadTitle || "").trim();
      const title = explicitTitle || (existingAria ? extractTitleFromAriaLabel(existingAria) : null);

      if (hasLink) {
        link.setAttribute("target", "_blank");

        const existingRel = (link.getAttribute("rel") || "").trim();
        const relParts = existingRel ? existingRel.split(/\s+/) : [];
        for (const needed of ["noopener", "noreferrer"]) {
          if (!relParts.includes(needed)) relParts.push(needed);
        }
        link.setAttribute("rel", relParts.join(" "));

        const label = explicitLabel || labelDownload;
        setDownloadLinkText(link, label);
        link.setAttribute("aria-label", title ? `${label}: ${title}` : label);
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

  function markEntryMetaLinks(root) {
    const links = root.querySelectorAll?.(".entry-item > p:first-of-type a") ?? [];

    for (const link of links) {
      const href = (link.getAttribute("href") || "").trim();
      const text = (link.textContent || "").trim();

      const isDoiLink = /^doi:/i.test(text);
      const isBareUrlLabel = /^https?:\/\//i.test(text);
      const isPdfLink = /\.pdf(?:$|[?#])/i.test(href);
      const isPhilPapersArchive = /philpapers\.org\/archive\//i.test(href);

      link.classList.toggle(
        "entry-meta-link--aux",
        isDoiLink || isBareUrlLabel || isPdfLink || isPhilPapersArchive,
      );
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => markEntryMetaLinks(document));
  } else {
    markEntryMetaLinks(document);
  }

  function markEntryTags(root) {
    const tagSpans = root.querySelectorAll?.(".entry-item span") ?? [];
    for (const span of tagSpans) {
      if (span.querySelector?.(".fa-tags")) {
        span.classList.add("entry-tags");
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => markEntryTags(document));
  } else {
    markEntryTags(document);
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

  function searchDateRank(value) {
    const date = (value || "").trim().toLowerCase();
    const manuscriptValues = new Set([
      "manuscript",
      "manuscrit",
      "manuskript",
      "under review",
      "en cours d’évaluation",
      "en cours d'evaluation",
      "in begutachtung",
    ]);
    const forthcomingValues = new Set([
      "forthcoming",
      "à paraître",
      "a paraitre",
      "im erscheinen",
      "in press",
      "sous presse",
    ]);

    if (manuscriptValues.has(date)) return 0;
    if (forthcomingValues.has(date)) return 1;
    if (/^\d{4}$/.test(date)) return 3;
    return 2;
  }

  function searchDateYear(value) {
    const date = (value || "").trim();
    if (!/^\d{4}$/.test(date)) return null;
    return Number.parseInt(date, 10);
  }

  function reorderSearchSuggestions(dropdownEl) {
    if (!dropdownEl || dropdownEl.dataset.sortingSuggestions === "1") return;

    let options = Array.from(dropdownEl.querySelectorAll('[role="option"]')).filter((node) =>
      node.querySelector(".suggestion-date")
    );
    if (!options.length) {
      options = Array.from(dropdownEl.querySelectorAll(".suggestion")).filter((node) =>
        node.querySelector(".suggestion-date")
      );
    }
    if (options.length < 2) return;

    const sorted = options
      .map((node, index) => {
        const dateText = node.querySelector(".suggestion-date")?.textContent ?? "";
        return {
          node,
          index,
          rank: searchDateRank(dateText),
          year: searchDateYear(dateText),
        };
      })
      .sort((a, b) => {
        if (a.rank !== b.rank) return a.rank - b.rank;
        if (a.rank === 3 && b.rank === 3 && a.year !== b.year) return (b.year ?? 0) - (a.year ?? 0);
        return a.index - b.index;
      });

    const hasChanges = sorted.some((item, index) => item.node !== options[index]);
    if (!hasChanges) return;

    dropdownEl.dataset.sortingSuggestions = "1";
    try {
      for (const item of sorted) {
        item.node.parentElement?.appendChild(item.node);
      }
    } finally {
      dropdownEl.dataset.sortingSuggestions = "0";
    }
  }

  function setupSearchSuggestionSorting(root) {
    const dropdowns = [
      root.querySelector("#search-dropdown-desktop"),
      root.querySelector("#search-dropdown-mobile"),
    ].filter(Boolean);
    if (!dropdowns.length) return;

    for (const dropdown of dropdowns) {
      reorderSearchSuggestions(dropdown);
      const observer = new MutationObserver(() => reorderSearchSuggestions(dropdown));
      observer.observe(dropdown, { childList: true, subtree: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setupSearchSuggestionSorting(document));
  } else {
    setupSearchSuggestionSorting(document);
  }
})();
