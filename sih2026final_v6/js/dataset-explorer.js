/**
 * Dataset Explorer - powers the "View All Datasets" modal on the Dashboard page.
 * Tab 1: browsable/searchable table of all 368 real historical landslide events.
 * Tab 2: honest summary of every data source in the system - real vs mock vs
 *        not-yet-integrated - matching the same real/mock split documented in
 *        PROTOTYPE_README.md so this never overstates what's actually live.
 */

const DATA_SOURCES_REGISTRY = [
  {
    name: '30m XGBoost Susceptibility Models (4 States Operational)',
    status: 'real',
    statusLabel: 'OPERATIONAL ML (4/8 STATES)',
    detail: 'Empirical 6-factor ML models trained on real inventories for Assam, Meghalaya, Nagaland, and Sikkim with 93.4% to 95.3% ROC-AUC accuracy on 30m UTM grids.',
    file: 'models/{state}/*.pkl & js/model_data.js'
  },
  {
    name: 'NASA LHASA v2 Dynamic Nowcast Engine',
    status: 'real',
    statusLabel: 'REAL NOWCAST PIPELINE',
    detail: 'Antecedent Rainfall Index (ARI) 7-day decaying precipitation weighting coupled with 30m susceptibility classes (Level 0 Safe to Level 4 Severe). Calibrated across dry, monsoon, and cloudburst storm conditions.',
    file: 'scripts/lhasa_engine.py & js/model_data.js'
  },
  {
    name: 'Copernicus & SRTM GL1 30m Digital Elevation Models',
    status: 'real',
    statusLabel: 'REAL GIS RASTERS',
    detail: 'High-resolution terrain grids processed into slope, aspect, curvature, and Topographic Wetness Index (TWI) rasters matching UTM Zones 45N and 46N.',
    file: 'data/processed/dem/ & factors/'
  },
  {
    name: 'Historical Landslide Records (Inventory)',
    status: 'real',
    statusLabel: 'REAL DATA',
    detail: '368 verified landslide events across all 8 NER states, 2007–2016, from a cleaned public inventory dataset. Includes dates, locations, triggers, severity, and casualties.',
    file: 'js/historical-events.js'
  },
  {
    name: 'Current Risk Monitoring (Sensors & Stations)',
    status: 'mock',
    statusLabel: 'HYBRID (MOCK TELEMETRY + REAL ML)',
    detail: '67 NER locations displaying real XGBoost susceptibility metrics and LHASA nowcasts alongside illustrative piezometer and inclinometer telemetry.',
    file: 'js/data.js'
  },
  {
    name: 'Dashboard / Alerts / Forecast / Verification',
    status: 'mock',
    statusLabel: 'MOCK / ILLUSTRATIVE',
    detail: 'Built on the same simulated dataset as Current Risk Monitoring. Functional UI, not yet connected to a live pipeline.',
    file: 'js/data.js'
  },
  {
    name: 'Event Replay 3-Day Buildup',
    status: 'real',
    statusLabel: 'REAL DATA (ECMWF ERA5 ARCHIVE)',
    detail: 'Verified daily precipitation and 7-day decaying Antecedent Rainfall Index (ARI) from ECMWF ERA5 Atmospheric Reanalysis via Open-Meteo Archive API. Escalates antecedent soil pore water saturation and calibrated slope displacement leading up to each verified historical landslide event.',
    file: 'js/historical_buildup_real.js & js/map.js'
  },
  {
    name: 'NASA Global Landslide Catalog (GLC)',
    status: 'planned',
    statusLabel: 'NOT YET INTEGRATED',
    detail: 'Global rainfall-triggered landslide catalog maintained by NASA Goddard since 2007. Identified as a candidate to expand/cross-check the historical event set for NER.',
    link: 'https://catalog.data.gov/dataset/global-landslide-catalog-export'
  },
  {
    name: 'GSI Landslide Database (Bhukosh / NGDR)',
    status: 'planned',
    statusLabel: 'NOT YET INTEGRATED',
    detail: 'India-authoritative landslide inventory maintained by the Geological Survey of India (91,000+ historical landslides, 33,904 field-validated). Candidate primary source for future NER training data.',
    link: 'https://bhukosh.gsi.gov.in/Bhukosh/Public'
  },
  {
    name: 'Login / Role-Based Access',
    status: 'functional-ui',
    statusLabel: 'FUNCTIONAL UI ONLY',
    detail: 'Real client-side logic switching between Public and Authority views. Not connected to a real backend/auth system.',
    file: 'js/main.js'
  },
  {
    name: 'Report Incident Form',
    status: 'functional-ui',
    statusLabel: 'FUNCTIONAL UI ONLY',
    detail: 'Captures input and stores it in-session. Not persisted to a real database yet.',
    file: 'pages/report.html'
  }
];

function statusBadgeHtml(status, label) {
  const map = {
    'real': 'bg-success',
    'mock': '',
    'planned': 'bg-secondary',
    'functional-ui': 'bg-info text-dark'
  };
  if (status === 'mock') {
    return `<span class="badge-simulated-data">${label}</span>`;
  }
  return `<span class="badge ${map[status] || 'bg-secondary'}">${label}</span>`;
}

function renderDatasetSources() {
  const container = document.getElementById('dataset-sources-list');
  if (!container) return;
  container.innerHTML = DATA_SOURCES_REGISTRY.map(src => `
    <div class="col-md-6">
      <div class="card border-0 shadow-sm h-100 p-3 bg-white">
        <div class="d-flex justify-content-between align-items-start mb-1 gap-2">
          <div class="fw-bold text-navy" style="font-size:0.85rem;">${src.name}</div>
          ${statusBadgeHtml(src.status, src.statusLabel)}
        </div>
        <div class="small text-secondary mb-2">${src.detail}</div>
        ${src.file ? `<div class="small text-muted"><i class="bi bi-file-earmark-code me-1"></i><code>${src.file}</code></div>` : ''}
        ${src.link ? `<a href="${src.link}" target="_blank" rel="noopener" class="small"><i class="bi bi-box-arrow-up-right me-1"></i>Source page</a>` : ''}
      </div>
    </div>
  `).join('');
}

function renderDatasetEventsTable(filterText) {
  const tbody = document.getElementById('dataset-events-table-body');
  const countEl = document.getElementById('dataset-events-shown-count');
  const badgeEl = document.getElementById('events-count-badge');
  if (!tbody) return;

  const allEvents = window.HISTORICAL_LANDSLIDE_EVENTS || [];
  if (badgeEl) badgeEl.textContent = allEvents.length;

  const q = (filterText || '').trim().toLowerCase();
  const filtered = q
    ? allEvents.filter(ev =>
        (ev.state || '').toLowerCase().includes(q) ||
        (ev.location || '').toLowerCase().includes(q) ||
        (ev.category || '').toLowerCase().includes(q) ||
        (ev.trigger || '').toLowerCase().includes(q) ||
        (ev.size || '').toLowerCase().includes(q) ||
        String(ev.id).includes(q)
      )
    : allEvents;

  tbody.innerHTML = filtered.map(ev => `
    <tr>
      <td class="text-muted">${ev.id}</td>
      <td>${ev.date}</td>
      <td>${ev.state}</td>
      <td>${ev.location}</td>
      <td><span class="badge bg-secondary-subtle text-secondary border">${ev.category}</span></td>
      <td><span class="badge bg-info-subtle text-info border">${ev.trigger}</span></td>
      <td>${ev.size}</td>
      <td class="${ev.fatalities > 0 ? 'text-danger fw-bold' : 'text-muted'}">${ev.fatalities}</td>
      <td class="${ev.injuries > 0 ? 'text-warning fw-bold' : 'text-muted'}">${ev.injuries}</td>
    </tr>
  `).join('') || `<tr><td colspan="9" class="text-center text-muted py-3">No matching events.</td></tr>`;

  if (countEl) countEl.textContent = `Showing ${filtered.length} of ${allEvents.length} events`;
}

document.addEventListener('DOMContentLoaded', () => {
  renderDatasetSources();
  renderDatasetEventsTable('');

  const searchInput = document.getElementById('dataset-events-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => renderDatasetEventsTable(e.target.value));
  }
});
