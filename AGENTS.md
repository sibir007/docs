# AGENTS.md

## Project

- This is a Python 3.11+ `aiohttp` server for serving downloaded static documentation from `sites/`.
- `new_server.py` is the current entrypoint: one server routes each request by the HTTP host name to `sites/<host>` and exposes the generated site list at `/docs_local`.
- `main.py` is the older alternative that starts one server per site on ports beginning at `8031`; do not assume it is equivalent to `new_server.py`.
- `sites/` is intentionally ignored by Git and contains local documentation data, not source code.

## Run

- Install/sync dependencies with `uv sync`.
- Run the current server with `uv run new_server.py`.
- `PORT` sets the preferred port (default `8080`); if it is occupied, the server selects another free port.
- Startup and shutdown modify `/etc/hosts` (or the Windows hosts file), so run with administrator privileges when required and stop cleanly to remove the managed block.
- The server binds to `0.0.0.0`, not only `localhost`; hostnames are generated from the directory names under `sites/`.

## Verification

- No test suite, CI workflow, or lint/typecheck configuration is present.
- After Python changes, run `uv run python -m compileall -q .` as the available syntax check.
- Do not treat generated site files, `__pycache__`, `.pytest_cache`, or `.mypy_cache` as source changes.

## Implementation Notes

- `lib.py` discovers non-hidden site directories; names beginning with `_` are excluded.
- `change_hosts.py` owns a marked block in the system hosts file; preserve its start/end markers when changing host management.
- `docs.py` renders `template.html` in memory and `new_server.py` serves that rendered HTML; update the template rather than duplicating page markup in the server.
- Static-file handling in `new_server.py` resolves paths and rejects traversal outside the selected site directory; preserve this boundary when modifying routing.
