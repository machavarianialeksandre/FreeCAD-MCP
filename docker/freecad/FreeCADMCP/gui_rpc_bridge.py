import os
import sys
import queue
import threading

import FreeCAD

try:
    from PySide import QtCore
except ImportError:
    from PySide2 import QtCore

APP_DIR = "/app"

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from rpc_server import FreeCADRPCServer, RequestHandler
from xmlrpc.server import SimpleXMLRPCServer


_request_queue = queue.Queue()

_timer = None
_server = None
_server_thread = None
_rpc_instance = None
_started = False


class _RPCRequest:
    def __init__(self, method, params):
        self.method = method
        self.params = params
        self.event = threading.Event()
        self.result = None
        self.error = None


class MainThreadRPCProxy:
    def __init__(self, rpc_instance):
        self.rpc_instance = rpc_instance

    def _dispatch(self, method, params):
        request = _RPCRequest(method, params)

        _request_queue.put(request)

        if not request.event.wait(timeout=120):
            raise TimeoutError(
                f"Timed out waiting for FreeCAD main thread: {method}"
            )

        if request.error is not None:
            raise request.error

        return request.result


def _process_requests():
    processed = 0

    while processed < 20:
        try:
            request = _request_queue.get_nowait()
        except queue.Empty:
            break

        try:
            method = getattr(_rpc_instance, request.method)
            request.result = method(*request.params)

        except Exception as exc:
            request.error = exc

            FreeCAD.Console.PrintError(
                f"FreeCAD MCP RPC error [{request.method}]: {exc}\n"
            )

        finally:
            request.event.set()
            processed += 1


def _run_xmlrpc_server():
    global _server

    host = os.environ.get("RPC_HOST", "0.0.0.0")
    port = int(os.environ.get("RPC_PORT", "9875"))

    try:
        _server = SimpleXMLRPCServer(
            (host, port),
            requestHandler=RequestHandler,
            allow_none=True,
            logRequests=False,
        )

        _server.register_introspection_functions()
        _server.register_instance(MainThreadRPCProxy(_rpc_instance))

        FreeCAD.Console.PrintMessage(
            f"FreeCAD MCP: XML-RPC listening on {host}:{port}\n"
        )

        _server.serve_forever()

    except Exception as exc:
        FreeCAD.Console.PrintError(
            f"FreeCAD MCP: XML-RPC server failed: {exc}\n"
        )


def start_rpc_server():
    global _timer
    global _server_thread
    global _rpc_instance
    global _started

    if _started:
        return

    _started = True

    _rpc_instance = FreeCADRPCServer()

    _timer = QtCore.QTimer()
    _timer.setInterval(10)
    _timer.timeout.connect(_process_requests)
    _timer.start()

    _server_thread = threading.Thread(
        target=_run_xmlrpc_server,
        name="FreeCAD-MCP-XMLRPC",
        daemon=True,
    )

    _server_thread.start()

    FreeCAD.Console.PrintMessage(
        "FreeCAD MCP: RPC bridge started\n"
    )