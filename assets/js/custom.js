(() => {
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
})();
