import { unlock } from "../core/data.js";
import { html, useState } from "../lib.js";

// The passphrase input has no name attribute, so even if scripts fail a native
// form submit can't put the passphrase in the URL.
export function Unlock({ onUnlocked }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    const pass = e.target.elements.pp.value;
    setBusy(true);
    setError("");
    try {
      if (await unlock(pass)) onUnlocked();
      else setError("Cette phrase de passe n'ouvre pas ce contenu.");
    } catch (err) {
      setError(`Déverrouillage impossible : ${err.message}`);
    }
    setBusy(false);
  };

  return html`<main><form class="card stack" style="margin-top:12vh" onSubmit=${submit}>
    <h1 style="margin:0">Français B2</h1>
    <p class="muted">Saisissez la phrase de passe une fois sur cet appareil. Elle reste sur l'appareil ; rien n'est envoyé.</p>
    <label class="sr-only" for="pp">Phrase de passe</label>
    <input id="pp" type="password" autocomplete="current-password" required autofocus />
    ${error ? html`<p role="alert" style="color:var(--bad);margin:0">${error}</p>` : null}
    <button class="btn primary" disabled=${busy}>${busy ? "Déverrouillage…" : "Déverrouiller"}</button>
  </form></main>`;
}
