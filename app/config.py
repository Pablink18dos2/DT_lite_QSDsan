"""IWA reference values and application settings for BSM1 simulator."""

from pydantic_settings import BaseSettings

# ============================================================================
# IWA REFERENCE VALUES (Dr. Ulf Jeppsson, Lund University, 2008)
# ============================================================================

IWA_SS_REF = {
    'S_I': 30.0,  # mg COD/L
    'S_S': 0.889,  # mg COD/L
    'X_I': 4.392,  # mg COD/L
    'X_S': 0.188,  # mg COD/L
    'X_BH': 9.782,  # mg COD/L
    'X_BA': 0.573,  # mg COD/L
    'X_P': 1.728,  # mg COD/L
    'S_O': 0.491,  # mg O2/L
    'S_NO': 10.415,  # mg N/L
    'S_NH': 1.733,  # mg N/L
    'S_ND': 0.688,  # mg N/L
    'X_ND': 0.013,  # mg N/L
    'S_ALK': 4.126,  # mol HCO3/m3
}

IWA_SS_TSS = 12.497  # mg SS/L
IWA_SS_SRT_TRAD = 7.32  # days
IWA_SS_SRT_SPEC = 9.14  # days

IWA_DYN_REF = {
    'S_NH': 4.759,  # mg N/L   (violates 4 mg/L limit - expected in open-loop)
    'S_NO': 8.824,  # mg N/L
    'TSS': 12.992,  # mg SS/L
    'TN': 15.569,  # mg N/L
    'COD': 48.296,  # mg COD/L
    'BOD5': 2.775,  # mg/L
    'Q_eff': 18061.3,  # m3/d
}

IWA_LIMITS = {
    'COD': 100,  # mg COD/L
    'BOD5': 10,  # mg/L
    'TN': 18,  # mg N/L
    'S_NH': 4,  # mg N/L
    'TSS': 30,  # mg SS/L
}

TOLERANCE = 0.05  # 5%

# ============================================================================
# BSM1 INFLUENT DECOMPOSITION CONSTANTS
# ============================================================================

# Default influent aggregate values (verified from BSM1 component sums)
COD_DEFAULT = 381.19  # mg/L  (S_I=30 + S_S=69.5 + X_I=51.2 + X_S=202.32 + X_BH=28.17)
TKN_DEFAULT = 51.35  # mg N/L  (S_NH=31.56 + S_ND=6.95 + X_ND=10.59 + i_XB*X_BH=2.25)
TSS_INF_DEFAULT = 211.27  # mg/L  (0.75 * (X_I + X_S + X_BH + X_BA + X_P))
SRT_DEFAULT = 9.14  # days (specific SRT from IWA reference)
WAS_DEFAULT = 385  # m3/d

# BSM1 reference DO in each aerobic reactor (from simulation at steady state)
# Used to calibrate DO -> KLa conversion via OUR back-calculation
DO_REF_O1 = 1.7174  # mg O2/L  (KLa=240, DOsat=8.0)
DO_REF_O2 = 2.4274  # mg O2/L  (KLa=240, DOsat=8.0)
DO_REF_O3 = 0.4902  # mg O2/L  (KLa=84,  DOsat=8.0)
DOSAT_DEFAULT = 8.0  # mg O2/L  (saturacion a 20C, 1 atm)

# OUR reference per reactor back-calculated: OUR = KLa_ref * (DOsat - DO_ref)
OUR_REF_O1 = 240 * (8.0 - DO_REF_O1)  # ~1508 mg O2/(L*d)
OUR_REF_O2 = 240 * (8.0 - DO_REF_O2)  # ~1337 mg O2/(L*d)
OUR_REF_O3 = 84 * (8.0 - DO_REF_O3)  # ~631 mg O2/(L*d)

# ============================================================================
# PI DO CONTROLLER PARAMETERS (BSM1 standard, Jeppsson 2008 - Lazo 2)
# ============================================================================

# Proportional-integral controller: u = Kp*e + (Kp/Ti)*integral(e)
# Variable manipulada: KLa [1/d], Variable controlada: S_O [mg O2/L]
PI_KP = 25.0  # proportional gain [1/d per mg O2/L error]
PI_TI = 0.002  # integral time [d]  (~2.88 min — fast integral, BSM1 standard)
PI_KLA_MAX = {  # actuator upper limits per reactor [1/d]
    'O1': 240.0,
    'O2': 240.0,
    'O3': 84.0,  # O3 has lower design KLa in BSM1
}
PI_KLA_MIN = 0.0  # actuator lower limit [1/d]
PI_PHASE2_DAYS = 100  # duration of PI phase [d] (run after standard SS warmup)

# BSM1 default component concentrations for decomposition ratios
BSM1_INF_COMPONENTS = {
    'S_I': 30.0,  # mg COD/L
    'S_S': 69.5,  # mg COD/L
    'X_I': 51.2,  # mg COD/L
    'X_S': 202.32,  # mg COD/L
    'X_BH': 28.17,  # mg COD/L
    'S_NH': 31.56,  # mg N/L
    'S_ND': 6.95,  # mg N/L
    'X_ND': 10.59,  # mg N/L
    'S_ALK': 84,  # mg/L (= 7 mol HCO3/m3 * 12)
}

# ============================================================================
# BSM1 DEFAULTS FOR USER-CONFIGURABLE PARAMETERS
# ============================================================================

BSM1_DEFAULTS = {
    # Influent (aggregated)
    'Q': {'value': 18446, 'unit': 'm3/d', 'min': 1000, 'max': 200000, 'label': 'Caudal influente'},
    'COD_total': {'value': 381.19, 'unit': 'mg/L', 'min': 50, 'max': 2000, 'label': 'COD total'},
    'TKN': {'value': 51.35, 'unit': 'mg N/L', 'min': 10, 'max': 300, 'label': 'TKN influente'},
    'TSS_inf': {'value': 211.27, 'unit': 'mg/L', 'min': 20, 'max': 1500, 'label': 'TSS influente'},
    # Geometry
    'V_anoxic': {
        'value': 1000,
        'unit': 'm3',
        'min': 100,
        'max': 20000,
        'label': 'Vol. reactor anoxico',
    },
    'V_aerobic': {
        'value': 1333,
        'unit': 'm3',
        'min': 100,
        'max': 20000,
        'label': 'Vol. reactor aerobico',
    },
    'Clarifier_area': {
        'value': 1500,
        'unit': 'm2',
        'min': 100,
        'max': 10000,
        'label': 'Area decantador',
    },
    'Clarifier_height': {
        'value': 4,
        'unit': 'm',
        'min': 1,
        'max': 10,
        'label': 'Altura decantador',
    },
    # Operation
    'Q_RAS': {
        'value': 18446,
        'unit': 'm3/d',
        'min': 0,
        'max': 200000,
        'label': 'Recirculacion externa (RAS)',
    },
    'Q_WAS': {'value': 385, 'unit': 'm3/d', 'min': 10, 'max': 5000, 'label': 'Purga (WAS)'},
    'SRT_target': {'value': 9.14, 'unit': 'days', 'min': 1, 'max': 40, 'label': 'SRT objetivo'},
    'Temperature': {'value': 20, 'unit': 'C', 'min': 5, 'max': 35, 'label': 'Temperatura'},
    'DO_O1': {
        'value': 1.72,
        'unit': 'mg O2/L',
        'min': 0.0,
        'max': 7.0,
        'label': 'OD reactor O1',
    },
    'DO_O2': {
        'value': 2.43,
        'unit': 'mg O2/L',
        'min': 0.0,
        'max': 7.0,
        'label': 'OD reactor O2',
    },
    'DO_O3': {
        'value': 0.49,
        'unit': 'mg O2/L',
        'min': 0.0,
        'max': 7.0,
        'label': 'OD reactor O3',
    },
    'KLa_O1': {
        'value': 240.0,
        'unit': '1/d',
        'min': 0,
        'max': 1000,
        'label': 'KLa reactor O1',
    },
    'KLa_O2': {
        'value': 240.0,
        'unit': '1/d',
        'min': 0,
        'max': 1000,
        'label': 'KLa reactor O2',
    },
    'KLa_O3': {
        'value': 84.0,
        'unit': '1/d',
        'min': 0,
        'max': 1000,
        'label': 'KLa reactor O3',
    },
    'DOsat': {
        'value': 8.0,
        'unit': 'mg O2/L',
        'min': 6.0,
        'max': 14.0,
        'label': 'OD saturacion',
    },
    'Q_intr': {
        'value': 55338,
        'unit': 'm3/d',
        'min': 0,
        'max': 300000,
        'label': 'Recirculacion interna',
    },
}

# Component units for API responses
COMPONENT_UNITS = {
    'S_I': 'mg COD/L',
    'S_S': 'mg COD/L',
    'X_I': 'mg COD/L',
    'X_S': 'mg COD/L',
    'X_BH': 'mg COD/L',
    'X_BA': 'mg COD/L',
    'X_P': 'mg COD/L',
    'S_O': 'mg O2/L',
    'S_NO': 'mg N/L',
    'S_NH': 'mg N/L',
    'S_ND': 'mg N/L',
    'X_ND': 'mg N/L',
    'S_ALK': 'mol HCO3/m3',
    'TSS': 'mg SS/L',
}


class Settings(BaseSettings):
    """Application settings, overridable via environment variables."""

    model_config = {'env_prefix': 'BSM1_'}

    t_days: int = 200
    method: str = 'BDF'
    tolerance: float = 0.05
    host: str = '0.0.0.0'
    port: int = 8000


settings = Settings()
