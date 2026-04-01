#!/usr/bin/with-contenv bashio
set -euo pipefail

bashio::log.info "Starte ChatGPT HA Exporter"
python3 /opt/export_bundle.py
bashio::log.info "Export abgeschlossen"
