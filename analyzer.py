"""
Water Quality Analysis Engine
Performs comprehensive multi-parameter evaluations against WHO and EPA drinking water standards.
Parameters: pH, TDS, Turbidity, Hardness, Chlorine, Temperature.
Outputs:
- Overall Status: 'Safe', 'Unsafe', or 'Needs Further Testing'
- Composite WQI Score (0 - 100)
- Parameter-by-parameter evaluation (Pass, Warning, Fail)
- Remediation recommendations
"""

DEFAULT_REFERENCE_LIMITS = {
    "ph": {
        "display_name": "pH Level",
        "unit": "pH",
        "min_safe": 6.5,
        "max_safe": 8.5,
        "ideal": 7.0,
        "description": "Safe acidity range for potable and domestic use."
    },
    "tds": {
        "display_name": "Total Dissolved Solids",
        "unit": "ppm",
        "min_safe": 50.0,
        "max_safe": 500.0,
        "warning_threshold": 1000.0,
        "ideal": 150.0,
        "description": "Combined mineral and dissolved organic matter content."
    },
    "turbidity": {
        "display_name": "Turbidity",
        "unit": "NTU",
        "min_safe": 0.0,
        "max_safe": 5.0,
        "ideal": 0.5,
        "description": "Cloudiness caused by suspended particulates and sediments."
    },
    "hardness": {
        "display_name": "Total Hardness",
        "unit": "mg/L as CaCO3",
        "min_safe": 0.0,
        "max_safe": 200.0,
        "warning_threshold": 300.0,
        "ideal": 100.0,
        "description": "Concentration of dissolved calcium and magnesium ions."
    },
    "chlorine": {
        "display_name": "Free Residual Chlorine",
        "unit": "ppm (mg/L)",
        "min_safe": 0.2,
        "max_safe": 2.0,
        "toxic_threshold": 4.0,
        "ideal": 0.5,
        "description": "Active disinfectant residual preventing bacterial regrowth."
    },
    "temperature": {
        "display_name": "Temperature",
        "unit": "°C",
        "min_safe": 12.0,
        "max_safe": 25.0,
        "ideal": 20.0,
        "description": "Thermal condition affecting gas solubility and bacterial kinetics."
    }
}


def analyze_water_sample(params: dict, custom_limits: dict = None) -> dict:
    """
    Evaluates 6 parameters: ph, tds, turbidity, hardness, chlorine, temperature.
    Returns complete analysis summary, status, WQI, and remediation recommendations.
    """
    limits = custom_limits or DEFAULT_REFERENCE_LIMITS

    ph = float(params.get("ph", 7.0))
    tds = float(params.get("tds", 250.0))
    turbidity = float(params.get("turbidity", 1.0))
    hardness = float(params.get("hardness", 120.0))
    chlorine = float(params.get("chlorine", 0.5))
    temperature = float(params.get("temperature", 21.0))

    evaluations = {}
    recommendations = []
    fail_count = 0
    warning_count = 0

    # 1. Evaluate pH
    ph_lim = limits.get("ph", DEFAULT_REFERENCE_LIMITS["ph"])
    min_ph = ph_lim.get("min_safe", 6.5)
    max_ph = ph_lim.get("max_safe", 8.5)

    if min_ph <= ph <= max_ph:
        evaluations["ph"] = {
            "status": "PASS",
            "value": ph,
            "unit": "pH",
            "acceptable_range": f"{min_ph} - {max_ph}",
            "finding": "Optimal neutral balance. Water is safe and non-corrosive."
        }
    elif 6.0 <= ph < min_ph or max_ph < ph <= 9.0:
        warning_count += 1
        evaluations["ph"] = {
            "status": "WARNING",
            "value": ph,
            "unit": "pH",
            "acceptable_range": f"{min_ph} - {max_ph}",
            "finding": f"Borderline {'mildly acidic' if ph < min_ph else 'mildly alkaline'} pH."
        }
        if ph < min_ph:
            recommendations.append("pH is slightly acidic: may leach metals from older plumbing. Consider a neutralizing calcite filter.")
        else:
            recommendations.append("pH is slightly alkaline: may cause light mineral scaling on fixtures.")
    else:
        fail_count += 1
        evaluations["ph"] = {
            "status": "FAIL",
            "value": ph,
            "unit": "pH",
            "acceptable_range": f"{min_ph} - {max_ph}",
            "finding": f"Severe pH violation ({'Extremely acidic' if ph < 6.0 else 'Extremely alkaline'}). Unfit for consumption."
        }
        recommendations.append("Critical pH hazard! Immediately cease drinking. Install dedicated chemical neutralization or acid-correction treatment.")

    # 2. Evaluate TDS
    tds_lim = limits.get("tds", DEFAULT_REFERENCE_LIMITS["tds"])
    max_tds = tds_lim.get("max_safe", 500.0)
    warn_tds = tds_lim.get("warning_threshold", 1000.0)

    if tds <= max_tds:
        evaluations["tds"] = {
            "status": "PASS",
            "value": tds,
            "unit": "ppm",
            "acceptable_range": f"≤ {max_tds}",
            "finding": "Excellent mineral balance. Pleasant taste and safe for consumption."
        }
    elif tds <= warn_tds:
        warning_count += 1
        evaluations["tds"] = {
            "status": "WARNING",
            "value": tds,
            "unit": "ppm",
            "acceptable_range": f"≤ {max_tds}",
            "finding": f"Elevated dissolved minerals ({tds} ppm). Acceptable for short term, but high mineral load."
        }
        recommendations.append("TDS is moderately elevated. A reverse osmosis (RO) membrane system or activated carbon filter is recommended.")
    else:
        fail_count += 1
        evaluations["tds"] = {
            "status": "FAIL",
            "value": tds,
            "unit": "ppm",
            "acceptable_range": f"≤ {max_tds}",
            "finding": f"Severe mineral load ({tds} ppm > {warn_tds} ppm). Risk of gastrointestinal irritation and severe pipe encrustation."
        }
        recommendations.append("Unsafe TDS level: high inorganic salt content. Water must undergo multi-stage Reverse Osmosis (RO) filtration before drinking.")

    # 3. Evaluate Turbidity
    turb_lim = limits.get("turbidity", DEFAULT_REFERENCE_LIMITS["turbidity"])
    max_turb = turb_lim.get("max_safe", 5.0)

    if turbidity <= 1.0:
        evaluations["turbidity"] = {
            "status": "PASS",
            "value": turbidity,
            "unit": "NTU",
            "acceptable_range": f"≤ {max_turb} (Ideal < 1.0)",
            "finding": "Crystal clear water with virtually zero suspended particles."
        }
    elif turbidity <= max_turb:
        evaluations["turbidity"] = {
            "status": "PASS",
            "value": turbidity,
            "unit": "NTU",
            "acceptable_range": f"≤ {max_turb}",
            "finding": "Within permissible EPA drinking limit, though slight particulate matter is detectable."
        }
    elif turbidity <= 10.0:
        warning_count += 1
        evaluations["turbidity"] = {
            "status": "WARNING",
            "value": turbidity,
            "unit": "NTU",
            "acceptable_range": f"≤ {max_turb}",
            "finding": f"Elevated cloudiness ({turbidity} NTU). Suspended particulate matter may shield microorganisms from disinfection."
        }
        recommendations.append("Elevated turbidity detected: Install sediment/particulate depth filters (5 micron) and inspect source for soil runoff.")
    else:
        fail_count += 1
        evaluations["turbidity"] = {
            "status": "FAIL",
            "value": turbidity,
            "unit": "NTU",
            "acceptable_range": f"≤ {max_turb}",
            "finding": f"Severe turbidity ({turbidity} NTU). High density of suspended sediment; high microbiological contamination hazard."
        }
        recommendations.append("Critical cloudiness! Water must undergo flocculation, settling, and micro-filtration. Do not drink untreated.")

    # 4. Evaluate Hardness
    hard_lim = limits.get("hardness", DEFAULT_REFERENCE_LIMITS["hardness"])
    max_hard = hard_lim.get("max_safe", 200.0)
    warn_hard = hard_lim.get("warning_threshold", 300.0)

    if hardness <= max_hard:
        evaluations["hardness"] = {
            "status": "PASS",
            "value": hardness,
            "unit": "mg/L CaCO3",
            "acceptable_range": f"≤ {max_hard}",
            "finding": "Soft to moderately soft water. Non-scaling and healthy."
        }
    elif hardness <= warn_hard:
        warning_count += 1
        evaluations["hardness"] = {
            "status": "WARNING",
            "value": hardness,
            "unit": "mg/L CaCO3",
            "acceptable_range": f"≤ {max_hard}",
            "finding": f"Hard water ({hardness} mg/L). May cause soap scum and mineral buildup on appliances and water heaters."
        }
        recommendations.append("Water is hard: Consider installing an ion-exchange water softener to prevent plumbing scale and appliance wear.")
    else:
        fail_count += 1
        evaluations["hardness"] = {
            "status": "FAIL",
            "value": hardness,
            "unit": "mg/L CaCO3",
            "acceptable_range": f"≤ {max_hard}",
            "finding": f"Extremely hard water ({hardness} mg/L). Severe mineral deposits, harsh on skin and digestive tract."
        }
        recommendations.append("Very hard water: Install a whole-house ion-exchange water softener and membrane filtration.")

    # 5. Evaluate Chlorine
    chlor_lim = limits.get("chlorine", DEFAULT_REFERENCE_LIMITS["chlorine"])
    min_chlor = chlor_lim.get("min_safe", 0.2)
    max_chlor = chlor_lim.get("max_safe", 2.0)
    toxic_chlor = chlor_lim.get("toxic_threshold", 4.0)

    water_source = params.get("water_source", "").lower()
    is_groundwater_or_purified = any(term in water_source for term in ["well", "borewell", "ground", "ro", "purified", "rain"])

    if min_chlor <= chlorine <= max_chlor:
        evaluations["chlorine"] = {
            "status": "PASS",
            "value": chlorine,
            "unit": "ppm",
            "acceptable_range": f"{min_chlor} - {max_chlor}",
            "finding": "Optimal residual disinfectant level. Pathogens and bacteria are suppressed."
        }
    elif chlorine < min_chlor:
        if is_groundwater_or_purified and chlorine == 0.0:
            # Groundwater or RO commonly has 0 chlorine, but check for microbial risk
            evaluations["chlorine"] = {
                "status": "PASS",
                "value": chlorine,
                "unit": "ppm",
                "acceptable_range": f"{min_chlor} - {max_chlor} (or 0 for unchlorinated raw well)",
                "finding": "Zero chlorine residual (characteristic of raw groundwater or purified RO water). Ensure microbiological testing is clean."
            }
        else:
            warning_count += 1
            evaluations["chlorine"] = {
                "status": "WARNING",
                "value": chlorine,
                "unit": "ppm",
                "acceptable_range": f"{min_chlor} - {max_chlor}",
                "finding": f"Chlorine residual is low or absent ({chlorine} ppm < {min_chlor} ppm). Potential vulnerability to bacterial re-growth in storage/pipes."
            }
            recommendations.append("Low/No disinfection residual in treated water. Disinfect via UV sterilizer, boiling, or slight sodium hypochlorite dosing.")
    elif chlorine <= toxic_chlor:
        warning_count += 1
        evaluations["chlorine"] = {
            "status": "WARNING",
            "value": chlorine,
            "unit": "ppm",
            "acceptable_range": f"{min_chlor} - {max_chlor}",
            "finding": f"High chlorine residual ({chlorine} ppm). Noticeable chlorine/bleach odor and taste."
        }
        recommendations.append("Chlorine is elevated: Install an activated carbon filter or aerate water to dissipate excess residual chlorine.")
    else:
        fail_count += 1
        evaluations["chlorine"] = {
            "status": "FAIL",
            "value": chlorine,
            "unit": "ppm",
            "acceptable_range": f"{min_chlor} - {max_chlor}",
            "finding": f"Excessive chlorine ({chlorine} ppm > {toxic_chlor} ppm). Chemical hazard: causes eye/skin/mucous irritation and trihalomethane risk."
        }
        recommendations.append("Toxic chlorine concentration! Do not ingest. Purge storage tanks and filter through granular activated carbon (GAC).")

    # 6. Evaluate Temperature
    temp_lim = limits.get("temperature", DEFAULT_REFERENCE_LIMITS["temperature"])
    max_temp = temp_lim.get("max_safe", 25.0)

    if temperature <= max_temp:
        evaluations["temperature"] = {
            "status": "PASS",
            "value": temperature,
            "unit": "°C",
            "acceptable_range": f"≤ {max_temp}°C",
            "finding": "Cool and thermally stable water temperature."
        }
    elif temperature <= 32.0:
        warning_count += 1
        evaluations["temperature"] = {
            "status": "WARNING",
            "value": temperature,
            "unit": "°C",
            "acceptable_range": f"≤ {max_temp}°C",
            "finding": f"Elevated temperature ({temperature}°C). Warm water promotes bacterial colonization and decreases dissolved gas retention."
        }
        recommendations.append("Water is warm. Ensure storage tanks are shaded or insulated to inhibit bacterial propagation.")
    else:
        fail_count += 1
        evaluations["temperature"] = {
            "status": "FAIL",
            "value": temperature,
            "unit": "°C",
            "acceptable_range": f"≤ {max_temp}°C",
            "finding": f"High temperature ({temperature}°C). Unsuitable for direct potable storage without cooling."
        }

    # 7. Compute Composite Water Quality Index (0 - 100)
    # Sub-indices
    q_ph = 100.0 - min(100.0, abs(ph - 7.0) * 35.0)
    q_tds = max(0.0, 100.0 - (tds / 1000.0) * 100.0)
    q_turb = max(0.0, 100.0 - (turbidity / 10.0) * 100.0)
    q_hard = max(0.0, 100.0 - (hardness / 350.0) * 100.0)
    
    if chlorine < 0.2 and not is_groundwater_or_purified:
        q_chlor = 65.0
    elif chlorine <= 2.0:
        q_chlor = 100.0 - abs(chlorine - 0.6) * 15.0
    else:
        q_chlor = max(0.0, 100.0 - (chlorine - 2.0) * 30.0)
        
    q_temp = max(0.0, 100.0 - max(0.0, temperature - 20.0) * 4.0)

    # Weights: pH (0.24), Turbidity (0.22), TDS (0.20), Hardness (0.14), Chlorine (0.12), Temp (0.08)
    wqi_score = round(
        (q_ph * 0.24) +
        (q_turb * 0.22) +
        (q_tds * 0.20) +
        (q_hard * 0.14) +
        (q_chlor * 0.12) +
        (q_temp * 0.08),
        1
    )
    wqi_score = max(5.0, min(100.0, wqi_score))

    # 8. Determine Overall Status: Safe, Unsafe, or Needs Further Testing
    if fail_count > 0 or wqi_score < 55.0:
        overall_status = "Unsafe"
        badge_color = "#dc2626"
        status_summary = "Water failed critical health or chemical thresholds. NOT SAFE for direct drinking without corrective treatment."
    elif warning_count >= 2 or (55.0 <= wqi_score < 78.0) or (warning_count == 1 and turbidity > 3.0):
        overall_status = "Needs Further Testing"
        badge_color = "#d97706"
        status_summary = "Water exhibits borderline chemical parameters. Microbiological or laboratory follow-up testing is recommended before consumption."
        recommendations.append("Conduct comprehensive laboratory culture (E. Coli / Coliforms) or multi-barrier filtration before drinking.")
    else:
        overall_status = "Safe"
        badge_color = "#16a34a"
        status_summary = "All examined physicochemical parameters conform strictly to safe drinking water guidelines."
        if not recommendations:
            recommendations.append("Water is within ideal potable limits. Routine periodic monitoring advised.")

    return {
        "overall_status": overall_status,
        "badge_color": badge_color,
        "wqi_score": wqi_score,
        "status_summary": status_summary,
        "evaluations": evaluations,
        "recommendations": recommendations,
        "fail_count": fail_count,
        "warning_count": warning_count,
        "input_params": {
            "ph": ph,
            "tds": tds,
            "turbidity": turbidity,
            "hardness": hardness,
            "chlorine": chlorine,
            "temperature": temperature
        }
    }
