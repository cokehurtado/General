/* Golf Club Second-Hand Tracker — dashboard logic (zero dependencies). */
"use strict";

(async function () {
  const $ = (sel) => document.querySelector(sel);

  const SERIES_VARS = ["--series-1", "--series-2", "--series-3"];
  const seriesColor = (i) =>
    getComputedStyle(document.documentElement).getPropertyValue(SERIES_VARS[i % 3]).trim();

  let latest, historyRows;
  try {
    const [latestRes, histRes] = await Promise.all([
      fetch("data/latest.json"),
      fetch("data/history.jsonl"),
    ]);
    if (!latestRes.ok) throw new Error("no data");
    latest = await latestRes.json();
    const histText = histRes.ok ? await histRes.text() : "";
    historyRows = histText
      .split("\n")
      .filter((l) => l.trim())
      .map((l) => JSON.parse(l));
  } catch (e) {
    $("#tiles").innerHTML =
      '<div class="empty-state">No data yet. Run <code>python3 tracker.py</code> ' +
      "(or <code>python3 tracker.py --demo</code> for a preview) and reload.</div>";
    return;
  }

  const fmtMoney = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: latest.currency || "USD",
    maximumFractionDigits: 0,
  });
  const fmtMoneyCents = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: latest.currency || "USD",
  });
  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  document.getElementById("ccy").textContent = latest.currency || "USD";
  if (latest.demo) $("#demoBanner").hidden = false;
  if (latest.generatedAt) {
    $("#updatedAt").textContent =
      "Last updated " + new Date(latest.generatedAt).toLocaleString();
  }

  /* ---------------- stat tiles ---------------- */

  const RATING_LABEL = {
    great: "▼ Great deal",
    good: "Good price",
    fair: "Fair price",
    high: "▲ Above market",
  };

  $("#tiles").innerHTML = latest.clubs
    .map((club, i) => {
      const best = club.listings[0];
      if (!best) {
        return `<div class="tile">
          <div class="club"><span class="swatch" style="background:${seriesColor(i)}"></span>${esc(club.fullName)}</div>
          <div class="empty">No matching listings right now.</div>
        </div>`;
      }
      const ref = club.reference;
      const pct = best.dealPct;
      const dir = pct >= 0 ? "down" : "up";
      const arrow = pct >= 0 ? "▼" : "▲";
      return `<div class="tile">
        <div class="club"><span class="swatch" style="background:${seriesColor(i)}"></span>${esc(club.fullName)}</div>
        <div class="value">${fmtMoney.format(best.total)}</div>
        <div class="delta">
          <span class="${dir}">${arrow} ${Math.abs(pct).toFixed(0)}%</span>
          vs reference ${fmtMoney.format(ref)} · ${club.stats.count} listings
        </div>
        <a class="view" href="${esc(best.url)}" target="_blank" rel="noopener">View lowest-priced listing ↗</a>
      </div>`;
    })
    .join("");

  /* ---------------- price history chart ---------------- */

  const clubIndex = new Map(latest.clubs.map((c, i) => [c.id, i]));
  const byDate = new Map(); // date -> {clubId: row}
  for (const r of historyRows) {
    if (!clubIndex.has(r.clubId)) continue;
    if (!byDate.has(r.date)) byDate.set(r.date, {});
    byDate.get(r.date)[r.clubId] = r;
  }
  const dates = [...byDate.keys()].sort();

  $("#legend").innerHTML = latest.clubs
    .map(
      (c, i) => `<span class="item"><span class="swatch" style="background:${seriesColor(i)}"></span>${esc(c.fullName)}</span>`
    )
    .join("");

  const chartEl = $("#chart");
  let selectedClub = "all";

  function drawChart() {
    chartEl.innerHTML = "";
    if (dates.length < 2) {
      chartEl.innerHTML = '<div class="empty-state">Price history will appear after a couple of runs.</div>';
      return;
    }

    const W = 900, H = 340;
    const P = { l: 58, r: 130, t: 16, b: 34 };
    const iw = W - P.l - P.r, ih = H - P.t - P.b;

    const vals = [];
    for (const d of dates)
      for (const c of latest.clubs) {
        const r = byDate.get(d)[c.id];
        if (r && r.median != null) vals.push(r.median);
      }
    let lo = Math.min(...vals), hi = Math.max(...vals);
    const padV = (hi - lo) * 0.1 || hi * 0.05 || 10;
    lo = Math.max(0, lo - padV); hi = hi + padV;

    const x = (i) => P.l + (i / (dates.length - 1)) * iw;
    const y = (v) => P.t + ih - ((v - lo) / (hi - lo)) * ih;

    // ~5 nice y ticks
    const step = niceStep((hi - lo) / 5);
    const t0 = Math.ceil(lo / step) * step;
    const ticks = [];
    for (let v = t0; v <= hi; v += step) ticks.push(v);

    const css = getComputedStyle(document.documentElement);
    const gridC = css.getPropertyValue("--grid").trim();
    const baseC = css.getPropertyValue("--baseline").trim();
    const mutedC = css.getPropertyValue("--muted").trim();
    const inkC = css.getPropertyValue("--ink-2").trim();

    let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Median asking price per club over the last 90 days">`;
    for (const v of ticks) {
      svg += `<line x1="${P.l}" y1="${y(v)}" x2="${W - P.r}" y2="${y(v)}" stroke="${gridC}" stroke-width="1"/>`;
      svg += `<text x="${P.l - 8}" y="${y(v) + 4}" text-anchor="end" font-size="11.5" fill="${mutedC}" style="font-variant-numeric:tabular-nums">${fmtMoney.format(v)}</text>`;
    }
    svg += `<line x1="${P.l}" y1="${P.t + ih}" x2="${W - P.r}" y2="${P.t + ih}" stroke="${baseC}" stroke-width="1"/>`;

    // x labels: ~6 evenly spaced dates
    const nLab = Math.min(6, dates.length);
    for (let k = 0; k < nLab; k++) {
      const i = Math.round((k / (nLab - 1)) * (dates.length - 1));
      svg += `<text x="${x(i)}" y="${H - 10}" text-anchor="middle" font-size="11.5" fill="${mutedC}">${fmtDate(dates[i])}</text>`;
    }

    // series lines + direct end labels (colored dot + ink text)
    const endLabels = [];
    latest.clubs.forEach((c, ci) => {
      const dim = selectedClub !== "all" && selectedClub !== c.id;
      let dPath = "", last = null;
      dates.forEach((d, i) => {
        const r = byDate.get(d)[c.id];
        if (!r || r.median == null) return;
        dPath += (dPath ? "L" : "M") + x(i).toFixed(1) + " " + y(r.median).toFixed(1);
        last = { i, v: r.median };
      });
      if (!dPath) return;
      svg += `<path d="${dPath}" fill="none" stroke="${seriesColor(ci)}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" opacity="${dim ? 0.25 : 1}"/>`;
      if (last) endLabels.push({ y: y(last.v), color: seriesColor(ci), label: c.label, x: x(last.i), dim });
    });

    // nudge end labels apart if they collide
    endLabels.sort((a, b) => a.y - b.y);
    for (let i = 1; i < endLabels.length; i++)
      if (endLabels[i].y - endLabels[i - 1].y < 15) endLabels[i].y = endLabels[i - 1].y + 15;
    for (const el of endLabels) {
      svg += `<circle cx="${el.x + 8}" cy="${el.y}" r="3.5" fill="${el.color}" opacity="${el.dim ? 0.25 : 1}"/>`;
      svg += `<text x="${el.x + 15}" y="${el.y + 4}" font-size="12" font-weight="600" fill="${inkC}" opacity="${el.dim ? 0.35 : 1}">${esc(el.label)}</text>`;
    }

    svg += `<line id="crosshair" y1="${P.t}" y2="${P.t + ih}" stroke="${baseC}" stroke-width="1" visibility="hidden"/>`;
    latest.clubs.forEach((c, ci) => {
      svg += `<circle id="hoverDot-${ci}" r="4.5" fill="${seriesColor(ci)}" stroke="var(--surface)" stroke-width="2" visibility="hidden"/>`;
    });
    svg += `<rect id="hoverZone" x="${P.l}" y="${P.t}" width="${iw}" height="${ih}" fill="transparent"/>`;
    svg += "</svg>";

    chartEl.innerHTML = svg + '<div class="tooltip" id="chartTip"></div>';

    // hover layer
    const svgEl = chartEl.querySelector("svg");
    const zone = chartEl.querySelector("#hoverZone");
    const cross = chartEl.querySelector("#crosshair");
    const tip = chartEl.querySelector("#chartTip");

    function onMove(evt) {
      const pt = svgEl.createSVGPoint();
      pt.x = evt.clientX; pt.y = evt.clientY;
      const loc = pt.matrixTransform(svgEl.getScreenCTM().inverse());
      const i = Math.max(0, Math.min(dates.length - 1,
        Math.round(((loc.x - P.l) / iw) * (dates.length - 1))));
      const d = dates[i];
      cross.setAttribute("x1", x(i)); cross.setAttribute("x2", x(i));
      cross.setAttribute("visibility", "visible");

      let rows = "";
      latest.clubs.forEach((c, ci) => {
        const dot = chartEl.querySelector(`#hoverDot-${ci}`);
        const r = byDate.get(d)[c.id];
        if (r && r.median != null) {
          dot.setAttribute("cx", x(i)); dot.setAttribute("cy", y(r.median));
          dot.setAttribute("visibility", "visible");
          rows += `<div class="t-row"><span class="dot" style="background:${seriesColor(ci)}"></span>
            ${esc(c.label)} <b>${fmtMoney.format(r.median)}</b></div>
            <div class="t-row" style="padding-left:14px;font-size:11.5px">low ${fmtMoney.format(r.min)} · ${r.count} listings</div>`;
        } else dot.setAttribute("visibility", "hidden");
      });
      tip.innerHTML = `<div class="t-date">${fmtDateLong(d)}</div>` + rows;
      tip.style.display = "block";
      const rect = chartEl.getBoundingClientRect();
      const px = ((x(i) - 0) / W) * rect.width;
      const left = px + 14 + tip.offsetWidth > rect.width ? px - tip.offsetWidth - 14 : px + 14;
      tip.style.left = Math.max(0, left) + "px";
      tip.style.top = "20px";
    }
    function onLeave() {
      cross.setAttribute("visibility", "hidden");
      tip.style.display = "none";
      latest.clubs.forEach((_, ci) =>
        chartEl.querySelector(`#hoverDot-${ci}`).setAttribute("visibility", "hidden"));
    }
    zone.addEventListener("mousemove", onMove);
    zone.addEventListener("mouseleave", onLeave);
  }

  function niceStep(raw) {
    const mag = Math.pow(10, Math.floor(Math.log10(raw || 1)));
    for (const m of [1, 2, 2.5, 5, 10]) if (raw <= m * mag) return m * mag;
    return 10 * mag;
  }
  function fmtDate(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }
  function fmtDateLong(iso) {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
  }

  /* ---------------- history table view ---------------- */

  const tableWrap = $("#historyTable");
  const toggle = $("#tableToggle");
  toggle.addEventListener("click", () => {
    const showTable = toggle.getAttribute("aria-pressed") !== "true";
    toggle.setAttribute("aria-pressed", String(showTable));
    tableWrap.hidden = !showTable;
    chartEl.style.display = showTable ? "none" : "";
    if (showTable && !tableWrap.innerHTML) {
      let html = '<div class="table-scroll"><table><thead><tr><th>Date</th>' +
        latest.clubs.map((c) => `<th class="num">${esc(c.label)} median</th><th class="num">low</th>`).join("") +
        "</tr></thead><tbody>";
      for (const d of [...dates].reverse()) {
        html += `<tr><td>${fmtDate(d)}</td>` + latest.clubs.map((c) => {
          const r = byDate.get(d)[c.id];
          return r
            ? `<td class="num">${fmtMoney.format(r.median)}</td><td class="num">${fmtMoney.format(r.min)}</td>`
            : '<td class="num">–</td><td class="num">–</td>';
        }).join("") + "</tr>";
      }
      tableWrap.innerHTML = html + "</tbody></table></div>";
    }
  });

  /* ---------------- filters + listings ---------------- */

  const filtersEl = $("#filters");
  const options = [{ id: "all", label: "All clubs" }].concat(
    latest.clubs.map((c) => ({ id: c.id, label: c.fullName })));
  filtersEl.innerHTML = options
    .map((o) => `<button data-id="${o.id}" aria-pressed="${o.id === "all"}">${esc(o.label)}</button>`)
    .join("");
  filtersEl.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-id]");
    if (!btn) return;
    selectedClub = btn.dataset.id;
    filtersEl.querySelectorAll("button").forEach((b) =>
      b.setAttribute("aria-pressed", String(b === btn)));
    renderListings();
    drawChart();
  });

  function badge(l) {
    return `<span class="badge ${l.rating}">${RATING_LABEL[l.rating]}</span>`;
  }

  function renderListings() {
    const clubs = latest.clubs.filter((c) => selectedClub === "all" || c.id === selectedClub);
    $("#listings").innerHTML = clubs
      .map((club) => {
        const ci = clubIndex.get(club.id);
        if (!club.listings.length) {
          return `<div class="club-section">
            <h2><span class="swatch" style="background:${seriesColor(ci)}"></span>${esc(club.fullName)}</h2>
            <div class="empty-state">No listings matched the filters on the last run.</div></div>`;
        }
        const rows = club.listings.map((l) => `<tr>
            <td class="title-cell">
              <a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.title)}</a>
              ${l.tags.map((t) => `<span class="tag${t === "NEW" ? " new" : ""}">${esc(t)}</span>`).join("")}
              ${l.buyingOption.includes("AUCTION") ? '<span class="tag">auction</span>' : ""}
            </td>
            <td>${esc(l.condition)}</td>
            <td>${esc(l.flex)}</td>
            <td class="num">${fmtMoneyCents.format(l.price)}</td>
            <td class="num">${l.shipping ? fmtMoneyCents.format(l.shipping) : "free"}</td>
            <td class="num"><strong>${fmtMoneyCents.format(l.total)}</strong></td>
            <td>${badge(l)} <span class="tag">${l.dealPct > 0 ? "−" : "+"}${Math.abs(l.dealPct).toFixed(0)}% vs ref</span></td>
            <td>${esc(l.seller.username)}${l.seller.feedbackPct ? ` <span class="tag">${esc(l.seller.feedbackPct)}%</span>` : ""}</td>
          </tr>`).join("");
        return `<div class="club-section">
          <h2><span class="swatch" style="background:${seriesColor(ci)}"></span>${esc(club.fullName)}</h2>
          <p class="stats-line">${club.stats.count} listings ·
            low ${fmtMoney.format(club.stats.min)} ·
            median ${fmtMoney.format(club.stats.median)} ·
            reference ${fmtMoney.format(club.reference)} ·
            retail ${fmtMoney.format(club.retailPrice)}</p>
          <div class="table-scroll"><table>
            <thead><tr><th>Listing</th><th>Condition</th><th>Flex</th>
              <th class="num">Price</th><th class="num">Shipping</th><th class="num">Total</th>
              <th>Deal</th><th>Seller</th></tr></thead>
            <tbody>${rows}</tbody>
          </table></div>
        </div>`;
      })
      .join("");
  }

  drawChart();
  renderListings();
})();
