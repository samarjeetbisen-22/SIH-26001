"""
NASA LHASA (Landslide Hazard Assessment for Situational Awareness) Engine for Sikkim.
Couples high-resolution static landslide susceptibility with dynamic antecedent rainfall triggers.
"""
import numpy as np
import rasterio

# Decaying Antecedent Rainfall Index (ARI) weights for 7 days (t = 0 to 6)
# w_t = (t + 1)^(-0.5)
DEFAULT_ARI_EXPONENT = 0.5
ARI_DAYS = 7
ARI_WEIGHTS = [(t + 1) ** (-DEFAULT_ARI_EXPONENT) for t in range(ARI_DAYS)]

# Alert Levels
ALERT_NONE = 0      # Safe / No Alert
ALERT_ADVISORY = 1  # Low / Advisory
ALERT_WATCH = 2     # Moderate / Watch
ALERT_WARNING = 3   # High / Warning
ALERT_SEVERE = 4    # Severe / Emergency
ALERT_NODATA = 255

ALERT_LABELS = {
    ALERT_NONE: "Level 0: No Alert (Safe)",
    ALERT_ADVISORY: "Level 1: Advisory (Low Hazard)",
    ALERT_WATCH: "Level 2: Watch (Moderate Hazard)",
    ALERT_WARNING: "Level 3: Warning (High Hazard)",
    ALERT_SEVERE: "Level 4: Severe (Critical Emergency)"
}

ALERT_COLORS = {
    ALERT_NONE: "#2ca02c",      # Green
    ALERT_ADVISORY: "#8c564b",  # Tan/Light Olive
    ALERT_WATCH: "#ff7f0e",     # Orange
    ALERT_WARNING: "#d62728",   # Bright Red
    ALERT_SEVERE: "#7f0000"     # Dark Burgundy / Purple
}

def calculate_ari(daily_rainfall_series):
    """
    Compute Antecedent Rainfall Index (ARI) from a list or array of daily rainfalls.
    daily_rainfall_series: [R_today, R_yesterday, R_2days_ago, ..., R_6days_ago]
    """
    n_days = min(len(daily_rainfall_series), len(ARI_WEIGHTS))
    ari = sum(daily_rainfall_series[t] * ARI_WEIGHTS[t] for t in range(n_days))
    return ari

def evaluate_lhasa_nowcast(susceptibility_arr, ari_arr, nodata_val=-9999.0):
    """
    Evaluate the NASA LHASA decision matrix for a 2D susceptibility array and 2D/scalar ARI.
    
    Decision Matrix:
    Static Susceptibility Classes:
      - Very Low:  P < 0.20
      - Low:       0.20 <= P < 0.40
      - Moderate:  0.40 <= P < 0.60
      - High:      0.60 <= P < 0.80
      - Very High: P >= 0.80
      
    Rainfall Trigger Thresholds (ARI in mm):
      - Low:       ARI < 40
      - Moderate:  40 <= ARI < 80
      - Heavy:     80 <= ARI < 140
      - Extreme:   ARI >= 140
    """
    # Create output array initialized to NoData
    nowcast = np.full(susceptibility_arr.shape, fill_value=ALERT_NODATA, dtype=np.uint8)
    
    # Valid mask
    valid = (susceptibility_arr != nodata_val) & ~np.isnan(susceptibility_arr)
    
    # Broadcast scalar ARI if needed
    if np.isscalar(ari_arr):
        ari = np.full(susceptibility_arr.shape, fill_value=ari_arr, dtype=np.float32)
    else:
        ari = ari_arr

    P = susceptibility_arr

    # Condition masks
    r_extreme = (ari >= 140.0) & valid
    r_heavy   = (ari >= 80.0) & (ari < 140.0) & valid
    r_mod     = (ari >= 40.0) & (ari < 80.0) & valid
    r_low     = (ari < 40.0) & valid

    s_vhigh = (P >= 0.80) & valid
    s_high  = (P >= 0.60) & (P < 0.80) & valid
    s_mod   = (P >= 0.40) & (P < 0.60) & valid
    s_low   = (P >= 0.20) & (P < 0.40) & valid
    s_vlow  = (P < 0.20) & valid

    # Level 0 (None / Safe) - Default for valid pixels
    nowcast[valid] = ALERT_NONE

    # Level 1: Advisory
    # Low rain on Very High susceptibility OR Moderate rain on Moderate susceptibility OR Heavy on Low OR Extreme on Very Low
    c_advisory = (
        (s_vhigh & r_low) |
        (s_mod & r_mod) |
        (s_low & r_heavy) |
        (s_vlow & r_extreme)
    )
    nowcast[c_advisory] = ALERT_ADVISORY

    # Level 2: Watch
    # Moderate rain on High susceptibility OR Heavy rain on Moderate susceptibility OR Extreme on Low
    c_watch = (
        (s_high & r_mod) |
        (s_mod & r_heavy) |
        (s_low & r_extreme)
    )
    nowcast[c_watch] = ALERT_WATCH

    # Level 3: Warning (High Hazard)
    # Moderate rain on Very High OR Heavy rain on High OR Extreme on Moderate
    c_warning = (
        (s_vhigh & r_mod) |
        (s_high & r_heavy) |
        (s_mod & r_extreme)
    )
    nowcast[c_warning] = ALERT_WARNING

    # Level 4: Severe (Critical Emergency)
    # Heavy or Extreme rain on Very High OR Extreme rain on High
    c_severe = (
        (s_vhigh & (r_heavy | r_extreme)) |
        (s_high & r_extreme)
    )
    nowcast[c_severe] = ALERT_SEVERE

    return nowcast

