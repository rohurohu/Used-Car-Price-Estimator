/**
 * Used Car Price Estimator - Frontend Interactivity & Visualizations
 * KLH University Machine Learning Course Project
 */

document.addEventListener("DOMContentLoaded", () => {
  const metadata = window.APP_METADATA || {};
  const CURRENT_YEAR = 2026;

  // DOM Elements
  const brandSelect = document.getElementById("brand-select");
  const modelSelect = document.getElementById("model-select");
  const yearInput = document.getElementById("year-input");
  const ageCalcTag = document.getElementById("age-calc-tag");
  const kmInput = document.getElementById("km-input");
  const fuelSelect = document.getElementById("fuel-select");
  const transSelect = document.getElementById("trans-select");
  const ownerSelect = document.getElementById("owner-select");
  const engineInput = document.getElementById("engine-input");
  const powerInput = document.getElementById("power-input");
  const mileageInput = document.getElementById("mileage-input");
  const seatsInput = document.getElementById("seats-input");

  const priceForm = document.getElementById("price-form");
  const submitBtn = document.getElementById("submit-btn");
  const resetBtn = document.getElementById("reset-btn");

  const toggleSpecsBtn = document.getElementById("toggle-specs-btn");
  const specsBody = document.getElementById("specs-body");
  const specsChevron = document.getElementById("specs-chevron");

  const themeToggle = document.getElementById("theme-toggle");

  // Populate Models for Selected Brand
  function populateModels(brand) {
    if (!metadata.brand_models_map || !metadata.brand_models_map[brand]) return;
    const models = metadata.brand_models_map[brand];
    modelSelect.innerHTML = "";
    models.forEach(m => {
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      modelSelect.appendChild(opt);
    });
  }

  // Fetch specs for brand + model
  async function fetchModelSpecs(brand, model) {
    try {
      const res = await fetch(`/api/model-specs?brand=${encodeURIComponent(brand)}&model=${encodeURIComponent(model)}`);
      const data = await res.json();
      if (data.status === "success" && data.specs) {
        engineInput.value = data.specs.engine_cc;
        powerInput.value = data.specs.max_power_bhp;
        mileageInput.value = data.specs.mileage_kmpl;
        seatsInput.value = data.specs.seats;
        updateXrayHUD();
      }
    } catch (e) {
      console.error("Failed to load model specs", e);
    }
  }

  // Update Age Tag
  function updateAgeTag() {
    const y = parseInt(yearInput.value) || CURRENT_YEAR;
    const age = Math.max(0, CURRENT_YEAR - y);
    ageCalcTag.textContent = `Age: ${age} yr${age === 1 ? '' : 's'}`;
    updateXrayHUD();
  }

  // Trigger Laser Scan across Car Chassis
  function triggerLaserScan() {
    const beam = document.getElementById("xray-laser-beam");
    if (beam) {
      beam.classList.remove("scanning");
      void beam.offsetWidth; // trigger reflow
      beam.classList.add("scanning");
    }
  }

  // Update Live Translucent Car X-Ray HUD Telemetry
  function updateXrayHUD() {
    const brand = brandSelect.value;
    const model = modelSelect.value;
    const year = parseInt(yearInput.value) || CURRENT_YEAR;
    const age = Math.max(0, CURRENT_YEAR - year);
    const km = parseFloat(kmInput.value) || 0;
    const fuel = fuelSelect.value;
    const trans = transSelect.value;
    const owner = ownerSelect.value;
    const engine = parseFloat(engineInput.value) || 1200;
    const power = parseFloat(powerInput.value) || 85;
    const mileage = parseFloat(mileageInput.value) || 18;
    const seats = seatsInput.value;

    const kmYear = Math.round(km / Math.max(age, 1));
    const specificOutput = (power / (engine / 1000)).toFixed(1);

    // Update X-Ray HUD badges and cards
    const vehicleBadge = document.getElementById("xray-vehicle-badge");
    if (vehicleBadge) vehicleBadge.innerHTML = `<i class="fa-solid fa-car"></i> ${brand} ${model} (${year})`;

    const hudEngine = document.getElementById("hud-val-engine");
    if (hudEngine) hudEngine.textContent = `${Number(engine).toLocaleString()} cc • ${power} bhp`;
    const hudPowerRatio = document.getElementById("hud-val-power-ratio");
    if (hudPowerRatio) hudPowerRatio.textContent = `Specific output: ${specificOutput} bhp/L`;

    const hudTrans = document.getElementById("hud-val-trans");
    if (hudTrans) hudTrans.textContent = `${trans} Transmission`;
    const hudTransMode = document.getElementById("hud-val-trans-mode");
    if (hudTransMode) hudTransMode.textContent = trans === "Automatic" ? "+7% Resale retention premium" : "Standard manual mechanical linkage";

    const hudKm = document.getElementById("hud-val-km");
    if (hudKm) hudKm.textContent = `${Number(km).toLocaleString()} km`;
    const hudKmIntensity = document.getElementById("hud-val-km-intensity");
    if (hudKmIntensity) hudKmIntensity.textContent = `${kmYear.toLocaleString()} km/year • ${kmYear > 15000 ? 'High' : (kmYear > 8000 ? 'Moderate' : 'Low')} usage`;

    const hudFuel = document.getElementById("hud-val-fuel");
    if (hudFuel) hudFuel.textContent = `${fuel} • ${mileage} kmpl`;

    const hudOwner = document.getElementById("hud-val-owner");
    if (hudOwner) hudOwner.textContent = `${owner} • ${seats} Seater`;

    // Update Hero HUD chips
    const heroEngine = document.getElementById("hero-hud-engine");
    if (heroEngine) heroEngine.textContent = `${Number(engine).toLocaleString()} cc`;
    const heroKm = document.getElementById("hero-hud-km");
    if (heroKm) heroKm.textContent = `${Number(km).toLocaleString()} km`;
    const heroTrans = document.getElementById("hero-hud-trans");
    if (heroTrans) heroTrans.textContent = trans;
  }

  // Input Listeners to trigger live HUD sync
  brandSelect.addEventListener("change", () => {
    populateModels(brandSelect.value);
    fetchModelSpecs(brandSelect.value, modelSelect.value);
    updateXrayHUD();
  });

  modelSelect.addEventListener("change", () => {
    fetchModelSpecs(brandSelect.value, modelSelect.value);
    updateXrayHUD();
  });

  yearInput.addEventListener("input", updateAgeTag);
  kmInput.addEventListener("input", updateXrayHUD);
  fuelSelect.addEventListener("change", () => {
    updateXrayHUD();
    document.querySelector(".node-fuel")?.classList.add("node-flash");
    setTimeout(() => document.querySelector(".node-fuel")?.classList.remove("node-flash"), 800);
  });
  transSelect.addEventListener("change", () => {
    updateXrayHUD();
    document.querySelector(".node-trans")?.classList.add("node-flash");
    setTimeout(() => document.querySelector(".node-trans")?.classList.remove("node-flash"), 800);
  });
  ownerSelect.addEventListener("change", updateXrayHUD);
  engineInput.addEventListener("input", updateXrayHUD);
  powerInput.addEventListener("input", updateXrayHUD);
  mileageInput.addEventListener("input", updateXrayHUD);
  seatsInput.addEventListener("change", updateXrayHUD);

  // Toggle Advanced Specs
  let specsExpanded = true;
  toggleSpecsBtn.addEventListener("click", () => {
    specsExpanded = !specsExpanded;
    specsBody.style.display = specsExpanded ? "block" : "none";
    specsChevron.style.transform = specsExpanded ? "rotate(0deg)" : "rotate(-90deg)";
  });

  // 1-Click Preset Buttons
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const presetData = JSON.parse(btn.getAttribute("data-preset"));
      applyPreset(presetData);
    });
  });

  function applyPreset(preset) {
    brandSelect.value = preset.brand;
    populateModels(preset.brand);
    modelSelect.value = preset.model;
    yearInput.value = preset.year;
    updateAgeTag();
    kmInput.value = preset.km_driven;
    fuelSelect.value = preset.fuel_type;
    transSelect.value = preset.transmission;
    ownerSelect.value = preset.owner;
    engineInput.value = preset.engine_cc;
    powerInput.value = preset.max_power_bhp;
    mileageInput.value = preset.mileage_kmpl;
    seatsInput.value = preset.seats;

    updateXrayHUD();
    triggerLaserScan();

    // Trigger prediction
    submitPrediction();
  }

  // Predict Price via API
  async function submitPrediction() {
    triggerLaserScan();
    const payload = {
      brand: brandSelect.value,
      model: modelSelect.value,
      year: parseInt(yearInput.value),
      km_driven: parseFloat(kmInput.value),
      fuel_type: fuelSelect.value,
      transmission: transSelect.value,
      owner: ownerSelect.value,
      engine_cc: parseFloat(engineInput.value),
      max_power_bhp: parseFloat(powerInput.value),
      mileage_kmpl: parseFloat(mileageInput.value),
      seats: parseInt(seatsInput.value)
    };

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Estimating...`;

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.status === "success" && data.prediction) {
        displayPrediction(data.prediction);
      } else {
        alert("Error in prediction: " + (data.message || "Unknown error"));
      }
    } catch (err) {
      console.error(err);
      alert("Failed to connect to prediction API.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Calculate Fair Price`;
    }
  }

  function displayPrediction(pred) {
    document.getElementById("res-price-lakhs").textContent = pred.formatted_lakhs;
    document.getElementById("res-price-inr").textContent = pred.formatted_inr;
    document.getElementById("res-range-str").textContent = pred.valuation_range.range_formatted;
    document.getElementById("latency-tag").innerHTML = `<i class="fa-regular fa-clock"></i> ${pred.latency_ms} ms (REST API)`;
    document.getElementById("res-model-badge").textContent = `Engine: ${pred.model_used}`;

    // Drivers
    const insights = pred.insights || {};
    document.getElementById("res-age-driver").textContent = `${insights.car_age_years} Years`;
    document.getElementById("res-km-year-driver").textContent = `${Number(insights.annual_mileage_km).toLocaleString()} km/yr`;
    document.getElementById("res-deprec-driver").textContent = `-${insights.estimated_depreciation}`;
    document.getElementById("res-fuel-driver").textContent = insights.fuel_efficiency_rating || "Moderate";
    document.getElementById("res-tip").textContent = insights.negotiation_tip || "";
  }

  // Handle Form Submit
  priceForm.addEventListener("submit", (e) => {
    e.preventDefault();
    submitPrediction();
  });

  // Reset form
  resetBtn.addEventListener("click", () => {
    priceForm.reset();
    populateModels(brandSelect.value);
    updateAgeTag();
    fetchModelSpecs(brandSelect.value, modelSelect.value);
  });

  // Initial populate
  if (brandSelect.value) {
    populateModels(brandSelect.value);
    modelSelect.value = "Creta";
    updateAgeTag();
    updateXrayHUD();
  }

  // Initialize Evaluation Charts (Chart.js)
  initDashboardCharts();

  // Load Dataset preview
  loadDatasetPreview();

  // Setup Live API Tester
  setupApiTester();

  // Theme toggle
  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("theme-light");
    const isLight = document.body.classList.contains("theme-light");
    themeToggle.innerHTML = isLight ? `<i class="fa-solid fa-sun"></i>` : `<i class="fa-solid fa-moon"></i>`;
  });
});

// Setup Evaluation Charts
function initDashboardCharts() {
  const metadata = window.APP_METADATA || {};
  const comparison = metadata.models_comparison || {};

  const models = Object.keys(comparison);
  const r2Scores = models.map(m => comparison[m].accuracy_pct);
  const maeVals = models.map(m => comparison[m].mae);
  const rmseVals = models.map(m => comparison[m].rmse);

  // 1. Model R² Comparison Chart
  const ctxModel = document.getElementById("modelComparisonChart");
  if (ctxModel) {
    new Chart(ctxModel, {
      type: "bar",
      data: {
        labels: models,
        datasets: [{
          label: "Accuracy (R² Score %)",
          data: r2Scores,
          backgroundColor: [
            "rgba(148, 163, 184, 0.7)",
            "rgba(59, 130, 246, 0.8)",
            "rgba(16, 185, 129, 0.9)"
          ],
          borderColor: [
            "#94a3b8",
            "#3b82f6",
            "#10b981"
          ],
          borderWidth: 2,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` R² Score: ${ctx.parsed.y.toFixed(2)}%`
            }
          }
        },
        scales: {
          y: {
            min: 50,
            max: 100,
            ticks: {
              callback: (v) => v + "%",
              color: "#9ca3af"
            },
            grid: { color: "rgba(255, 255, 255, 0.05)" }
          },
          x: {
            ticks: { color: "#9ca3af" },
            grid: { display: false }
          }
        }
      }
    });
  }

  // 2. Error Metrics Chart (MAE vs RMSE)
  const ctxError = document.getElementById("errorMetricsChart");
  if (ctxError) {
    new Chart(ctxError, {
      type: "bar",
      data: {
        labels: models,
        datasets: [
          {
            label: "MAE (₹ Lakhs)",
            data: maeVals,
            backgroundColor: "rgba(59, 130, 246, 0.7)",
            borderRadius: 6
          },
          {
            label: "RMSE (₹ Lakhs)",
            data: rmseVals,
            backgroundColor: "rgba(239, 68, 68, 0.6)",
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: "#9ca3af", font: { size: 12 } }
          }
        },
        scales: {
          y: {
            ticks: {
              callback: (v) => "₹" + v + "L",
              color: "#9ca3af"
            },
            grid: { color: "rgba(255, 255, 255, 0.05)" }
          },
          x: {
            ticks: { color: "#9ca3af" },
            grid: { display: false }
          }
        }
      }
    });
  }

  // 3. Feature Importance Chart
  const ctxFeature = document.getElementById("featureImportanceChart");
  if (ctxFeature && metadata.feature_importances) {
    const topFeatures = metadata.feature_importances.slice(0, 7);
    new Chart(ctxFeature, {
      type: "bar",
      data: {
        labels: topFeatures.map(f => f.feature),
        datasets: [{
          label: "Importance Weight (%)",
          data: topFeatures.map(f => f.importance),
          backgroundColor: "rgba(139, 92, 246, 0.75)",
          borderColor: "#8b5cf6",
          borderWidth: 1.5,
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Impact: ${ctx.parsed.x}%`
            }
          }
        },
        scales: {
          x: {
            ticks: {
              callback: (v) => v + "%",
              color: "#9ca3af"
            },
            grid: { color: "rgba(255, 255, 255, 0.05)" }
          },
          y: {
            ticks: { color: "#9ca3af" },
            grid: { display: false }
          }
        }
      }
    });
  }

  // 4. Depreciation Trend Curve
  const ctxTrend = document.getElementById("depreciationTrendChart");
  if (ctxTrend) {
    const years = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12];
    const hatchCurve = years.map(y => Math.round(100 * Math.pow(1 - 0.09, y)));
    const sedanCurve = years.map(y => Math.round(100 * Math.pow(1 - 0.10, y)));
    const luxuryCurve = years.map(y => Math.round(100 * Math.pow(1 - 0.135, y)));

    new Chart(ctxTrend, {
      type: "line",
      data: {
        labels: years.map(y => y === 0 ? "New" : `${y} yr`),
        datasets: [
          {
            label: "Mass Hatchback / SUV (Maruti/Hyundai)",
            data: hatchCurve,
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.1)",
            tension: 0.35,
            fill: false
          },
          {
            label: "Mid Sedan (Honda / Toyota)",
            data: sedanCurve,
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            tension: 0.35,
            fill: false
          },
          {
            label: "Luxury (BMW / Mercedes)",
            data: luxuryCurve,
            borderColor: "#f59e0b",
            backgroundColor: "rgba(245, 158, 11, 0.1)",
            tension: 0.35,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: "#9ca3af", font: { size: 11 } }
          }
        },
        scales: {
          y: {
            ticks: {
              callback: (v) => v + "%",
              color: "#9ca3af"
            },
            grid: { color: "rgba(255, 255, 255, 0.05)" }
          },
          x: {
            ticks: { color: "#9ca3af" },
            grid: { display: false }
          }
        }
      }
    });
  }
}

// Load Dataset Preview Table
async function loadDatasetPreview() {
  const tbody = document.getElementById("dataset-tbody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/dataset-preview?limit=10");
    const data = await res.json();
    if (data.status === "success" && data.rows) {
      tbody.innerHTML = "";
      data.rows.forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>${r.brand}</strong></td>
          <td>${r.model}</td>
          <td>${r.year}</td>
          <td>${Number(r.km_driven).toLocaleString()}</td>
          <td><span class="badge badge-info">${r.fuel_type}</span></td>
          <td>${r.transmission}</td>
          <td>${r.owner}</td>
          <td>${r.engine_cc}</td>
          <td>${r.max_power_bhp}</td>
          <td>${r.mileage_kmpl}</td>
          <td><strong style="color: #60a5fa;">₹ ${r.selling_price}L</strong></td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="11" class="text-center">Failed to load preview data.</td></tr>`;
  }

  const refreshBtn = document.getElementById("refresh-dataset-btn");
  if (refreshBtn) {
    refreshBtn.onclick = loadDatasetPreview;
  }
}

// Live REST API Tester Console
function setupApiTester() {
  const sendBtn = document.getElementById("send-api-test-btn");
  const reqText = document.getElementById("api-request-json");
  const resCode = document.getElementById("api-response-json");

  if (!sendBtn || !reqText || !resCode) return;

  sendBtn.addEventListener("click", async () => {
    let payload;
    try {
      payload = JSON.parse(reqText.value);
    } catch (e) {
      alert("Invalid JSON format in request payload.");
      return;
    }

    sendBtn.disabled = true;
    resCode.textContent = "// Sending HTTP POST to /api/predict...";

    try {
      const t0 = performance.now();
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      const clientLatency = Math.round(performance.now() - t0);

      resCode.textContent = JSON.stringify({
        ...data,
        client_roundtrip_ms: clientLatency
      }, null, 2);
    } catch (err) {
      resCode.textContent = JSON.stringify({
        error: "Network error",
        details: err.message
      }, null, 2);
    } finally {
      sendBtn.disabled = false;
    }
  });
}
