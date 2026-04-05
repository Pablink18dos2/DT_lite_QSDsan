# Docker Build & Run

Build and run the BSM1 simulator Docker container.

## Instructions

1. **Build the image**:
   ```bash
   docker compose build
   ```

2. **Start the container**:
   ```bash
   docker compose up -d
   ```

3. **Verify health**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Run a simulation** (optional, as requested by user):
   ```bash
   curl -X POST http://localhost:8000/simulate/steady-state
   ```

5. **Check logs** if there are issues:
   ```bash
   docker compose logs -f bsm1-simulator
   ```

6. **Stop**:
   ```bash
   docker compose down
   ```

Report the health check result and any errors encountered.

$ARGUMENTS
