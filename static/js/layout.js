class LayoutComponents extends HTMLElement {
  constructor() {
    super();
  }

  getStyleValues() {
    return Object.entries(
      Object.getOwnPropertyDescriptors(Object.getPrototypeOf(this))
    )
      .filter(([key, descriptor]) => typeof descriptor.get == "function")
      .map(([key]) => this[key]);
  }

  generateCss() {
    throw new Error("Override generateCss() and print the css stylesheet!");
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  render() {
    this.styleId = `${this.constructor.name}-${this.getStyleValues()}`;
    this.dataset.styleId = this.styleId;

    if (document.getElementById(this.styleId)) return;
    const styleElement = document.createElement("style");
    styleElement.id = this.styleId;
    const css = this.generateCss();
    if (css.indexOf(`[data-style-id="${this.styleId}"]`) === -1) {
        throw new Error("Use [data-style-id=\"${this.styleId}\"] in the generateCss function!");
    }
    styleElement.innerHTML = css.replace(/\s\s+/g, " ").trim();
    document.head.appendChild(styleElement);
  }
}

class Cluster extends LayoutComponents {
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
}

class Stack extends LayoutComponents {
  constructor() {
    super();
  }

  get space() {
    return this.getAttribute("space") || "var(--s0)";
  }

  generateCss() {
    return `[data-style-id="${this.styleId}"] > * + * {
      margin-top: ${this.space};
    }
    `;
  }
}

if ("customElements" in window) {
  customElements.define("cluster-l", Cluster);
  customElements.define("space-l", class extends HTMLElement {});
  customElements.define("stack-l", Stack);
}
