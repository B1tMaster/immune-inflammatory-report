"""
Constants and reference ranges for immune inflammatory indices.
"""

from typing import Dict, List, Tuple

# Field name mappings for PDF parsing
FIELD_MAPPINGS = {
    "neutrophils": [
        "neutrophils", "neutrophil", "segs", "segmented neutrophils", 
        "pmn", "polymorphonuclear", "poly"
    ],
    "lymphocytes": [
        "lymphocytes", "lymphocyte", "lymphs", "lympho"
    ],
    "platelets": [
        "platelets", "platelet", "plt", "thrombocytes"
    ],
    "monocytes": [
        "monocytes", "monocyte", "monos", "mono"
    ],
}

# Unit conversion factors to cells/µL
UNIT_CONVERSIONS = {
    "x10³/L": 1.0,
    "x10^3/L": 1.0,
    "K/µL": 1000.0,
    "K/uL": 1000.0,
    "cells/µL": 1.0,
    "cells/uL": 1.0,
    "/µL": 1.0,
    "/uL": 1.0,
    "10³/L": 1.0,
    "10^3/L": 1.0,
}

# Physiological ranges for validation (cells/µL)
PHYSIOLOGICAL_RANGES = {
    "neutrophils": (1000, 25000),
    "lymphocytes": (500, 8000),
    "platelets": (100000, 1000000),
    "monocytes": (100, 2000),
}

# Reference ranges for immune inflammatory indices

# Systemic Immune-Inflammation Index (SII)
SII_RANGES = {
    "normal": (0, 500),
    "mild": (500, 800),
    "moderate": (800, 1200),
    "high": (1200, 2000),
    "very_high": (2000, float('inf'))
}

# Neutrophil-to-Lymphocyte Ratio (NLR)
NLR_RANGES = {
    "normal": (0, 2.0),
    "mild": (2.0, 3.0),
    "moderate": (3.0, 5.0),
    "high": (5.0, 8.0),
    "very_high": (8.0, float('inf'))
}

# Platelet-to-Lymphocyte Ratio (PLR)
PLR_RANGES = {
    "normal": (0, 150),
    "mild": (150, 200),
    "moderate": (200, 300),
    "high": (300, float('inf'))
}

# Systemic Inflammatory Response Index (SIRI)
SIRI_RANGES = {
    "normal": (0, 1.0),
    "mild": (1.0, 2.0),
    "moderate": (2.0, 3.0),
    "high": (3.0, float('inf'))
}

# Monocyte-to-Lymphocyte Ratio (MLR)
MLR_RANGES = {
    "normal": (0, 0.3),
    "mild": (0.3, 0.5),
    "moderate": (0.5, 0.8),
    "high": (0.8, float('inf'))
}

# Pan-Immune Inflammation Value (PIV)
PIV_RANGES = {
    "normal": (0, 300),
    "mild": (300, 600),
    "moderate": (600, 1200),
    "high": (1200, float('inf'))
}

# All reference ranges combined
REFERENCE_RANGES = {
    "sii": SII_RANGES,
    "nlr": NLR_RANGES,
    "plr": PLR_RANGES,
    "siri": SIRI_RANGES,
    "mlr": MLR_RANGES,
    "piv": PIV_RANGES,
}

# Clinical interpretations
INTERPRETATIONS = {
    "sii": {
        "normal": "Normal systemic immune-inflammation balance",
        "mild": "Mildly elevated systemic inflammation - monitor and consider lifestyle interventions",
        "moderate": "Moderately elevated systemic inflammation - clinical evaluation recommended",
        "high": "High systemic inflammation - medical intervention likely needed",
        "very_high": "Very high systemic inflammation - urgent medical attention recommended"
    },
    "nlr": {
        "normal": "Normal neutrophil-lymphocyte balance",
        "mild": "Mild immune activation - may indicate early inflammatory response",
        "moderate": "Moderate immune activation - clinical correlation recommended",
        "high": "High immune activation - significant inflammatory burden",
        "very_high": "Very high immune activation - critical inflammatory state"
    },
    "plr": {
        "normal": "Normal platelet-lymphocyte balance",
        "mild": "Mildly elevated thrombotic/inflammatory risk",
        "moderate": "Moderately elevated thrombotic/inflammatory risk",
        "high": "High thrombotic/inflammatory risk"
    },
    "siri": {
        "normal": "Normal systemic inflammatory response",
        "mild": "Mild systemic inflammatory response",
        "moderate": "Moderate systemic inflammatory response",
        "high": "High systemic inflammatory response"
    },
    "mlr": {
        "normal": "Normal monocyte activation",
        "mild": "Mild monocyte activation",
        "moderate": "Moderate monocyte activation indicating tissue inflammation",
        "high": "High monocyte activation indicating significant tissue inflammation"
    },
    "piv": {
        "normal": "Normal pan-immune inflammation status",
        "mild": "Mildly elevated pan-immune inflammation",
        "moderate": "Moderately elevated pan-immune inflammation",
        "high": "High pan-immune inflammation across multiple cell types"
    }
}

# PDF parsing patterns
PDF_SECTION_HEADERS = [
    "FBC", "CBC", "HAEMATOLOGY", "HEMATOLOGY", "BLOOD COUNT", 
    "FULL BLOOD COUNT", "COMPLETE BLOOD COUNT"
]

# Common laboratory names and formats
SUPPORTED_LAB_FORMATS = [
    "Innoquest Diagnostics",
    "LabCorp",
    "Quest Diagnostics", 
    "Generic"
]