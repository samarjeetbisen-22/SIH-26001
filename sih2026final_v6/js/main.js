/**
 * NER Landslide Risk Monitoring System
 * Main UI Interactivity, Dynamic Auth Header, Verification, Alerts & Priority Zoom
 */

let activeSelectedReportId = null;

document.addEventListener('DOMContentLoaded', () => {
  checkAuthorityPageGuard();
  initDynamicNavHeader();
  initRiskMapRoleView();
  initSidebarToggles();
  initLiveClock();
  initSearchFilter();
  initAuthorityModal();
  initLoginFormHandler();
  initReportFormHandler();
  initDashboardInteractivity();
  initVerificationCenter();
  initAlertControlCenter();
  initAlertHistoryPage();
  initPriorityTable();
});

/**
 * Enforces authority access protection on operational pages
 */
function checkAuthorityPageGuard() {
  const authorityPages = ['dashboard.html', 'verification.html', 'alerts.html', 'alert-history.html'];
  const path = window.location.pathname;
  const isAuthPage = authorityPages.some(page => path.includes(page));

  if (!isAuthPage) return;

  const session = window.getAuthoritySession ? window.getAuthoritySession() : null;
  const isAuth = session && session.loggedIn;

  if (!isAuth) {
    const mainContainer = document.querySelector('main') || document.querySelector('.container-fluid') || document.body;
    if (mainContainer) {
      const isPagesDir = path.includes('/pages/');
      const loginUrl = isPagesDir ? 'login.html' : 'pages/login.html';
      
      mainContainer.innerHTML = `
        <div class="container py-5 my-5 text-center">
          <div class="card border-0 shadow-lg mx-auto p-4 p-md-5" style="max-width: 540px; border-top: 5px solid var(--gov-navy) !important; border-radius: 12px; background: #ffffff;">
            <div class="mb-3">
              <i class="bi bi-shield-lock-fill text-navy" style="font-size: 3.5rem; color: var(--gov-navy);"></i>
            </div>
            <h4 class="fw-extrabold text-navy mb-2">Authority Access Required</h4>
            <p class="text-muted small mb-4">
              This operational section is restricted to authorized SDMA / NDMA Disaster Management Officers and Field Command Personnel.
            </p>
            <div class="d-grid gap-2">
              <a href="${loginUrl}" class="btn btn-navy py-2 fw-bold shadow-sm" style="background-color: var(--gov-navy); border: none; color: #fff;">
                <i class="bi bi-person-badge me-2"></i> GO TO AUTHORITY LOGIN
              </a>
              <a href="${isPagesDir ? 'risk-map.html' : 'pages/risk-map.html'}" class="btn btn-outline-secondary py-2 fw-semibold">
                <i class="bi bi-map me-1"></i> Return to Public Risk Map
              </a>
            </div>
          </div>
        </div>
      `;
    }
  }
}

/**
 * Dynamically toggles Navbar links and Auth Actions based on Authority session
 */
function initDynamicNavHeader() {
  const session = window.getAuthoritySession ? window.getAuthoritySession() : null;
  const isAuth = session && session.loggedIn;

  const authLinks = document.querySelectorAll('.auth-only-link');
  const publicOnlyLinks = document.querySelectorAll('.public-only-link');
  const actionContainer = document.getElementById('auth-nav-action-container');
  const isPagesDir = window.location.pathname.includes('/pages/');

  if (isAuth) {
    // Show authority navbar links
    authLinks.forEach(link => link.classList.remove('d-none'));
    // Hide public-only navbar links (Report Incident) when logged in as Authority
    publicOnlyLinks.forEach(link => link.classList.add('d-none'));

    if (actionContainer) {
      actionContainer.innerHTML = `
        <div class="d-flex align-items-center gap-2">
          <span class="badge bg-navy text-white fw-bold py-2 px-3 border" style="background-color: var(--gov-navy); font-size: 0.78rem;">
            Authority Access: ${session.user || 'NDMA Officer'}
          </span>
          <button class="btn btn-outline-danger btn-sm fw-bold px-3" onclick="handleAuthorityLogout()">
            Logout
          </button>
        </div>
      `;
    }
  } else {
    // Hide authority navbar links for public users
    authLinks.forEach(link => link.classList.add('d-none'));
    // Show public-only navbar links (Report Incident) for public users
    publicOnlyLinks.forEach(link => link.classList.remove('d-none'));

    if (actionContainer) {
      const loginUrl = isPagesDir ? 'login.html' : 'pages/login.html';
      actionContainer.innerHTML = `
        <a href="${loginUrl}" class="btn btn-gov-auth btn-sm fw-bold">
          Authority Login
        </a>
      `;
    }
  }
}

function handleAuthorityLogout() {
  if (window.clearAuthoritySession) {
    window.clearAuthoritySession();
  }
  const isPagesDir = window.location.pathname.includes('/pages/');
  window.location.href = isPagesDir ? 'risk-map.html' : 'pages/risk-map.html';
}
window.handleAuthorityLogout = handleAuthorityLogout;

/**
 * Toggles GIS map UI components between Public Citizen View and Authority View
 */
function initRiskMapRoleView() {
  if (!document.getElementById('map')) return;

  const session = window.getAuthoritySession ? window.getAuthoritySession() : null;
  const isAuth = session && session.loggedIn;

  const authSections = document.querySelectorAll('.authority-only-section');
  const publicSections = document.querySelectorAll('.public-only-section');
  const legendContainer = document.getElementById('map-legend-container');

  if (isAuth) {
    authSections.forEach(sec => sec.classList.remove('d-none'));
    publicSections.forEach(sec => sec.classList.add('d-none'));
    if (legendContainer) {
      legendContainer.classList.remove('d-none');
      if (window.updateMapLegend) window.updateMapLegend();
    }
  } else {
    authSections.forEach(sec => sec.classList.add('d-none'));
    publicSections.forEach(sec => sec.classList.remove('d-none'));
    if (legendContainer) {
      legendContainer.classList.add('d-none');
    }
  }

  // Bind public layer toggle checkboxes
  document.querySelectorAll('.public-layer-toggle').forEach(chk => {
    chk.addEventListener('change', (e) => {
      const layerId = e.target.getAttribute('data-layer-id');
      if (window.GIS_LAYERS_REGISTRY && window.GIS_LAYERS_REGISTRY[layerId]) {
        window.GIS_LAYERS_REGISTRY[layerId].setVisible(e.target.checked);
      }
    });
  });
}
window.initRiskMapRoleView = initRiskMapRoleView;


function initSidebarToggles() {
  const btnToggleLeft = document.getElementById('btn-toggle-left');
  const sidebarLeft = document.getElementById('sidebar-left');
  const iconLeft = document.getElementById('icon-toggle-left');

  if (btnToggleLeft && sidebarLeft) {
    btnToggleLeft.addEventListener('click', () => {
      sidebarLeft.classList.toggle('collapsed');
      if (iconLeft) {
        iconLeft.className = sidebarLeft.classList.contains('collapsed') ? 'bi bi-chevron-right' : 'bi bi-chevron-left';
      }
      setTimeout(() => { if (window.map) window.map.updateSize(); }, 300);
    });
  }

  const btnToggleRight = document.getElementById('btn-toggle-right');
  const sidebarRight = document.getElementById('sidebar-right');
  const iconRight = document.getElementById('icon-toggle-right');

  if (btnToggleRight && sidebarRight) {
    btnToggleRight.addEventListener('click', () => {
      sidebarRight.classList.toggle('collapsed');
      if (iconRight) {
        iconRight.className = sidebarRight.classList.contains('collapsed') ? 'bi bi-chevron-left' : 'bi bi-chevron-right';
      }
      setTimeout(() => { if (window.map) window.map.updateSize(); }, 300);
    });
  }
}

function initLiveClock() {
  const clockEl = document.getElementById('live-system-time');
  const syncEl = document.getElementById('last-sync-time');

  function updateTimes() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
    
    if (clockEl) clockEl.innerText = `${timeStr} IST`;
    if (syncEl) syncEl.innerText = `Last Telemetry Sync: Just Now (${timeStr})`;
  }

  updateTimes();
  setInterval(updateTimes, 30000);
}

function initSearchFilter() {
  const searchInput = document.getElementById('search-location-input');
  const dropdown = document.getElementById('search-results-dropdown');
  if (!searchInput) return;

  function getRiskBadgeClass(level) {
    switch (level) {
      case 'Severe': return 'badge-risk-severe';
      case 'High': return 'badge-risk-high';
      case 'Moderate': return 'badge-risk-moderate';
      default: return 'badge-risk-low';
    }
  }

  function selectAndHighlightLocation(loc) {
    searchInput.value = loc.name;
    if (dropdown) dropdown.classList.add('d-none');

    if (loc.hasPredefinedData !== false) {
      if (window.highlightLocationMarker) {
        window.highlightLocationMarker(loc);
      } else if (window.flyToLocation && window.selectLocation) {
        window.flyToLocation(loc.lon, loc.lat, 10);
        window.selectLocation(loc);
      }
    } else {
      if (window.flyToLocation) {
        window.flyToLocation(loc.lon, loc.lat, 9.5);
      }
      if (window.selectNoRiskLocation) {
        window.selectNoRiskLocation(loc.name, loc.state, loc.district, loc.lat, loc.lon);
      }
    }
  }

  function renderSuggestions(query) {
    if (!dropdown) return;

    if (!query) {
      dropdown.classList.add('d-none');
      dropdown.innerHTML = '';
      document.querySelectorAll('.quick-loc-item').forEach(item => {
        item.style.display = 'flex';
      });
      return;
    }

    const q = query.toLowerCase();
    const searchable = window.ALL_SEARCHABLE_LOCATIONS || [...NE_LOCATIONS_DATA, ...(window.UNLISTED_LOCATIONS_DATA || [])];
    
    const matches = searchable.filter(loc => {
      return loc.name.toLowerCase().includes(q) ||
             (loc.state && loc.state.toLowerCase().includes(q)) ||
             (loc.district && loc.district.toLowerCase().includes(q));
    });

    // Also filter quick jump list for visual alignment
    document.querySelectorAll('.quick-loc-item').forEach(item => {
      const text = item.innerText.toLowerCase();
      item.style.display = text.includes(q) ? 'flex' : 'none';
    });

    if (matches.length > 0) {
      let html = '';
      matches.forEach((loc, index) => {
        const riskLevel = loc.riskLevel || 'Low';
        const riskClass = getRiskBadgeClass(riskLevel);
        const badgeText = loc.hasPredefinedData !== false ? riskLevel : 'No Risk Data';
        const badgeColorClass = loc.hasPredefinedData !== false ? riskClass : 'bg-success text-white';

        html += `
          <div class="search-result-item ${index === 0 ? 'active' : ''}" data-loc-name="${loc.name}">
            <div>
              <div class="fw-bold text-navy">📍 ${loc.name}</div>
              <div class="small text-muted" style="font-size: 0.7rem;">${loc.district || ''}, ${loc.state || ''}</div>
            </div>
            <span class="risk-level-badge ${badgeColorClass}" style="font-size: 0.65rem; padding: 2px 6px;">${badgeText}</span>
          </div>
        `;
      });
      dropdown.innerHTML = html;
      dropdown.classList.remove('d-none');

      dropdown.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
          const name = item.getAttribute('data-loc-name');
          const loc = searchable.find(l => l.name === name);
          if (loc) {
            selectAndHighlightLocation(loc);
          }
        });
      });
    } else {
      dropdown.innerHTML = `
        <div class="search-no-results p-2 small text-muted">
          <i class="bi bi-info-circle me-1 text-primary"></i>
          Click Enter to zoom to <strong>"${query}"</strong> (No predefined risk data)
        </div>
      `;
      dropdown.classList.remove('d-none');
    }
  }

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    renderSuggestions(query);
  });

  searchInput.addEventListener('focus', (e) => {
    const query = e.target.value.trim();
    if (query) renderSuggestions(query);
  });

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const rawQuery = searchInput.value.trim();
      if (!rawQuery) return;
      const query = rawQuery.toLowerCase();

      const searchable = window.ALL_SEARCHABLE_LOCATIONS || [...NE_LOCATIONS_DATA, ...(window.UNLISTED_LOCATIONS_DATA || [])];
      const match = searchable.find(loc => loc.name.toLowerCase().includes(query) || (loc.state && loc.state.toLowerCase().includes(query)));

      if (match) {
        selectAndHighlightLocation(match);
      } else {
        // Fallback for custom search term not in list
        if (dropdown) dropdown.classList.add('d-none');
        const formattedName = rawQuery.charAt(0).toUpperCase() + rawQuery.slice(1);
        if (window.flyToLocation) window.flyToLocation(92.8, 26.2, 8.5);
        if (window.selectNoRiskLocation) {
          window.selectNoRiskLocation(formattedName, "Assam Sector", "Custom Query Zone", 26.2, 92.8);
        }
      }
    }
  });

  document.addEventListener('click', (e) => {
    if (dropdown && !searchInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.add('d-none');
    }
  });
}


function initAuthorityModal() {
  const btnLogin = document.getElementById('btn-authority-login');
  if (btnLogin) {
    btnLogin.addEventListener('click', (e) => {
      const session = window.getAuthoritySession ? window.getAuthoritySession() : null;
      const isPagesDir = window.location.pathname.includes('/pages/');
      if (session) {
        window.location.href = isPagesDir ? 'dashboard.html' : 'pages/dashboard.html';
      } else {
        window.location.href = isPagesDir ? 'login.html' : 'pages/login.html';
      }
    });
  }
}

/* ==========================================================================
   AUTOMATIC EMERGENCY RESPONSE PRIORITIZATION SYSTEM
   ========================================================================== */

/* ==========================================================================
   AUTOMATIC EMERGENCY RESPONSE PRIORITIZATION SYSTEM
   ========================================================================== */

function getExposureScore(level) {
  switch (level) {
    case 'Very High': return 100;
    case 'High': return 75;
    case 'Medium': return 50;
    case 'Low': return 25;
    default: return 50;
  }
}

function getRoadScore(importance) {
  if (!importance) return 50;
  if (importance.includes('Critical') || importance.includes('National')) return 100;
  if (importance.includes('State')) return 75;
  if (importance.includes('District')) return 50;
  return 25;
}

function getInfraScore(infra) {
  switch (infra) {
    case 'Critical': return 100;
    case 'High': return 80;
    case 'Medium': return 60;
    case 'Low': return 30;
    default: return 0;
  }
}

function getVerifiedReportsScore(count) {
  if (count >= 3) return 100;
  if (count === 2) return 60;
  if (count === 1) return 30;
  return 0;
}

function getResponseLevelObj(score) {
  if (score >= 81) return { label: 'CRITICAL RESPONSE', badgeClass: 'priority-badge-critical' };
  if (score >= 61) return { label: 'HIGH PRIORITY', badgeClass: 'priority-badge-high' };
  if (score >= 31) return { label: 'MEDIUM PRIORITY', badgeClass: 'priority-badge-medium' };
  return { label: 'LOW PRIORITY', badgeClass: 'priority-badge-low' };
}

function getPriorityBadgeClass(label) {
  if (label.includes('CRITICAL')) return 'priority-badge-critical';
  if (label.includes('HIGH')) return 'priority-badge-high';
  if (label.includes('MEDIUM')) return 'priority-badge-medium';
  return 'priority-badge-low';
}

const FALLBACK_PRIORITY_CORRIDORS = [
  {
    id: "loc-tawang",
    locationId: "loc-tawang",
    corridorName: "Tawang Road Corridor (NH-13 Sela Pass)",
    state: "Arunachal Pradesh",
    district: "Tawang District",
    lat: 27.5861,
    lon: 91.8594,
    centerCoords: [91.8594, 27.5861],
    riskScore: 88,
    exposureLevel: "High",
    roadImportance: "Critical Corridor / National Highway",
    criticalInfrastructure: "Critical",
    infraDescription: "Sela Tunnel South Portal & Defense Convoy Substation"
  },
  {
    id: "loc-aizawl",
    locationId: "loc-aizawl",
    corridorName: "Aizawl Slope Zone (Hunthar Ridge)",
    state: "Mizoram",
    district: "Aizawl District",
    lat: 23.7271,
    lon: 92.7176,
    centerCoords: [92.7176, 23.7271],
    riskScore: 82,
    exposureLevel: "High",
    roadImportance: "State Highway",
    criticalInfrastructure: "High",
    infraDescription: "Aizawl Water Supply Mains & Ridge Power Line"
  },
  {
    id: "loc-shillong",
    locationId: "loc-shillong",
    corridorName: "Shillong Hills Corridor (NH-6 Shillong-Jowai)",
    state: "Meghalaya",
    district: "East Khasi Hills",
    lat: 25.5788,
    lon: 91.8933,
    centerCoords: [91.8933, 25.5788],
    riskScore: 76,
    exposureLevel: "High",
    roadImportance: "State Highway",
    criticalInfrastructure: "High",
    infraDescription: "Umiam Hydro Reservoir Feeder & Shillong Peak Radar"
  },
  {
    id: "loc-kohima",
    locationId: "loc-kohima",
    corridorName: "Kohima Phesama Bypass Corridor (NH-2)",
    state: "Nagaland",
    district: "Kohima District",
    lat: 25.6751,
    lon: 94.1086,
    centerCoords: [94.1086, 25.6751],
    riskScore: 79,
    exposureLevel: "Medium",
    roadImportance: "State Highway",
    criticalInfrastructure: "Medium",
    infraDescription: "High-Voltage Transmission Towers & Optic Fiber Trunk"
  },
  {
    id: "loc-gangtok",
    locationId: "loc-gangtok",
    corridorName: "Gangtok - Dikchu Corridor (NH-10)",
    state: "Sikkim",
    district: "East Sikkim",
    lat: 27.3389,
    lon: 88.6065,
    centerCoords: [88.6065, 27.3389],
    riskScore: 75,
    exposureLevel: "Medium",
    roadImportance: "State Highway",
    criticalInfrastructure: "Medium",
    infraDescription: "Teesta Hydel Intake & Singtam Feeder"
  }
];

function getCardBorderClass(label) {
  if (label.includes('CRITICAL')) return 'priority-card-critical';
  if (label.includes('HIGH')) return 'priority-card-high';
  if (label.includes('MEDIUM')) return 'priority-card-medium';
  return 'priority-card-low';
}

function getCorridorsData() {
  if (window.EMERGENCY_RESPONSE_PRIORITIES && window.EMERGENCY_RESPONSE_PRIORITIES.length > 0) {
    return window.EMERGENCY_RESPONSE_PRIORITIES;
  }
  if (typeof EMERGENCY_RESPONSE_PRIORITIES !== 'undefined' && EMERGENCY_RESPONSE_PRIORITIES.length > 0) {
    return EMERGENCY_RESPONSE_PRIORITIES;
  }
  return FALLBACK_PRIORITY_CORRIDORS;
}

function calculateEmergencyPriority() {
  const container = document.getElementById('priority-list-container');
  const tableBody = document.getElementById('priority-table-body');
  if (!container && !tableBody) return;

  const corridors = getCorridorsData();
  const locations = window.NE_LOCATIONS_DATA || (typeof NE_LOCATIONS_DATA !== 'undefined' ? NE_LOCATIONS_DATA : []);
  const storedReports = window.getStoredReports ? window.getStoredReports() : [];
  const verifiedReports = storedReports.filter(r => r.status === 'VERIFIED');

  const calculatedList = corridors.map(corr => {
    const locMatch = locations.find(l => l.id === corr.id || l.id === corr.locationId || l.name.toLowerCase() === corr.state.toLowerCase() || corr.corridorName.toLowerCase().includes(l.name.toLowerCase())) || {};

    const nearbyVerifiedCount = verifiedReports.filter(r => {
      if (r.locationName && (r.locationName.includes(corr.district) || r.locationName.includes(corr.state) || r.state === corr.state)) {
        return true;
      }
      if (r.lat && r.lon && corr.lat && corr.lon) {
        const dLat = Math.abs(r.lat - corr.lat);
        const dLon = Math.abs(r.lon - corr.lon);
        return dLat < 0.6 && dLon < 0.6;
      }
      return false;
    }).length;

    const riskScore = corr.riskScore || locMatch.riskScore || 50;
    const expScore = getExposureScore(corr.exposureLevel);
    const roadScore = getRoadScore(corr.roadImportance);
    const verifiedScore = getVerifiedReportsScore(nearbyVerifiedCount);
    const infraScore = getInfraScore(corr.criticalInfrastructure);

    const riskContrib = riskScore * 0.40;
    const expContrib = expScore * 0.20;
    const roadContrib = roadScore * 0.15;
    const verifiedContrib = verifiedScore * 0.15;
    const infraContrib = infraScore * 0.10;

    const totalPriorityScore = Math.min(100, Math.max(0, Math.round(riskContrib + expContrib + roadContrib + verifiedContrib + infraContrib)));
    const responseObj = getResponseLevelObj(totalPriorityScore);

    let shortName = corr.corridorName.split(' ')[0];
    if (corr.corridorName.includes('Bomdila')) shortName = 'Bomdila';
    if (corr.corridorName.includes('Shillong')) shortName = 'Shillong';
    if (corr.corridorName.includes('Aizawl')) shortName = 'Aizawl';
    if (corr.corridorName.includes('Tawang')) shortName = 'Tawang';
    if (corr.corridorName.includes('Guwahati')) shortName = 'Guwahati';
    if (corr.corridorName.includes('Kohima')) shortName = 'Kohima';
    if (corr.corridorName.includes('Gangtok')) shortName = 'Gangtok';

    const priorityLevelText = responseObj.label.includes('CRITICAL') ? 'CRITICAL PRIORITY' :
                              responseObj.label.includes('HIGH') ? 'HIGH PRIORITY' :
                              responseObj.label.includes('MEDIUM') ? 'MEDIUM PRIORITY' : 'LOW PRIORITY';

    return {
      ...corr,
      name: shortName,
      fullLoc: locMatch,
      rainfall24h: locMatch.rainfall24h || 142.5,
      soilMoisture: locMatch.soilMoisture || 85,
      slopeAngle: locMatch.slopeAngle || 42,
      riskLevel: locMatch.riskLevel || (riskScore > 80 ? 'Severe' : 'High'),
      verifiedCount: nearbyVerifiedCount,
      expScore,
      roadScore,
      verifiedScore,
      infraScore,
      totalPriorityScore,
      responseLevel: priorityLevelText,
      badgeClass: getPriorityBadgeClass(priorityLevelText)
    };
  });

  // Sort descending by totalPriorityScore
  calculatedList.sort((a, b) => b.totalPriorityScore - a.totalPriorityScore);

  // Assign automatic ranks
  calculatedList.forEach((item, index) => {
    item.rank = `#${index + 1}`;
  });

  window.CALCULATED_PRIORITIES_LIST = calculatedList;

  if (container) {
    container.innerHTML = calculatedList.map((item, idx) => {
      const cardBorderClass = getCardBorderClass(item.responseLevel);
      return `
        <div class="priority-item-card ${cardBorderClass}" 
             data-priority-id="${item.id}"
             data-priority-idx="${idx}"
             onclick="clickPriorityItem('${item.id}', ${idx})">
          <div class="d-flex align-items-center gap-2">
            <span class="priority-rank-tag">${item.rank}</span>
            <span class="priority-item-name">${item.name}</span>
          </div>
          <span class="priority-item-badge ${item.badgeClass}">${item.responseLevel}</span>
        </div>
      `;
    }).join('');

    container.querySelectorAll('.priority-item-card').forEach(card => {
      card.addEventListener('mouseenter', (e) => {
        const id = card.getAttribute('data-priority-id');
        const idx = parseInt(card.getAttribute('data-priority-idx'));
        showPriorityHoverTooltip(id, idx, card);
      });

      card.addEventListener('mouseleave', () => {
        hidePriorityHoverTooltip();
      });
    });
  }
}


function showPriorityHoverTooltip(id, idx, targetEl) {
  const list = window.CALCULATED_PRIORITIES_LIST || [];
  const item = list.find(l => l.id === id) || list[idx];
  if (!item) return;

  let tooltipEl = document.getElementById('priority-hover-tooltip');
  if (!tooltipEl) {
    tooltipEl = document.createElement('div');
    tooltipEl.id = 'priority-hover-tooltip';
    tooltipEl.className = 'priority-hover-tooltip d-none';
    document.body.appendChild(tooltipEl);
  }

  tooltipEl.innerHTML = `
    <div class="fw-bold text-navy border-bottom pb-1 mb-2 d-flex justify-content-between align-items-center">
      <span class="small text-uppercase"><i class="bi bi-info-circle-fill text-primary me-1"></i> WHY THIS PRIORITY?</span>
      <span class="priority-item-badge ${item.badgeClass}">${item.responseLevel}</span>
    </div>

    <div class="fw-extrabold text-dark small mb-2"><i class="bi bi-geo-alt me-1 text-danger"></i>${item.rank} ${item.name} Corridor</div>

    <div class="table-responsive mb-2">
      <table class="table table-sm table-borderless small mb-0" style="font-size: 0.74rem;">
        <tbody>
          <tr>
            <td class="text-muted p-0 py-1">Landslide Risk:</td>
            <td class="fw-bold text-end p-0 py-1 text-danger">${item.riskLevel} (${item.riskScore}/100)</td>
          </tr>
          <tr>
            <td class="text-muted p-0 py-1">Rainfall 24h:</td>
            <td class="fw-bold text-end p-0 py-1 text-primary">${item.rainfall24h} mm</td>
          </tr>
          <tr>
            <td class="text-muted p-0 py-1">Soil Moisture:</td>
            <td class="fw-bold text-end p-0 py-1 text-dark">${item.soilMoisture}% (${item.exposureLevel})</td>
          </tr>
          <tr>
            <td class="text-muted p-0 py-1">Slope:</td>
            <td class="fw-bold text-end p-0 py-1 text-dark">${item.slopeAngle}°</td>
          </tr>
          <tr>
            <td class="text-muted p-0 py-1">Road Importance:</td>
            <td class="fw-bold text-end p-0 py-1 text-dark">${item.roadImportance.includes('Critical') ? 'Critical Corridor' : 'State Highway'}</td>
          </tr>
          <tr>
            <td class="text-muted p-0 py-1">Verified Reports:</td>
            <td class="fw-bold text-end p-0 py-1 text-success">${item.verifiedCount} Confirmed</td>
          </tr>
          <tr>
            <td class="text-muted p-0 py-1">Infrastructure:</td>
            <td class="fw-bold text-end p-0 py-1 text-dark">${item.criticalInfrastructure || 'Nearby'}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="d-flex justify-content-between align-items-center pt-2 border-top fw-bold" style="font-size: 0.8rem;">
      <span class="text-navy">Priority Score:</span>
      <span class="text-danger fs-6">${item.totalPriorityScore} / 100</span>
    </div>
  `;

  const rect = targetEl.getBoundingClientRect();
  const tooltipWidth = 310;

  let left = rect.right + 12;
  if (left + tooltipWidth > window.innerWidth) {
    left = rect.left - tooltipWidth - 12;
  }

  let top = rect.top - 10;
  if (top + 280 > window.innerHeight) {
    top = window.innerHeight - 290;
  }

  tooltipEl.style.left = `${Math.max(10, left)}px`;
  tooltipEl.style.top = `${Math.max(10, top)}px`;
  tooltipEl.classList.remove('d-none');
}

function hidePriorityHoverTooltip() {
  const tooltipEl = document.getElementById('priority-hover-tooltip');
  if (tooltipEl) {
    tooltipEl.classList.add('d-none');
  }
}

function clickPriorityItem(id, idx) {
  hidePriorityHoverTooltip();

  const list = window.CALCULATED_PRIORITIES_LIST || [];
  const item = list.find(l => l.id === id) || list[idx];
  if (!item) return;

  const locations = window.NE_LOCATIONS_DATA || [];
  const matchLoc = locations.find(l => l.id === item.id || l.name.toLowerCase() === item.name.toLowerCase() || l.name.toLowerCase() === item.state.toLowerCase()) || {
    id: item.id,
    name: item.corridorName,
    lat: item.lat,
    lon: item.lon,
    riskScore: item.riskScore,
    riskLevel: item.riskLevel || 'High',
    state: item.state,
    district: item.district
  };

  if (window.highlightLocationMarker) {
    window.highlightLocationMarker(matchLoc);
  } else if (window.flyToLocation) {
    window.flyToLocation(item.lon, item.lat, 10.5);
  }
}

function showPriorityExplainability(id, idx) {
  clickPriorityItem(id, idx);
}

function initPriorityTable() {
  calculateEmergencyPriority();
}

window.calculateEmergencyPriority = calculateEmergencyPriority;
window.showPriorityExplainability = showPriorityExplainability;
window.clickPriorityItem = clickPriorityItem;



/* ==========================================================================
   AUTHORITY AUTHENTICATION & LOGIN (PART 4)
   ========================================================================== */

function initLoginFormHandler() {
  const loginForm = document.getElementById('authority-login-form');
  if (!loginForm) return;

  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const u = document.getElementById('login-username').value.trim();
    const p = document.getElementById('login-password').value.trim();
    const errAlert = document.getElementById('login-error-alert');

    if (u === 'admin' && p === 'demo123') {
      if (window.setAuthoritySession) {
        window.setAuthoritySession(u);
      }
      window.location.href = 'dashboard.html';
    } else {
      if (errAlert) errAlert.classList.remove('d-none');
    }
  });
}

function handleAuthorityLogout() {
  if (window.clearAuthoritySession) {
    window.clearAuthoritySession();
  }
  const isPagesDir = window.location.pathname.includes('/pages/');
  window.location.href = isPagesDir ? 'login.html' : 'pages/login.html';
}

/* ==========================================================================
   EMERGENCY ALERT CONTROL CENTER & HISTORY (PART 6)
   ========================================================================== */

function initAlertControlCenter() {
  const selectDistrict = document.getElementById('alert-select-district');
  if (!selectDistrict) return;

  // Visual card selection sync for channel checkboxes
  document.querySelectorAll('.channel-chk').forEach(chk => {
    chk.addEventListener('change', () => {
      const card = chk.closest('.channel-card');
      if (card) {
        if (chk.checked) card.classList.add('selected');
        else card.classList.remove('selected');
      }
      if (window.refreshCapPreview) window.refreshCapPreview();
    });
  });

  updateTargetAreaMetadata();
}

function updateTargetAreaMetadata() {
  const districtSelect = document.getElementById('alert-select-district');
  if (!districtSelect) return;
  const districtKey = districtSelect.value || 'tawang';
  const metadataMap = window.MOCK_ALERT_AREAS_DATA || (typeof MOCK_ALERT_AREAS_DATA !== 'undefined' ? MOCK_ALERT_AREAS_DATA : {});
  const meta = metadataMap[districtKey] || metadataMap['tawang'] || {
    district: "Tawang District, Arunachal Pradesh",
    riskLevel: "Severe",
    nearbyVillages: "Jang, Kiting, Lhou, Lumla, Mukto",
    affectedRoads: "Sela Pass South Approach Road (NH-13)",
    estPopulation: 14850
  };

  const nameEl = document.getElementById('meta-target-name');
  const badgeEl = document.getElementById('meta-risk-badge');
  const vilEl = document.getElementById('meta-villages');
  const roadEl = document.getElementById('meta-roads');
  const popEl = document.getElementById('meta-population');

  if (nameEl) nameEl.innerText = meta.district || "Target District";
  if (badgeEl) {
    const rClass = typeof getRiskBadgeClass === 'function' ? getRiskBadgeClass(meta.riskLevel) : 'badge-risk-severe';
    badgeEl.className = `risk-level-badge ${rClass}`;
    badgeEl.innerText = `${meta.riskLevel || 'High'} Risk`;
  }
  if (vilEl) vilEl.innerText = meta.nearbyVillages || "--";
  if (roadEl) roadEl.innerText = meta.affectedRoads || "--";
  if (popEl) popEl.innerText = `${(meta.estPopulation || 15000).toLocaleString('en-IN')} Residents`;

  // Empirical ML Model Insight
  const mlEl = document.getElementById('meta-ml-insight');
  if (mlEl) {
    const stKey = meta.stateKey || (districtKey === 'gangtok' ? 'sikkim' : districtKey === 'shillong' ? 'meghalaya' : districtKey === 'kohima' ? 'nagaland' : (districtKey === 'haflong' || districtKey === 'guwahati') ? 'assam' : null);
    const allMetrics = window.LHASA_MODEL_METRICS || [];
    const m = stKey ? allMetrics.find(x => x.stateKey === stKey) : null;
    const nowcasts = window.LHASA_NOWCAST_RESULTS || {};
    const n = stKey ? nowcasts[stKey] : null;

    if (m && m.status === 'complete') {
      const extreme = n && n.scenarios ? n.scenarios.extreme : null;
      const l3l4 = extreme ? (extreme.l3 + extreme.l4).toFixed(1) : '--';
      mlEl.className = 'mt-2 pt-2 border-top small d-block';
      mlEl.innerHTML = `
        <div class="d-flex align-items-center justify-content-between mb-1">
          <span class="badge bg-success text-white" style="font-size: 0.68rem;"><i class="bi bi-cpu me-1"></i>30m XGBoost Model Active</span>
          <span class="fw-bold text-success" style="font-size: 0.72rem;">${m.testAUC.toFixed(1)}% Test AUC</span>
        </div>
        <div class="text-dark" style="font-size: 0.72rem;">Dominant Driver: <strong>${m.topFeature} (${m.topFeaturePct}%)</strong></div>
        <div class="text-danger" style="font-size: 0.72rem;">Extreme Nowcast Warning: <strong>${l3l4}% Area (L3+L4)</strong></div>
      `;
    } else {
      mlEl.className = 'mt-2 pt-2 border-top small d-block';
      mlEl.innerHTML = `
        <div class="d-flex align-items-center justify-content-between mb-1">
          <span class="badge bg-secondary text-white" style="font-size: 0.68rem;">Model In Queue</span>
          <span class="text-muted" style="font-size: 0.7rem;">Copernicus 30m Grid Scheduled</span>
        </div>
        <div class="text-muted" style="font-size: 0.7rem;">Field inventory points identified & queued for training.</div>
      `;
    }
  }
}

function selectAlertCategory(catName, cardEl) {
  document.querySelectorAll('.alert-type-card').forEach(card => card.classList.remove('selected'));
  if (cardEl) cardEl.classList.add('selected');
  const inputEl = document.getElementById('selected-alert-type');
  if (inputEl) inputEl.value = catName;
}

function generateAutoAlertTemplate() {
  const category = document.getElementById('selected-alert-type').value || 'Severe Emergency Alert';
  const districtKey = document.getElementById('alert-select-district').value || 'tawang';
  const metadataMap = window.MOCK_ALERT_AREAS_DATA || {};
  const meta = metadataMap[districtKey] || metadataMap['tawang'];

  const msgEl = document.getElementById('alert-message-text');
  if (!msgEl) return;

  const stKey = meta.stateKey || (districtKey === 'gangtok' ? 'sikkim' : districtKey === 'shillong' ? 'meghalaya' : districtKey === 'kohima' ? 'nagaland' : (districtKey === 'haflong' || districtKey === 'guwahati') ? 'assam' : null);
  const allMetrics = window.LHASA_MODEL_METRICS || [];
  const m = stKey ? allMetrics.find(x => x.stateKey === stKey) : null;

  let template = "";
  if (category === 'Evacuation Advisory') {
    template = `EMERGENCY EVACUATION DIRECTIVE: Saturated soil & severe slope instability reported in ${meta.district}. Residents in ${meta.nearbyVillages} must evacuate immediately to designated SDMA relief centers.`;
  } else if (category === 'Road Closure') {
    template = `ROAD CLOSURE BULLETIN: ${meta.affectedRoads} is closed to traffic due to active landslide debris & rockfall risk. Avoid travel along this sector until BRO clearance.`;
  } else if (category === 'High Risk Alert') {
    template = `LANDSLIDE HIGH RISK ALERT: Continuous precipitation triggering active ground displacement in ${meta.district}. Commuters on ${meta.affectedRoads} must exercise extreme caution.`;
  } else if (category === 'Warning') {
    template = `WEATHER & LANDSLIDE WARNING: Heavy rain radar forecast for ${meta.district}. Slope monitoring active in ${meta.nearbyVillages}. Keep emergency kits ready.`;
  } else {
    template = `SEVERE EMERGENCY BROADCAST: Heavy precipitation triggering critical landslide risk across ${meta.district}. All field teams in ${meta.nearbyVillages} on high alert. Immediate standby required.`;
  }

  if (m && m.status === 'complete') {
    template += ` [XGBoost ML Advisory: High ${m.topFeature} saturation detected • Model Confidence: ${m.testAUC.toFixed(1)}% Test AUC]`;
  }

  msgEl.value = template;
}

function triggerAlertConfirmationModal() {
  const districtKey = document.getElementById('alert-select-district')?.value || 'gangtok';
  const metadataMap = window.MOCK_ALERT_AREAS_DATA || (typeof MOCK_ALERT_AREAS_DATA !== 'undefined' ? MOCK_ALERT_AREAS_DATA : {});
  const meta = metadataMap[districtKey] || metadataMap['gangtok'] || { district: "Gangtok Urban Belt", riskLevel: "Severe", estPopulation: 42000 };

  const category = document.getElementById('selected-alert-type')?.value || 'Severe Emergency Alert';
  const message = (document.getElementById('alert-message-text')?.value || "").trim();

  const radiusKm = parseInt(document.getElementById('selected-geo-radius')?.value || '15', 10);
  const radiusOpt = (window.GEO_RADIUS_OPTIONS || []).find(o => o.radiusKm === radiusKm) || { basePopMultiplier: 1.0, cbsTowers: 8, loraGateways: 11 };
  const scaledPop = Math.round((meta.estPopulation || 42000) * radiusOpt.basePopMultiplier);

  const langKey = document.getElementById('selected-alert-language')?.value || 'english';
  let selectedChannels = [];
  document.querySelectorAll('.channel-chk:checked').forEach(chk => selectedChannels.push(chk.value));

  // If no channel is checked, re-check primary channels
  if (selectedChannels.length === 0) {
    document.querySelectorAll('.channel-chk').forEach(chk => {
      chk.checked = true;
      const card = chk.closest('.channel-card');
      if (card) card.classList.add('selected');
      selectedChannels.push(chk.value);
    });
  }

  if (!message) {
    alert("Please enter or auto-fill an alert broadcast message.");
    return;
  }

  const popEl = document.getElementById('confirm-pop-count');
  if (popEl) popEl.innerText = scaledPop.toLocaleString('en-IN');

  const areaEl = document.getElementById('confirm-target-area');
  if (areaEl) areaEl.innerText = meta.district;

  const typeEl = document.getElementById('confirm-alert-type');
  if (typeEl) typeEl.innerText = category;

  const chanEl = document.getElementById('confirm-channels');
  if (chanEl) chanEl.innerText = selectedChannels.join(' • ');

  const msgEl = document.getElementById('confirm-message');
  if (msgEl) msgEl.innerText = message;

  const radEl = document.getElementById('confirm-radius');
  if (radEl) radEl.innerText = `${radiusKm} km Circle (${radiusOpt.cbsTowers} CBS Towers, ${radiusOpt.loraGateways} LoRa Sirens)`;

  const langEl = document.getElementById('confirm-language');
  if (langEl) langEl.innerText = langKey.toUpperCase();

  const modalEl = document.getElementById('alertConfirmModal');
  if (modalEl && window.bootstrap) {
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
  } else if (modalEl) {
    modalEl.classList.add('show');
    modalEl.style.display = 'block';
  }
}

function executeEmergencyAlertDispatch() {
  const districtKey = document.getElementById('alert-select-district')?.value || 'gangtok';
  const metadataMap = window.MOCK_ALERT_AREAS_DATA || (typeof MOCK_ALERT_AREAS_DATA !== 'undefined' ? MOCK_ALERT_AREAS_DATA : {});
  const meta = metadataMap[districtKey] || metadataMap['gangtok'] || { district: "Gangtok Urban Belt", riskLevel: "Severe", estPopulation: 42000 };

  const category = document.getElementById('selected-alert-type')?.value || 'Severe Emergency Alert';
  const message = (document.getElementById('alert-message-text')?.value || "").trim();

  const radiusKm = parseInt(document.getElementById('selected-geo-radius')?.value || '15', 10);
  const radiusOpt = (window.GEO_RADIUS_OPTIONS || []).find(o => o.radiusKm === radiusKm) || { basePopMultiplier: 1.0, cbsTowers: 8, loraGateways: 11 };
  const scaledPop = Math.round((meta.estPopulation || 42000) * radiusOpt.basePopMultiplier);

  const langKey = document.getElementById('selected-alert-language')?.value || 'english';
  let selectedChannels = [];
  document.querySelectorAll('.channel-chk:checked').forEach(chk => selectedChannels.push(chk.value));

  if (selectedChannels.length === 0) {
    selectedChannels.push("Cell Broadcast (CBS)", "LoRaWAN Siren Mesh", "Online Multi-Lingual SMS");
  }

  const session = window.getAuthoritySession ? window.getAuthoritySession() : null;
  const officer = session ? `${session.user} (${session.role})` : "NDMA Command Duty Officer";

  const alerts = window.getStoredAlerts ? window.getStoredAlerts() : [];
  const alertId = `ALT-NER-2026-${String(alerts.length + 1).padStart(3, '0')}`;
  const now = new Date();
  const dateStr = `${now.toISOString().slice(0, 10)} ${now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })} IST`;

  const coords = {
    gangtok: { lat: 27.3389, lon: 88.6065 },
    kohima: { lat: 25.6751, lon: 94.1086 },
    shillong: { lat: 25.5788, lon: 91.8933 },
    haflong: { lat: 25.1685, lon: 93.0163 },
    tawang: { lat: 27.5860, lon: 91.8594 },
    aizawl: { lat: 23.7271, lon: 92.7176 },
    guwahati: { lat: 26.1445, lon: 91.7362 }
  }[districtKey] || { lat: 27.3389, lon: 88.6065 };

  const langNameMap = {
    english: "English",
    nepali: "नेपाली (Nepali)",
    assamese: "অসমীয়া (Assamese)",
    khasi: "Ka Ktien Khasi (Khasi)",
    nagamese: "Nagamese / English",
    hindi: "हिंदी (Hindi)"
  };

  const newAlertObj = {
    id: alertId,
    timestamp: dateStr,
    authority: officer,
    targetArea: meta.district,
    riskLevel: meta.riskLevel || 'Severe',
    alertType: category,
    channels: selectedChannels,
    geoRadiusKm: radiusKm,
    cbsTowers: radiusOpt.cbsTowers,
    loraGateways: radiusOpt.loraGateways,
    language: langKey,
    langName: langNameMap[langKey] || langKey,
    modelTriggered: false,
    recipients: scaledPop,
    status: "DISPATCHED (LIVE SIMULATION)",
    message: message || "Emergency Landslide Broadcast",
    lat: coords.lat,
    lon: coords.lon
  };

  if (window.generateCapXmlPayload) {
    newAlertObj.capXml = window.generateCapXmlPayload(newAlertObj);
  }

  if (window.saveNewAlert) {
    window.saveNewAlert(newAlertObj);
  }

  const succIdEl = document.getElementById('success-alert-id');
  if (succIdEl) succIdEl.innerText = alertId;

  const succAreaEl = document.getElementById('success-alert-area');
  if (succAreaEl) succAreaEl.innerText = `${meta.district} (${radiusKm} km Circle)`;

  const confirmModalEl = document.getElementById('alertConfirmModal');
  const successModalEl = document.getElementById('alertSuccessModal');

  function openSuccessModal() {
    if (successModalEl && window.bootstrap) {
      const succModal = bootstrap.Modal.getOrCreateInstance(successModalEl);
      succModal.show();
    } else {
      alert(`OPERATIONAL BROADCAST: Multi-Channel Alert ${alertId} dispatched successfully across ${radiusKm}km radius!`);
    }
  }

  if (confirmModalEl && window.bootstrap) {
    const bsConfirmModal = bootstrap.Modal.getInstance(confirmModalEl) || bootstrap.Modal.getOrCreateInstance(confirmModalEl);
    let transitionDone = false;
    const onHidden = () => {
      confirmModalEl.removeEventListener('hidden.bs.modal', onHidden);
      if (!transitionDone) {
        transitionDone = true;
        openSuccessModal();
      }
    };
    confirmModalEl.addEventListener('hidden.bs.modal', onHidden);
    bsConfirmModal.hide();
    setTimeout(() => {
      if (!transitionDone) {
        transitionDone = true;
        openSuccessModal();
      }
    }, 350);
  } else {
    openSuccessModal();
  }
}

function initAlertHistoryPage() {
  const tableBody = document.getElementById('alert-history-table-body');
  if (!tableBody) return;

  const alerts = window.getStoredAlerts ? window.getStoredAlerts() : [];

  // Update Dynamic Metric KPI Cards if present on page
  const totalEl = document.getElementById('kpi-total-broadcasts');
  if (totalEl) totalEl.innerText = `${alerts.length} Active Logs`;

  const aiCount = alerts.filter(a => a.modelTriggered || (a.authority && (a.authority.includes('AI Model') || a.authority.includes('SYSTEM') || a.authority.includes('Autonomous')))).length;
  const aiEl = document.getElementById('kpi-ai-model-triggered');
  if (aiEl) aiEl.innerText = `${aiCount} Autonomous`;

  const langSet = new Set();
  alerts.forEach(a => {
    const l = a.langName || a.language;
    if (l) langSet.add(l.toLowerCase());
  });
  const langEl = document.getElementById('kpi-regional-languages');
  if (langEl) langEl.innerText = `${Math.max(langSet.size, 4)} Languages`;

  if (alerts.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">No emergency alert history recorded.</td></tr>`;
    return;
  }

  tableBody.innerHTML = alerts.map(alt => {
    const riskBadgeClass = getRiskBadgeClass(alt.riskLevel);
    const radius = alt.geoRadiusKm || 15;
    const towers = alt.cbsTowers || (radius === 5 ? 2 : radius === 15 ? 8 : radius === 25 ? 18 : 46);
    const sirens = alt.loraGateways || (radius === 5 ? 3 : radius === 15 ? 11 : radius === 25 ? 24 : 60);
    const isModel = alt.modelTriggered || (alt.authority && alt.authority.includes('AI Model')) || (alt.authority && alt.authority.includes('SYSTEM'));

    const triggerBadge = isModel 
      ? `<span class="badge bg-success-subtle text-success border border-success px-2 py-1" style="font-size: 0.68rem;"><i class="bi bi-cpu-fill me-1"></i>AI Model Nowcast</span>`
      : `<span class="badge bg-primary-subtle text-primary border border-primary px-2 py-1" style="font-size: 0.68rem;"><i class="bi bi-person-badge-fill me-1"></i>Authority Dispatch</span>`;

    const langDisplay = alt.langName || (alt.language ? alt.language.toUpperCase() : 'English');

    const channelBadges = (alt.channels || []).map(ch => {
      let icon = 'bi-broadcast';
      let colorClass = 'bg-light text-navy';
      if (ch.includes('Cell Broadcast') || ch.includes('CBS')) {
        icon = 'bi-phone-fill';
        colorClass = 'bg-danger text-white';
      } else if (ch.includes('LoRa') || ch.includes('Radio')) {
        icon = 'bi-soundwave';
        colorClass = 'bg-primary text-white';
      } else if (ch.includes('SMS')) {
        icon = 'bi-chat-left-text-fill';
        colorClass = 'bg-success text-white';
      }
      return `<span class="badge ${colorClass} border me-1 mb-1" style="font-size: 0.68rem;"><i class="bi ${icon} me-1"></i>${ch.split(' ')[0]}</span>`;
    }).join('');

    return `
      <tr>
        <td>
          <div class="fw-extrabold text-navy font-monospace">${alt.id}</div>
          <div class="mt-1">${triggerBadge}</div>
        </td>
        <td class="small text-muted" style="white-space: nowrap;">
          <i class="bi bi-clock me-1 text-primary"></i>${alt.timestamp}
        </td>
        <td>
          <div class="fw-bold text-dark">${alt.targetArea}</div>
          <div class="d-flex align-items-center gap-2 mt-1">
            <span class="risk-level-badge ${riskBadgeClass}" style="font-size: 0.65rem;">${alt.riskLevel}</span>
            <span class="text-secondary small" style="font-size: 0.72rem;">${alt.alertType}</span>
          </div>
        </td>
        <td>
          <div class="fw-bold text-navy"><i class="bi bi-bullseye text-danger me-1"></i>${radius} km Radius</div>
          <div class="small text-muted" style="font-size: 0.72rem;">
            ${towers} CBS Towers • ${sirens} LoRa Sirens
          </div>
        </td>
        <td>
          <div class="mb-1">
            <span class="badge bg-secondary-subtle text-dark border px-2 py-1" style="font-size: 0.7rem;">
              <i class="bi bi-translate me-1 text-primary"></i>${langDisplay}
            </span>
          </div>
          <div class="d-flex flex-wrap">${channelBadges}</div>
        </td>
        <td class="fw-bold text-navy" style="white-space: nowrap;">
          <i class="bi bi-people-fill text-muted me-1"></i>${(alt.recipients || 42000).toLocaleString('en-IN')}
        </td>
        <td>
          <button type="button" class="btn btn-outline-navy btn-sm fw-bold py-1 px-2" style="font-size: 0.72rem;" onclick="showCapDetailModal('${alt.id}')">
            <i class="bi bi-code-square me-1 text-primary"></i>Inspect CAP XML
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function resetAlertHistoryUI() {
  if (confirm("Reset alert history archive to canonical multi-state operational baseline?")) {
    if (window.resetStoredAlerts) {
      window.resetStoredAlerts();
    }
    initAlertHistoryPage();
  }
}
window.resetAlertHistoryUI = resetAlertHistoryUI;

/* ==========================================================================
   REPORT VERIFICATION CENTER & AUDIT LOG (PART 5)
   ========================================================================== */

function initVerificationCenter() {
  const tableBody = document.getElementById('verification-table-body');
  if (!tableBody) return;

  renderVerificationTable('ALL');
  renderAuditLogTable();
}

function renderVerificationTable(filter = 'ALL') {
  const tableBody = document.getElementById('verification-table-body');
  if (!tableBody) return;

  const reports = window.getStoredReports ? window.getStoredReports() : [];
  let filtered = reports;

  if (filter !== 'ALL') {
    filtered = reports.filter(r => r.status === filter);
  }

  if (filtered.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-4 text-muted">
          <i class="bi bi-inbox fs-3 mb-1 d-block text-secondary"></i>
          No reports matching filter "${filter}".
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = filtered.map(rep => {
    const badgeClass = getReportStatusBadgeClass(rep.status);
    const riskBadgeClass = getRiskBadgeClass(rep.riskLevel || 'High');

    return `
      <tr>
        <td class="fw-bold text-navy">${rep.id}</td>
        <td>
          <img src="${rep.image}" style="width: 50px; height: 38px; object-fit: cover; border-radius: 4px;" class="border" alt="Thumbnail">
        </td>
        <td><span class="badge bg-light text-dark border"><i class="bi bi-exclamation-octagon me-1"></i>${rep.type}</span></td>
        <td>
          <div class="fw-semibold text-dark">${rep.locationName}</div>
          <div class="text-muted small" style="font-size: 0.72rem;">${rep.lat.toFixed(4)}° N, ${rep.lon.toFixed(4)}° E</div>
        </td>
        <td class="small text-muted"><i class="bi bi-clock me-1"></i>${rep.submittedAt}</td>
        <td><span class="risk-level-badge ${riskBadgeClass}">${rep.riskLevel || 'High'}</span></td>
        <td><span class="${badgeClass}">${rep.status}</span></td>
        <td>
          <button class="btn btn-navy btn-sm fw-bold px-3" style="background-color: var(--gov-navy); border: none; font-size: 0.78rem;" onclick="selectReportForVerification('${rep.id}')">
            <i class="bi bi-pencil-square me-1"></i> Review
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function selectReportForVerification(reportId) {
  const reports = window.getStoredReports ? window.getStoredReports() : [];
  const rep = reports.find(r => r.id === reportId);
  if (!rep) return;

  activeSelectedReportId = reportId;

  document.getElementById('modal-report-id').innerText = rep.id;
  document.getElementById('modal-report-location').innerText = `${rep.locationName} (${rep.lat.toFixed(4)}° N, ${rep.lon.toFixed(4)}° E)`;
  document.getElementById('modal-report-img').src = rep.image;
  document.getElementById('modal-report-author').innerText = rep.reporterName;
  document.getElementById('modal-report-contact').innerText = rep.reporterContact;
  document.getElementById('modal-report-time').innerText = rep.submittedAt;
  document.getElementById('modal-report-type').innerText = `⚠️ ${rep.type}`;
  document.getElementById('modal-report-desc').innerText = rep.description;
  
  const remarksInput = document.getElementById('authority-remarks-input');
  if (remarksInput) remarksInput.value = rep.authorityRemarks || '';

  const badgeEl = document.getElementById('modal-report-status-badge');
  if (badgeEl) {
    badgeEl.className = getReportStatusBadgeClass(rep.status);
    badgeEl.innerText = rep.status;
  }

  const modalEl = document.getElementById('verifyActionModal');
  if (modalEl && window.bootstrap) {
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}

function executeAuthorityAction(action) {
  if (!activeSelectedReportId) return;

  const remarksInput = document.getElementById('authority-remarks-input');
  const remarks = remarksInput ? remarksInput.value.trim() : '';

  if (window.updateReportStatus) {
    window.updateReportStatus(activeSelectedReportId, action, remarks);
  }

  // Recalculate priority automatically when report verification status changes
  if (window.calculateEmergencyPriority) {
    window.calculateEmergencyPriority();
  }

  const modalEl = document.getElementById('verifyActionModal');
  if (modalEl && window.bootstrap) {
    const bsModal = bootstrap.Modal.getInstance(modalEl);
    if (bsModal) bsModal.hide();
  }

  alert(`Report ${activeSelectedReportId} status updated to: ${action}`);

  renderVerificationTable('ALL');
  renderAuditLogTable();
}


function renderAuditLogTable() {
  const tableBody = document.getElementById('audit-log-table-body');
  if (!tableBody) return;

  const logs = window.getAuditLogs ? window.getAuditLogs() : [];

  if (logs.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-3">No audit log entries recorded.</td></tr>`;
    return;
  }

  tableBody.innerHTML = logs.map(log => `
    <tr>
      <td class="fw-bold text-navy">${log.id}</td>
      <td class="small fw-semibold text-dark"><i class="bi bi-person-badge me-1 text-primary"></i>${log.authority}</td>
      <td><span class="badge bg-dark text-white font-monospace small">${log.action}</span></td>
      <td class="fw-bold text-dark">${log.reportId}</td>
      <td class="small text-muted"><i class="bi bi-clock me-1"></i>${log.timestamp}</td>
      <td class="small text-secondary">${log.remarks}</td>
    </tr>
  `).join('');
}

function filterVerificationTable(filter) {
  document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
  
  if (filter === 'ALL') document.getElementById('filter-all').classList.add('active');
  if (filter === 'PENDING VERIFICATION') document.getElementById('filter-pending').classList.add('active');
  if (filter === 'VERIFIED') document.getElementById('filter-verified').classList.add('active');

  renderVerificationTable(filter);
}

function getReportStatusBadgeClass(status) {
  switch (status) {
    case 'VERIFIED': return 'badge-status-verified';
    case 'REJECTED': case 'DISMISSED': return 'badge-status-rejected';
    case 'NEEDS FIELD INSPECTION': return 'badge-status-inspection';
    default: return 'badge-pending-report';
  }
}

function getRiskBadgeClass(level) {
  switch (level) {
    case 'Severe': return 'badge-risk-severe';
    case 'High': return 'badge-risk-high';
    case 'Moderate': return 'badge-risk-moderate';
    default: return 'badge-risk-low';
  }
}

/* ==========================================================================
   OPERATIONS DASHBOARD & REPORT VERIFICATION (PART 4)
   ========================================================================== */

function initDashboardInteractivity() {
  const container = document.getElementById('pending-reports-dashboard-list');
  const tableBody = document.getElementById('verified-incidents-table-body');
  const mlTable = document.getElementById('ml-models-table-body');
  if (!container && !tableBody && !mlTable) return;

  renderDashboardPendingReports();
  renderDashboardVerifiedTable();
  renderDashboardMLModelsTable();
}

function renderDashboardMLModelsTable() {
  const tbody = document.getElementById('ml-models-table-body');
  if (!tbody || !window.LHASA_MODEL_METRICS) return;

  const metrics = window.LHASA_MODEL_METRICS;
  const nowcasts = window.LHASA_NOWCAST_RESULTS || {};

  tbody.innerHTML = metrics.map(m => {
    if (m.status === 'complete') {
      const nowcast = nowcasts[m.stateKey];
      const extreme = nowcast && nowcast.scenarios ? nowcast.scenarios.extreme : null;
      const combinedL3L4 = extreme ? (extreme.l3 + extreme.l4).toFixed(1) : '--';
      const ariVal = extreme ? Math.round(extreme.ari) : '--';

      return `
        <tr class="table-success-subtle">
          <td class="fw-bold text-navy">
            <i class="bi bi-geo-alt-fill text-success me-1"></i>${m.state}
          </td>
          <td>
            <span class="badge bg-success text-white"><i class="bi bi-check-circle-fill me-1"></i>Operational</span>
          </td>
          <td>${m.events} events <span class="text-muted small">(${m.eventType})</span></td>
          <td>${m.gridSize} <span class="text-muted small">(${m.crs})</span></td>
          <td class="fw-bold text-primary">${m.cvAUC.toFixed(2)}%</td>
          <td class="fw-bold text-success">${m.testAUC.toFixed(2)}%</td>
          <td>${m.accuracy.toFixed(2)}%</td>
          <td>
            <span class="badge bg-info-subtle text-info border border-info">
              ${m.topFeature} (${m.topFeaturePct}%)
            </span>
          </td>
          <td class="fw-bold text-danger">
            ${combinedL3L4}% <span class="small text-muted">(ARI ${ariVal}mm)</span>
          </td>
          <td>
            <button class="btn btn-outline-navy btn-sm py-0 px-2 fw-semibold" onclick="showModelFeatureModal('${m.stateKey}')">
              <i class="bi bi-sliders me-1"></i>Drivers
            </button>
          </td>
        </tr>
      `;
    } else {
      const plannedDetails = {
        manipur: "NH-37 / NH-102 Corridor (Copernicus 30m pending)",
        arunachal: "Tawang & Siang Valley (Copernicus 30m pending)",
        mizoram: "Aizawl Ridge Slips & NH-306 (Copernicus 30m pending)",
        tripura: "Low Relief Terrain (Copernicus 30m pending)"
      };
      return `
        <tr class="text-muted">
          <td class="fw-bold text-secondary">
            <i class="bi bi-geo-alt me-1"></i>${m.state}
          </td>
          <td>
            <span class="badge bg-secondary text-white">In Queue</span>
          </td>
          <td>${plannedDetails[m.stateKey] || 'Pending inventory mosaic'}</td>
          <td>Pending raster mosaic</td>
          <td>--</td>
          <td>--</td>
          <td>--</td>
          <td>--</td>
          <td>--</td>
          <td>
            <span class="badge bg-light text-muted border small">Queued</span>
          </td>
        </tr>
      `;
    }
  }).join('');
}

function showModelFeatureModal(stateKey) {
  if (!window.LHASA_MODEL_METRICS) return;
  const m = window.LHASA_MODEL_METRICS.find(x => x.stateKey === stateKey);
  if (!m) return;

  const nowcasts = window.LHASA_NOWCAST_RESULTS || {};
  const stateNowcast = nowcasts[stateKey] || {};

  // Title & model file
  const titleEl = document.getElementById('mfm-state-title');
  const fileEl = document.getElementById('mfm-model-file');
  if (titleEl) titleEl.innerText = `${m.state} — 30m XGBoost Empirical Model Architecture`;
  if (fileEl) fileEl.innerText = `${m.modelFile} • CRS: ${m.crs} • Grid: ${m.gridSize}`;

  // Key metrics
  const testAucEl = document.getElementById('mfm-test-auc');
  const cvAucEl = document.getElementById('mfm-cv-auc');
  const accEl = document.getElementById('mfm-accuracy');
  const eventsEl = document.getElementById('mfm-events');
  const eventTypeEl = document.getElementById('mfm-event-type');

  if (testAucEl) testAucEl.innerText = `${m.testAUC.toFixed(2)}%`;
  if (cvAucEl) cvAucEl.innerText = `${m.cvAUC.toFixed(2)}%`;
  if (accEl) accEl.innerText = `${m.accuracy.toFixed(2)}%`;
  if (eventsEl) eventsEl.innerText = m.events;
  if (eventTypeEl) eventTypeEl.innerText = m.eventType;

  // Features bar breakdown
  const featuresContainer = document.getElementById('mfm-features-bars');
  if (featuresContainer && m.featureImportance) {
    const factorNames = {
      lithology: { label: "Lithology / Bedrock Unit", icon: "bi-layers-fill", color: "#2563eb" },
      elevation: { label: "Digital Elevation (30m)", icon: "bi-triangle-fill", color: "#059669" },
      slope: { label: "Slope Angle Gradient", icon: "bi-graph-up-arrow", color: "#dc2626" },
      twi: { label: "Topographic Wetness Index (TWI)", icon: "bi-droplet-fill", color: "#0891b2" },
      aspect: { label: "Terrain Aspect (Orientation)", icon: "bi-compass", color: "#d97706" },
      curvature: { label: "Profile / Plan Curvature", icon: "bi-bezier2", color: "#7c3aed" }
    };

    const sortedFeatures = Object.entries(m.featureImportance).sort((a, b) => b[1] - a[1]);

    featuresContainer.innerHTML = sortedFeatures.map(([key, pct]) => {
      const meta = factorNames[key] || { label: key, icon: "bi-dot", color: "#475569" };
      return `
        <div class="mb-2">
          <div class="d-flex justify-content-between align-items-center small mb-1">
            <span class="fw-semibold text-navy"><i class="bi ${meta.icon} me-1" style="color: ${meta.color};"></i>${meta.label}</span>
            <span class="fw-bold" style="color: ${meta.color};">${pct.toFixed(1)}%</span>
          </div>
          <div class="progress" style="height: 7px; background-color: #e2e8f0;">
            <div class="progress-bar" style="width: ${pct}%; background-color: ${meta.color};"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Scenarios Table
  const scenariosBody = document.getElementById('mfm-scenarios-body');
  const contextEl = document.getElementById('mfm-extreme-context');
  if (contextEl && stateNowcast.extremeContext) {
    contextEl.innerHTML = `<i class="bi bi-info-circle me-1 text-primary"></i><strong>Terrain context:</strong> ${stateNowcast.extremeContext}`;
  }

  if (scenariosBody && stateNowcast.scenarios) {
    const sc = stateNowcast.scenarios;
    scenariosBody.innerHTML = Object.entries(sc).map(([k, s]) => {
      const combined = (s.l3 + s.l4).toFixed(1);
      const isExtreme = k === 'extreme';
      return `
        <tr class="${isExtreme ? 'table-danger-subtle fw-bold' : ''}">
          <td class="text-start">${s.label}</td>
          <td>${s.ari.toFixed(1)}</td>
          <td>${s.l0.toFixed(1)}%</td>
          <td>${s.l1.toFixed(1)}%</td>
          <td>${s.l2.toFixed(1)}%</td>
          <td class="${s.l3 > 0 ? 'text-warning text-dark' : ''}">${s.l3.toFixed(1)}%</td>
          <td class="${s.l4 > 0 ? 'text-danger' : ''}">${s.l4.toFixed(1)}%</td>
          <td class="${combined > 0 ? 'text-danger fw-bold' : ''}">${combined}%</td>
        </tr>
      `;
    }).join('');
  }

  // Map link button
  const mapBtn = document.getElementById('mfm-view-map-btn');
  if (mapBtn) {
    mapBtn.href = `risk-map.html?focus=${stateKey}`;
  }

  const modalEl = document.getElementById('modelFeatureModal');
  if (modalEl && window.bootstrap) {
    const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
    modal.show();
  }
}

function renderDashboardPendingReports() {
  const container = document.getElementById('pending-reports-dashboard-list');
  if (!container) return;

  const reports = window.getStoredReports ? window.getStoredReports() : [];
  const pendingOnly = reports.filter(r => r.status === 'PENDING VERIFICATION');

  const pendingStatEl = document.getElementById('stat-pending-count');
  const pendingBtnLabel = document.getElementById('btn-pending-count-label');
  if (pendingStatEl) pendingStatEl.innerText = pendingOnly.length;
  if (pendingBtnLabel) pendingBtnLabel.innerText = pendingOnly.length;

  if (pendingOnly.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center py-4 text-muted">
        <i class="bi bi-check-circle-fill text-success fs-2 mb-2 d-block"></i>
        <h6 class="fw-bold text-navy">All Public Reports Reviewed!</h6>
        <p class="small mb-0">No unverified pending reports remaining in the queue.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = pendingOnly.map(rep => `
    <div class="col-md-6 col-lg-4" id="report-card-${rep.id}">
      <div class="card h-100 border rounded-1 shadow-none overflow-hidden" style="border: 1px solid var(--gov-border) !important; border-left: 3px solid #b45309 !important; background-color: #ffffff;">
        <div class="position-relative" style="background-color: #f1f5f9; height: 130px;">
          <img src="${rep.image}" alt="Field Report" 
               onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" 
               style="height: 130px; width: 100%; object-fit: cover;">
          <div style="display: none; height: 130px; width: 100%; background-color: #f8fafc; align-items: center; justify-content: center; color: #64748b; font-size: 0.75rem; font-weight: 600;" class="border-bottom">
            Field Photo Unavailable
          </div>
          <span class="position-absolute top-0 end-0 m-2 badge-pending-report">PENDING</span>
        </div>
        <div class="card-body p-3">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <span class="fw-bold text-navy small">${rep.id}</span>
            <span class="badge bg-light text-dark border small fw-semibold">${rep.state}</span>
          </div>
          <h6 class="fw-bold text-navy mb-1" style="font-size: 0.88rem;">${rep.type}</h6>
          <p class="text-secondary small mb-2" style="font-size: 0.78rem;">${rep.locationName}</p>
          <p class="small text-muted mb-3" style="font-size: 0.75rem; line-height: 1.35;">${rep.description}</p>
          
          <div class="small text-muted mb-3 pt-2 border-top d-flex justify-content-between" style="font-size: 0.72rem;">
            <span>Reporter: <strong class="text-dark">${rep.reporterName}</strong></span>
            <span>${rep.submittedAt}</span>
          </div>

          <div class="d-flex gap-2">
            <button class="btn btn-navy btn-sm fw-semibold flex-grow-1" onclick="verifyReportAction('${rep.id}')" style="font-size: 0.78rem;">
              Verify & Dispatch
            </button>
            <button class="btn btn-outline-danger btn-sm px-3" onclick="rejectReportAction('${rep.id}')" style="font-size: 0.78rem;">
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}

function verifyReportAction(reportId) {
  if (window.updateReportStatus) {
    window.updateReportStatus(reportId, 'VERIFIED', 'Verified via Operations Dashboard.');
    alert(`Report ${reportId} has been VERIFIED. Status updated in system database and GIS map.`);
    renderDashboardPendingReports();
    renderDashboardVerifiedTable();
  }
}

function rejectReportAction(reportId) {
  if (confirm(`Are you sure you want to dismiss pending report ${reportId}?`)) {
    if (window.updateReportStatus) {
      window.updateReportStatus(reportId, 'REJECTED', 'Dismissed via Operations Dashboard.');
      renderDashboardPendingReports();
    }
  }
}

function togglePendingReportsReviewFilter() {
  const container = document.getElementById('pending-reports-dashboard-list');
  if (container) {
    container.scrollIntoView({ behavior: 'smooth' });
  }
}

function renderDashboardVerifiedTable() {
  const tableBody = document.getElementById('verified-incidents-table-body');
  if (!tableBody) return;

  const reports = window.getStoredReports ? window.getStoredReports() : [];
  const verifiedUserReports = reports.filter(r => r.status === 'VERIFIED');

  tableBody.innerHTML = verifiedUserReports.map(inc => `
    <tr>
      <td class="fw-bold text-navy">${inc.id}</td>
      <td>
        <div class="fw-semibold text-dark">${inc.locationName}</div>
        <div class="text-muted small">${inc.state}</div>
      </td>
      <td><span class="badge bg-warning-subtle text-dark border"><i class="bi bi-exclamation-octagon me-1"></i>${inc.type}</span></td>
      <td><span class="risk-level-badge ${getRiskBadgeClass(inc.riskLevel || 'High')}">${inc.riskLevel || 'Severe'}</span></td>
      <td class="small text-muted"><i class="bi bi-clock me-1"></i>${inc.submittedAt}</td>
      <td class="small fw-semibold text-navy"><i class="bi bi-shield-check text-success me-1"></i>${inc.authorityRemarks || 'SDMA Field Verification Confirmed'}</td>
    </tr>
  `).join('');
}

/* ==========================================================================
   INCIDENT REPORTING FORM HANDLERS (PART 3)
   ========================================================================== */

function selectIncidentType(typeName, cardElement) {
  const targetCard = cardElement ? (cardElement.closest ? (cardElement.closest('.incident-type-card') || cardElement) : cardElement) : null;
  
  document.querySelectorAll('.incident-type-card').forEach(card => card.classList.remove('selected'));
  if (targetCard) {
    targetCard.classList.add('selected');
  }

  const inputEl = document.getElementById('selected-incident-type');
  if (inputEl) {
    inputEl.value = typeName;
  }

  const otherContainer = document.getElementById('other-hazard-container');
  const otherInput = document.getElementById('other-hazard-input');
  if (otherContainer) {
    if (typeName === 'Other') {
      otherContainer.classList.remove('d-none');
      if (otherInput) otherInput.focus();
    } else {
      otherContainer.classList.add('d-none');
    }
  }
}


function previewSelectedImage(input) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function(e) {
      const imgThumb = document.getElementById('image-preview-thumb');
      const container = document.getElementById('image-preview-container');
      if (imgThumb && container) {
        imgThumb.src = e.target.result;
        container.classList.remove('d-none');
      }
    };
    reader.readAsDataURL(input.files[0]);
  }
}

function clearSelectedImage() {
  const input = document.getElementById('input-image-file');
  const container = document.getElementById('image-preview-container');
  if (input) input.value = '';
  if (container) container.classList.add('d-none');
}

function previewSelectedVideo(input) {
  if (input.files && input.files[0]) {
    const filenameEl = document.getElementById('video-filename');
    const infoBox = document.getElementById('video-preview-info');
    if (filenameEl && infoBox) {
      filenameEl.innerText = input.files[0].name;
      infoBox.classList.remove('d-none');
    }
  }
}

function getUserCurrentGPSLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        document.getElementById('report-lat').value = lat.toFixed(6);
        document.getElementById('report-lon').value = lon.toFixed(6);
        alert(`Location Updated via GPS: ${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E`);
      },
      (error) => {
        alert("GPS Location access unavailable. Defaulting to monitored regional coordinates (25.5788° N, 91.8933° E).");
        document.getElementById('report-lat').value = (25.5788).toFixed(6);
        document.getElementById('report-lon').value = (91.8933).toFixed(6);
      }
    );
  } else {
    alert("Geolocation is not supported by your browser.");
  }
}

function updateReportStateMLStatus() {
  const select = document.getElementById('report-state');
  const banner = document.getElementById('report-state-ml-banner');
  if (!select || !banner) return;

  const stateName = select.value;
  const stateKeyMap = {
    "Sikkim": "sikkim",
    "Nagaland": "nagaland",
    "Meghalaya": "meghalaya",
    "Assam": "assam"
  };
  const stKey = stateKeyMap[stateName];
  const allMetrics = window.LHASA_MODEL_METRICS || [];
  const m = stKey ? allMetrics.find(x => x.stateKey === stKey) : null;

  if (m && m.status === 'complete') {
    banner.innerHTML = `<span class="badge bg-success text-white me-1"><i class="bi bi-cpu-fill me-1"></i>30m XGBoost Active</span> <span class="text-dark fw-semibold">${m.testAUC.toFixed(1)}% Test AUC • Dominant driver: ${m.topFeature}</span> <div class="text-muted small">Validated incident reports directly append to the ground-truth model retraining pipeline.</div>`;
  } else {
    banner.innerHTML = `<span class="badge bg-secondary text-white me-1"><i class="bi bi-clock-history me-1"></i>Model Scheduled</span> <span class="text-muted">Field reports provide ground-truth inventory for upcoming ${stateName} model release.</span>`;
  }
}

function initReportFormHandler() {
  const form = document.getElementById('incident-report-form');
  if (document.getElementById('report-state')) {
    updateReportStateMLStatus();
  }
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    let type = document.getElementById('selected-incident-type').value || 'Landslide';
    if (type === 'Other') {
      const customType = document.getElementById('other-hazard-input') ? document.getElementById('other-hazard-input').value.trim() : '';
      type = customType ? `Other (${customType})` : 'Other Hazard';
    }
    const lat = parseFloat(document.getElementById('report-lat').value) || 26.0;
    const lon = parseFloat(document.getElementById('report-lon').value) || 92.5;
    const state = document.getElementById('report-state').value;
    const district = document.getElementById('report-district').value;
    const description = document.getElementById('report-description').value;
    const reporterName = document.getElementById('report-author-name').value;
    const reporterPhone = document.getElementById('report-author-phone').value;

    const imgThumb = document.getElementById('image-preview-thumb');
    const imageSrc = (imgThumb && imgThumb.src && imgThumb.src.length > 50) 
      ? imgThumb.src 
      : "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7?w=600&auto=format&fit=crop";

    const reportId = `REP-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    const now = new Date();
    const dateStr = `${now.toISOString().slice(0, 10)} ${now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;

    const newReportObj = {
      id: reportId,
      type: type,
      lat: lat,
      lon: lon,
      state: state,
      district: district,
      locationName: `${district}, ${state}`,
      description: description,
      reporterName: reporterName,
      reporterContact: reporterPhone,
      status: "PENDING VERIFICATION",
      riskLevel: "Severe",
      submittedAt: dateStr,
      image: imageSrc
    };

    if (window.saveNewReport) {
      window.saveNewReport(newReportObj);
    }

    document.getElementById('success-report-id').innerText = reportId;
    document.getElementById('success-report-type').innerText = type;
    document.getElementById('success-report-coords').innerText = `${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E`;

    const modalEl = document.getElementById('reportSuccessModal');
    if (modalEl && window.bootstrap) {
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    } else {
      alert(`Report ${reportId} Submitted Successfully! Status: PENDING VERIFICATION`);
    }

    form.reset();
    clearSelectedImage();
  });
}

function renderDetailedAnalysisCharts(loc) {
  if (typeof Chart === 'undefined') return;

  const weights = loc.riskFactorWeights || { rainfall: 30, slope: 25, soilMoisture: 20, insarCreep: 15, vegetationLoss: 10 };
  const trendData = loc.insarTrendData || [0, -1, -3, -6, -9, -12];

  const ctxFactors = document.getElementById('chart-risk-factors');
  if (ctxFactors) {
    if (window.chartRiskFactorsInstance) window.chartRiskFactorsInstance.destroy();

    window.chartRiskFactorsInstance = new Chart(ctxFactors, {
      type: 'radar',
      data: {
        labels: ['Rainfall Intensity', 'Slope Steepness', 'Soil Saturation', 'InSAR Ground Creep', 'Vegetation Loss'],
        datasets: [{
          label: `${loc.name} Factor Weight`,
          data: [weights.rainfall, weights.slope, weights.soilMoisture, weights.insarCreep, weights.vegetationLoss],
          backgroundColor: 'rgba(37, 99, 235, 0.25)',
          borderColor: '#1e3a8a',
          pointBackgroundColor: '#dc2626',
          pointBorderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { r: { angleLines: { color: '#cbd5e1' }, grid: { color: '#e2e8f0' }, ticks: { display: false } } },
        plugins: { legend: { display: false } }
      }
    });
  }

  const ctxTimeline = document.getElementById('chart-insar-timeline');
  if (ctxTimeline) {
    if (window.chartInsarTimelineInstance) window.chartInsarTimelineInstance.destroy();

    window.chartInsarTimelineInstance = new Chart(ctxTimeline, {
      type: 'line',
      data: {
        labels: ['Month -5', 'Month -4', 'Month -3', 'Month -2', 'Month -1', 'Current'],
        datasets: [{
          label: 'Cumulative Displacement (mm)',
          data: trendData,
          borderColor: loc.riskLevel === 'Severe' ? '#dc2626' : '#2563eb',
          backgroundColor: loc.riskLevel === 'Severe' ? 'rgba(220, 38, 38, 0.1)' : 'rgba(37, 99, 235, 0.1)',
          fill: true,
          tension: 0.3,
          borderWidth: 2.5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: '#f1f5f9' } },
          y: { grid: { color: '#e2e8f0' }, title: { display: true, text: 'Deformation (mm)' } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }
}

window.renderDetailedAnalysisCharts = renderDetailedAnalysisCharts;

/* =====================================================================
 * PREVENTION PLAN - automatically generated from a location's own
 * riskFactorWeights (the same 5 factors driving the radar chart above),
 * so different locations produce visibly different plans depending on
 * what's actually driving their risk. This is a rule-based mapping
 * (factor -> known mitigation practices), not a live model - labeled
 * "Rule-based (illustrative)" in the UI, consistent with the rest of
 * this prototype's real-vs-mock convention.
 * ===================================================================== */

const PREVENTION_KNOWLEDGE_BASE = {
  rainfall: {
    label: 'Rainfall Intensity',
    icon: 'bi-cloud-rain-heavy-fill',
    measures: [
      'Construct surface drainage channels/catch-water drains to divert runoff away from the slope face',
      'Install French drains or sub-surface drainage to relieve pore-water pressure',
      'Issue rainfall-threshold early warnings to residents ahead of forecast heavy spells',
      'Restrict new construction and excavation during peak monsoon months'
    ]
  },
  slope: {
    label: 'Slope Steepness',
    icon: 'bi-graph-down-arrow',
    measures: [
      'Slope stabilization: retaining walls, soil nailing, or gabion structures on steep cut-slopes',
      'Bench/terrace steep sections to reduce effective slope angle',
      'Restrict heavy vehicle movement and blasting on roads cut into steep slopes',
      'Regular geotechnical inspection of cut-slope stability along this corridor'
    ]
  },
  soilMoisture: {
    label: 'Soil Saturation',
    icon: 'bi-moisture',
    measures: [
      'Install horizontal sub-surface drains to lower the water table in saturated zones',
      'Deploy soil-moisture sensors for continuous saturation monitoring',
      'Check for and repair leaking water pipelines/irrigation channels near the slope',
      'Avoid water-intensive land use directly upslope of vulnerable zones'
    ]
  },
  insarCreep: {
    label: 'InSAR Ground Creep',
    icon: 'bi-activity',
    measures: [
      'Install ground-based extensometers/inclinometers to validate and densify InSAR creep readings',
      'Flag this zone for restricted new habitation until creep rate stabilizes',
      'Set up automated real-time movement alert thresholds tied to inclinometer data',
      'Schedule follow-up satellite (InSAR) passes at higher frequency for this zone'
    ]
  },
  vegetationLoss: {
    label: 'Vegetation Loss',
    icon: 'bi-tree-fill',
    measures: [
      'Bioengineering measures: vetiver grass or root-reinforcement planting on exposed slopes',
      'Community afforestation/reforestation drive on the denuded catchment above this zone',
      'Regulate/monitor deforestation and mining permits upslope',
      'Enforce buffer-zone tree retention rules for any nearby construction'
    ]
  }
};

function generatePreventionPlan(loc) {
  const weights = loc.riskFactorWeights || { rainfall: 30, slope: 25, soilMoisture: 20, insarCreep: 15, vegetationLoss: 10 };
  const ranked = Object.keys(weights)
    .map(key => ({ key, weight: weights[key], ...PREVENTION_KNOWLEDGE_BASE[key] }))
    .sort((a, b) => b.weight - a.weight);

  return {
    riskLevel: loc.riskLevel,
    riskScore: loc.riskScore,
    primary: ranked.slice(0, 2),   // top 2 factors -> priority interventions
    secondary: ranked.slice(2)     // remaining factors -> monitoring measures
  };
}

function renderPreventionTab(loc) {
  const plan = generatePreventionPlan(loc);

  // Urgency banner, driven by the location's actual composite risk level
  const banner = document.getElementById('prevention-urgency-banner');
  const titleEl = document.getElementById('prevention-urgency-title');
  const textEl = document.getElementById('prevention-urgency-text');
  const urgencyMap = {
    'Severe': { cls: 'alert-danger', title: '⚠️ Immediate Intervention Advised', text: `Composite risk score ${plan.riskScore}/100 (Severe). Priority interventions below should be actioned without delay; consider restricting access/habitation in the most affected zones until mitigated.` },
    'High': { cls: 'alert-warning', title: '⚠️ Priority Intervention Recommended', text: `Composite risk score ${plan.riskScore}/100 (High). Priority interventions below should be scheduled in the near term, ahead of the next monsoon/high-rainfall period.` },
    'Moderate': { cls: 'alert-info', title: 'ℹ️ Preventive Measures Recommended', text: `Composite risk score ${plan.riskScore}/100 (Moderate). Preventive and monitoring measures below help keep this location from escalating further.` },
    'Low': { cls: 'alert-success', title: '✅ Routine Monitoring Sufficient', text: `Composite risk score ${plan.riskScore}/100 (Low). No urgent intervention required — routine monitoring of the factors below is recommended.` }
  };
  const u = urgencyMap[plan.riskLevel] || urgencyMap['Moderate'];
  if (banner) banner.className = `alert p-3 mb-3 small ${u.cls}`;
  if (titleEl) titleEl.textContent = u.title;
  if (textEl) textEl.textContent = u.text;

  // Priority interventions - top 2 contributing factors, full measure lists
  const primaryContainer = document.getElementById('prevention-primary-list');
  if (primaryContainer) {
    primaryContainer.innerHTML = plan.primary.map((f, i) => `
      <div class="prevention-card rank-${i + 1}">
        <div class="prevention-card-header">
          <span class="prevention-card-title"><i class="bi ${f.icon} me-1"></i>${f.label}</span>
          <span class="prevention-card-weight">${f.weight}% of composite risk</span>
        </div>
        <ul>${f.measures.map(m => `<li>${m}</li>`).join('')}</ul>
      </div>
    `).join('');
  }

  // Secondary / monitoring - remaining factors, condensed to top 2 measures each
  const secondaryContainer = document.getElementById('prevention-secondary-list');
  if (secondaryContainer) {
    secondaryContainer.innerHTML = plan.secondary.map(f => `
      <div class="prevention-secondary-item">
        <i class="bi ${f.icon} text-muted"></i>
        <span><strong>${f.label}</strong> (${f.weight}%) — ${f.measures[0]}</span>
      </div>
    `).join('');
  }
}
window.renderPreventionTab = renderPreventionTab;
window.selectIncidentType = selectIncidentType;
window.previewSelectedImage = previewSelectedImage;
window.clearSelectedImage = clearSelectedImage;
window.previewSelectedVideo = previewSelectedVideo;
window.getUserCurrentGPSLocation = getUserCurrentGPSLocation;
window.handleAuthorityLogout = handleAuthorityLogout;
window.verifyReportAction = verifyReportAction;
window.rejectReportAction = rejectReportAction;
window.togglePendingReportsReviewFilter = togglePendingReportsReviewFilter;
window.selectReportForVerification = selectReportForVerification;
window.executeAuthorityAction = executeAuthorityAction;
window.filterVerificationTable = filterVerificationTable;
window.updateTargetAreaMetadata = updateTargetAreaMetadata;
window.selectAlertCategory = selectAlertCategory;
window.generateAutoAlertTemplate = generateAutoAlertTemplate;
window.triggerAlertConfirmationModal = triggerAlertConfirmationModal;
window.executeEmergencyAlertDispatch = executeEmergencyAlertDispatch;
function zoomToPriorityLocation(lat, lon, zoom = 12) {
  if (window.focusMapOnCoordinates) {
    window.focusMapOnCoordinates(lat, lon, zoom);
  } else if (window.map && window.ol) {
    window.map.getView().animate({ center: window.ol.proj.fromLonLat([lon, lat]), zoom: zoom, duration: 800 });
  }
}
window.zoomToPriorityLocation = zoomToPriorityLocation;
window.renderDashboardMLModelsTable = renderDashboardMLModelsTable;
window.showModelFeatureModal = showModelFeatureModal;
window.updateReportStateMLStatus = updateReportStateMLStatus;

// Auto-Run Priority Calculation Immediately & On Window Load
if (typeof calculateEmergencyPriority === 'function') {
  calculateEmergencyPriority();
}
window.addEventListener('load', () => {
  if (typeof calculateEmergencyPriority === 'function') {
    calculateEmergencyPriority();
  }
});

window.initDynamicNavHeader = initDynamicNavHeader;
