<div align="center">

# 🏗️ FreeCAD MCP

### FreeCAD + MCP + Docker + Claude

**Windows-friendly • Dockerized • Localhost-only • No local Python required**

[![Docker](https://img.shields.io/badge/Docker-Desktop-2496ED?logo=docker&logoColor=white)](https://www.docker.com/products/docker-desktop/)
[![FreeCAD](https://img.shields.io/badge/FreeCAD-MCP-orange)](https://www.freecad.org/)
[![MCP](https://img.shields.io/badge/Model_Context_Protocol-MCP-blueviolet)](https://modelcontextprotocol.io/)
[![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Security](https://img.shields.io/badge/Network-Localhost_Only-success)](#-security)
[![Tunnel](https://img.shields.io/badge/Cloudflare_Tunnel-Disabled-success)](#-security)

<br>

A Windows/Docker-friendly fork of **FreeCAD-MCP**, configured for running FreeCAD together with an MCP server and AI clients such as Claude.

</div>

---

## ✨ What does this provide?

This project creates a local AI-to-CAD stack:

```text
┌───────────────────────┐
│     Claude Desktop    │
│      or MCP Client    │
└───────────┬───────────┘
            │
            │ MCP / stdio
            ▼
┌───────────────────────┐
│  freecad-mcp-server   │
│       Docker          │
└───────────┬───────────┘
            │
            │ XML-RPC :9875
            ▼
┌───────────────────────┐
│      FreeCAD MCP      │
│       Docker          │
└───────────┬───────────┘
            │
            ▼
       .FCStd / CAD
```

### Included

✅ FreeCAD in Docker  
✅ MCP server in Docker  
✅ Browser-based FreeCAD GUI  
✅ MCP debug interface  
✅ Claude Desktop integration  
✅ No Windows Python installation required  
✅ Localhost-only network exposure  
✅ Cloudflare public tunnel disabled  
✅ Windows CRLF protection  
✅ FreeCAD compatibility fixes  

---

# 🚀 Quick Start

If Docker Desktop and Git are already installed:

```powershell
git clone https://github.com/machavarianialeksandre/FreeCAD-MCP.git
cd FreeCAD-MCP

docker compose --profile server build
docker compose --profile server up -d
docker compose --profile server ps
```

You want to see:

```text
freecad-mcp          Up ... (healthy)
freecad-mcp-server   Up ... (healthy)
```

Then open:

| Component | Address |
|---|---|
| 🖥️ FreeCAD GUI | `http://127.0.0.1:3000` |
| 🧪 MCP Debug UI | `http://127.0.0.1:7860` |
| 🔌 FreeCAD RPC | `127.0.0.1:9875` |
| 🖱️ VNC | `127.0.0.1:5900` |

---

# 📋 Requirements

### Required

- Windows 10 / 11
- Docker Desktop
- Git

### Optional

- Claude Desktop

> **Python does not need to be installed on Windows.**
>
> Python and MCP dependencies run inside Docker.

---

# 🐳 1. Verify Docker

Start **Docker Desktop** first.

Then:

```powershell
docker version
```

You should see both:

```text
Client:
```

and:

```text
Server: Docker Desktop
```

Check Docker context:

```powershell
docker context ls
```

Recommended active context:

```text
desktop-linux
```

---

# 📥 2. Clone the Repository

Example:

```powershell
cd D:\DockerProjects
```

Clone:

```powershell
git clone https://github.com/machavarianialeksandre/FreeCAD-MCP.git
```

Enter the directory:

```powershell
cd FreeCAD-MCP
```

---

# 🔨 3. Build

Normal build:

```powershell
docker compose --profile server build
```

For a completely clean rebuild:

```powershell
docker compose --profile server build --no-cache
```

> The first build takes longer because Docker must download the FreeCAD image, Python environment and dependencies.

---

# ▶️ 4. Start

```powershell
docker compose --profile server up -d
```

Check:

```powershell
docker compose --profile server ps
```

Expected:

```text
NAME                 STATUS
freecad-mcp          Up ... (healthy)
freecad-mcp-server   Up ... (healthy)
```

Both containers should eventually become:

```text
healthy
```

---

# 🖥️ 5. FreeCAD GUI

Open in your browser:

```text
http://127.0.0.1:3000
```

This is the FreeCAD instance running inside Docker.

---

# 🧪 6. MCP Debug Interface

Open:

```text
http://127.0.0.1:7860
```

This exposes the local MCP debug / Gradio interface.

---

# 🔌 7. Test FreeCAD RPC

PowerShell:

```powershell
Test-NetConnection 127.0.0.1 -Port 9875
```

Expected:

```text
TcpTestSucceeded : True
```

> Use `127.0.0.1` instead of `localhost` to avoid an irrelevant IPv6 `::1` warning on some Windows systems.

---

# ❤️ 8. MCP → FreeCAD Health Check

Run:

```powershell
docker exec freecad-mcp-server python -c "from src.freecad_client import FreeCADClient; c=FreeCADClient('freecad',9875); print('PING:',c.ping()); print('DOCS:',c.list_documents())"
```

Expected:

```text
PING: True
DOCS: []
```

An empty document list is normal when no FreeCAD documents are open.

---

# ✍️ 9. Full Read / Write Test

Create a FreeCAD document through MCP:

```powershell
docker exec freecad-mcp-server python -c "from src.freecad_client import FreeCADClient; c=FreeCADClient('freecad',9875); print('CREATE:',c.create_document('MCP_Test')); print('DOCS:',c.list_documents())"
```

Expected:

```text
CREATE: MCP_Test
DOCS: [DocumentInfo(name='MCP_Test', file_path=None, objects=[], modified=False)]
```

This confirms the full path:

```text
MCP
 │
 ▼
FreeCAD RPC
 │
 ▼
FreeCAD Document
```

---

# 🤖 Claude Desktop

The containers must already be running:

```powershell
docker compose --profile server up -d
```

Claude can then start the MCP server inside the existing Docker container.

Example Claude Desktop configuration:

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

On Windows the Claude Desktop configuration is commonly located under:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

If the file already contains other MCP servers, add `freecad` to the existing `mcpServers` object.

After changing the configuration:

1. Start Docker Desktop.
2. Start the FreeCAD MCP stack.
3. Verify both containers are healthy.
4. Completely close Claude Desktop.
5. Start Claude Desktop again.

### First Claude test

Try:

```text
List all open FreeCAD documents.
```

Then:

```text
Create a new FreeCAD document named Apartment_Test.
```

Then a geometry test:

```text
Create a box in FreeCAD with dimensions
4000 mm × 3000 mm × 200 mm.
```

---

# 🔐 Security

This fork intentionally uses more restrictive defaults.

## Localhost-only

Docker ports are bound to:

```text
127.0.0.1
```

rather than:

```text
0.0.0.0
```

Current bindings:

```text
127.0.0.1:3000
127.0.0.1:5900
127.0.0.1:7860
127.0.0.1:9875
```

This prevents direct access from other devices on the local network.

## Public tunnel disabled

```text
ENABLE_TUNNEL=false
```

Automatic Cloudflare public tunnel creation is disabled.

## Recommendation

For AI clients such as Claude:

> Keep powerful MCP actions on **Ask / Manual approval** where possible.

Be particularly careful with arbitrary Python/code execution functionality.

---

# ⏹️ Stop

```powershell
docker compose --profile server down
```

---

# 🔄 Start Again Later

Once installation is complete, normal daily startup is only:

```powershell
cd D:\DockerProjects\FreeCAD-MCP

docker compose --profile server up -d

docker compose --profile server ps
```

If both containers are:

```text
healthy
```

the environment is ready.

No rebuild is normally required.

---

# ♻️ Restart

```powershell
docker compose --profile server restart
```

Then:

```powershell
docker compose --profile server ps
```

---

# 📜 Logs

### FreeCAD

```powershell
docker compose logs --tail=100 freecad
```

### MCP

```powershell
docker compose --profile server logs --tail=100 mcp
```

### Live logs

```powershell
docker compose --profile server logs -f
```

Stop following logs with:

```text
Ctrl+C
```

---

# 🧹 Clean Rebuild

If Docker source/configuration has changed:

```powershell
docker compose --profile server down
docker compose --profile server build --no-cache
docker compose --profile server up -d
```

Then:

```powershell
docker compose --profile server ps
```

---

# 📦 Git Configuration

This fork:

```text
https://github.com/machavarianialeksandre/FreeCAD-MCP
```

Upstream:

```text
https://github.com/proximile/FreeCAD-MCP
```

Recommended remotes:

```text
origin   → machavarianialeksandre/FreeCAD-MCP
upstream → proximile/FreeCAD-MCP
```

Check:

```powershell
git remote -v
```

Fetch upstream:

```powershell
git fetch upstream
```

> Review upstream changes before merging because this fork contains Windows/Docker compatibility and security-default modifications.

---

# 🪟 Windows Line Ending Protection

This fork includes `.gitattributes`.

Linux-sensitive files are forced to use LF:

```text
*.sh
*.py
*.yml
*.yaml
Dockerfile
Dockerfile.*
```

This prevents Windows CRLF from producing errors such as:

```text
exec /app/start.sh: no such file or directory
```

---

# 🛠️ Fixes Included in This Fork

### ✅ Windows CRLF / Docker fix

The original Docker startup script could become:

```text
#!/bin/bash\r
```

instead of:

```text
#!/bin/bash
```

which causes Linux to report:

```text
exec /app/start.sh: no such file or directory
```

`.gitattributes` now protects relevant files.

---

### ✅ MCP Docker build fix

`pyproject.toml` references:

```text
README.md
```

The MCP Docker image therefore now copies the README before:

```text
pip install -e .
```

This avoids:

```text
OSError: Readme file does not exist: README.md
```

---

### ✅ FreeCAD document compatibility

Some FreeCAD builds do not expose:

```text
App.Document.Touched
```

The RPC document listing implementation has been made more defensive so `list_documents()` works on these versions.

---

### ✅ Safer network defaults

Changed from public/all-interface bindings to:

```text
127.0.0.1
```

for local-only access.

---

### ✅ Public tunnel disabled

```text
ENABLE_TUNNEL=false
```

is used by default.

---

# 🧯 Troubleshooting

<details>

<summary><strong>Docker API / dockerDesktopLinuxEngine error</strong></summary>

<br>

Example:

```text
failed to connect to the docker API
dockerDesktopLinuxEngine
```

Most likely cause:

> Docker Desktop is not running.

Start Docker Desktop and verify:

```powershell
docker version
```

</details>

---

<details>

<summary><strong>Container keeps restarting</strong></summary>

<br>

Check:

```powershell
docker compose --profile server ps -a
```

Then inspect FreeCAD:

```powershell
docker compose logs --tail=100 freecad
```

Or MCP:

```powershell
docker compose --profile server logs --tail=100 mcp
```

</details>

---

<details>

<summary><strong>/app/start.sh: no such file or directory</strong></summary>

<br>

Check the generated shell script:

```powershell
docker run --rm --entrypoint /bin/sh freecad-mcp-freecad -c "sed -n '1l' /app/start.sh"
```

Correct:

```text
#!/bin/bash$
```

Incorrect:

```text
#!/bin/bash\r$
```

`\r` means Windows CRLF line endings were introduced.

This fork includes `.gitattributes` to prevent that.

</details>

---

<details>

<summary><strong>MCP reports FreeCAD connection refused during startup</strong></summary>

<br>

You may see:

```text
FreeCAD ping failed: [Errno 111] Connection refused
```

If both containers later report `healthy`, this may simply be startup timing.

Verify the actual connection:

```powershell
docker exec freecad-mcp-server python -c "from src.freecad_client import FreeCADClient; c=FreeCADClient('freecad',9875); print(c.ping())"
```

Expected:

```text
True
```

</details>

---

<details>

<summary><strong>HOME variable is not set</strong></summary>

<br>

Docker Compose may show:

```text
The "HOME" variable is not set. Defaulting to a blank string.
```

This warning does not prevent the core FreeCAD + MCP services from running.

Optional PowerShell workaround:

```powershell
$env:HOME=$env:USERPROFILE
```

</details>

---

<details>

<summary><strong>version is obsolete warning</strong></summary>

<br>

Docker Compose V2 may show:

```text
the attribute `version` is obsolete
```

This is a warning and does not prevent the stack from running.

</details>

---

# ⚡ Daily Cheat Sheet

### Start

```powershell
docker compose --profile server up -d
```

### Status

```powershell
docker compose --profile server ps
```

### Test

```powershell
docker exec freecad-mcp-server python -c "from src.freecad_client import FreeCADClient; c=FreeCADClient('freecad',9875); print('PING:',c.ping())"
```

Expected:

```text
PING: True
```

### FreeCAD

```text
http://127.0.0.1:3000
```

### MCP Debug

```text
http://127.0.0.1:7860
```

### Stop

```powershell
docker compose --profile server down
```

---

# 🌳 Project Relationships

```text
proximile/FreeCAD-MCP
        │
        │ upstream
        ▼
machavarianialeksandre/FreeCAD-MCP
        │
        │ Windows + Docker fixes
        ▼
      Local PC
        │
        ▼
   Docker Desktop
     ├── FreeCAD
     └── MCP
```

---

# 🙏 Upstream

Based on:

**proximile/FreeCAD-MCP**

```text
https://github.com/proximile/FreeCAD-MCP
```

Thanks to the original project authors and contributors.

---

<div align="center">

### FreeCAD + Docker + MCP

**Local • Reproducible • AI-ready**

</div>
