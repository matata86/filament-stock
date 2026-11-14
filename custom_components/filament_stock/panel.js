// Filament Stock scanner: scan a barcode to add a spool. The card opens it in a dialog.
// Scanner: the Home Assistant app (external bus) when it has one, else the
// browser BarcodeDetector (needs HTTPS), else the code is typed in.
// The stock card (filament-stock-card.js) imports the scanner and strings from here.

export const STRINGS = {
  en: {
    title: "Filament stock",
    hint: "Scan the barcode on the box or spool to add one spool.",
    scan: "Scan barcode",
    stop: "Stop",
    code: "Barcode",
    add: "Add",
    scan_desc: "Point the camera at the barcode on the box or spool.",
    no_camera: "No camera here (it needs the Home Assistant app or HTTPS). Type the code instead.",
    camera_error: "Camera error: ",
    misread: "Misread, hold the camera still and try again.",
    added: "{label}: +{added} g, now {grams} g",
    undo: "Undo",
    undone: "Undone, the spool is taken off. The code stays assigned (remove it on the filament).",
    unknown: "Unknown code {code}. Which filament is it?",
    brand: "Brand",
    material: "Material",
    color: "Colour",
    photo: "Photograph label",
    shoot: "Take photo",
    reading: "Reading the label…",
    read: "The label says: {brand} {material} {color}. Check the choice and assign.",
    read_none: "The label says: {brand} {material} {color}. No matching filament in stock, pick it by hand.",
    assign: "Assign and add a spool",
    none: "Unknown code {code}. No filaments yet: set the profile on an AMS slot first.",
    error: "Error: ",
  },
  cs: {
    title: "Sklad filamentů",
    hint: "Naskenujte čárový kód z krabice nebo cívky, přičte se jedna cívka.",
    scan: "Skenovat kód",
    stop: "Zastavit",
    code: "Čárový kód",
    add: "Přidat",
    scan_desc: "Namiřte kameru na čárový kód na krabici nebo cívce.",
    no_camera: "Kamera tu není dostupná (potřebuje aplikaci Home Assistant nebo HTTPS). Zadejte kód ručně.",
    camera_error: "Chyba kamery: ",
    misread: "Špatně načteno, podržte kameru v klidu a zkuste znovu.",
    added: "{label}: +{added} g, nyní {grams} g",
    undo: "Zpět",
    undone: "Vráceno, cívka odečtena. Kód zůstává přiřazený (odebrat ho jde u filamentu).",
    unknown: "Neznámý kód {code}. Který je to filament?",
    brand: "Značka",
    material: "Materiál",
    color: "Barva",
    photo: "Vyfotit štítek",
    shoot: "Vyfotit",
    reading: "Čtu štítek…",
    read: "Na štítku je: {brand} {material} {color}. Zkontrolujte výběr a přiřaďte.",
    read_none: "Na štítku je: {brand} {material} {color}. Ve skladu nic odpovídajícího není, vyberte ručně.",
    assign: "Přiřadit a přidat cívku",
    none: "Neznámý kód {code}. Zatím žádný filament: nastavte nejdřív profil na slotu AMS.",
    error: "Chyba: ",
  },
};

// EAN-8/UPC-A/EAN-13/GTIN-14: the last digit checks the rest, so a misread digit fails.
// Other codes (QR, Code 128 with letters) have no check digit here and pass.
export const plausible = (code) => {
  if (!/^\d+$/.test(code) || ![8, 12, 13, 14].includes(code.length)) return true;
  const digits = [...code].map(Number).reverse();
  return digits.reduce((sum, d, i) => sum + d * (i % 2 ? 3 : 1), 0) % 10 === 0;
};

export const fill = (text, values) => text.replace(/\{(\w+)\}/g, (_, k) => values[k]);

// Photo as base64 JPEG, longest side at most 1600 px (smaller message, enough to read a label).
const shrink = async (file) => {
  const bitmap = await createImageBitmap(file);
  const scale = Math.min(1, 1600 / Math.max(bitmap.width, bitmap.height));
  const canvas = el("canvas", { width: Math.round(bitmap.width * scale), height: Math.round(bitmap.height * scale) });
  canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.85).split(",")[1];
};

const el = (tag, props = {}, ...children) => {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
};

// Scan one barcode: the app's native scanner, else the camera in `video` (BarcodeDetector).
// Returns {promise, stop}; the promise gives the code, or null when stopped or cancelled.
// A misread (wrong check digit) never comes out: the app scanner stays open with a notice,
// the browser one waits until two frames in a row agree.
export const startScan = (hass, video, t) => {
  let stop = () => {};
  const promise = new Promise((resolve, reject) => {
    const ext = hass.auth.external;
    if (ext && ext.config && ext.config.hasBarCodeScanner) {
      let off = null;
      const done = (code) => {
        if (typeof off === "function") off();
        resolve(code);
      };
      off = ext.addCommandHandler((msg) => {
        if (msg.command === "bar_code/scan_result") {
          if (!plausible(msg.payload.rawValue)) {
            ext.fireMessage({ type: "bar_code/notify", payload: { message: t.misread } });
            return true;
          }
          ext.fireMessage({ type: "bar_code/close" });
          done(msg.payload.rawValue);
          return true;
        }
        if (msg.command === "bar_code/aborted") {
          done(null);
          return true;
        }
        return false;
      });
      stop = () => {
        ext.fireMessage({ type: "bar_code/close" });
        done(null);
      };
      ext.fireMessage({ type: "bar_code/scan", payload: { title: t.scan, description: t.scan_desc } });
      return;
    }
    if (!("BarcodeDetector" in window && navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) {
      reject(new Error(t.no_camera));
      return;
    }
    let stream = null;
    let live = true;
    const end = () => {
      live = false;
      if (stream) stream.getTracks().forEach((track) => track.stop());
      video.srcObject = null;
      video.hidden = true;
    };
    stop = () => {
      end();
      resolve(null);
    };
    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        if (!live) return end();
        video.srcObject = stream;
        video.hidden = false;
        await video.play();
        const detector = new BarcodeDetector();
        let last = null;
        while (live) {
          const code = (await detector.detect(video)).map((c) => c.rawValue).find(plausible);
          if (code && code === last && live) {
            end();
            return resolve(code);
          }
          last = code || null;
          await new Promise((wait) => setTimeout(wait, 100));
        }
      } catch (err) {
        end();
        reject(new Error(t.camera_error + err.message));
      }
    })();
  });
  return { promise, stop: () => stop() };
};

// The frontend loads ha-form, ha-card, ha-alert... lazily. Loading the config
// panel pulls them in (the usual custom-panel trick; internal API, so guarded).
const loadHaElements = async () => {
  if (customElements.get("ha-form") && customElements.get("ha-card") && customElements.get("ha-alert")) return;
  try {
    await customElements.whenDefined("partial-panel-resolver");
    const resolver = document.createElement("partial-panel-resolver");
    resolver.hass = { panels: [{ url_path: "tmp", component_name: "config" }] };
    resolver._updateRoutes();
    await resolver.routerOptions.routes.tmp.load();
    await customElements.whenDefined("ha-panel-config");
    await document.createElement("ha-panel-config").routerOptions.routes.automation.load();
  } catch (err) {
    // Without them the panel still works, with plain inputs.
  }
};

class FilamentStockPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this._building) this._building = this._build();
    if (this.shadowRoot) this.shadowRoot.querySelectorAll("ha-form").forEach((e) => (e.hass = hass));
  }

  // The card's scan button: open the scanner straight away.
  async start() {
    await this._building;
    if (!this._scan) this._toggle();
  }

  disconnectedCallback() {
    this._stop();
  }

  async _build() {
    await loadHaElements();
    const t = (this._t = STRINGS[this._hass.language] || STRINGS.en);
    const root = this.attachShadow({ mode: "open" });
    root.append(
      el("style", {
        textContent: `
        :host { display: block; color: var(--primary-text-color); font-family: var(--ha-font-family-body, sans-serif); }
        .card-content, #out { display: grid; gap: 16px; }
        .card-actions { display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap; margin-top: 16px; }
        video { width: 100%; border-radius: var(--ha-card-border-radius, 12px); background: #000; }
        input, select { font: inherit; padding: 12px; width: 100%; box-sizing: border-box; }
        [hidden] { display: none !important; }`,
      }),
    );
    this._scanButton = this._button(t.scan, () => this._toggle());
    this._video = el("video", { hidden: true, playsInline: true, muted: true });
    this._code = this._form({ name: "code", selector: { text: {} } }, t.code);
    this._out = el("div", { id: "out" });
    root.append(
      el("div", { className: "card-content" }, el("div", { textContent: t.hint }), this._video, this._code, this._out),
      el(
        "div",
        { className: "card-actions" },
        this._button(t.add, () => this._submit(this._code.data.code), false),
        this._scanButton,
      ),
    );
  }

  _button(text, onclick, filled = true) {
    const button = el("ha-button", { textContent: text, onclick });
    button.setAttribute("appearance", filled ? "filled" : "plain");
    return button;
  }

  // One field in the Home Assistant look (ha-form); plain input or select as a fallback.
  // The value is always in `.data[schema.name]`.
  _form(schema, label, data = {}) {
    if (customElements.get("ha-form")) {
      const form = el("ha-form", { hass: this._hass, schema: [schema], data, computeLabel: () => label });
      form.addEventListener("value-changed", (ev) => (form.data = ev.detail.value));
      return form;
    }
    const options = schema.selector.select && schema.selector.select.options;
    const input = options
      ? el("select", {}, ...options.map((o) => el("option", { value: o.value, textContent: o.label })))
      : el("input", { placeholder: label });
    input.value = data[schema.name] || "";
    Object.defineProperty(input, "data", {
      get: () => ({ [schema.name]: input.value }),
      set: (value) => (input.value = value[schema.name] || ""),
    });
    return input;
  }

  _alert(type, text, ...children) {
    this._out.replaceChildren(el("ha-alert", { alertType: type }, text, ...children));
  }

  async _toggle() {
    if (this._scan) return this._stop();
    const scan = (this._scan = startScan(this._hass, this._video, this._t));
    this._scanButton.textContent = this._t.stop;
    try {
      const code = await scan.promise;
      if (code) this._submit(code);
    } catch (err) {
      this._alert(err.message === this._t.no_camera ? "info" : "error", err.message);
    } finally {
      if (this._scan === scan) this._stop();
    }
  }

  _stop() {
    if (this._scan) this._scan.stop();
    this._scan = null;
    if (this._stream) this._stream.getTracks().forEach((track) => track.stop());
    this._stream = null;
    if (this._scanButton) this._scanButton.textContent = this._t.scan;
  }

  async _call(type, data) {
    try {
      return await this._hass.callWS({ type: `filament_stock/${type}`, ...data });
    } catch (err) {
      this._alert("error", this._t.error + (err.message || err.code));
      return null;
    }
  }

  async _submit(code) {
    if (!code || !code.trim()) return;
    const result = await this._call("scan", { code });
    if (!result) return;
    this._code.data = {};
    if (result.known) return this._showAdded(result);
    if (!result.items.length) return this._alert("warning", fill(this._t.none, result));
    // Brand first (empty until picked), then material, then colour; each step appears once the one
    // before is picked and only offers what fits. A step with a single option picks itself.
    const fields = ["brand", "material", "color"];
    const value = (item, field) => item[field] || (field === "color" ? item.label : "—");
    const pick = {};
    const box = el("div", { className: "card-content" });
    let chosen = null;
    let assign;
    const render = () => {
      let rest = result.items;
      const forms = [];
      for (const [i, field] of fields.entries()) {
        const values = [...new Set(rest.map((item) => value(item, field)))].sort((a, b) => (a === "—") - (b === "—") || a.localeCompare(b));
        if (!values.includes(pick[field])) pick[field] = i && values.length === 1 ? values[0] : undefined;
        const options = values.map((v) => ({ value: v, label: v }));
        const form = this._form(
          { name: field, selector: { select: { options, mode: "dropdown" } } },
          this._t[field],
          pick[field] ? { [field]: pick[field] } : {},
        );
        const changed = () => {
          if (form.data[field] && form.data[field] !== pick[field]) {
            pick[field] = form.data[field];
            fields.slice(i + 1).forEach((next) => delete pick[next]);
            render();
          }
        };
        form.addEventListener("value-changed", changed);
        form.addEventListener("change", changed);
        forms.push(form);
        if (!pick[field]) break;
        rest = rest.filter((item) => value(item, field) === pick[field]);
      }
      box.replaceChildren(...forms);
      chosen = pick.color ? rest[0] : null;
      if (assign) assign.disabled = !chosen;
    };
    assign = this._button(this._t.assign, async () => {
      if (!chosen) return;
      const added = await this._call("assign", { entry_id: chosen.entry_id, key: chosen.key, code: result.code });
      if (added) this._showAdded(added);
    });
    render();
    const note = el("div");
    const actions = el("div", { className: "card-actions" }, assign);
    if (result.ai) actions.prepend(this._photoButton(result, note, (item) => {
      fields.forEach((field) => (pick[field] = value(item, field)));
      render();
    }));
    this._out.replaceChildren(el("ha-alert", { alertType: "warning" }, fill(this._t.unknown, result)), box, note, actions);
  }

  // Unknown code: photograph the label, the AI task reads it and picks the matching item.
  // Live camera in the panel when the page may use it (HTTPS or the app); the HA app's file
  // picker ignores `capture` and opens only the gallery, so a file is just the fallback.
  _photoButton(result, note, select) {
    const t = this._t;
    const read = async (source) => {
      note.replaceChildren(el("ha-alert", { alertType: "info" }, t.reading));
      try {
        const got = await this._hass.callWS({ type: "filament_stock/recognize", image: await shrink(source), mime: "image/jpeg" });
        const item = got.key && result.items.find((i) => i.key === got.key && i.entry_id === got.entry_id);
        if (item) select(item);
        note.replaceChildren(el("ha-alert", { alertType: item ? "success" : "warning" }, fill(item ? t.read : t.read_none, got)));
      } catch (err) {
        note.replaceChildren(el("ha-alert", { alertType: "error" }, t.error + (err.message || err.code)));
      }
    };
    const input = el("input", { type: "file", accept: "image/*", hidden: true });
    input.setAttribute("capture", "environment");
    input.onchange = () => {
      const file = input.files[0];
      input.value = "";
      if (file) read(file);
    };
    const camera = async () => {
      this._stop();
      let stream;
      try {
        stream = this._stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: { ideal: 1920 }, height: { ideal: 1080 } },
        });
      } catch (err) {
        return input.click();
      }
      const video = el("video", { playsInline: true, muted: true, srcObject: stream });
      const shoot = this._button(t.shoot, async () => {
        const frame = await createImageBitmap(video);
        this._stop();
        read(frame);
      });
      const cancel = this._button(t.stop, () => {
        this._stop();
        note.replaceChildren();
      }, false);
      note.replaceChildren(el("div", { className: "card-content" }, video, el("div", { className: "card-actions" }, cancel, shoot)));
      await video.play();
    };
    const live = navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
    // The input sits next to the button, inside it its click would bubble back to the button.
    return el("span", {}, this._button(t.photo, () => (live ? camera() : input.click()), false), input);
  }

  _showAdded(result) {
    const undo = this._button(
      this._t.undo,
      async () => {
        const done = await this._call("undo", { entry_id: result.entry_id, key: result.key, code: result.code });
        if (done) this._alert("info", this._t.undone);
      },
      false,
    );
    undo.slot = "action";
    this._alert("success", fill(this._t.added, result), undo);
  }
}

if (!customElements.get("filament-stock-scan")) customElements.define("filament-stock-scan", FilamentStockPanel);
