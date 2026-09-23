FROM lscr.io/linuxserver/freecad:latest

LABEL maintainer="FreeCAD MCP"
LABEL description="FreeCAD with MCP dependencies - APT isolation test"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-pil \
    libegl1 \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    xvfb \
    libosmesa6-dev \
    libglew-dev \
    freeglut3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    Pillow \
    trimesh \
    matplotlib \
    numpy \
    vtk

COPY rpc_server.py /app/rpc_server.py
COPY render_video.py /app/render_video.py

# FreeCAD GUI addon that exposes the existing RPC API
# from the same FreeCAD process shown in Selkies.
COPY FreeCADMCP/ /opt/freecad/usr/Mod/FreeCADMCP/

EXPOSE 9875
EXPOSE 3000
EXPOSE 3001