# Docker Conventions

## Image
- Base: `python:3.13-slim`
- Single-stage build (NumPy/SciPy dominate size, multi-stage doesn't help)
- Always run `app/patch.py` after `pip install` to fix pkg_resources

## Compose
- Service name: `bsm1-simulator`, container: `bsm1-api`
- Port: 8000 (configurable via BSM1_PORT env var)
- Memory limit: 2GB (SciPy ODE solver can be hungry)
- Volume `./results:/app/results` for persistent output

## API Framework
- FastAPI with uvicorn
- Pydantic v2 for all schemas
- Settings via `pydantic-settings` with `BSM1_` env prefix
- Swagger UI at `/docs`

## Thread Safety
- QSDsan uses global state (flowsheet, thermo)
- All simulation calls go through `threading.Lock` in `app/engine.py`
- One simulation at a time (acceptable for 2-5 second runs)

## Testing
- `pytest` with `@pytest.mark.slow` for simulation tests
- `python -m pytest tests/ -m "not slow"` for fast tests
- `python -m pytest tests/` for full suite including simulation
