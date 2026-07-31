/**
 * <ordered-checkbox-list>
 *
 * Renders a list of checkboxes from `items`. Checking a box appends its value to the end
 * of the ordered `value` array; unchecking it removes it from wherever it sits. Fires
 * `order-change` (CustomEvent, detail: { value: string[] }) on every change.
 *
 * Attributes:
 *   wrapper-class, input-class, label-class - applied verbatim to the shadow-internal
 *     wrapper/input/label elements, for consumers who want to reuse an existing stylesheet
 *   stylesheet-href - optional <link rel="stylesheet"> injected into the shadow root so
 *     wrapper-class/input-class/label-class actually render styled
 *
 * Properties:
 *   items - array of { value, label } (or plain strings) describing the checkboxes to render
 *   value - ordered array of currently-checked values; get returns live order, set
 *     reconciles checked state and order (e.g. to restore from a URL query param)
 *
 * CSS Parts: wrapper, input, label (per checkbox row) for ::part() styling.
 */
class OrderedCheckboxList extends HTMLElement {
  static get observedAttributes() {
    return ["wrapper-class", "input-class", "label-class", "stylesheet-href"];
  }

  constructor() {
    super();
    this._items = [];
    this._order = [];
    this.attachShadow({ mode: "open" });
  }

  connectedCallback() {
    this._render();
  }

  attributeChangedCallback() {
    this._render();
  }

  get items() {
    return this._items;
  }

  set items(newItems) {
    this._items = (newItems ?? []).map((item) =>
      typeof item === "string" ? { value: item, label: item } : item
    );
    // Keep only still-existing values, preserving their relative order
    const validValues = new Set(this._items.map((item) => item.value));
    this._order = this._order.filter((value) => validValues.has(value));
    this._render();
  }

  get value() {
    return [...this._order];
  }

  set value(newValue) {
    this._order = [...(newValue ?? [])];
    this._render();
  }

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

  _instanceId() {
    if (!this._id) {
      this._id = this.id || `ordered-checkbox-list-${Math.random().toString(36).slice(2)}`;
    }
    return this._id;
  }
}

customElements.define("ordered-checkbox-list", OrderedCheckboxList);
