import sys
import FreeCAD

MOD_DIR = "/opt/freecad/usr/Mod/FreeCADMCP"

if MOD_DIR not in sys.path:
    sys.path.insert(0, MOD_DIR)

try:
    from gui_rpc_bridge import start_rpc_server

    start_rpc_server()

    FreeCAD.Console.PrintMessage(
        "FreeCAD MCP: GUI RPC bridge initialization requested\n"
    )

except Exception as exc:
    FreeCAD.Console.PrintError(
        f"FreeCAD MCP: failed to initialize GUI RPC bridge: {exc}\n"
    )