/**
 * @typedef {Object} OrderedCheckboxListItem
 * @property {string} value
 * @property {string} label
 */

/**
 * @typedef {Object} OrderChangeEventDetail
 * @property {string[]} value - The ordered array of currently-checked values.
 */

/**
 * Renders a list of checkboxes from `items`. Checking a box appends its value to the end
 * of the ordered `value` array; unchecking it removes it from wherever it sits.
 *
 * @element ordered-checkbox-list
 *
 * @attr {string} wrapper-class - Applied verbatim to the shadow-internal wrapper `<div>`,
 *   for consumers who want to reuse an existing stylesheet.
 * @attr {string} input-class - Applied verbatim to the shadow-internal `<input>`.
 * @attr {string} label-class - Applied verbatim to the shadow-internal `<label>`.
 * @attr {string} stylesheet-href - Optional `<link rel="stylesheet">` href injected into
 *   the shadow root so `wrapper-class`/`input-class`/`label-class` actually render styled.
 *
 * @csspart wrapper - The `<div>` wrapping each checkbox/label pair.
 * @csspart input - Each `<input type="checkbox">`.
 * @csspart label - Each `<label>`.
 *
 * @fires {CustomEvent<OrderChangeEventDetail>} order-change - Fired after every check/uncheck.
 */
class OrderedCheckboxList extends HTMLElement {
  /** @returns {string[]} */
  static get observedAttributes() {
    return ["wrapper-class", "input-class", "label-class", "stylesheet-href"];
  }

  constructor() {
    super();
    /** @type {OrderedCheckboxListItem[]} */
    this._items = [];
    /** @type {string[]} */
    this._order = [];
    this.attachShadow({ mode: "open" });
  }

  /** @returns {void} */
  connectedCallback() {
    this._render();
  }

  /** @returns {void} */
  attributeChangedCallback() {
    this._render();
  }

  /** @type {OrderedCheckboxListItem[]} */
  get items() {
    return this._items;
  }

  /**
   * @param {(OrderedCheckboxListItem | string)[]} newItems - Plain strings are normalized
   *   to `{ value: s, label: s }`. Re-renders, preserving checked state for values that
   *   still exist.
   */
  set items(newItems) {
    this._items = (newItems ?? []).map((item) =>
      typeof item === "string" ? { value: item, label: item } : item
    );
    // Keep only still-existing values, preserving their relative order
    const validValues = new Set(this._items.map((item) => item.value));
    this._order = this._order.filter((value) => validValues.has(value));
    this._render();
  }

  /** @type {string[]} The ordered array of currently-checked values. */
  get value() {
    return [...this._order];
  }

  /**
   * @param {string[]} newValue - Reconciles which boxes are checked and their order (e.g.
   *   to restore state from a URL query param).
   */
  set value(newValue) {
    this._order = [...(newValue ?? [])];
    this._render();
  }

  /** @returns {void} */
  _render() {
    if (!this.shadowRoot) {
      return;
    }

    const wrapperClass = this.getAttribute("wrapper-class") ?? "";
    const inputClass = this.getAttribute("input-class") ?? "";
    const labelClass = this.getAttribute("label-class") ?? "";
    const stylesheetHref = this.getAttribute("stylesheet-href");

    const stylesheetLink = stylesheetHref
      ? `<link rel="stylesheet" href="${stylesheetHref}">`
      : "";

    const rows = this._items
      .map((item, index) => {
        const inputId = `${this._instanceId()}-${index}`;
        const checked = this._order.includes(item.value);
        return `
          <div part="wrapper" class="${wrapperClass}">
            <input
              type="checkbox"
              part="input"
              class="${inputClass}"
              id="${inputId}"
              data-value="${item.value}"
              ${checked ? "checked" : ""}
            />
            <label part="label" class="${labelClass}" for="${inputId}">${item.label}</label>
          </div>
        `;
      })
      .join("");

    this.shadowRoot.innerHTML = `${stylesheetLink}${rows}`;

    this.shadowRoot.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
      checkbox.addEventListener("change", (event) => this._handleChange(event));
    });
  }

  /**
   * @param {Event & { target: HTMLInputElement }} event
   * @returns {void}
   */
  _handleChange(event) {
    const value = event.target.dataset.value;

    if (event.target.checked) {
      this._order.push(value);
    } else {
      const index = this._order.indexOf(value);
      if (index >= 0) {
        this._order.splice(index, 1);
      }
    }

    this.dispatchEvent(
      new CustomEvent("order-change", {
        bubbles: true,
        composed: true,
        detail: { value: [...this._order] },
      })
    );
  }

  /** @returns {string} */
  _instanceId() {
    if (!this._id) {
      this._id = this.id || `ordered-checkbox-list-${Math.random().toString(36).slice(2)}`;
    }
    return this._id;
  }
}

customElements.define("ordered-checkbox-list", OrderedCheckboxList);
