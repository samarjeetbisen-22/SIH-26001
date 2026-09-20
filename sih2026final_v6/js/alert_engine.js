/**
 * NER Landslide Early Warning System — Advanced Alert & Broadcast Engine
 * Features:
 *  1. Direct Trigger from ML Model Nowcast (NASA LHASA v2 + 30m XGBoost)
 *  2. Multi-Lingual SMS & Online Broadcasts in Regional Languages (English, Hindi, Nepali, Assamese, Khasi, Nagamese)
 *  3. Offline Geo-Fenced Radius Alerting (Cell Broadcast CBS, LoRaWAN / VHF Mesh Sirens)
 *  4. CAP-CP (Common Alerting Protocol - India Profile v1.2) XML/JSON Generator
 */

const REGIONAL_TRANSLATIONS = {
  sikkim: {
    english: {
      langName: "English",
      title: "CRITICAL LANDSLIDE EMERGENCY (Level 4)",
      message: "EMERGENCY DIRECTIVE: Extreme antecedent rainfall has breached critical slope saturation in East Sikkim along NH-10. Immediate landslide probability high near Dikchu and 9th Mile. Evacuate active slip zones immediately."
    },
    nepali: {
      langName: "नेपाली (Nepali)",
      title: "गम्भीर पहिरो चेतावनी (स्तर ४)",
      message: "आपतकालीन निर्देशन: अत्यधिक वर्षाका कारण पूर्वी सिक्किमको एनएच-१० र डिक्चु क्षेत्रमा जमिन भासिने र ठूलो पहिरो जाने उच्च जोखिम उत्पन्न भएको छ। भिरालो र जोखिमयुक्त ठाउँबाट तुरुन्त सुरक्षित स्थानमा जानुहोस्।"
    },
    hindi: {
      langName: "हिंदी (Hindi)",
      title: "गंभीर भूस्खलन आपातकाल (स्तर 4)",
      message: "आपातकालीन चेतावनी: पूर्व सिक्किम में एनएच-10 और डिक्चु मार्ग पर अत्यधिक वर्षा के कारण भारी भूस्खलन की अत्यधिक संभावना है। ढलानों के निचले इलाकों से तुरंत सुरक्षित आश्रय स्थलों पर जाएँ।"
    }
  },
  nagaland: {
    english: {
      langName: "English",
      title: "LANDSLIDE WARNING ALERT (Level 3)",
      message: "WARNING ADVISORY: High rainfall intensity triggering active ground subsidence along NH-29 Kohima-Dimapur bypass and Phesama sinking zone. Avoid travel; heavy vehicles restricted."
    },
    nagamese: {
      langName: "Nagamese / English",
      title: "LANDSLIDE DANGER WARNING (Level 3)",
      message: "HOSHIYAR THAKIBI: Bishi borokh pori ase, Kohima NH-29 aru Phesama sinking zone te mati dhori jabo laga bishi risk ase. Gari loi jabo naparibo, safe jaka te thakibi."
    },
    hindi: {
      langName: "हिंदी (Hindi)",
      title: "भूस्खलन चेतावनी (स्तर 3)",
      message: "चेतावनी सूचना: कोहिमा-दीमापुर बाईपास (एनएच-29) और फेसामा धंसाव क्षेत्र में भारी बारिश से सक्रिय भूस्खलन का खतरा। पर्वतीय सड़कों पर यात्रा से बचें।"
    }
  },
  meghalaya: {
    english: {
      langName: "English",
      title: "LANDSLIDE & FLASH RUNOFF ADVISORY (Level 2/3)",
      message: "HIGH ADVISORY: Saturated plateau terrain along NH-6 Shillong-Jowai corridor and Cherrapunji escarpment. Caution advised near rock-cut highway sections."
    },
    khasi: {
      langName: "Ka Ktien Khasi (Khasi)",
      title: "KA JINGMA NA KA JINGTWA KA KHYNDEW",
      message: "KA JINGMA JUR: Ka jingther u slap ka la pynlong ka jingma kaba khraw ha NH-6 Shillong-Jowai bad ki thain Cherrapunji. Ki paidbah kiba shong ha ki jaka riat ki dei ban phet noh sha ki jaka ba shngain."
    },
    hindi: {
      langName: "हिंदी (Hindi)",
      title: "भूस्खलन एवं चट्टान गिरने की चेतावनी",
      message: "पठारी चेतावनी: शिलांग-जोवाई राजमार्ग (एनएच-6) और चेरापूंजी ढलानों पर मिट्टी संतृप्त होने से चट्टानें खिसकने का खतरा है। सुरक्षित रहें।"
    }
  },
  assam: {
    english: {
      langName: "English",
      title: "HILL SLOPE HAZARD ALERT (Dima Hasao)",
      message: "LANDSLIDE WATCH: Prolonged hill rainfall detected along NH-27 Haflong section and Lumding-Badarpur rail alignment. Maintenance and monitoring crews on standby."
    },
    assamese: {
      langName: "অসমীয়া (Assamese)",
      title: "ভূমিস্খলন আৰু ৰে'ল পথৰ সতৰ্কবাৰ্তা",
      message: "ভূমিস্খলনৰ সতৰ্কবাৰ্তা: ধাৰাসাৰ বৰষুণৰ বাবে ডিমা হাছাওৰ পাহাৰীয়া এলেকা আৰু এন এইচ-২৭ হাফলং সংযোগী পথত ভূমিস্খলনৰ আশংকা। পাহাৰীয়া পথত সাৱধানে চলাচল কৰক।"
    },
    hindi: {
      langName: "हिंदी (Hindi)",
      title: "असम पहाड़ी भूस्खलन निगरानी सूचना",
      message: "दीमा हसाओ और हाफलॉन्ग पहाड़ी खंड (एनएच-27) पर निरंतर वर्षा के कारण सतर्कता बरतें। ढलानों और रेलवे संरेखण के पास सावधानी रखें।"
    }
  },
  tawang: {
    english: {
      langName: "English",
      title: "MOUNTAIN PASS HAZARD ALERT (Level 3)",
      message: "HIGH RISK ALERT: High rainfall detected on Sela Pass approach corridor in Tawang. Steep slope debris movement active. Army and border commuters exercise caution."
    },
    hindi: {
      langName: "हिंदी (Hindi)",
      title: "तवांग पर्वतीय भूस्खलन चेतावनी",
      message: "उच्च जोखिम चेतावनी: तवांग सेला दर्रा मार्ग पर अत्यधिक वर्षा से भूस्खलन का सक्रिय खतरा। खड़ी ढलानों वाले मोड़ों पर यात्रा में अत्यधिक सतर्कता बरतें।"
    }
  },
  aizawl: {
    english: {
      langName: "English",
      title: "RIDGE SUBSIDENCE EMERGENCY (Level 4)",
      message: "EMERGENCY DIRECTIVE: Severe saturation on Laipuitlang and Hunthar ridge slopes in Aizawl. Critical slope creep detected. Relocate to safe community shelters immediately."
    },
    hindi: {
      langName: "हिंदी (Hindi)",
      title: "आइजोल रिज भूस्खलन आपातकाल",
      message: "आपातकालीन चेतावनी: आइजोल हुंथार और लइपुइतलाँग रिज पर अत्यधिक मिट्टी संतृप्ति से भू-धंसाव का संकट। संवेदनशील ढलानों से तुरंत सुरक्षित स्थानों पर जाएँ।"
    }
  }
};

// Standard Geo-Fencing Radii & Estimated Impact Population
const GEO_RADIUS_OPTIONS = [
  { radiusKm: 5,  label: "5 km (Immediate Foothills & Slopes)", basePopMultiplier: 0.25, cbsTowers: 2, loraGateways: 3 },
  { radiusKm: 15, label: "15 km (District Corridor & Towns)",    basePopMultiplier: 1.0,  cbsTowers: 8, loraGateways: 11 },
  { radiusKm: 25, label: "25 km (Sub-Divisional Catchment)",    basePopMultiplier: 2.4,  cbsTowers: 18, loraGateways: 24 },
  { radiusKm: 50, label: "50 km (Regional Hill Belt)",           basePopMultiplier: 5.2,  cbsTowers: 46, loraGateways: 60 }
];

/**
 * Returns canonical state key from district dropdown value
 */
function getDistrictStateKey(districtKey) {
  if (!districtKey) return 'sikkim';
  const k = districtKey.toLowerCase();
  if (k.includes('gangtok') || k.includes('sikkim')) return 'sikkim';
  if (k.includes('kohima') || k.includes('nagaland')) return 'nagaland';
  if (k.includes('shillong') || k.includes('meghalaya')) return 'meghalaya';
  if (k.includes('haflong') || k.includes('guwahati') || k.includes('assam')) return 'assam';
  if (k.includes('tawang')) return 'tawang';
  if (k.includes('aizawl')) return 'aizawl';
  return 'sikkim';
}

/**
 * Generates official CAP-CP (Common Alerting Protocol - India Profile v1.2) XML payload
 */
function generateCapXmlPayload(alertData) {
  const identifier = alertData.id || `IN-NDMA-NER-${Date.now()}`;
  const sender = "operations@ndma-ner.gov.in";
  const sent = alertData.sentIso || new Date().toISOString();
  const status = "Actual";
  const msgType = "Alert";
  const scope = "Public";
  
  const lat = alertData.lat || 27.3389;
  const lon = alertData.lon || 88.6065;
  const radius = alertData.geoRadiusKm || 15;

  return `<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>${identifier}</identifier>
  <sender>${sender}</sender>
  <sent>${sent}</sent>
  <status>${status}</status>
  <msgType>${msgType}</msgType>
  <scope>${scope}</scope>
  <info>
    <category>Geo</category>
    <event>Landslide / Mass Movement Hazard</event>
    <urgency>${alertData.riskLevel === 'Severe' ? 'Immediate' : 'Expected'}</urgency>
    <severity>${alertData.riskLevel === 'Severe' ? 'Extreme' : 'Severe'}</severity>
    <certainty>Observed</certainty>
    <eventCode>
      <valueName>DisasterType</valueName>
      <value>LS-01</value>
    </eventCode>
    <expires>${new Date(Date.now() + 24 * 3600 * 1000).toISOString()}</expires>
    <headline>${alertData.alertType || 'Landslide Emergency Broadcast'}: ${alertData.targetArea}</headline>
    <description>${alertData.message}</description>
    <instruction>Avoid steep slopes, follow police diversions, and evacuate active drainage lines.</instruction>
    <contact>NER Emergency Control Centre (+91-361-2237219)</contact>
    <parameter>
      <valueName>ModelTrigger</valueName>
      <value>${alertData.modelTriggered ? 'NASA-LHASA-v2-XGBoost-30m' : 'Manual-Operator-Dispatch'}</value>
    </parameter>
    <parameter>
      <valueName>DeliveryModes</valueName>
      <value>${(alertData.channels || []).join(',')}</value>
    </parameter>
    <parameter>
      <valueName>RegionalLanguage</valueName>
      <value>${alertData.language || 'english'}</value>
    </parameter>
    <parameter>
      <valueName>OfflineCoverage</valueName>
      <value>${radius}km-Circle; CBS-Towers:${alertData.cbsTowers || 8}; LoRa-Sirens:${alertData.loraGateways || 11}</value>
    </parameter>
    <area>
      <areaDesc>${alertData.targetArea} (${radius}km buffer)</areaDesc>
      <circle>${Number(lat).toFixed(4)},${Number(lon).toFixed(4)} ${radius}.0</circle>
    </area>
  </info>
</alert>`.trim();
}

/**
 * Handle Geo-Fenced Radius Selection
 */
function selectGeoRadius(radiusKm, btnEl) {
  const hiddenInput = document.getElementById('selected-geo-radius');
  if (hiddenInput) hiddenInput.value = radiusKm;

  // Toggle active button class
  document.querySelectorAll('.radius-btn').forEach(btn => {
    btn.classList.remove('btn-danger', 'active');
    btn.classList.add('btn-outline-secondary');
  });
  if (btnEl) {
    btnEl.classList.remove('btn-outline-secondary');
    btnEl.classList.add('btn-danger', 'active');
  }

  // Update badge display
  const badgeEl = document.getElementById('display-radius-badge');
  if (badgeEl) badgeEl.innerText = `${radiusKm} km Radius`;

  // Find radius config
  const opt = GEO_RADIUS_OPTIONS.find(o => o.radiusKm === radiusKm) || GEO_RADIUS_OPTIONS[1];

  // Base population calculation from current district
  const districtKey = document.getElementById('alert-select-district')?.value || 'gangtok';
  const metaMap = window.MOCK_ALERT_AREAS_DATA || {};
  const basePop = metaMap[districtKey]?.estPopulation || 42000;
  const scaledPop = Math.round(basePop * opt.basePopMultiplier);

  const popEl = document.getElementById('radius-population');
  if (popEl) popEl.innerText = `${scaledPop.toLocaleString('en-IN')} Residents`;

  const towersEl = document.getElementById('radius-towers');
  if (towersEl) towersEl.innerText = `${opt.cbsTowers} Cellular Towers`;

  const gatewaysEl = document.getElementById('radius-gateways');
  if (gatewaysEl) gatewaysEl.innerText = `${opt.loraGateways} Gateways Ready`;

  // Also update metadata population display
  const metaPopEl = document.getElementById('meta-population');
  if (metaPopEl) metaPopEl.innerText = `${scaledPop.toLocaleString('en-IN')} Residents`;

  refreshCapPreview();
}

/**
 * Handle Language selection tab click
 */
function selectAlertLanguage(langKey, btnEl) {
  const hiddenInput = document.getElementById('selected-alert-language');
  if (hiddenInput) hiddenInput.value = langKey;

  // Update button group style
  const langGroup = document.getElementById('lang-selector-group');
  if (langGroup) {
    langGroup.querySelectorAll('button').forEach(b => {
      b.classList.remove('btn-navy', 'active');
      b.classList.add('btn-outline-navy');
    });
  }
  if (btnEl) {
    btnEl.classList.remove('btn-outline-navy');
    btnEl.classList.add('btn-navy', 'active');
  }

  const districtKey = document.getElementById('alert-select-district')?.value || 'gangtok';
  const stateKey = getDistrictStateKey(districtKey);
  updateMultilingualPreview(stateKey, langKey);
  refreshCapPreview();
}

/**
 * Pre-populates alert form with live model prediction metrics
 */
function fillAlertFromModelPrediction(stateKey) {
  const liveMap = window.REALTIME_WEATHER_LHASA || {};
  const data = liveMap[stateKey];

  // Set target district dropdown
  const districtSelect = document.getElementById('alert-select-district');
  if (districtSelect) {
    const optMatch = Array.from(districtSelect.options).find(o => 
      o.value.toLowerCase().includes(stateKey) || 
      (stateKey === 'sikkim' && o.value === 'gangtok') || 
      (stateKey === 'meghalaya' && o.value === 'shillong') || 
      (stateKey === 'nagaland' && o.value === 'kohima') || 
      (stateKey === 'assam' && (o.value === 'haflong' || o.value === 'guwahati'))
    );
    if (optMatch) {
      districtSelect.value = optMatch.value;
      if (window.updateTargetAreaMetadata) window.updateTargetAreaMetadata();
    }
  }

  // Set category according to model nowcast
  let targetCat = 'Warning';
  if (data && (data.ari >= 100 || (data.nowcast && data.nowcast.l4 > 5.0))) {
    targetCat = 'Severe Emergency Alert';
  } else if (data && (data.ari >= 60 || (data.nowcast && data.nowcast.l3 > 5.0))) {
    targetCat = 'High Risk Alert';
  }

  if (window.selectAlertCategory) {
    const cardEl = Array.from(document.querySelectorAll('.alert-type-card')).find(c => 
      c.textContent.toLowerCase().includes(targetCat.toLowerCase().split(' ')[0])
    );
    if (cardEl) window.selectAlertCategory(targetCat, cardEl);
  }

  // Choose appropriate native regional language
  let nativeLang = 'english';
  if (stateKey === 'sikkim') nativeLang = 'nepali';
  else if (stateKey === 'nagaland') nativeLang = 'nagamese';
  else if (stateKey === 'meghalaya') nativeLang = 'khasi';
  else if (stateKey === 'assam') nativeLang = 'assamese';

  // Highlight language button
  const langGroup = document.getElementById('lang-selector-group');
  if (langGroup) {
    const targetBtn = Array.from(langGroup.querySelectorAll('button')).find(b => 
      b.getAttribute('onclick') && b.getAttribute('onclick').includes(nativeLang)
    );
    if (targetBtn) {
      langGroup.querySelectorAll('button').forEach(b => {
        b.classList.remove('btn-navy', 'active');
        b.classList.add('btn-outline-navy');
      });
      targetBtn.classList.remove('btn-outline-navy');
      targetBtn.classList.add('btn-navy', 'active');
    }
  }
  const langInput = document.getElementById('selected-alert-language');
  if (langInput) langInput.value = nativeLang;

  // Update live translation preview
  updateMultilingualPreview(stateKey, nativeLang);

  // Set radius to 15km
  const radBtn = document.querySelectorAll('.radius-btn')?.[1];
  selectGeoRadius(15, radBtn);

  refreshCapPreview();

  // Notification toast
  if (window.showMonitoringToast) {
    window.showMonitoringToast(
      "Model Auto-Fill Applied",
      `Populated alert parameters from real-time NASA LHASA v2 nowcast for ${stateKey.toUpperCase()}.`,
      false
    );
  }

  return true;
}

/**
 * Updates text in the message box based on selected regional language
 */
function updateMultilingualPreview(stateKey, lang = 'english') {
  const stateDict = REGIONAL_TRANSLATIONS[stateKey] || REGIONAL_TRANSLATIONS.sikkim;
  const langObj = stateDict[lang] || stateDict.english || Object.values(stateDict)[0];

  const msgTextarea = document.getElementById('alert-message-text');
  if (msgTextarea && langObj) {
    msgTextarea.value = langObj.message;
  }

  const langBadge = document.getElementById('active-lang-badge');
  if (langBadge && langObj) {
    langBadge.textContent = langObj.langName;
  }

  // Update SMS character count & segment calculation
  updateSmsCharCounter();
}

/**
 * Computes SMS characters and segments (GSM-7 vs Unicode)
 */
function updateSmsCharCounter() {
  const msgTextarea = document.getElementById('alert-message-text');
  const counterEl = document.getElementById('sms-char-counter');
  if (!msgTextarea || !counterEl) return;

  const text = msgTextarea.value || "";
  const len = text.length;
  const isUnicode = /[^\u0000-\u007f]/.test(text); // Checks if regional script (Nepali, Assamese, Hindi, etc.)

  const perPart = isUnicode ? 70 : 160;
  const parts = Math.max(1, Math.ceil(len / perPart));

  counterEl.innerHTML = `<i class="bi bi-chat-dots me-1"></i>${len} chars • <strong>${parts} SMS part${parts > 1 ? 's' : ''}</strong> (${isUnicode ? 'Unicode Regional' : 'Standard GSM-7'})`;
}

/**
 * Regenerates the live CAP-CP XML payload inspector
 */
function refreshCapPreview() {
  const capPreviewEl = document.getElementById('cap-xml-preview');
  if (!capPreviewEl) return;

  const districtKey = document.getElementById('alert-select-district')?.value || 'gangtok';
  const metaMap = window.MOCK_ALERT_AREAS_DATA || {};
  const meta = metaMap[districtKey] || { district: "Gangtok Urban Belt", riskLevel: "Severe", estPopulation: 42000 };

  const category = document.getElementById('selected-alert-type')?.value || 'Severe Emergency Alert';
  const message = document.getElementById('alert-message-text')?.value || "";
  const radius = parseInt(document.getElementById('selected-geo-radius')?.value || '15', 10);
  const lang = document.getElementById('selected-alert-language')?.value || 'english';

  const selectedChannels = [];
  document.querySelectorAll('.channel-chk:checked').forEach(chk => selectedChannels.push(chk.value));

  const coords = {
    gangtok: { lat: 27.3389, lon: 88.6065 },
    kohima: { lat: 25.6751, lon: 94.1086 },
    shillong: { lat: 25.5788, lon: 91.8933 },
    haflong: { lat: 25.1685, lon: 93.0163 },
    tawang: { lat: 27.5860, lon: 91.8594 },
    aizawl: { lat: 23.7271, lon: 92.7176 },
    guwahati: { lat: 26.1445, lon: 91.7362 }
  }[districtKey] || { lat: 27.3389, lon: 88.6065 };

  const alertData = {
    id: `IN-NER-ALERT-${Date.now().toString().slice(-6)}`,
    sentIso: new Date().toISOString(),
    targetArea: meta.district,
    riskLevel: meta.riskLevel || 'Severe',
    alertType: category,
    message: message,
    geoRadiusKm: radius,
    cbsTowers: radius === 5 ? 2 : radius === 15 ? 8 : radius === 25 ? 18 : 46,
    loraGateways: radius === 5 ? 3 : radius === 15 ? 11 : radius === 25 ? 24 : 60,
    channels: selectedChannels,
    language: lang,
    lat: coords.lat,
    lon: coords.lon,
    modelTriggered: true
  };

  capPreviewEl.textContent = generateCapXmlPayload(alertData);
}

/**
 * Toggle Autonomous AI Model Direct Dispatch
 */
function toggleAutonomousAlertMode(el) {
  const isEnabled = el ? el.checked : true;
  localStorage.setItem('NER_AUTO_DISPATCH_ENABLED', isEnabled ? 'true' : 'false');
  if (window.showMonitoringToast) {
    window.showMonitoringToast(
      isEnabled ? "AI Model Autonomous Dispatch ACTIVE" : "AI Model Autonomous Dispatch PAUSED",
      isEnabled 
        ? "Severe (Level 4) and Warning (Level 3) breaches will automatically queue geofenced emergency broadcasts."
        : "Automated alerts disabled. Manual authority approval required for all warning dispatches.",
      isEnabled
    );
  }
}

/**
 * Displays modal with full CAP-CP XML payload & details in alert-history page
 */
function showCapDetailModal(alertId) {
  const alerts = window.getStoredAlerts ? window.getStoredAlerts() : [];
  const alertItem = alerts.find(a => a.id === alertId);
  if (!alertItem) return;

  const modalEl = document.getElementById('capProtocolModal');
  if (!modalEl) return;

  document.getElementById('cap-modal-alert-id').textContent = alertItem.id;
  document.getElementById('cap-modal-target').textContent = alertItem.targetArea;
  document.getElementById('cap-modal-type').textContent = alertItem.alertType;
  document.getElementById('cap-modal-radius').textContent = `${alertItem.geoRadiusKm || 15} km Geofenced Broadcast Circle`;
  document.getElementById('cap-modal-lang').textContent = alertItem.langName || alertItem.language || 'English';
  document.getElementById('cap-modal-msg').textContent = alertItem.message;
  document.getElementById('cap-modal-xml').textContent = alertItem.capXml || generateCapXmlPayload(alertItem);

  if (window.bootstrap) {
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }
}

/**
 * Copies CAP XML text to clipboard
 */
function copyCapXmlToClipboard() {
  const xmlText = document.getElementById('cap-modal-xml')?.textContent;
  if (!xmlText) return;
  navigator.clipboard.writeText(xmlText).then(() => {
    alert("CAP-CP v1.2 XML payload copied to clipboard!");
  }).catch(() => {
    alert("Unable to copy to clipboard.");
  });
}

// Global Exports
window.REGIONAL_TRANSLATIONS = REGIONAL_TRANSLATIONS;
window.GEO_RADIUS_OPTIONS = GEO_RADIUS_OPTIONS;
window.getDistrictStateKey = getDistrictStateKey;
window.generateCapXmlPayload = generateCapXmlPayload;
window.fillAlertFromModelPrediction = fillAlertFromModelPrediction;
window.selectGeoRadius = selectGeoRadius;
window.selectAlertLanguage = selectAlertLanguage;
window.updateMultilingualPreview = updateMultilingualPreview;
window.updateSmsCharCounter = updateSmsCharCounter;
window.refreshCapPreview = refreshCapPreview;
window.toggleAutonomousAlertMode = toggleAutonomousAlertMode;
window.showCapDetailModal = showCapDetailModal;
window.copyCapXmlToClipboard = copyCapXmlToClipboard;

