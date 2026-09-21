# Image de l'agent Hestia (appliance headless / e-paper).
#
# ⚠️ Hestia pilote le réseau du foyer et du matériel : le conteneur doit tourner
# en réseau host, avec CAP_NET_RAW et le passthrough des périphériques SPI/GPIO
# (voir compose.yaml et docs/DOCKER.md).

# ----- build -----------------------------------------------------------------
FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock VERSION README.md ./
COPY src ./src

# Dépendances + agent (extras matériels : sonde DHCP, e-paper, vérif OTA).
RUN uv sync --frozen --no-dev --extra net --extra hardware --extra ota

# Pilote e-paper Waveshare (absent de PyPI). Désactivable : --build-arg WAVESHARE=0.
ARG WAVESHARE=1
RUN if [ "$WAVESHARE" = "1" ]; then \
      apt-get update && apt-get install -y --no-install-recommends git && \
      git clone --depth 1 https://github.com/waveshare/e-Paper.git /tmp/epaper && \
      cp -r /tmp/epaper/RaspberryPi_JetsonNano/python/lib/waveshare_epd \
            /app/.venv/lib/python3.11/site-packages/ && \
      rm -rf /tmp/epaper && \
      apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* ; \
    fi

# ----- runtime ---------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Police pour le rendu de l'écran.
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"

# La configuration est montée depuis l'hôte (/etc/hestia), l'état est persistant
# (/var/lib/hestia) — voir compose.yaml.
ENTRYPOINT ["hestia"]
