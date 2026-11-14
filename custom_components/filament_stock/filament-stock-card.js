/**
 * Filament Stock card: list of filaments, search, filters by brand / material / colour.
 * A click on a filament opens a dialog: set the grams, add a full spool, link barcodes.
 *
 * Plain custom element with Home Assistant's own controls (ha-card, ha-input, ha-select),
 * like the Nokturno card. The integration loads it as a Lovelace resource.
 *
 *   type: custom:filament-stock-card
 *   title: Filament        # optional
 *   show_header: true      # optional
 *   show_empty: false      # optional, filaments with 0 g (a toggle in the card too)
 */

import { STRINGS, fill, startScan } from "./panel.js";

const CARD = {
  en: {
    title: "Filament",
    search: "Search filament",
    all: "All",
    count: "{n} filaments · {kg} kg",
    shown: "{n} of {all} · {grams}",
    show_empty: "Show empty ({n})",
    hide_empty: "Hide empty",
    nothing: "No filament matches.",
    empty: "No filaments yet: set the profile on an AMS slot first.",
    grams: "Grams left",
    save: "Save",
    add_spool: "Add a full spool (+{g} g)",
    codes: "Barcodes",
    no_codes: "No barcode yet.",
    link: "Link",
    edit: "Edit",
    remove: "Remove",
    linked: "Code {code} linked.",
    saved: "Saved: {grams} g",
    spool_added: "+{g} g, now {grams} g",
    close: "Close",
    sync: "Load profiles from Bambu Cloud",
    synced: "Profiles loaded: {profiles} own, {new} new, {changed} changed.",
    low: "Running low",
  },
  cs: {
    title: "Filament",
    search: "Hledat filament",
    all: "Vše",
    count: "{n} filamentů · {kg} kg",
    shown: "{n} z {all} · {grams}",
    show_empty: "Zobrazit prázdné ({n})",
    hide_empty: "Skrýt prázdné",
    nothing: "Nic tomu neodpovídá.",
    empty: "Zatím žádný filament: nastavte nejdřív profil na slotu AMS.",
    grams: "Zbývá gramů",
    save: "Uložit",
    add_spool: "Přidat celou cívku (+{g} g)",
    codes: "Čárové kódy",
    no_codes: "Zatím žádný kód.",
    link: "Přiřadit",
    edit: "Upravit",
    remove: "Odebrat",
    linked: "Kód {code} přiřazen.",
    saved: "Uloženo: {grams} g",
    spool_added: "+{g} g, nyní {grams} g",
    close: "Zavřít",
    sync: "Načíst profily z Bambu Cloudu",
    synced: "Profily načtené: {profiles} vlastních, {new} nových, {changed} změněných.",
    low: "Dochází",
  },
};

const DIALOG_CSS = `
        .fs-body { min-width:min(80vw, 380px); font-family: var(--ha-font-family-body, sans-serif); }
        .fs-title { display:inline-flex; align-items:center; gap:10px; }
        .fs-dot { flex:none; width:28px; height:28px; border-radius:50%; border:2px solid var(--divider-color);
          box-sizing:border-box; background: var(--secondary-background-color); }
        .fs-body .big { display:flex; align-items:center; gap:12px; margin:0 0 4px; font-size:2rem; font-weight:500; font-variant-numeric: tabular-nums; }
        .fs-body .big small { font-size:.9rem; color: var(--warning-color); font-weight:400; margin-left:6px; }
        .fs-body .sec { margin-top:16px; font-size:.75rem; font-weight:600; letter-spacing:.02em;
          color: var(--secondary-text-color); text-transform:uppercase; }
        .fs-body .line { display:flex; gap:8px; margin-top:6px; align-items:center; }
        .fs-body input { flex:1; min-width:0; font:inherit; padding:10px 12px; border-radius:10px; height:40px;
          border:1px solid var(--divider-color); background: var(--secondary-background-color);
          color: var(--primary-text-color); box-sizing:border-box; }
        .fs-body ha-control-button { flex:none; min-width:96px; height:40px; }
        .fs-body ha-control-button.wide { display:block; width:100%; margin-top:8px; }
        .fs-body ha-control-button ha-icon { --mdc-icon-size:20px; margin-right:4px; vertical-align:-4px; }
        .fs-body .code { display:flex; align-items:center; gap:4px; padding:2px 0;
          border-bottom:1px solid var(--divider-color); font-variant-numeric: tabular-nums; }
        .fs-body .code span { flex:1; }
        .fs-body .code input { padding:6px 8px; height:36px; }
        .fs-body .code ha-icon-button { --mdc-icon-button-size:36px; --mdc-icon-size:20px; color: var(--secondary-text-color); }
        .fs-body .muted { color: var(--secondary-text-color); font-size:.85rem; margin-top:6px; }
        .fs-body video { width:100%; border-radius:10px; background:#000; margin-top:8px; }
        .fs-body video[hidden] { display:none; }
        .fs-body .fs-note { margin-top:12px; padding:8px 10px; border-radius:10px; font-size:.85rem; }
        .fs-body .fs-note.ok { background: rgba(var(--rgb-success-color), .15); }
        .fs-body .fs-note.error { background: rgba(var(--rgb-error-color), .15); }
        .fs-body filament-stock-scan { display:block; }
        /* fallback without ha-dialog (old frontend) */
        .filament-stock-dialog { position:fixed; inset:0; z-index:99; background:rgba(0,0,0,.5);
          display:flex; align-items:center; justify-content:center; padding:16px; box-sizing:border-box; }
        .filament-stock-dialog .panel { background: var(--card-background-color); color: var(--primary-text-color);
          border-radius:24px; padding:8px 24px 24px; max-width:440px; max-height:calc(100vh - 32px); overflow:auto; box-sizing:border-box; }
        .filament-stock-dialog .phead { display:flex; align-items:center; gap:8px; min-height:56px; font-size:1.3rem; }
        .filament-stock-dialog .phead .fs-title { flex:1; }
        .filament-stock-dialog .phead small { display:block; font-size:.85rem; color: var(--secondary-text-color); }
`;

const FILTERS = ["brand", "material", "color"];
const ALL = "*";

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

class FilamentStockCard extends HTMLElement {
  setConfig(config) {
    this._config = { show_header: true, ...config };
    this._filter = { brand: ALL, material: ALL, color: ALL };
    this._query = "";
    this._empty = !!this._config.show_empty;
  }

  static getStubConfig() {
    return { type: "custom:filament-stock-card" };
  }

  getCardSize() {
    return 6;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6 };
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._t) {
      const lang = String((hass.locale && hass.locale.language) || hass.language || "en").slice(0, 2);
      this._lang = lang;
      this._t = { ...(STRINGS[lang] || STRINGS.en), ...(CARD[lang] || CARD.en) };
      this._ready().then(() => {
        this._render();
        this._load();
      });
      return;
    }
    if (this._scanner) this._scanner.hass = hass;
    // A new hass comes on every state change in the house; reload only when a stock entity changed.
    if (this._root && this._stockChanged()) this._load();
  }

  async _ready() {
    const needed = ["ha-card", "ha-input", "ha-select", "ha-icon", "ha-control-button", "ha-icon-button"];
    if (needed.every((tag) => customElements.get(tag))) return;
    try {
      await window.loadCardHelpers();
    } catch (err) {
      // Older frontend: it renders anyway.
    }
    await Promise.race([
      Promise.all(needed.map((tag) => customElements.whenDefined(tag))),
      new Promise((done) => setTimeout(done, 3000)),
    ]);
  }

  // Stock entities are the number entities with these attributes; state objects only change
  // when the entity does, so comparing references is enough.
  _stockChanged() {
    const states = this._hass.states;
    const now = Date.now();
    if (!this._ids || now - this._idsAt > 60000) {
      this._ids = Object.keys(states).filter((id) => id.startsWith("number.") && states[id].attributes.spools !== undefined && "filament_id" in states[id].attributes);
      this._idsAt = now;
    }
    const snap = this._ids.map((id) => states[id]);
    const prev = this._snap;
    this._snap = snap;
    return !prev || prev.length !== snap.length || snap.some((s, i) => s !== prev[i]);
  }

  async _ws(type, data = {}) {
    return this._hass.callWS({ type: `filament_stock/${type}`, ...data });
  }

  async _load() {
    try {
      const { items } = await this._ws("items");
      this._items = items.sort((a, b) => (a.brand || "~").localeCompare(b.brand || "~") || a.material.localeCompare(b.material) || a.color.localeCompare(b.color));
      this._error = "";
    } catch (err) {
      this._error = this._t.error + (err.message || err.code);
    }
    this._paint();
    if (this._open) this._paintDialog();
  }

  _num(n, digits = 0) {
    return Number(n).toLocaleString(this._lang, { maximumFractionDigits: digits });
  }

  _render() {
    const t = this._t;
    this.attachShadow({ mode: "open" });
    this.shadowRoot.innerHTML = `
      <style>
        ha-card { padding: 12px 14px 8px; }
        .head { display:flex; align-items:center; gap:8px; margin-bottom:10px; }
        .head h2 { margin:0; font-size:1.15rem; font-weight:500; flex:1; }
        .head .sum { font-size:.8rem; color: var(--secondary-text-color); }
        .filters { display:grid; grid-template-columns:repeat(auto-fit, minmax(110px, 1fr)); gap:8px; margin-top:8px; }
        .filters ha-select { width:100%; }
        .pick { display:flex; flex-direction:column; justify-content:center; gap:1px; padding:5px 10px;
                background: var(--secondary-background-color); border-radius:12px; min-height:48px; }
        .pick > span { font-size:.7rem; color: var(--secondary-text-color); }
        .pick select { border:none; background:none; color: var(--primary-text-color); font:inherit; font-size:.9rem;
                       padding:0; width:100%; outline:none; }
        .pick option { background: var(--card-background-color, #1c1c1c); color: var(--primary-text-color); }
        /* like the Nokturno card: search, then the button over the full width */
        .bar { display:grid; grid-template-columns:1fr; gap:8px; }
        #q { display:block; }
        /* scan + sync in one row, like Hledat + the cache bin in Nokturno */
        .scanrow { display:flex; gap:8px; align-items:stretch; }
        ha-control-button#scan { flex:1; }
        ha-control-button#sync { flex:0 0 40px; --control-button-padding: 0; }
        ha-control-button#sync ha-icon { --mdc-icon-size:18px; }
        ha-control-button#sync.busy ha-icon { animation: fs-spin 1s linear infinite; }
        @keyframes fs-spin { to { transform: rotate(360deg); } }
        ha-control-button#scan ha-icon { --mdc-icon-size:20px; margin-right:4px; vertical-align:-4px; }
        .list { margin-top:8px; }
        .row { display:flex; align-items:center; gap:12px; width:100%; padding:10px 4px; border:none; background:none;
               color:inherit; font:inherit; text-align:left; cursor:pointer; border-bottom:1px solid var(--divider-color); }
        .row:last-child { border-bottom:none; }
        .row:hover { background: var(--secondary-background-color); border-radius:8px; }
        .dot { flex:none; width:26px; height:26px; border-radius:50%; border:2px solid var(--divider-color);
               box-sizing:border-box; background: var(--secondary-background-color); }
        .name { flex:1; min-width:0; }
        .name .l { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .name .s { font-size:.78rem; color: var(--secondary-text-color); }
        .qty { text-align:right; white-space:nowrap; font-variant-numeric: tabular-nums; }
        .qty .g { font-weight:500; }
        .row.zero .g { color: var(--secondary-text-color); font-weight:400; }
        .row.low:not(.zero) .g { color: var(--warning-color, #ff9800); }
        .toggle { border:none; background:none; color: var(--primary-color); font:inherit; cursor:pointer; padding:0; }
        .total { display:flex; justify-content:space-between; gap:8px; margin:10px 4px 0; font-size:.85rem;
                 color: var(--secondary-text-color); font-variant-numeric: tabular-nums; }
        .muted { color: var(--secondary-text-color); font-size:.85rem; margin:12px 2px; }
        .err { color: var(--error-color); font-size:.85rem; margin-top:8px; }
        [hidden] { display:none !important; }
      </style>
      <ha-card>
        <div class="head"${this._config.show_header ? "" : " hidden"}>
          <ha-icon icon="mdi:printer-3d-nozzle"></ha-icon>
          <h2>${esc(this._config.title || t.title)}</h2>
          <span class="sum" id="sum"></span>
        </div>
        <div class="bar">
          <ha-input id="q" placeholder="${esc(t.search)}" with-clear></ha-input>
          <div class="scanrow">
            <ha-control-button id="scan"><ha-icon icon="mdi:barcode-scan"></ha-icon> ${esc(t.scan)}</ha-control-button>
            <ha-control-button id="sync" title="${esc(t.sync)}"><ha-icon icon="mdi:sync"></ha-icon></ha-control-button>
          </div>
        </div>
        <div class="filters" id="filters"></div>
        <div class="total"><button class="toggle" id="empty"></button><span id="total"></span></div>
        <div class="err" id="err" hidden></div>
        <div class="list" id="list"></div>
      </ha-card>`;
    this._root = this.shadowRoot;
    const q = this._root.querySelector("#q");
    const onQuery = () => {
      const inner = q.shadowRoot && q.shadowRoot.querySelector("wa-input, input");
      const deeper = inner && inner.shadowRoot && inner.shadowRoot.querySelector("input");
      this._query = (q.value || (deeper && deeper.value) || (inner && inner.value) || "").trim().toLowerCase();
      this._paintList();
    };
    ["input", "change", "value-changed"].forEach((ev) => q.addEventListener(ev, onQuery));
    this._root.querySelector("#empty").addEventListener("click", () => {
      this._empty = !this._empty;
      this._paintFilters();
      this._paintList();
    });
    this._root.querySelector("#scan").addEventListener("click", () => this._openScan());
    this._root.querySelector("#sync").addEventListener("click", () => this._sync());
    this._root.querySelector("#list").addEventListener("click", (e) => {
      const row = e.composedPath().find((n) => n.dataset && n.dataset.i !== undefined);
      if (row) this._openDialog(this._shown[+row.dataset.i]);
    });
  }

  // Profiles from Bambu Cloud again (new names and filaments), then the list.
  async _sync() {
    const button = this._root.querySelector("#sync");
    if (button.classList.contains("busy")) return;
    button.classList.add("busy");
    let message;
    try {
      const res = await this._ws("sync");
      message = fill(this._t.synced, res);
    } catch (err) {
      message = this._t.error + (err.message || err.code);
    }
    button.classList.remove("busy");
    // Toast of Home Assistant, as its own actions report.
    this.dispatchEvent(new CustomEvent("hass-notification", { detail: { message }, bubbles: true, composed: true }));
    await this._load();
  }

  _matches(item, skip) {
    return (this._empty || item.grams > 0) && FILTERS.every((f) => f === skip || this._filter[f] === ALL || this._value(item, f) === this._filter[f]);
  }

  _value(item, field) {
    return item[field] || "—";
  }

  _paint() {
    if (!this._root) return;
    const err = this._root.querySelector("#err");
    err.hidden = !this._error;
    err.textContent = this._error || "";
    const items = this._items || [];
    const kg = items.reduce((sum, i) => sum + i.grams, 0) / 1000;
    this._root.querySelector("#sum").textContent = fill(this._t.count, { n: items.length, kg: this._num(kg, 1) });
    this._paintFilters();
    this._paintList();
  }

  // Each filter offers what is left after the other two, so no choice leads to an empty list.
  _paintFilters() {
    const t = this._t;
    const box = this._root.querySelector("#filters");
    const items = this._items || [];
    const lists = FILTERS.map((f) => {
      const values = [...new Set(items.filter((i) => this._matches(i, f)).map((i) => this._value(i, f)))].sort((a, b) => (a === "—") - (b === "—") || a.localeCompare(b));
      if (!values.includes(this._filter[f])) this._filter[f] = ALL;
      return [{ value: ALL, label: t.all }, ...values.map((v) => ({ value: v, label: v }))];
    });
    const key = JSON.stringify([lists, this._filter]);
    if (key === this._filterKey) return;
    this._filterKey = key;
    const native = !customElements.get("ha-select");
    box.replaceChildren(
      ...FILTERS.map((f, n) => {
        const apply = (e) => {
          const value = (e && e.detail && e.detail.value) ?? e.target.value;
          if (value == null || value === "" || value === this._filter[f]) return;
          this._filter[f] = value;
          this._paintFilters();
          this._paintList();
        };
        if (native) {
          const label = document.createElement("label");
          label.className = "pick";
          label.innerHTML = `<span>${esc(t[f])}</span><select>${lists[n].map((o) => `<option value="${esc(o.value)}"${o.value === this._filter[f] ? " selected" : ""}>${esc(o.label)}</option>`).join("")}</select>`;
          label.querySelector("select").addEventListener("change", apply);
          return label;
        }
        const select = document.createElement("ha-select");
        select.label = t[f];
        select.options = lists[n];
        select.value = this._filter[f];
        // ha-select only reports the choice; the value is set back here.
        select.addEventListener("value-changed", apply);
        select.addEventListener("selected", apply);
        return select;
      }),
    );
  }

  _paintList() {
    if (!this._root) return;
    const t = this._t;
    const list = this._root.querySelector("#list");
    const q = this._query;
    this._shown = (this._items || []).filter((i) => this._matches(i) && (!q || `${i.label} ${i.brand} ${i.material} ${i.color}`.toLowerCase().includes(q)));
    if (!this._items) return;
    const empty = this._items.filter((i) => i.grams <= 0).length;
    const toggle = this._root.querySelector("#empty");
    toggle.hidden = !empty;
    toggle.textContent = this._empty ? t.hide_empty : fill(t.show_empty, { n: empty });
    // Total of what the search and filters leave, under 1 kg in grams.
    const grams = this._shown.reduce((sum, i) => sum + i.grams, 0);
    this._root.querySelector("#total").textContent = fill(t.shown, {
      n: this._shown.length,
      all: this._items.length,
      grams: grams >= 1000 ? `${this._num(grams / 1000, 2)} kg` : `${this._num(grams)} g`,
    });
    if (!this._items.length) return (list.innerHTML = `<div class="muted">${esc(t.empty)}</div>`);
    if (!this._shown.length) return (list.innerHTML = `<div class="muted">${esc(t.nothing)}</div>`);
    list.innerHTML = this._shown
      .map((i, n) => {
        const sub = [i.brand, i.material].filter(Boolean).join(" · ");
        const cls = ["row", i.grams <= 0 ? "zero" : "", i.low ? "low" : ""].join(" ");
        return `<button class="${cls}" data-i="${n}">
          <span class="dot" style="${i.hex ? `background:#${esc(i.hex)}` : ""}"></span>
          <span class="name"><div class="l">${esc(i.label)}</div>${sub ? `<div class="s">${esc(sub)}</div>` : ""}</span>
          <span class="qty"><div class="g">${this._num(i.grams)} g</div></span>
        </button>`;
      })
      .join("");
  }

  // --- dialog ---------------------------------------------------------------

  // The dialog of Home Assistant (ha-dialog, like more-info and the Nokturno card), in the page,
  // not in the card. Old frontend without it: an overlay of our own with the same content.
  _openDialog(item) {
    if (!item) return;
    const sub = [item.brand, item.material, item.color].filter(Boolean).join(" · ");
    this._frame(esc(item.label), sub);
    this._open = { entry_id: item.entry_id, key: item.key };
    this._note = null;
    this._editing = null;
    this._paintDialog();
  }

  // Scan button: the scanner from panel.js in the same dialog. A known code adds a spool (with
  // Undo), an unknown one is assigned by brand, material and colour.
  _openScan() {
    const body = this._frame(esc(this._t.scan), "");
    const scanner = (this._scanner = document.createElement("filament-stock-scan"));
    scanner.hass = this._hass;
    body.appendChild(scanner);
    scanner.start();
  }

  // Opens an empty dialog and returns its body element (this._wrap).
  _frame(title, sub) {
    this._closeDialog();
    const t = this._t;
    const close = `<ha-icon-button data-close label="${esc(t.close)}" title="${esc(t.close)}"><ha-icon icon="mdi:close"></ha-icon></ha-icon-button>`;
    let dlg;
    if (customElements.get("ha-dialog")) {
      dlg = document.createElement("ha-dialog");
      dlg.setAttribute("open", "");
      // newer ha-dialog (webawesome) reads header-title, older the heading slot
      const plain = title.replace(/<[^>]*>/g, "");
      dlg.heading = plain;
      dlg.headerTitle = plain;
      dlg.setAttribute("header-title", plain);
      // HA 2026: title from header-title, subtitle slot, its own close button; older: the heading slot
      dlg.innerHTML = `<style>${DIALOG_CSS}</style>${sub ? `<span slot="headerSubtitle">${esc(sub)}</span>` : ""}
        <ha-dialog-header slot="heading">
          <span slot="navigationIcon">${close}</span>
          <span slot="title">${title}</span>${sub ? `<span slot="subtitle">${esc(sub)}</span>` : ""}
        </ha-dialog-header><div class="fs-body"></div>`;
      ["closed", "wa-after-hide"].forEach((ev) => dlg.addEventListener(ev, () => this._dlg === dlg && this._closeDialog()));
    } else {
      dlg = document.createElement("div");
      dlg.className = "filament-stock-dialog";
      dlg.innerHTML = `<style>${DIALOG_CSS}</style><div class="panel" role="dialog" aria-modal="true">
          <div class="phead"><div class="fs-title">${title}${sub ? `<small>${esc(sub)}</small>` : ""}</div>${close}</div>
          <div class="fs-body"></div></div>`;
      dlg.addEventListener("click", (e) => e.target === dlg && this._closeDialog());
      const onKey = (e) => {
        if (e.key === "Escape") {
          e.stopPropagation();
          this._closeDialog();
        }
      };
      window.addEventListener("keydown", onKey, true);
      this._offKey = () => window.removeEventListener("keydown", onKey, true);
    }
    dlg.querySelector("[data-close]").addEventListener("click", () => this._closeDialog());  // old dialogs only
    document.body.appendChild(dlg);
    this._dlg = dlg;
    return (this._wrap = dlg.querySelector(".fs-body"));
  }

  _closeDialog() {
    if (this._scan) this._scan.stop();
    this._scan = null;
    if (this._offKey) this._offKey();
    this._offKey = null;
    this._scanner = null;
    const dlg = this._dlg;
    this._dlg = this._wrap = this._open = null;
    if (!dlg) return;
    // newer ha-dialog may not close on close(): hide it, then remove it after the animation
    dlg.open = false;
    dlg.removeAttribute("open");
    setTimeout(() => dlg.remove(), 300);
  }

  _paintDialog() {
    const wrap = this._wrap;
    const item = this._open && (this._items || []).find((i) => i.entry_id === this._open.entry_id && i.key === this._open.key);
    if (!wrap || !item) return this._closeDialog();
    const t = this._t;
    const note = this._note ? `<div class="fs-note ${this._note.type}">${esc(this._note.text)}</div>` : "";
    const icon = (act, mdi, title, code) => `<ha-icon-button data-act="${act}" data-code="${esc(code)}" label="${esc(title)}" title="${esc(title)}"><ha-icon icon="${mdi}"></ha-icon></ha-icon-button>`;
    wrap.innerHTML = `
        <div class="big"><span class="fs-dot" style="${item.hex ? `background:#${esc(item.hex)}` : ""}"></span>${this._num(item.grams)} g${item.low && item.grams > 0 ? `<small>${esc(t.low)}</small>` : ""}</div>
        <div class="sec">${esc(t.grams)}</div>
        <div class="line">
          <input id="fs-grams" type="number" inputmode="decimal" min="0" step="1" value="${item.grams}">
          <ha-control-button data-act="save">${esc(t.save)}</ha-control-button>
        </div>
        <ha-control-button class="wide" data-act="spool"><ha-icon icon="mdi:plus-circle-outline"></ha-icon> ${esc(fill(t.add_spool, { g: this._num(item.spool) }))}</ha-control-button>
        <div class="sec">${esc(t.codes)}</div>
        ${item.barcodes.length ? item.barcodes.map((c) => c === this._editing
          ? `<div class="code"><input id="fs-edit" inputmode="numeric" value="${esc(c)}">${icon("rename", "mdi:check", t.save, c)}</div>`
          : `<div class="code"><span>${esc(c)}</span>${icon("edit", "mdi:pencil", t.edit, c)}${icon("unlink", "mdi:close", t.remove, c)}</div>`).join("") : `<div class="muted">${esc(t.no_codes)}</div>`}
        <video id="fs-video" playsinline muted hidden></video>
        <ha-control-button class="wide" data-act="scan"><ha-icon icon="mdi:barcode-scan"></ha-icon> <span>${esc(this._scan ? t.stop : t.scan)}</span></ha-control-button>
        <div class="line">
          <input id="fs-code" inputmode="numeric" placeholder="${esc(t.code)}">
          <ha-control-button data-act="link">${esc(t.link)}</ha-control-button>
        </div>
        ${note}`;
    wrap.querySelectorAll("[data-act]").forEach((b) => b.addEventListener("click", () => this._act(b.dataset.act, b.dataset.code, item)));
    wrap.querySelector("#fs-grams").addEventListener("keydown", (e) => e.key === "Enter" && this._act("save", null, item));
    const edit = wrap.querySelector("#fs-edit");
    if (edit) {
      edit.focus();
      edit.addEventListener("keydown", (e) => e.key === "Enter" && this._act("rename", this._editing, item));
    }
    wrap.querySelector("#fs-code").addEventListener("keydown", (e) => e.key === "Enter" && this._act("link", null, item));
  }

  async _act(act, code, item) {
    const t = this._t;
    const key = { entry_id: item.entry_id, key: item.key };
    const done = async (type, text) => {
      this._note = { type, text };
      await this._load();
    };
    try {
      if (act === "save") {
        const grams = parseFloat(String(this._wrap.querySelector("#fs-grams").value).replace(",", "."));
        if (!Number.isFinite(grams) || grams < 0) return;
        const res = await this._ws("set", { ...key, grams });
        return done("ok", fill(t.saved, { grams: this._num(res.grams) }));
      }
      if (act === "spool") {
        const res = await this._ws("spool", key);
        return done("ok", fill(t.spool_added, { g: this._num(item.spool), grams: this._num(res.grams) }));
      }
      if (act === "unlink") {
        await this._ws("barcode", { ...key, code, remove: true });
        return done(null, "");
      }
      if (act === "edit") {
        this._editing = code;
        return this._paintDialog();
      }
      if (act === "rename") {
        const value = this._wrap.querySelector("#fs-edit").value.trim();
        this._editing = null;
        if (!value || value === code) return this._paintDialog();
        await this._ws("barcode", { ...key, code: value });
        await this._ws("barcode", { ...key, code, remove: true });
        return done("ok", fill(t.linked, { code: value }));
      }
      if (act === "link") {
        const value = this._wrap.querySelector("#fs-code").value.trim();
        if (!value) return;
        await this._ws("barcode", { ...key, code: value });
        return done("ok", fill(t.linked, { code: value }));
      }
      if (act === "scan") {
        if (this._scan) {
          this._scan.stop();
          this._scan = null;
          return this._paintDialog();
        }
        const video = this._wrap.querySelector("#fs-video");
        const scan = (this._scan = startScan(this._hass, video, t));
        this._wrap.querySelector('[data-act="scan"] span').textContent = t.stop;
        let value = null;
        try {
          value = await scan.promise;
        } finally {
          if (this._scan === scan) this._scan = null;
        }
        if (!value) return this._paintDialog();
        await this._ws("barcode", { ...key, code: value });
        return done("ok", fill(t.linked, { code: value }));
      }
    } catch (err) {
      this._note = { type: "error", text: err.message && err.message.startsWith(t.error) ? err.message : (err.message || t.error + err.code) };
      this._paintDialog();
    }
  }

  disconnectedCallback() {
    this._closeDialog();
  }
}

if (!customElements.get("filament-stock-card")) customElements.define("filament-stock-card", FilamentStockCard);
window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "filament-stock-card")) {
  window.customCards.push({
    type: "filament-stock-card",
    name: "Filament Stock",
    description: "Filament list with search and filters; set grams, add a spool, link barcodes.",
  });
}
