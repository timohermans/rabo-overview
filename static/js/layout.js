class Cluster extends HTMLElement {
  constructor() {
    super();
  }

  generateCss() {
    return `
    [data-style-id="${this.styleId}"] {
      justify-content: ${this.justify};
      align-items: ${this.align};
      gap: ${this.space};
    }
  `;
  }

  get justify() {
    return this.getAttribute("justify") || "flex-start";
  }

  get align() {
    return this.getAttribute("align") || "flex-start";
  }

  get space() {
    return this.getAttribute("space") || "var(--s1)";
  }

  static get observedAttributes() {
    return ["justify", "align", "space"];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  render() {
    this.styleId = `Cluster-${[this.justify, this.align, this.space].join("")}`;
    this.dataset.styleId = this.styleId;

    if (document.getElementById(this.styleId)) return;
    const styleEl = document.createElement("style");
    styleEl.id = this.styleId;
    styleEl.innerHTML = this.generateCss().replace(/\s\s+/g, " ").trim();
    document.head.appendChild(styleEl);
  }
}

class Center extends HTMLElement {
  constructor() {
    super();
  }
}

if ("customElements" in window) {
  customElements.define("cluster-l", Cluster);
  customElements.define("space-l", class extends HTMLElement {});
}
