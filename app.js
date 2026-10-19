"use strict";
const ORDER = ["Top Stories","World","Business","Technology","Science","Sports","Health"];
let data = null, active = "All", query = "";
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s || "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeUrl = (u) => /^https?:\/\//i.test(u || "") ? u : "#";

function ago(iso) {
  if (!iso) return "";
  const m = Math.round((Date.now() - new Date(iso)) / 60000);
  if (m < 1) return "just now"; if (m < 60) return m + "m ago";
  const h = Math.round(m / 60); if (h < 24) return h + "h ago";
  return new Date(iso).toLocaleDateString(undefined, {month: "short", day: "numeric"});
}

function card(s, lead) {
  return `<article class="card${lead ? " lead" : ""}">
    <div class="meta"><span class="src">${esc(s.source)}</span><time datetime="${esc(s.published)}" title="${s.published ? esc(new Date(s.published).toLocaleString()) : ""}">${ago(s.published)}</time></div>
    <h3><a href="${esc(safeUrl(s.link))}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a></h3>
    ${s.summary ? `<p>${esc(s.summary)}</p>` : ""}
    <a class="read" href="${esc(safeUrl(s.link))}" target="_blank" rel="noopener noreferrer">Read at ${esc(s.source)} →</a></article>`;
}

function render() {
  const q = query.toLowerCase(); let total = 0, html = "";
  for (const sec of ORDER) {
    if (active !== "All" && active !== sec) continue;
    const items = (data.sections[sec] || []).filter((s) => !q || (s.title + " " + s.summary + " " + s.source).toLowerCase().includes(q));
    if (!items.length) continue; total += items.length;
    html += `<section class="section"><h2>${esc(sec)} <small>${items.length} stories</small></h2><div class="grid">${items.map((s, i) => card(s, i === 0 && !q)).join("")}</div></section>`;
  }
  $("#main").innerHTML = html || `<div class="notice">No stories match “${esc(query)}”.</div>`;
  $("#count").textContent = total + " stories";
}

function nav() {
  $("#sections").innerHTML = ["All", ...ORDER].map((s) => `<button data-s="${s}" class="${s === active ? "active" : ""}">${s}</button>`).join("");
}

$("#today").textContent = new Date().toLocaleDateString(undefined, {weekday: "long", year: "numeric", month: "long", day: "numeric"});
nav();
$("#sections").addEventListener("click", (e) => {
  const b = e.target.closest("button"); if (!b || !data) return;
  active = b.dataset.s; nav(); render(); window.scrollTo({top: 0, behavior: "smooth"});
});
$("#search").addEventListener("input", (e) => { query = e.target.value.trim(); if (data) render(); });

fetch("news.json", {cache: "no-store"})
  .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
  .then((d) => {
    data = d;
    $("#updated").textContent = "Updated " + new Date(d.generated_at).toLocaleString(undefined, {dateStyle: "medium", timeStyle: "short"});
    $("#feeds").textContent = "Sources: " + [...new Set(Object.values(d.sections).flat().map((s) => s.source))].join(" · ");
    render();
  })
  .catch(() => {
    $("#updated").textContent = "No data";
    $("#main").innerHTML = `<div class="notice"><h2>Today's news isn't loaded yet</h2><p>news.json is missing or couldn't be read. Run <code>python3 update_news.py</code>, then serve the folder with <code>python3 -m http.server</code> and reload.</p></div>`;
  });
