"""Pydantic models for BSM1 simulator API request/response schemas."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class PlantParameters(BaseModel):
    """User-configurable plant parameters for BSM1 simulation."""

    # Influent (aggregated)
    Q: float = Field(default=18446, ge=1000, le=200000, description='Influent flow (m3/d)')
    COD_total: float = Field(default=381.19, ge=50, le=2000, description='Total COD (mg/L)')
    TKN: float = Field(default=51.35, ge=10, le=300, description='TKN influent (mg N/L)')
    TSS_inf: float = Field(default=211.27, ge=20, le=1500, description='TSS influent (mg/L)')

    # Geometry
    V_anoxic: float = Field(
        default=1000, ge=100, le=20000, description='Anoxic reactor volume (m3)'
    )
    V_aerobic: float = Field(
        default=1333, ge=100, le=20000, description='Aerobic reactor volume (m3)'
    )
    Clarifier_area: float = Field(default=1500, ge=100, le=10000, description='Clarifier area (m2)')
    Clarifier_height: float = Field(default=4, ge=1, le=10, description='Clarifier height (m)')

    # Operation
    Q_RAS: float = Field(default=18446, ge=0, le=200000, description='RAS flow (m3/d)')
    sludge_control: Literal['WAS', 'SRT'] = Field(default='WAS', description='Sludge control mode')
    Q_WAS: float | None = Field(default=385, ge=10, le=5000, description='WAS flow (m3/d)')
    SRT_target: float | None = Field(default=None, ge=1, le=40, description='Target SRT (days)')
    Temperature: float = Field(default=20, ge=5, le=35, description='Temperature (C)')
    # Aeration control: 'DO' uses PI controller with DO setpoint; 'KLa' applies KLa directly
    aeration_control: Literal['DO', 'KLa'] = Field(
        default='DO', description='Aeration control mode'
    )
    DO_O1: float = Field(
        default=1.72, ge=0.0, le=7.0, description='DO setpoint reactor O1 (mg O2/L)'
    )
    DO_O2: float = Field(
        default=2.43, ge=0.0, le=7.0, description='DO setpoint reactor O2 (mg O2/L)'
    )
    DO_O3: float = Field(
        default=0.49, ge=0.0, le=7.0, description='DO setpoint reactor O3 (mg O2/L)'
    )
    KLa_O1: float | None = Field(
        default=None, ge=0.0, le=1000.0, description='KLa reactor O1 (1/d); 0=no aeration'
    )
    KLa_O2: float | None = Field(
        default=None, ge=0.0, le=1000.0, description='KLa reactor O2 (1/d); 0=no aeration'
    )
    KLa_O3: float | None = Field(
        default=None, ge=0.0, le=1000.0, description='KLa reactor O3 (1/d); 0=no aeration'
    )
    DOsat: float = Field(default=8.0, ge=6.0, le=14.0, description='DO saturation (mg O2/L)')
    Q_intr: float = Field(
        default=55338, ge=0, le=300000, description='Internal recirculation (m3/d)'
    )

    @model_validator(mode='after')
    def validate_modes(self):
        if self.sludge_control == 'SRT' and self.SRT_target is None:
            raise ValueError('SRT_target is required when sludge_control is SRT')
        if self.sludge_control == 'WAS' and self.Q_WAS is None:
            raise ValueError('Q_WAS is required when sludge_control is WAS')
        if self.aeration_control == 'KLa':
            missing = [
                f
                for f, v in [
                    ('KLa_O1', self.KLa_O1),
                    ('KLa_O2', self.KLa_O2),
                    ('KLa_O3', self.KLa_O3),
                ]
                if v is None
            ]
            if missing:
                raise ValueError(f'{", ".join(missing)} required when aeration_control is KLa')
        return self


class PreSimulationResponse(BaseModel):
    """Response from pre-check endpoint before running simulation."""

    Q_WAS_calculated: float | None = None
    SRT_estimated: float | None = None
    KLa_O1: float | None = None
    KLa_O2: float | None = None
    KLa_O3: float | None = None
    warnings: list[str] = []
    valid: bool = True


class SimulationRequest(BaseModel):
    """Parameters for a steady-state BSM1 simulation."""

    t_days: int = Field(default=200, ge=50, le=1000, description='Simulation time in days')
    method: str = Field(default='BDF', pattern='^(BDF|Radau)$', description='ODE solver method')
    tolerance: float = Field(
        default=0.05, gt=0, le=0.5, description='Validation tolerance (fraction)'
    )
    plant: PlantParameters = Field(default_factory=PlantParameters)


class ComponentResult(BaseModel):
    """Validation result for a single ASM1 component."""

    component: str
    obtained: float
    reference: float
    error_pct: float
    passed: bool
    unit: str


class SimulationResult(BaseModel):
    """Complete simulation result with validation."""

    timestamp: str
    method_used: str
    compute_time_seconds: float
    components: list[ComponentResult]
    pass_count: int
    total_count: int
    all_passed: bool
    aggregates: dict[str, float | str | None]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    qsdsan_version: str
    python_version: str


class IWAReferenceResponse(BaseModel):
    """IWA reference values for BSM1."""

    steady_state: dict[str, float]
    steady_state_tss: float
    steady_state_srt_trad: float
    steady_state_srt_spec: float
    dynamic: dict[str, float]
    limits: dict[str, float]
    tolerance: float


class ValidateRequest(BaseModel):
    """Custom values to validate against IWA reference."""

    values: dict[str, float] = Field(
        description='Component values to validate, e.g. {"S_NH": 1.8, "S_NO": 10.5}'
    )
    tolerance: float = Field(default=0.05, gt=0, le=0.5)
