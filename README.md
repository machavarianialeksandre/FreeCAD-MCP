<div align="center">

# 🏗️ FreeCAD MCP

**Control FreeCAD through MCP while viewing the same live FreeCAD GUI in your browser.**

[![Docker](https://img.shields.io/badge/Docker-Desktop-2496ED?logo=docker&logoColor=white)](https://www.docker.com/products/docker-desktop/)
[![FreeCAD](https://img.shields.io/badge/FreeCAD-LinuxServer.io-orange)](https://www.freecad.org/)
[![MCP](https://img.shields.io/badge/MCP-Enabled-7B61FF)](#)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?logo=windows&logoColor=white)](#)
[![Security](https://img.shields.io/badge/Ports-localhost--only-success)](#security)

A Docker-based FreeCAD + MCP environment designed for Windows/Docker Desktop.

</div>

---

## ✨ What this fork changes

This fork modernizes the Docker integration for the current LinuxServer.io FreeCAD / Selkies stack and fixes several Windows + Docker compatibility issues.

Most importantly, MCP/RPC now runs **inside the same FreeCAD GUI process** that you see in the browser.

```text
MCP client
    │
    ▼
freecad-mcp-server
    │
    │ XML-RPC :9875
    ▼
FreeCAD GUI process
    │
    ├── Qt main thread
    ├── FreeCAD documents
    └── Selkies browser GUI
```

So when MCP creates or modifies a document, the change appears in the **same live FreeCAD session** in the browser.

---

## 🧱 Architecture

```text
┌──────────────────────────────┐
│ MCP Client / Claude Desktop  │
└──────────────┬───────────────┘
               │ MCP / stdio
               ▼
┌──────────────────────────────┐
│ freecad-mcp-server           │
│ Docker container             │
└──────────────┬───────────────┘
               │ XML-RPC :9875
               ▼
┌─────────────────────────────────────────────┐
│ freecad-mcp                                 │
│                                             │
│  LinuxServer.io /init                       │
│      │                                      │
│      ├── Selkies / Wayland                  │
│      ├── labwc                              │
│      └── FreeCAD GUI process                │
│              │                              │
│              └── FreeCADMCP InitGui bridge  │
│                     │                       │
│                     ├── XML-RPC listener    │
│                     └── Qt main-thread queue│
└──────────────────────┬──────────────────────┘
                       │
                       ▼
                Browser GUI
             https://127.0.0.1:3001
```

---

## ✅ Requirements

- Windows 10 or Windows 11
- Docker Desktop
- Git
- WSL2 backend for Docker Desktop
- Modern browser such as Edge or Chrome
- Optional: Claude Desktop or another MCP-compatible client

You do **not** need a local FreeCAD or Python installation for the Docker stack.

---

## 🚀 Quick start

```powershell
git clone https://github.com/machavarianialeksandre/FreeCAD-MCP.git
cd FreeCAD-MCP
docker compose --profile server build
docker compose --profile server up -d
docker compose --profile server ps
```

Expected services:

```text
freecad-mcp
freecad-mcp-server
```

Both should eventually report `healthy`.

---

## 🖥️ Open the FreeCAD GUI

Open:

```text
https://127.0.0.1:3001
```

The first time, your browser may warn about the self-signed certificate. Choose the browser option equivalent to:

```text
Advanced → Continue to 127.0.0.1
```

For direct browser access, prefer HTTPS `3001`.

---

## 🔌 Local ports

| Port | Purpose | Address |
|---|---|---|
| `3001` | FreeCAD Selkies HTTPS GUI | `https://127.0.0.1:3001` |
| `3000` | Selkies HTTP endpoint | `http://127.0.0.1:3000` |
| `9875` | FreeCAD XML-RPC | `127.0.0.1:9875` |
| `7860` | MCP debug interface | `http://127.0.0.1:7860` |

Ports are bound to `127.0.0.1` so they are not exposed to the LAN by default.

---

## 🧠 How the GUI RPC bridge works

Older Docker setups launched a second headless FreeCAD process for XML-RPC:

```text
FreeCAD GUI process
        ≠
Headless RPC FreeCAD process
```

A document created through MCP could exist in the RPC process but not appear in the browser GUI.

This fork loads an addon into the normal GUI process:

```text
docker/freecad/FreeCADMCP/
├── Init.py
├── InitGui.py
└── gui_rpc_bridge.py
```

`InitGui.py` starts the RPC bridge when FreeCAD GUI initializes. The network listener runs in a background thread, while FreeCAD operations are queued onto the Qt GUI main thread.

Result:

```text
MCP action
   ↓
XML-RPC request
   ↓
FreeCAD GUI main thread
   ↓
same document visible in browser
```

---

## 🧪 Health checks

Check containers:

```powershell
docker compose --profile server ps
```

Direct RPC ping:

```powershell
docker exec freecad-mcp python3 -c "import xmlrpc.client; c=xmlrpc.client.ServerProxy('http://127.0.0.1:9875', allow_none=True); print(c.ping())"
```

Expected:

```text
pong
```

Check listener:

```powershell
docker exec freecad-mcp sh -lc "ss -lntp | grep 9875 || true"
```

Test MCP container → FreeCAD:

```powershell
docker exec freecad-mcp-server python -c "from src.freecad_client import FreeCADClient; c=FreeCADClient('freecad',9875); print('PING:',c.ping()); print('DOCS:',c.list_documents())"
```

Expected:

```text
PING: True
```

---

## 🧪 End-to-end GUI test

Create a document through XML-RPC:

```powershell
docker exec freecad-mcp python3 -c "import xmlrpc.client; c=xmlrpc.client.ServerProxy('http://127.0.0.1:9875', allow_none=True); print('CREATE:', c.create_document('MCP_GUI_Test')); print('DOCS:', c.list_documents())"
```

`MCP_GUI_Test` should immediately appear in the browser FreeCAD GUI.

Test from the MCP server container:

```powershell
docker exec freecad-mcp-server python -c "from src.freecad_client import FreeCADClient; c=FreeCADClient('freecad',9875); print('PING:',c.ping()); print('CREATE:',c.create_document('MCP_Server_Test')); print('DOCS:',c.list_documents())"
```

`MCP_Server_Test` should appear in the same GUI session.

---

## 🤖 Claude Desktop example

```json
{
  "mcpServers": {
    "freecad": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "freecad-mcp-server",
        "python",
        "-m",
        "src.mcp_server"
      ]
    }
  }
}
```

On Windows, Claude Desktop configuration is commonly located under:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

Restart Claude Desktop after changing MCP configuration.

---

## 🛠️ Common commands

Start:

```powershell
docker compose --profile server up -d
```

Stop:

```powershell
docker compose --profile server down
```

Status:

```powershell
docker compose --profile server ps
```

Show stopped containers too:

```powershell
docker compose --profile server ps -a
```

FreeCAD logs:

```powershell
docker compose logs -f freecad
```

MCP logs:

```powershell
docker compose logs -f mcp
```

Rebuild FreeCAD:

```powershell
docker compose build --no-cache freecad
```

Rebuild everything:

```powershell
docker compose --profile server build --no-cache
```

---

## 🪟 Windows line endings

Docker shell scripts must use Unix `LF`, not Windows `CRLF`.

This fork includes `.gitattributes` rules similar to:

```gitattributes
* text=auto

*.sh text eol=lf
*.py text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
Dockerfile text eol=lf
Dockerfile.* text eol=lf
```

A previous failure looked like:

```text
exec /app/start.sh: no such file or directory
```

although the file existed. The real cause was a CRLF shebang:

```text
#!/bin/bash\r
```

---

## 🧯 Troubleshooting

### Selkies sidebar appears but the center is black

Check processes:

```powershell
docker exec freecad-mcp sh -lc "ps aux | grep -Ei 'FreeCAD|AppRun|selkies|labwc' | grep -v grep"
```

A healthy GUI stack should include Selkies/labwc and a normal GUI FreeCAD process.

### Stale `/config` causes a black GUI

This project persists `/config` to:

```text
data/freecad
```

If FreeCAD works with a fresh config but not with the persistent bind mount:

```powershell
docker compose --profile server down
Rename-Item .\data\freecad freecad-backup
New-Item -ItemType Directory .\data\freecad
docker compose --profile server up -d
```

Then open:

```text
https://127.0.0.1:3001
```

Keep the backup until the new configuration is confirmed stable.

### GUI works in `docker run` but not in Compose

Compare runtime settings:

```powershell
docker inspect freecad-mcp --format "ENV={{json .Config.Env}}"
docker inspect freecad-mcp --format "MOUNTS={{json .Mounts}}"
docker inspect freecad-mcp --format "ENTRYPOINT={{json .Config.Entrypoint}} CMD={{json .Config.Cmd}} SHM={{.HostConfig.ShmSize}}"
```

Pay particular attention to `/config`.

### RPC port refuses connections

```powershell
docker exec freecad-mcp sh -lc "ss -lntp | grep 9875 || true"
```

Verify the addon:

```powershell
docker exec freecad-mcp sh -lc "ls -la /opt/freecad/usr/Mod/FreeCADMCP"
```

Expected:

```text
Init.py
InitGui.py
gui_rpc_bridge.py
```

### `list_documents()` fails with `Touched`

This fork includes a compatibility fix in `rpc_server.py` that avoids depending directly on `doc.Touched`.

### MCP Docker build says `README.md` is missing

The MCP Dockerfile must copy `README.md` before:

```dockerfile
RUN pip install --no-cache-dir -e .
```

This fork includes that fix.

---

## 🔐 Security

This setup is intended primarily for local development.

Ports are bound to:

```text
127.0.0.1
```

rather than `0.0.0.0`.

Cloud/public tunneling is disabled by default.

Recommended practice:

- keep MCP and FreeCAD ports localhost-only;
- do not expose XML-RPC directly to the internet;
- review actions that can execute arbitrary code;
- use manual approval when working with untrusted prompts or files;
- use an authenticated reverse proxy or VPN for remote access.

---

## 📁 Persistent data

Typical mounts:

```text
data/freecad          → /config
data/models           → /data/models
data/exports          → /data/exports
data/trellis/outputs  → /data/trellis/outputs
cache                 → /data/cache
```

FreeCAD/Selkies user configuration lives under `data/freecad`. Models and exports are separate.

---

## 🔄 Git remotes

Typical fork setup:

```text
origin   https://github.com/machavarianialeksandre/FreeCAD-MCP.git
upstream https://github.com/proximile/FreeCAD-MCP.git
```

Fetch upstream:

```powershell
git fetch upstream
```

---

## 🧹 Local backup files

Temporary troubleshooting backups should not be committed.

Recommended `.gitignore` entries:

```gitignore
docker/freecad/Dockerfile.backup
docker/freecad/Dockerfile.known-good
```

---

## 📋 Daily cheat sheet

```powershell
docker compose --profile server up -d
docker compose --profile server ps
```

Open FreeCAD:

```text
https://127.0.0.1:3001
```

Test RPC:

```powershell
docker exec freecad-mcp python3 -c "import xmlrpc.client; c=xmlrpc.client.ServerProxy('http://127.0.0.1:9875', allow_none=True); print(c.ping())"
```

Stop:

```powershell
docker compose --profile server down
```

---

## 🧩 Key fixes in this fork

- Windows CRLF → LF Docker compatibility
- MCP Docker build copies `README.md` before editable install
- FreeCAD `list_documents()` compatibility fix
- localhost-only port bindings
- public tunnel disabled by default
- current Selkies browser GUI support
- HTTPS GUI on port `3001`
- stale `/config` recovery procedure
- removal of the old dual-FreeCAD-process architecture
- GUI-loaded `FreeCADMCP` addon
- XML-RPC background listener
- Qt main-thread execution bridge
- MCP-created documents visible immediately in the live browser GUI

---

## 🙏 Upstream

Based on **proximile/FreeCAD-MCP**.

This fork preserves the original MCP integration concept while modernizing the Docker/GUI integration and improving Windows compatibility.

---

## 📄 License

Refer to the repository's existing license and upstream project terms.
