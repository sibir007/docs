# local-docs

`local-docs` serves downloaded static documentation sites through one
host-based local server.

## Installation

```bash
pip install local-docs
```

For development, install the project with its development dependencies:

```bash
uv sync
```

## Usage

Put each downloaded site in its own directory under `sites/`, then run:

```bash
local-docs
```

The server listens on `127.0.0.1:8080` by default. If that port is busy, a
free port is selected automatically. The `/docs_local` page lists all
available sites. Site requests are routed by their HTTP host name, for
example:

```text
http://site-1:8080/
http://site-1:8080/about
http://127.0.0.1:8080/docs_local
```

The command also supports `python -m local_docs`.

## Configuration

Environment variables can configure the server:

```bash
HOST=127.0.0.1
PORT=8080
SITES_DIR=/path/to/sites
OPEN_BROWSER=1
LOG_LEVEL=INFO
```

The browser opens `/docs_local` after startup by default. Disable it with:

```bash
OPEN_BROWSER=0 local-docs
```

Command-line options override environment variables:
`--host`, `--port`, `--sites-dir`, `--open-browser`, `--no-browser`, and
`--log-level`.

The application manages its marked entries in the system hosts file and
removes them during clean shutdown. Running the command may therefore
require administrator privileges.
