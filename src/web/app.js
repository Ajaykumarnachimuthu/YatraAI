/**
 * YATRA AI — Client Application Logic
 * Interacts with /api/health, /api/corridors, /api/personas, and /api/recommend
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const systemStatus = document.getElementById("systemStatus");
  const statusText = document.getElementById("statusText");
  const personaChips = document.getElementById("personaChips");
  const resetDnaBtn = document.getElementById("resetDnaBtn");
  const searchForm = document.getElementById("searchForm");
  const formError = document.getElementById("formError");
  const swapCityBtn = document.getElementById("swapCityBtn");
  const originCity = document.getElementById("originCity");
  const destinationCity = document.getElementById("destinationCity");
  const departureWindow = document.getElementById("departureWindow");
  const tripPurpose = document.getElementById("tripPurpose");
  const leadDays = document.getElementById("leadDays");
  const emptyState = document.getElementById("emptyState");
  const loadingState = document.getElementById("loadingState");
  const recommendationsView = document.getElementById("recommendationsView");
  const corridorHeader = document.getElementById("corridorHeader");
  const candidateCountPill = document.getElementById("candidateCountPill");
  const recommendedHeroCard = document.getElementById("recommendedHeroCard");
  const alternativesGrid = document.getElementById("alternativesGrid");

  const dnaInputs = {
    cost_sensitivity: document.getElementById("dna_cost"),
    time_sensitivity: document.getElementById("dna_time"),
    reliability_sensitivity: document.getElementById("dna_reliability"),
    comfort_preference: document.getElementById("dna_comfort"),
    transfer_tolerance: document.getElementById("dna_transfer"),
    departure_time_flexibility: document.getElementById("dna_flexibility"),
    sustainability_preference: document.getElementById("dna_sustainability"),
  };

  const dnaValDisplays = {
    cost_sensitivity: document.getElementById("val_cost"),
    time_sensitivity: document.getElementById("val_time"),
    reliability_sensitivity: document.getElementById("val_reliability"),
    comfort_preference: document.getElementById("val_comfort"),
    transfer_tolerance: document.getElementById("val_transfer"),
    departure_time_flexibility: document.getElementById("val_flexibility"),
    sustainability_preference: document.getElementById("val_sustainability"),
  };

  let personasData = [];

  // ============================================================================
  // 1. Initial Data Fetching
  // ============================================================================

  async function initApp() {
    try {
      // 1. Health check
      const healthRes = await fetch("/api/health");
      if (healthRes.ok) {
        const health = await healthRes.json();
        statusText.textContent = `Model: ${health.model_family} (τ=${health.decision_threshold})`;
      } else {
        statusText.textContent = "Offline";
      }

      // 2. Fetch personas
      const personasRes = await fetch("/api/personas");
      if (personasRes.ok) {
        const pData = await personasRes.json();
        personasData = pData.personas || [];
        renderPersonaChips(personasData);
      }

      // 3. Fetch corridors
      const corrRes = await fetch("/api/corridors");
      if (corrRes.ok) {
        const cData = await corrRes.json();
        populateCities(cData.metro_cities || []);
      }
    } catch (err) {
      console.warn("API initialization warning:", err);
      statusText.textContent = "API Ready (Offline fallback)";
    }
  }

  function populateCities(cities) {
    if (!cities || cities.length === 0) return;
    const currentOrigin = originCity.value;
    const currentDest = destinationCity.value;

    originCity.innerHTML = "";
    destinationCity.innerHTML = "";

    cities.forEach((city) => {
      const opt1 = document.createElement("option");
      opt1.value = city;
      opt1.textContent = city;
      originCity.appendChild(opt1);

      const opt2 = document.createElement("option");
      opt2.value = city;
      opt2.textContent = city;
      destinationCity.appendChild(opt2);
    });

    if (cities.includes(currentOrigin)) originCity.value = currentOrigin;
    if (cities.includes(currentDest)) destinationCity.value = currentDest;
  }

  function renderPersonaChips(personas) {
    personaChips.innerHTML = "";

    // Add Custom DNA chip
    const customChip = document.createElement("button");
    customChip.type = "button";
    customChip.className = "chip active";
    customChip.id = "chip_custom";
    customChip.textContent = "Custom DNA";
    customChip.addEventListener("click", () => activateChip(customChip));
    personaChips.appendChild(customChip);

    personas.forEach((p, idx) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip";
      chip.textContent = p.persona_name;
      chip.addEventListener("click", () => {
        activateChip(chip);
        applyDna(p.travel_dna);
      });
      personaChips.appendChild(chip);
    });
  }

  function activateChip(chipElement) {
    document.querySelectorAll(".persona-chips .chip").forEach((c) => c.classList.remove("active"));
    chipElement.classList.add("active");
  }

  function applyDna(dnaMap) {
    Object.keys(dnaInputs).forEach((key) => {
      if (dnaMap[key] !== undefined) {
        const val = parseFloat(dnaMap[key]).toFixed(2);
        dnaInputs[key].value = val;
        dnaValDisplays[key].textContent = val;
      }
    });
  }

  function getDnaObject() {
    const dna = {};
    Object.keys(dnaInputs).forEach((key) => {
      dna[key] = parseFloat(dnaInputs[key].value);
    });
    return dna;
  }

  // Slider change listeners
  Object.keys(dnaInputs).forEach((key) => {
    dnaInputs[key].addEventListener("input", (e) => {
      const val = parseFloat(e.target.value).toFixed(2);
      dnaValDisplays[key].textContent = val;
      const customChip = document.getElementById("chip_custom");
      if (customChip) activateChip(customChip);
    });
  });

  resetDnaBtn.addEventListener("click", () => {
    const neutralDna = {
      cost_sensitivity: 0.50,
      time_sensitivity: 0.50,
      reliability_sensitivity: 0.50,
      comfort_preference: 0.50,
      transfer_tolerance: 0.50,
      departure_time_flexibility: 0.50,
      sustainability_preference: 0.50,
    };
    applyDna(neutralDna);
    const customChip = document.getElementById("chip_custom");
    if (customChip) activateChip(customChip);
  });

  // Swap city button
  swapCityBtn.addEventListener("click", () => {
    const temp = originCity.value;
    originCity.value = destinationCity.value;
    destinationCity.value = temp;
  });

  // ============================================================================
  // 2. Search & Recommendation Execution
  // ============================================================================

  searchForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    formError.textContent = "";

    const orig = originCity.value;
    const dest = destinationCity.value;

    if (orig === dest) {
      formError.textContent = "Origin and destination cannot be identical.";
      return;
    }

    const payload = {
      origin_city: orig,
      destination_city: dest,
      departure_window: departureWindow.value,
      trip_purpose: tripPurpose.value,
      party_size: 1,
      lead_days: parseInt(leadDays.value, 10),
      travel_dna: getDnaObject(),
    };

    emptyState.classList.add("hidden");
    recommendationsView.classList.add("hidden");
    loadingState.classList.remove("hidden");

    try {
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      loadingState.classList.add("hidden");

      if (!res.ok) {
        formError.textContent = data.detail || "Unable to retrieve recommendations.";
        emptyState.classList.remove("hidden");
        return;
      }

      renderRecommendations(data);
    } catch (err) {
      loadingState.classList.add("hidden");
      formError.textContent = "Connection error. Ensure the FastAPI backend is running.";
      emptyState.classList.remove("hidden");
    }
  });

  function renderRecommendations(data) {
    const { search_query, recommended_journey, itineraries, total_candidates } = data;

    corridorHeader.textContent = `${search_query.origin_city} → ${search_query.destination_city}`;
    candidateCountPill.textContent = `${total_candidates} Journey Options`;

    // 1. Render Hero Recommended Journey
    if (recommended_journey) {
      const isFlight = recommended_journey.mode === "Flight";
      const iconSvg = isFlight
        ? `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>`
        : `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="3" width="16" height="16" rx="2"/><path d="M4 11h16M12 3v8m-4 8l-2 2m12-2l2 2"/></svg>`;

      const reasonsHtml = recommended_journey.feature_reasons
        .map(
          (r) => `<span class="reason-pill"><span class="icon">✓</span> ${escapeHtml(r)}</span>`
        )
        .join("");

      recommendedHeroCard.innerHTML = `
        <div class="card-top-row">
          <div class="recommendation-badge">
            <span>★</span> RECOMMENDED FOR YOU
          </div>
          <div class="fit-score-box">
            <span class="fit-label">Personalization Match</span>
            <span class="fit-value">${Math.round(recommended_journey.ml_personalization_score * 100)}%</span>
          </div>
        </div>

        <div class="journey-main-row">
          <div class="journey-service">
            <div class="mode-icon ${isFlight ? 'flight' : 'rail'}">
              ${iconSvg}
            </div>
            <div>
              <div class="service-title">${escapeHtml(recommended_journey.carrier)} (${escapeHtml(recommended_journey.service_identifier)})</div>
              <div class="service-meta">${escapeHtml(recommended_journey.service_tier)} • ${escapeHtml(recommended_journey.departure_window)}</div>
            </div>
          </div>

          <div class="metric-box">
            <span class="metric-label">Estimated Fare</span>
            <span class="metric-val fare">₹${recommended_journey.cost_inr.toLocaleString()}</span>
          </div>

          <div class="metric-box">
            <span class="metric-label">Duration</span>
            <span class="metric-val">${recommended_journey.duration_hours.toFixed(1)} hrs</span>
          </div>

          <div class="metric-box">
            <span class="metric-label">Punctuality</span>
            <span class="metric-val">${Math.round(recommended_journey.historical_punctuality_rate * 100)}%</span>
          </div>
        </div>

        <div class="feature-reasons-list">
          ${reasonsHtml}
        </div>
      `;
    }

    // 2. Render Alternative Journeys
    const alternatives = itineraries.slice(1);
    alternativesGrid.innerHTML = "";

    if (alternatives.length === 0) {
      alternativesGrid.innerHTML = `<p class="section-desc">No other alternatives in this consideration set.</p>`;
    } else {
      alternatives.forEach((alt) => {
        const isFlight = alt.mode === "Flight";
        const iconSvg = isFlight
          ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>`
          : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="3" width="16" height="16" rx="2"/><path d="M4 11h16M12 3v8"/></svg>`;

        const card = document.createElement("div");
        card.className = "alternative-card";
        card.innerHTML = `
          <div class="journey-service">
            <span class="card-rank">#${alt.rank}</span>
            <div class="mode-icon ${isFlight ? 'flight' : 'rail'}" style="width:36px; height:36px;">
              ${iconSvg}
            </div>
            <div>
              <div class="service-title" style="font-size:0.95rem;">${escapeHtml(alt.carrier)} (${escapeHtml(alt.service_identifier)})</div>
              <div class="service-meta">${escapeHtml(alt.service_tier)} • ${escapeHtml(alt.departure_window)}</div>
            </div>
          </div>

          <div class="metric-box">
            <span class="metric-label">Fare</span>
            <span class="metric-val" style="font-size:1rem; color:var(--accent-emerald);">₹${alt.cost_inr.toLocaleString()}</span>
          </div>

          <div class="metric-box">
            <span class="metric-label">Duration</span>
            <span class="metric-val" style="font-size:1rem;">${alt.duration_hours.toFixed(1)}h</span>
          </div>

          <div class="metric-box">
            <span class="metric-label">Reliability</span>
            <span class="metric-val" style="font-size:1rem;">${Math.round(alt.historical_punctuality_rate * 100)}%</span>
          </div>

          <div class="fit-score-box" style="padding:0.25rem 0.5rem;">
            <span class="fit-value" style="font-size:0.85rem;">${Math.round(alt.ml_personalization_score * 100)}%</span>
          </div>
        `;
        alternativesGrid.appendChild(card);
      });
    }

    recommendationsView.classList.remove("hidden");
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initialize
  initApp();
});
