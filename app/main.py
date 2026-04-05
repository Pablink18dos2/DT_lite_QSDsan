"""FastAPI application for BSM1 simulator API."""

import asyncio
import pathlib
import sys

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .config import (
    BSM1_DEFAULTS,
    IWA_DYN_REF,
    IWA_LIMITS,
    IWA_SS_REF,
    IWA_SS_SRT_SPEC,
    IWA_SS_SRT_TRAD,
    IWA_SS_TSS,
    TOLERANCE,
    settings,
)
from .engine import pre_check, run_steady_state_simulation, validate_components
from .excel_parser import parse_bsm1_excel
from .excel_template import generate_bsm1_template
from .models import (
    HealthResponse,
    IWAReferenceResponse,
    PlantParameters,
    PreSimulationResponse,
    SimulationRequest,
    SimulationResult,
    ValidateRequest,
)

app = FastAPI(
    title='BSM1 Simulator API',
    description=(
        'Digital Twin lite for Wastewater Treatment Plants. '
        'Simulates the IWA BSM1 benchmark using QSDsan/EXPOsan '
        'and validates against reference values (Jeppsson, 2008).'
    ),
    version='1.0.0',
)

# Serve static files (web UI)
_static_dir = pathlib.Path(__file__).parent / 'static'
app.mount('/static', StaticFiles(directory=str(_static_dir)), name='static')

# In-memory storage for latest result.
# NOTE: no es thread-safe. Aceptable para despliegue mono-usuario.
# Para multi-usuario, reemplazar por almacenamiento por sesion o base de datos.
_latest_result: SimulationResult | None = None


@app.get('/', include_in_schema=False)
async def root():
    """Serve the web UI."""
    return FileResponse(
        str(_static_dir / 'index.html'),
        headers={'Cache-Control': 'no-cache, no-store, must-revalidate'},
    )


@app.get('/health', response_model=HealthResponse)
async def health_check():
    """Check API health and QSDsan availability."""
    try:
        import qsdsan as qs

        qsdsan_version = qs.__version__
    except ImportError:
        qsdsan_version = 'NOT INSTALLED'

    return HealthResponse(
        status='ok',
        qsdsan_version=qsdsan_version,
        python_version=sys.version.split()[0],
    )


@app.get('/reference/iwa', response_model=IWAReferenceResponse)
async def get_iwa_reference():
    """Return all IWA BSM1 reference values."""
    return IWAReferenceResponse(
        steady_state=IWA_SS_REF,
        steady_state_tss=IWA_SS_TSS,
        steady_state_srt_trad=IWA_SS_SRT_TRAD,
        steady_state_srt_spec=IWA_SS_SRT_SPEC,
        dynamic=IWA_DYN_REF,
        limits=IWA_LIMITS,
        tolerance=TOLERANCE,
    )


@app.get('/defaults/plant')
async def get_plant_defaults():
    """Return BSM1 default plant parameters with ranges and labels."""
    return BSM1_DEFAULTS


@app.post('/simulate/pre-check', response_model=PreSimulationResponse)
async def simulate_pre_check(plant: PlantParameters | None = None):
    """Validate plant parameters and return calculated values before simulation.

    Returns calculated WAS (if SRT mode), estimated SRT, and warnings.
    """
    if plant is None:
        plant = PlantParameters()
    return pre_check(plant)


@app.post('/simulate/steady-state', response_model=SimulationResult)
async def simulate_steady_state(request: SimulationRequest | None = None):
    """Run a BSM1 steady-state simulation.

    Uses default parameters if no body is provided.
    Simulation takes approximately 2-5 seconds.
    """
    global _latest_result

    if request is None:
        request = SimulationRequest()

    try:
        result = await asyncio.to_thread(
            run_steady_state_simulation,
            t_days=request.t_days,
            method=request.method,
            tolerance=request.tolerance,
            plant=request.plant,
        )
    except (RuntimeError, Exception) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    _latest_result = result
    return result


@app.get('/results/latest', response_model=SimulationResult)
async def get_latest_results():
    """Return the most recent simulation result."""
    if _latest_result is None:
        raise HTTPException(
            status_code=404,
            detail='No hay resultados. Ejecute POST /simulate/steady-state primero.',
        )
    return _latest_result


@app.post('/validate', response_model=list)
async def validate_custom_values(request: ValidateRequest):
    """Validate custom component values against IWA reference.

    Provide a dictionary of component IDs and their values.
    Returns validation results for each recognized component.
    """
    if not request.values:
        raise HTTPException(status_code=400, detail='No se proporcionaron valores.')

    results = validate_components(request.values, request.tolerance)
    if not results:
        raise HTTPException(
            status_code=400,
            detail='Ningun ID de componente ASM1 reconocido en los valores proporcionados.',
        )
    return results


@app.get('/export/excel-template', tags=['Excel'])
async def export_excel_template():
    """Download the BSM1 parameter template (.xlsx) with default values and SCADA tag columns."""
    content = await asyncio.to_thread(generate_bsm1_template)
    return Response(
        content=content,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename="BSM1_plantilla.xlsx"'},
    )


@app.post('/simulate/from-excel', response_model=SimulationResult, tags=['Simulation'])
async def simulate_from_excel(file: UploadFile = File(...)):  # noqa: B008
    """Upload a filled BSM1 Excel template (.xlsx) and run a steady-state simulation.

    Parses plant parameters and SCADA/lab tags from the file.
    Tags are echoed in aggregates as '_tag_<param_id>' for traceability.
    """
    global _latest_result

    content = await file.read()
    try:
        request, tags, excel_warnings = await asyncio.to_thread(parse_bsm1_excel, content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f'Error al parsear Excel: {e}') from e

    try:
        result = await asyncio.to_thread(
            run_steady_state_simulation,
            t_days=request.t_days,
            method=request.method,
            tolerance=request.tolerance,
            plant=request.plant,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    for param_id, tag_str in tags.items():
        result.aggregates[f'_tag_{param_id}'] = tag_str

    if excel_warnings:
        result.aggregates['_warnings_excel'] = '; '.join(excel_warnings)

    _latest_result = result
    return result


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
