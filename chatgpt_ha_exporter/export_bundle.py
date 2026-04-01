#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import tarfile
import traceback
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

HA_CONFIG_DIR = Path("/homeassistant")
DATA_DIR = Path("/data")
SHARE_DIR = Path("/share")
OPTIONS_PATH = DATA_DIR / "options.json"
SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
EXPORTER_VERSION = "0.1.1"

DEFAULT_OPTIONS: dict[str, Any] = {
    "export_name_prefix": "ha_chatgpt_export",
    "include_current_state_snapshot": True,
    "include_service_catalog": True,
    "include_dashboards": True,
    "include_blueprints": True,
    "include_custom_components": True,
    "include_python_scripts": True,
    "include_pyscript": True,
    "include_logs": True,
    "max_log_lines": 4000,
    "include_recorder_summary": True,
    "recorder_days": 14,
    "include_raw_storage_files": True,
}

SENSITIVE_KEY_PARTS = {
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "client_secret",
    "private_key",
    "certificate",
    "cert",
    "webhook",
    "authorization",
    "auth",
    "bearer",
    "cloudhook",
    "network_key",
    "security_key",
    "pan_id",
    "extended_pan_id",
    "ssid",
    "psk",
    "wpa",
    "cookie",
}

LOCATION_KEY_PARTS = {
    "latitude",
    "longitude",
    "elevation",
    "gps",
    "location_name",
    "internal_url",
    "external_url",
    "address",
}

TEXT_LINE_REDACTIONS = [
    (re.compile(r"(?im)^(\s*[^#\n]*?(?:password|passwd|token|secret|api[_-]?key|client_secret|refresh_token|access_token|webhook_id|webhook_url)\s*:\s*).*$"), r"\1<redacted>"),
    (re.compile(r"(?im)(Authorization\s*:\s*Bearer\s+)[^\s]+"), r"\1<redacted>"),
    (re.compile(r"(?im)(mqtt://[^:@\s]+:)[^@\s]+(@)"), r"\1<redacted>\2"),
]

STORAGE_ALLOWLIST = {
    "core.area_registry",
    "core.device_registry",
    "core.entity_registry",
    "core.floor_registry",
    "core.label_registry",
    "core.config_entries",
    "core.config",
    "core.restore_state",
    "core.exposed_entities",
    "lovelace",
    "lovelace_dashboards",
    "lovelace_resources",
    "energy",
    "person",
}

STORAGE_PREFIX_ALLOWLIST = (
    "lovelace.",
)

SKIP_NAMES = {
    ".DS_Store",
    "__pycache__",
}
SKIP_SUFFIXES = {".pyc", ".pyo"}


class IgnoreUnknownLoader(yaml.SafeLoader):
    pass


def _unknown_constructor(loader: IgnoreUnknownLoader, tag_suffix: str, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


IgnoreUnknownLoader.add_multi_constructor("!", _unknown_constructor)


@dataclass
class ExportStats:
    included_files: list[str] = field(default_factory=list)
    excluded_items: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    api_calls: list[str] = field(default_factory=list)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def load_options() -> dict[str, Any]:
    options = DEFAULT_OPTIONS.copy()
    if OPTIONS_PATH.exists():
        try:
            loaded = json.loads(OPTIONS_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                options.update(loaded)
        except Exception as exc:
            print(f"WARN: Konnte options.json nicht lesen: {exc}")
    return options


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def looks_sensitive_key(key: str) -> bool:
    k = key.lower()
    return any(part in k for part in SENSITIVE_KEY_PARTS)


def looks_location_key(key: str) -> bool:
    k = key.lower()
    return any(part in k for part in LOCATION_KEY_PARTS)


def sanitize_string(value: str, parent_key: str | None = None) -> str:
    if parent_key and looks_sensitive_key(parent_key):
        return "<redacted>"
    if parent_key and looks_location_key(parent_key):
        return "<redacted>"

    trimmed = value
    for pattern, repl in TEXT_LINE_REDACTIONS:
        trimmed = pattern.sub(repl, trimmed)

    if re.search(r"Bearer\s+[A-Za-z0-9._\-]{16,}", trimmed):
        trimmed = re.sub(r"Bearer\s+[A-Za-z0-9._\-]{16,}", "Bearer <redacted>", trimmed)

    if re.fullmatch(r"[A-Za-z0-9_\-]{32,}", trimmed):
        return "<redacted-like-token>"

    if len(trimmed) > 4000:
        trimmed = trimmed[:4000] + "…<truncated>"
    return trimmed


def sanitize_data(obj: Any, parent_key: str | None = None) -> Any:
    if isinstance(obj, dict):
        new: dict[str, Any] = {}
        for key, value in obj.items():
            key_str = str(key)
            if looks_sensitive_key(key_str):
                new[key_str] = "<redacted>"
            elif looks_location_key(key_str):
                new[key_str] = "<redacted>"
            else:
                new[key_str] = sanitize_data(value, key_str)
        return new
    if isinstance(obj, list):
        return [sanitize_data(item, parent_key) for item in obj]
    if isinstance(obj, tuple):
        return [sanitize_data(item, parent_key) for item in obj]
    if isinstance(obj, str):
        return sanitize_string(obj, parent_key)
    return obj


def sanitize_text_file(text: str) -> str:
    result = text
    for pattern, repl in TEXT_LINE_REDACTIONS:
        result = pattern.sub(repl, result)
    return result


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def write_ndjson(path: Path, rows: Iterable[Any]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def relative_to_or_name(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except Exception:
        return path.name


def export_raw_text(src: Path, dst: Path, stats: ExportStats) -> None:
    try:
        text = src.read_text(encoding="utf-8", errors="ignore")
        ensure_dir(dst.parent)
        dst.write_text(sanitize_text_file(text), encoding="utf-8")
        stats.included_files.append(str(dst))
    except Exception as exc:
        stats.warnings.append(f"Konnte Textdatei nicht exportieren: {src} ({exc})")


def parse_yaml_file(src: Path) -> Any:
    text = src.read_text(encoding="utf-8", errors="ignore")
    return yaml.load(text, Loader=IgnoreUnknownLoader)


def export_yaml(src: Path, raw_dst: Path, normalized_dst: Path, stats: ExportStats) -> None:
    export_raw_text(src, raw_dst, stats)
    try:
        parsed = parse_yaml_file(src)
        sanitized = sanitize_data(parsed)
        write_json(normalized_dst, sanitized)
        stats.included_files.append(str(normalized_dst))
    except Exception as exc:
        stats.warnings.append(f"YAML-Normalisierung fehlgeschlagen für {src}: {exc}")


def export_json(src: Path, raw_dst: Path, normalized_dst: Path, stats: ExportStats) -> None:
    try:
        raw = src.read_text(encoding="utf-8", errors="ignore")
        ensure_dir(raw_dst.parent)
        raw_dst.write_text(sanitize_text_file(raw), encoding="utf-8")
        stats.included_files.append(str(raw_dst))
    except Exception as exc:
        stats.warnings.append(f"JSON-Rohdatei konnte nicht exportiert werden {src}: {exc}")

    try:
        data = json.loads(src.read_text(encoding="utf-8", errors="ignore"))
        sanitized = sanitize_data(data)
        write_json(normalized_dst, sanitized)
        stats.included_files.append(str(normalized_dst))
    except Exception as exc:
        stats.warnings.append(f"JSON-Normalisierung fehlgeschlagen für {src}: {exc}")


def should_export_storage(name: str) -> bool:
    if name in STORAGE_ALLOWLIST:
        return True
    return any(name.startswith(prefix) for prefix in STORAGE_PREFIX_ALLOWLIST)


def iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file())


def should_skip_path(path: Path) -> bool:
    if path.name in SKIP_NAMES:
        return True
    if path.suffix in SKIP_SUFFIXES:
        return True
    return any(part == "__pycache__" for part in path.parts)


def copy_tree_sanitized(src_root: Path, dst_root: Path, stats: ExportStats, text_mode: bool = True) -> None:
    if not src_root.exists():
        stats.excluded_items.append(f"Fehlt: {src_root}")
        return

    for src in iter_files(src_root):
        if should_skip_path(src):
            continue
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        ensure_dir(dst.parent)
        if text_mode:
            try:
                content = src.read_text(encoding="utf-8", errors="ignore")
                dst.write_text(sanitize_text_file(content), encoding="utf-8")
                stats.included_files.append(str(dst))
                continue
            except Exception:
                pass
        shutil.copy2(src, dst)
        stats.included_files.append(str(dst))


def api_get_json(url: str, stats: ExportStats) -> Any:
    stats.api_calls.append(url)
    headers = {"Content-Type": "application/json"}
    if SUPERVISOR_TOKEN:
        headers["Authorization"] = f"Bearer {SUPERVISOR_TOKEN}"
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def try_api(url: str, stats: ExportStats) -> tuple[bool, Any]:
    try:
        return True, api_get_json(url, stats)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        stats.warnings.append(f"API-Aufruf fehlgeschlagen {url}: {exc}")
        return False, None


def redact_states_payload(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for item in states:
        attrs = sanitize_data(item.get("attributes", {}), "attributes")
        result.append(
            {
                "entity_id": item.get("entity_id"),
                "state": sanitize_data(item.get("state"), "state"),
                "last_changed": item.get("last_changed"),
                "last_updated": item.get("last_updated"),
                "attributes": attrs,
            }
        )
    return result


def export_api_inventory(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    metadata: dict[str, Any] = {}

    ok, supervisor_info = try_api("http://supervisor/info", stats)
    if ok:
        sanitized = sanitize_data(supervisor_info)
        write_json(export_dir / "inventory" / "supervisor_info.json", sanitized)
        metadata["supervisor_info_exported"] = True

    ok, core_info = try_api("http://supervisor/core/info", stats)
    if ok:
        sanitized = sanitize_data(core_info)
        write_json(export_dir / "inventory" / "core_info.json", sanitized)
        metadata["core_info_exported"] = True

    ok, addons_info = try_api("http://supervisor/addons", stats)
    if ok:
        sanitized = sanitize_data(addons_info)
        write_json(export_dir / "inventory" / "addons.json", sanitized)
        metadata["addons_exported"] = True

    ok, api_config = try_api("http://supervisor/core/api/config", stats)
    if ok:
        sanitized = sanitize_data(api_config)
        write_json(export_dir / "inventory" / "api_config.json", sanitized)
        metadata["api_config_exported"] = True

    if options.get("include_service_catalog", True):
        ok, services = try_api("http://supervisor/core/api/services", stats)
        if ok:
            sanitized = sanitize_data(services)
            write_json(export_dir / "inventory" / "services.json", sanitized)
            metadata["services_exported"] = True

    if options.get("include_current_state_snapshot", True):
        ok, states = try_api("http://supervisor/core/api/states", stats)
        if ok and isinstance(states, list):
            redacted_states = redact_states_payload(states)
            write_ndjson(export_dir / "runtime" / "state_snapshot.ndjson", redacted_states)
            metadata["state_snapshot_count"] = len(redacted_states)

    return metadata


def export_config_files(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    raw_root = export_dir / "source_sanitized" / "config"
    norm_root = export_dir / "normalized" / "config"
    details: dict[str, Any] = {"yaml_files": [], "directories": []}

    top_level_files = [
        "configuration.yaml",
        "automations.yaml",
        "scripts.yaml",
        "scenes.yaml",
        "secrets.yaml",
        "ui-lovelace.yaml",
        "customize.yaml",
        "customize_glob.yaml",
        "groups.yaml",
    ]

    for name in top_level_files:
        src = HA_CONFIG_DIR / name
        if not src.exists():
            continue
        raw_dst = raw_root / name
        normalized_dst = norm_root / f"{name}.json"
        export_yaml(src, raw_dst, normalized_dst, stats)
        details["yaml_files"].append(name)

    def export_directory_yaml(dir_name: str) -> None:
        src_root = HA_CONFIG_DIR / dir_name
        if not src_root.exists():
            return
        details["directories"].append(dir_name)
        for src in iter_files(src_root):
            if src.suffix.lower() not in {".yaml", ".yml"}:
                continue
            rel = src.relative_to(HA_CONFIG_DIR)
            raw_dst = raw_root / rel
            normalized_dst = norm_root / f"{rel.as_posix().replace('/', '__')}.json"
            export_yaml(src, raw_dst, normalized_dst, stats)

    if options.get("include_blueprints", True):
        export_directory_yaml("blueprints")
    export_directory_yaml("packages")
    export_directory_yaml("themes")
    if options.get("include_dashboards", True):
        export_directory_yaml("dashboards")

    if options.get("include_custom_components", True):
        copy_tree_sanitized(
            HA_CONFIG_DIR / "custom_components",
            export_dir / "source_sanitized" / "custom_components",
            stats,
            text_mode=True,
        )
        details["directories"].append("custom_components")

    if options.get("include_python_scripts", True):
        copy_tree_sanitized(
            HA_CONFIG_DIR / "python_scripts",
            export_dir / "source_sanitized" / "python_scripts",
            stats,
            text_mode=True,
        )
        details["directories"].append("python_scripts")

    if options.get("include_pyscript", True):
        copy_tree_sanitized(
            HA_CONFIG_DIR / "pyscript",
            export_dir / "source_sanitized" / "pyscript",
            stats,
            text_mode=True,
        )
        details["directories"].append("pyscript")

    return details


def export_storage(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    storage_root = HA_CONFIG_DIR / ".storage"
    raw_root = export_dir / "source_sanitized" / "storage"
    norm_root = export_dir / "normalized" / "storage"
    info: dict[str, Any] = {"included": [], "available": []}

    if not storage_root.exists():
        stats.excluded_items.append(".storage fehlt")
        return info

    for src in iter_files(storage_root):
        name = src.name
        info["available"].append(name)
        if not should_export_storage(name):
            continue
        raw_dst = raw_root / name
        normalized_dst = norm_root / f"{name}.json"
        export_json(src, raw_dst, normalized_dst, stats)
        info["included"].append(name)

    write_json(export_dir / "inventory" / "storage_inventory.json", info)
    return info


def tail_lines(path: Path, count: int) -> str:
    dq: deque[str] = deque(maxlen=count)
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            dq.append(line)
    return "".join(dq)


def export_logs(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> None:
    if not options.get("include_logs", True):
        return
    log_file = HA_CONFIG_DIR / "home-assistant.log"
    if not log_file.exists():
        stats.excluded_items.append("home-assistant.log fehlt")
        return
    try:
        text = tail_lines(log_file, int(options.get("max_log_lines", 4000)))
        sanitized = sanitize_text_file(text)
        out = export_dir / "runtime" / "home-assistant.log.tail.txt"
        ensure_dir(out.parent)
        out.write_text(sanitized, encoding="utf-8")
        stats.included_files.append(str(out))
    except Exception as exc:
        stats.warnings.append(f"Log-Export fehlgeschlagen: {exc}")


def query_one(cursor: sqlite3.Cursor, sql: str, params: tuple[Any, ...] = ()) -> Any:
    cursor.execute(sql, params)
    row = cursor.fetchone()
    if row is None:
        return None
    return row[0] if len(row) == 1 else row


def export_recorder_summary(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    summary: dict[str, Any] = {"exported": False}
    if not options.get("include_recorder_summary", True):
        return summary

    db_path = HA_CONFIG_DIR / "home-assistant_v2.db"
    if not db_path.exists():
        stats.excluded_items.append("Recorder-DB fehlt")
        return summary

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        summary["tables"] = tables
        table_counts: dict[str, Any] = {}
        for table in tables:
            try:
                table_counts[table] = query_one(cursor, f"SELECT COUNT(*) FROM {table}")
            except sqlite3.DatabaseError:
                table_counts[table] = None
        summary["table_counts"] = table_counts

        days = int(options.get("recorder_days", 14))
        cutoff = (now_utc() - timedelta(days=days)).timestamp()
        summary["days"] = days

        entity_rows: list[dict[str, Any]] = []
        if "states" in tables and "states_meta" in tables:
            try:
                cursor.execute(
                    """
                    SELECT sm.entity_id,
                           COUNT(*) AS row_count,
                           MIN(s.last_updated_ts) AS first_ts,
                           MAX(s.last_updated_ts) AS last_ts,
                           COUNT(DISTINCT s.state) AS distinct_states
                    FROM states s
                    JOIN states_meta sm ON s.metadata_id = sm.metadata_id
                    WHERE s.last_updated_ts >= ?
                    GROUP BY sm.entity_id
                    ORDER BY row_count DESC
                    LIMIT 1000
                    """,
                    (cutoff,),
                )
                for entity_id, row_count, first_ts, last_ts, distinct_states in cursor.fetchall():
                    entity_rows.append(
                        {
                            "entity_id": entity_id,
                            "row_count": row_count,
                            "first_ts": first_ts,
                            "last_ts": last_ts,
                            "distinct_states": distinct_states,
                        }
                    )
            except sqlite3.DatabaseError as exc:
                stats.warnings.append(f"Recorder-Entity-Summary fehlgeschlagen: {exc}")

        summary["top_entities"] = entity_rows[:200]
        write_json(export_dir / "runtime" / "recorder_summary.json", summary)
        if entity_rows:
            write_ndjson(export_dir / "runtime" / "recorder_top_entities.ndjson", entity_rows)
        summary["exported"] = True
        conn.close()
        return summary
    except Exception as exc:
        stats.warnings.append(f"Recorder-Export fehlgeschlagen: {exc}")
        return summary


def generate_export_summary(
    export_dir: Path,
    options: dict[str, Any],
    stats: ExportStats,
    config_info: dict[str, Any],
    storage_info: dict[str, Any],
    api_info: dict[str, Any],
    recorder_info: dict[str, Any],
) -> None:
    included_hint = [
        "Sanitisierte Konfigurationsdateien",
        "Normalisierte JSON/NDJSON-Dateien",
        "Entity-/Device-/Area-Registries",
        "Config Entries (sanitisiert)",
        "Add-on- und System-Inventar",
        "Aktueller States-Snapshot" if options.get("include_current_state_snapshot", True) else "Kein States-Snapshot",
        "Service-Katalog" if options.get("include_service_catalog", True) else "Kein Service-Katalog",
        "Recorder-Zusammenfassung" if options.get("include_recorder_summary", True) else "Keine Recorder-Zusammenfassung",
        "Log-Tail" if options.get("include_logs", True) else "Kein Log-Tail",
    ]

    excluded_by_design = [
        "Echte Secret-Werte",
        "Auth-/Token-Dateien",
        "SSL-Schlüssel und Zertifikate",
        "Volle Recorder-Datenbank",
        "Medien-Dateien",
        "Zigbee-/Z-Wave-Netzwerkschlüssel",
        "Komplette Drittanbieter-Add-on-Konfigurationsordner",
    ]

    lines = [
        "# ChatGPT Home Assistant Export Summary",
        "",
        f"Erstellt: {now_utc().isoformat()}",
        "",
        "## Ziel",
        "Dieser Export ist für eine andere ChatGPT-Instanz gedacht, damit sie dein Setup möglichst fehlerarm analysieren, verbessern, erweitern und refactoren kann.",
        "",
        "## Enthalten",
    ]
    lines.extend(f"- {item}" for item in included_hint)
    lines.extend(
        [
            "",
            "## Bewusst ausgeschlossen",
        ]
    )
    lines.extend(f"- {item}" for item in excluded_by_design)
    lines.extend(
        [
            "",
            "## Wichtige Einstiegsdateien für ChatGPT",
            "- metadata/export_manifest.json",
            "- metadata/export_summary.md",
            "- inventory/*.json",
            "- normalized/storage/*.json",
            "- normalized/config/*.json",
            "- runtime/state_snapshot.ndjson",
            "- runtime/recorder_summary.json",
            "",
            "## Beobachtungen",
            f"- Exportierte YAML-Dateien: {len(config_info.get('yaml_files', []))}",
            f"- Exportierte Verzeichnisse: {', '.join(config_info.get('directories', [])) or 'keine'}",
            f"- Exportierte .storage-Dateien: {len(storage_info.get('included', []))}",
            f"- API-Aufrufe erfolgreich/versucht: {len(api_info)} Metadatenblöcke, {len(stats.api_calls)} Aufrufe",
            f"- Recorder exportiert: {'ja' if recorder_info.get('exported') else 'nein'}",
            "",
            "## Warnungen",
        ]
    )
    if stats.warnings:
        lines.extend(f"- {warning}" for warning in stats.warnings)
    else:
        lines.append("- Keine")

    out = export_dir / "metadata" / "export_summary.md"
    ensure_dir(out.parent)
    out.write_text("\n".join(lines), encoding="utf-8")
    stats.included_files.append(str(out))


def create_checksums(export_dir: Path) -> None:
    checksum_path = export_dir / "metadata" / "checksums.sha256"
    ensure_dir(checksum_path.parent)
    with checksum_path.open("w", encoding="utf-8") as out:
        for path in sorted(p for p in export_dir.rglob("*") if p.is_file() and p != checksum_path):
            rel = path.relative_to(export_dir)
            out.write(f"{sha256_file(path)}  {rel.as_posix()}\n")


def create_archive(export_dir: Path) -> Path:
    archive_path = export_dir.with_suffix(".tar.gz")
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(export_dir, arcname=export_dir.name)
    return archive_path


def main() -> int:
    options = load_options()
    prefix = str(options.get("export_name_prefix", "ha_chatgpt_export")).strip() or "ha_chatgpt_export"
    timestamp = now_utc().strftime("%Y%m%dT%H%M%SZ")
    export_dir = SHARE_DIR / f"{prefix}_{timestamp}"
    ensure_dir(export_dir)
    stats = ExportStats()

    config_info = export_config_files(export_dir, options, stats)
    storage_info = export_storage(export_dir, options, stats)
    api_info = export_api_inventory(export_dir, options, stats)
    recorder_info = export_recorder_summary(export_dir, options, stats)
    export_logs(export_dir, options, stats)

    generate_export_summary(export_dir, options, stats, config_info, storage_info, api_info, recorder_info)
    create_checksums(export_dir)
    archive_path = create_archive(export_dir)

    included_file_count = sum(1 for path in export_dir.rglob("*") if path.is_file()) + 1
    manifest = {
        "exporter": {
            "name": "ChatGPT HA Exporter",
            "version": EXPORTER_VERSION,
            "created_at": now_utc().isoformat(),
        },
        "paths": {
            "homeassistant_config": str(HA_CONFIG_DIR),
            "share": str(SHARE_DIR),
            "export_dir": str(export_dir),
            "archive_path": str(archive_path),
        },
        "options": options,
        "counts": {
            "included_files": included_file_count,
            "warnings": len(stats.warnings),
            "api_calls": len(stats.api_calls),
        },
        "config_info": config_info,
        "storage_info": storage_info,
        "api_info": api_info,
        "recorder_info": recorder_info,
        "warnings": stats.warnings,
        "excluded_items": stats.excluded_items,
    }

    write_json(export_dir / "metadata" / "export_manifest.json", manifest)
    create_checksums(export_dir)

    print(f"Export-Verzeichnis: {export_dir}")
    print(f"Archiv: {archive_path}")
    if stats.warnings:
        print("Warnungen:")
        for warning in stats.warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        print("UNBEHANDELTER FEHLER")
        traceback.print_exc()
        raise
