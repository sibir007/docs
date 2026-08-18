# AGENTS.md

## Project

- This is a Python 3.11+ `aiohttp` server for serving downloaded static documentation from `sites/`.
- `local_docs` is the only application implementation and entrypoint. It routes each request by the HTTP host name to `sites/<host>` and exposes the generated site list at `/docs_local`.
- `sites/` is intentionally ignored by Git and contains local documentation data, not source code.

## Run

- Install/sync dependencies with `uv sync`.
- Run the current server with `uv run local-docs` or `uv run python -m local_docs`.
- `PORT` sets the preferred port (default `8080`); if it is occupied, the server selects another free port.
- Startup and shutdown modify `/etc/hosts` (or the Windows hosts file), so run with administrator privileges when required and stop cleanly to remove the managed block.
- The server binds to `127.0.0.1`; hostnames are generated from the directory names under `sites/`.

## Verification

- No test suite, CI workflow, or lint/typecheck configuration is present.
- After Python changes, run `uv run python -m compileall -q .` as the available syntax check.
- Do not treat generated site files, `__pycache__`, `.pytest_cache`, or `.mypy_cache` as source changes.

## Implementation Notes

- `src/local_docs/site_registry.py` discovers non-hidden site directories; names beginning with `_` are excluded.
- `src/local_docs/hosts_manager.py` owns a marked block in the system hosts file; preserve its start/end markers when changing host management.
- `src/local_docs/index_renderer.py` renders `src/local_docs/templates/index.html`; update the template rather than duplicating page markup in the server.
- Static-file handling in `src/local_docs/static_files.py` resolves paths and rejects traversal outside the selected site directory; preserve this boundary when modifying routing.
