# Server Restart Rules

## When to apply
Every time the user asks to restart the server, test the web, or start the server for manual testing.

## Restart procedure (always follow this order)

### 1. Kill all existing Python processes
```bash
taskkill /F /IM python.exe /T 2>/dev/null
```
If processes survive (port still LISTENING after kill), identify PIDs with:
```bash
netstat -ano | grep ":800" | grep LISTEN
```
Then kill each PID individually via cmd (Git Bash taskkill may fail silently):
```bash
cmd /c "taskkill /F /PID <pid1> & taskkill /F /PID <pid2> ..."
```

### 2. Clear pyc cache for any modified files
```bash
find app/__pycache__ -name "<modified_module>*" -delete
```

### 3. Check port availability
```bash
netstat -ano | grep ":800" | grep LISTEN
```
- If port 8000 is free: start on 8000.
- If port 8000 still occupied after kill attempts: start on **8001** instead.

### 4. Start uvicorn WITHOUT --reload
`--reload` can serve stale pyc caches. Always start clean:
```bash
"C:\Users\pamongo\AppData\Local\Programs\Python\Python313\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port <PORT>
```
Run in background and wait ~5 seconds before verifying.

### 5. Verify with health check
```bash
curl -s http://127.0.0.1:<PORT>/health
```
Expected: `{"status":"ok","qsdsan_version":"1.3.0","python_version":"3.13.0"}`

### 6. Give the user the URL
Always tell the user the exact URL: `http://127.0.0.1:<PORT>`
Remind them to do `Ctrl+Shift+R` in the browser if they had a previous session open.

## Notes
- Python executable: `C:\Users\pamongo\AppData\Local\Programs\Python\Python313\python.exe`
- Default port: 8000. Fallback: 8001.
- Never use `--reload` for manual testing (stale cache risk).
- Multiple uvicorn processes can accumulate from previous sessions; always kill all before restarting.
