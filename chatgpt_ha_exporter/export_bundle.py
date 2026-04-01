#!/usr/bin/env python3
from __future__ import annotations
import fnmatch
import hashlib
import json
import os
import re
import shutil
import socket
import sqlite3
import tarfile
import time
import traceback
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import yaml
HA_CONFIG_DIR = Path("/homeassistant")
ADDON_CONFIG_DIR = Path("/config")
DATA_DIR = Path("/data")
SHARE_DIR = Path("/share")
WORK_DIR = DATA_DIR / "workdir"
OPTIONS_PATH = DATA_DIR / "options.json"
SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
EXPORTER_VERSION = "0.5.6"
TEXT_FILE_SUFFIXES = {
    ".txt", ".yaml", ".yml", ".json", ".py", ".js", ".ts", ".md", ".conf", ".cfg", ".ini", ".xml", ".csv", ".log", ".html", ".css", ".sh",
}
YAML_EXTENSIONS = {".yaml", ".yml"}
HELPER_DOMAINS = {
    "input_boolean",
    "input_number",
    "input_select",
    "input_datetime",
    "input_text",
    "input_button",
    "counter",
    "timer",
    "schedule",
}
DEFAULT_OPTIONS: dict[str, Any] = {
    "export_name_prefix": "ha_chatgpt_export",
    "include_current_state_snapshot": True,
    "include_service_catalog": True,
    "include_dashboards": True,
    "include_blueprints": True,
    "include_custom_components": True,
    "include_python_scripts": True,
    "include_pyscript": True,
    "include_appdaemon": True,
    "include_esphome": True,
    "include_themes": True,
    "include_logs": True,
    "include_log_archives": True,
    "max_log_lines": 500,
    "include_recorder_summary": True,
    "include_recorder_deep_export": True,
    "include_recorder_db_copy": False,
    "recorder_days": 3,
    "recorder_state_sample_limit": 2000,
    "recorder_event_sample_limit": 1000,
    "recorder_statistics_limit": 500,
    "recorder_entity_history_limit": 100,
    "include_raw_storage_files": True,
    "include_extended_storage": True,
    "include_security_storage": True,
    "include_backup_metadata": True,
    "include_frontend_storage": True,
    "include_trace_storage": True,
    "include_helper_source_definitions": True,
    "include_template_source_definitions": True,
    "include_relationship_integrity_report": True,
    "include_supervisor_logs": True,
    "include_addon_logs": True,
    "addon_log_lines": 250,
    "include_multi_state_snapshots": True,
    "multi_state_snapshot_count": 3,
    "multi_state_snapshot_interval_seconds": 4,
    "include_backup_deep_context": True,
    "include_operator_intent_template": True,
    "include_operator_intent_import": True,
    "include_security_exposure_report": True,
    "include_addon_options_export": True,
    "include_integration_profiles": True,
    "include_uncertainty_register": True,
    "include_addon_stats": True,
    "slim_hacs_assets": True,
}
SENSITIVE_EXACT_KEYS = {
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "client_secret",
    "private_key",
    "network_key",
    "security_key",
    "pan_id",
    "extended_pan_id",
}
SENSITIVE_TOKEN_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "private",
    "certificate",
    "cert",
    "webhook",
    "authorization",
    "bearer",
    "cloudhook",
    "cookie",
    "csrf",
    "ssid",
    "psk",
    "wpa",
    "mac",
    "serial",
    "imei",
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
    "street",
    "postal",
    "zip",
    "city",
    "country",
}
RELATIONSHIP_KEY_PARTS = {
    "device_id": "device",
    "area_id": "area",
    "floor_id": "floor",
    "label_id": "label",
    "config_entry_id": "config_entry",
    "config_entries": "config_entry",
    "entry_id": "config_entry",
    "primary_config_entry": "config_entry",
}
ENTITY_ID_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
NETWORK_VALUE_KEY_PARTS = {"host", "hostname", "ip", "address", "server", "broker", "url", "uri"}
IDENTIFIER_PRESERVE_KEYS = {"slug", "version", "version_latest", "components", "domain", "platform", "repository", "event_type", "state", "title", "name", "timezone", "system_managed", "source"}

def key_suggests_network_value(parent_key: str | None) -> bool:
    if not parent_key:
        return False
    key = parent_key.lower()
    return any(part in key for part in NETWORK_VALUE_KEY_PARTS)

def key_suggests_identifier(parent_key: str | None) -> bool:
    if not parent_key:
        return False
    key = parent_key.lower()
    if key in IDENTIFIER_PRESERVE_KEYS:
        return False
    return key == "id" or key.endswith("_id") or "uuid" in key or key == "unique_id" or key == "client_id"

def is_entity_id_like(value: str) -> bool:
    return bool(ENTITY_ID_RE.fullmatch(value.strip()))

REGISTRY_ID_CONTEXT = {
    "core.device_registry": {"path_contains": ("devices",), "kind": "device", "keys": {"id", "config_entries", "area_id", "primary_config_entry"}},
    "core.entity_registry": {"path_contains": ("entities",), "kind": "entity_registry", "keys": {"device_id", "config_entry_id", "area_id", "id"}},
    "core.area_registry": {"path_contains": ("areas",), "kind": "area", "keys": {"id", "floor_id"}},
    "core.floor_registry": {"path_contains": ("floors",), "kind": "floor", "keys": {"id"}},
    "core.label_registry": {"path_contains": ("labels",), "kind": "label", "keys": {"id"}},
    "core.config_entries": {"path_contains": ("entries",), "kind": "config_entry", "keys": {"entry_id", "id"}},
}
TEXT_LINE_REDACTIONS = [
    (re.compile(r"(?im)^(\s*[^#\n]*?(?:password|passwd|token|secret|api[_-]?key|client_secret|refresh_token|access_token|webhook_id|webhook_url)\s*:\s*).*$"), r"\1<redacted>"),
    (re.compile(r"(?im)(Authorization\s*:\s*Bearer\s+)[^\s]+"), r"\1<redacted>"),
    (re.compile(r"(?im)(mqtt://[^:@\s]+:)[^@\s]+(@)"), r"\1<redacted>\2"),
    (re.compile(r"(?im)(https?://)([^/@\s:]+)(:[^@\s]+)?@"), r"\1<redacted-user>@"),
]
STORAGE_EXACT_BASE = {
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
    "trace.saved_traces",
    "repairs.issue_registry",
    "input_boolean",
    "input_number",
    "input_select",
    "input_datetime",
    "input_text",
    "input_button",
    "counter",
    "schedule",
    "timer",
    "template",
    "http",
    "http.auth",
    "core.network",
    "auth_provider.homeassistant",
    "homeassistant.exposed_entities",
    "application_credentials",
    "backup",
    "frontend.system_data",
    "frontend_panels",
    "mobile_app",
    "assist_pipeline.pipelines",
    "bluetooth.passive_update_processor",
    "bluetooth.remote_scanners",
    "esphome.dashboard",
    "hacs.critical",
    "hacs.data",
    "hacs.hacs",
    "hacs.repositories",
    "auth",
}
STORAGE_PREFIX_BASE = (
    "lovelace.",
    "frontend.user_data_",
    "esphome.",
)
STORAGE_GLOB_BASE = (
    "broadlink_remote_*_codes",
    "broadlink_remote_*_flags",
)
SKIP_NAMES = {".DS_Store", "__pycache__"}
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
@dataclass
class OutputTargetResult:
    label: str
    root: Path
    export_dir: Path | None = None
    archive_path: Path | None = None
    ok: bool = False
    message: str = ""
@dataclass
class OutputTargets:
    primary: OutputTargetResult
    mirrors: list[OutputTargetResult]
class Pseudonymizer:
    def __init__(self) -> None:
        self.maps: dict[str, dict[str, str]] = defaultdict(dict)
        self.counters: Counter[str] = Counter()
    def pseudonymize(self, scope: str, value: str, prefix: str | None = None) -> str:
        text = str(value)
        if text in self.maps[scope]:
            return self.maps[scope][text]
        self.counters[scope] += 1
        token_prefix = prefix or scope.replace("_", "-")
        digest = hashlib.sha256(f"{scope}|{text}".encode("utf-8")).hexdigest()[:10]
        token = f"<{token_prefix}-{self.counters[scope]:03d}-{digest}>"
        self.maps[scope][text] = token
        return token
PSEUDONYMIZER = Pseudonymizer()
def now_utc() -> datetime:
    return datetime.now(timezone.utc)
def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
def read_export_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return read_json_file(path)
    except Exception:
        return None
def flatten_strings(obj: Any, *, max_items: int = 500) -> list[str]:
    values: list[str] = []
    def walk(item: Any) -> None:
        if len(values) >= max_items:
            return
        if isinstance(item, str):
            values.append(item)
        elif isinstance(item, dict):
            for v in item.values():
                walk(v)
        elif isinstance(item, list):
            for v in item:
                walk(v)
    walk(obj)
    return values
def recursive_find_key(obj: Any, key_name: str) -> list[Any]:
    results: list[Any] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key) == key_name:
                results.append(value)
            results.extend(recursive_find_key(value, key_name))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(recursive_find_key(item, key_name))
    return results
def count_entities_in_structure(obj: Any) -> int:
    entity_ids = set()
    def walk(item: Any) -> None:
        if isinstance(item, dict):
            for key, value in item.items():
                if key == 'entity_id' and isinstance(value, str):
                    entity_ids.add(value)
                else:
                    walk(value)
        elif isinstance(item, list):
            for value in item:
                walk(value)
    walk(obj)
    return len(entity_ids)
def count_mappingish_items(obj: Any) -> int | None:
    if isinstance(obj, dict):
        for key in ('data', 'items', 'entries', 'entities', 'providers', 'users', 'pipelines', 'apps', 'credentials', 'panels', 'mounts', 'backups'):
            value = obj.get(key)
            if isinstance(value, (list, dict)):
                return len(value)
        return len(obj)
    if isinstance(obj, list):
        return len(obj)
    return None
def summarize_schema_keys(schema: Any) -> list[str]:
    if not isinstance(schema, dict):
        return []
    return sorted(str(k) for k in schema.keys())[:500]
def trim_addon_info_payload(info: dict[str, Any]) -> dict[str, Any]:
    keep = {
        'name', 'slug', 'version', 'version_latest', 'update_available', 'installed', 'state',
        'boot', 'auto_update', 'watchdog', 'ingress', 'ingress_panel', 'hassio_api',
        'hassio_role', 'homeassistant_api', 'build', 'stage', 'repository', 'advanced',
        'host_network', 'host_pid', 'host_ipc', 'host_dbus', 'full_access', 'privileged',
        'protected', 'startup', 'services_role', 'system_managed', 'system_managed_config_entry',
        'network', 'network_description', 'options', 'schema', 'translation', 'translations',
        'url', 'webui', 'documentation', 'changelog', 'arch', 'machine', 'devices', 'usb',
        'audio', 'audio_input', 'audio_output', 'gpio', 'udev', 'docker_api', 'auth_api'
    }
    trimmed = {k: v for k, v in info.items() if k in keep}
    return trimmed
def truthy_path(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
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
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def looks_sensitive_key(key: str) -> bool:
    k = key.lower().replace("-", "_")
    if k in SENSITIVE_EXACT_KEYS:
        return True
    tokens = [token for token in re.split(r"[^a-z0-9]+", k) if token]
    return any(token in SENSITIVE_TOKEN_KEYS for token in tokens)
def looks_location_key(key: str) -> bool:
    k = key.lower()
    return any(part in k for part in LOCATION_KEY_PARTS)
def should_skip_path(path: Path) -> bool:
    if path.name in SKIP_NAMES:
        return True
    if path.suffix in SKIP_SUFFIXES:
        return True
    return any(part == "__pycache__" for part in path.parts)
def iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file())
def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_FILE_SUFFIXES
def sanitize_text_file(text: str) -> str:
    result = text
    for pattern, repl in TEXT_LINE_REDACTIONS:
        result = pattern.sub(repl, result)
    # redact obvious URLs with credentials
    result = re.sub(r"(?i)(https?://)([^/@\s:]+)(:[^@\s]+)?@", r"\1<redacted-user>@", result)
    result = re.sub(r"(?i)(mqtt://[^:@\s]+:)[^@\s]+(@)", r"\1<redacted>\2", result)
    return result
def sanitize_string(value: str, parent_key: str | None = None, context: dict[str, Any] | None = None) -> str:
    if parent_key and looks_sensitive_key(parent_key):
        return "<redacted>"
    if parent_key and looks_location_key(parent_key):
        return "<redacted>"
    if context and parent_key == "key" and context.get("storage_name"):
        return str(context["storage_name"])
    if context and parent_key == "id" and context.get("storage_name") in HELPER_DOMAINS:
        path_parts = tuple(context.get("path_parts", ()))
        if any(part in path_parts for part in ("items", "schedules", context.get("storage_name"))):
            return sanitize_text_file(value)
    if parent_key in RELATIONSHIP_KEY_PARTS and value:
        kind = RELATIONSHIP_KEY_PARTS[parent_key]
        return PSEUDONYMIZER.pseudonymize(kind, value)
    if context:
        storage_name = context.get("storage_name")
        path_parts: tuple[str, ...] = context.get("path_parts", ())
        registry_context = REGISTRY_ID_CONTEXT.get(storage_name)
        if registry_context and parent_key in registry_context["keys"] and any(part in path_parts for part in registry_context["path_contains"]):
            if parent_key == "id":
                return PSEUDONYMIZER.pseudonymize(registry_context["kind"], value)
            if parent_key == "config_entries":
                return PSEUDONYMIZER.pseudonymize("config_entry", value)
    trimmed = sanitize_text_file(value)
    if is_entity_id_like(trimmed):
        return trimmed
    try:
        parsed = urlparse(trimmed)
        if parsed.scheme and parsed.netloc:
            host = parsed.hostname or "host"
            pseudo_host = PSEUDONYMIZER.pseudonymize("host", host, "host")
            new_url = trimmed.replace(host, pseudo_host)
            if parsed.username:
                new_url = re.sub(rf"{re.escape(parsed.scheme)}://[^@]+@", f"{parsed.scheme}://<redacted-user>@", new_url)
            return new_url
    except Exception:
        pass
    if key_suggests_identifier(parent_key):
        if re.fullmatch(r"[0-9a-fA-F-]{36}", trimmed):
            return PSEUDONYMIZER.pseudonymize("uuid", trimmed, "uuid")
        if re.fullmatch(r"[A-Fa-f0-9]{16,}", trimmed) or re.fullmatch(r"[A-Za-z0-9_\-]{24,}", trimmed):
            return PSEUDONYMIZER.pseudonymize("opaque_id", trimmed, "id")
    if key_suggests_network_value(parent_key):
        host_like = trimmed.strip()
        if re.fullmatch(r"[A-Za-z0-9_.:-]+", host_like) and len(host_like) < 255:
            try:
                socket.inet_aton(host_like)
                return PSEUDONYMIZER.pseudonymize("ip", host_like, "ip")
            except OSError:
                if "." in host_like and not host_like.endswith(".yaml") and not host_like.endswith(".json"):
                    return PSEUDONYMIZER.pseudonymize("host", host_like, "host")
    if len(trimmed) > 8000:
        trimmed = trimmed[:8000] + "…<truncated>"
    return trimmed
def sanitize_data(obj: Any, parent_key: str | None = None, *, context: dict[str, Any] | None = None) -> Any:
    if isinstance(obj, dict):
        new: dict[str, Any] = {}
        base_path = tuple(context.get("path_parts", ())) if context else tuple()
        for key, value in obj.items():
            key_str = str(key)
            child_context = dict(context or {})
            child_context["path_parts"] = base_path + (key_str,)
            if looks_sensitive_key(key_str):
                new[key_str] = "<redacted>"
            elif looks_location_key(key_str):
                new[key_str] = "<redacted>"
            else:
                new[key_str] = sanitize_data(value, key_str, context=child_context)
        return new
    if isinstance(obj, list):
        base_path = tuple(context.get("path_parts", ())) if context else tuple()
        return [sanitize_data(item, parent_key, context={**(context or {}), "path_parts": base_path + (str(idx),)}) for idx, item in enumerate(obj)]
    if isinstance(obj, tuple):
        base_path = tuple(context.get("path_parts", ())) if context else tuple()
        return [sanitize_data(item, parent_key, context={**(context or {}), "path_parts": base_path + (str(idx),)}) for idx, item in enumerate(obj)]
    if isinstance(obj, str):
        return sanitize_string(obj, parent_key, context)
    return obj
def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
def write_ndjson(path: Path, rows: Iterable[Any]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")
def parse_yaml_file(src: Path) -> Any:
    text = src.read_text(encoding="utf-8", errors="ignore")
    return yaml.load(text, Loader=IgnoreUnknownLoader)
def export_raw_text(src: Path, dst: Path, stats: ExportStats) -> None:
    try:
        text = src.read_text(encoding="utf-8", errors="ignore")
        ensure_dir(dst.parent)
        dst.write_text(sanitize_text_file(text), encoding="utf-8")
        stats.included_files.append(str(dst))
    except Exception as exc:
        stats.warnings.append(f"Konnte Textdatei nicht exportieren: {src} ({exc})")
def export_yaml(src: Path, raw_dst: Path, normalized_dst: Path, stats: ExportStats) -> None:
    export_raw_text(src, raw_dst, stats)
    try:
        parsed = parse_yaml_file(src)
        sanitized = sanitize_data(parsed, context={"source": str(src), "path_parts": tuple()})
        write_json(normalized_dst, sanitized)
        stats.included_files.append(str(normalized_dst))
    except Exception as exc:
        stats.warnings.append(f"YAML-Normalisierung fehlgeschlagen für {src}: {exc}")
def export_json(src: Path, raw_dst: Path | None, normalized_dst: Path, stats: ExportStats, *, storage_name: str | None = None) -> None:
    if raw_dst is not None:
        try:
            raw = src.read_text(encoding="utf-8", errors="ignore")
            ensure_dir(raw_dst.parent)
            raw_dst.write_text(sanitize_text_file(raw), encoding="utf-8")
            stats.included_files.append(str(raw_dst))
        except Exception as exc:
            stats.warnings.append(f"JSON-Rohdatei konnte nicht exportiert werden {src}: {exc}")
    try:
        data = json.loads(src.read_text(encoding="utf-8", errors="ignore"))
        sanitized = sanitize_data(data, context={"source": str(src), "storage_name": storage_name, "path_parts": tuple()})
        write_json(normalized_dst, sanitized)
        stats.included_files.append(str(normalized_dst))
    except Exception as exc:
        stats.warnings.append(f"JSON-Normalisierung fehlgeschlagen für {src}: {exc}")
def copy_tree_sanitized(src_root: Path, dst_root: Path, stats: ExportStats) -> None:
    if not src_root.exists():
        stats.excluded_items.append(f"Fehlt: {src_root}")
        return
    for src in iter_files(src_root):
        if should_skip_path(src):
            continue
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        ensure_dir(dst.parent)
        if is_text_file(src):
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
    with urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)
def api_get_text(url: str, stats: ExportStats, accept: str = "text/plain") -> str:
    stats.api_calls.append(url)
    headers = {"Accept": accept}
    if SUPERVISOR_TOKEN:
        headers["Authorization"] = f"Bearer {SUPERVISOR_TOKEN}"
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="ignore")
def try_api_json(url: str, stats: ExportStats) -> tuple[bool, Any]:
    try:
        return True, api_get_json(url, stats)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        stats.warnings.append(f"API-Aufruf fehlgeschlagen {url}: {exc}")
        return False, None
def try_api_text(url: str, stats: ExportStats, accept: str = "text/plain") -> tuple[bool, str | None]:
    try:
        return True, api_get_text(url, stats, accept=accept)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        stats.warnings.append(f"API-Textaufruf fehlgeschlagen {url}: {exc}")
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
def detect_theme_include(configuration_text: str) -> dict[str, Any]:
    result = {
        "declared": False,
        "directive": None,
        "include_target": None,
        "checked_path": None,
        "status": "not_declared",
        "yaml_files": [],
        "non_yaml_files": [],
        "note": None,
    }
    pattern = re.compile(r"(?ms)^frontend\s*:\s*(?:#.*\n|\s+.*\n)*?\s+themes\s*:\s*(!include_dir_merge_named)\s+([^\s#]+)")
    match = pattern.search(configuration_text)
    if not match:
        return result
    result["declared"] = True
    result["directive"] = match.group(1)
    result["include_target"] = match.group(2).strip()
    path = HA_CONFIG_DIR / result["include_target"]
    result["checked_path"] = str(path)
    if not path.exists():
        result["status"] = "missing"
        result["note"] = f"configuration.yaml deklariert frontend/themes via {result['directive']} {result['include_target']}, aber das Verzeichnis {path} fehlt."
        return result
    if not path.is_dir():
        result["status"] = "unreadable"
        result["note"] = f"Der Theme-Pfad {path} ist kein lesbares Verzeichnis."
        return result
    try:
        files = sorted([p for p in path.iterdir() if p.is_file()])
    except Exception:
        result["status"] = "unreadable"
        result["note"] = f"Das Verzeichnis {path} war nicht lesbar."
        return result
    if not files:
        result["status"] = "empty"
        result["note"] = f"Das Verzeichnis {path} ist leer."
        return result
    result["yaml_files"] = [p.name for p in files if p.suffix.lower() in YAML_EXTENSIONS]
    result["non_yaml_files"] = [p.name for p in files if p.suffix.lower() not in YAML_EXTENSIONS]
    if result["yaml_files"]:
        result["status"] = "ok"
    else:
        result["status"] = "contains_non_yaml_only"
        result["note"] = f"In {path} wurden nur Nicht-YAML-Dateien gefunden."
    return result
def walk_helper_template_defs(obj: Any, source_name: str, source_type: str, *, path: tuple[str, ...] = ()) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    helpers: list[dict[str, Any]] = []
    templates: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = path + (str(key),)
            if key in HELPER_DOMAINS:
                helpers.append({
                    "source": source_name,
                    "source_type": source_type,
                    "helper_domain": key,
                    "path": "/".join(current_path),
                    "definition": sanitize_data(value, context={"path_parts": tuple(current_path)}),
                })
            if key == "template":
                templates.append({
                    "source": source_name,
                    "source_type": source_type,
                    "path": "/".join(current_path),
                    "definition": sanitize_data(value, context={"path_parts": tuple(current_path)}),
                })
            sub_helpers, sub_templates = walk_helper_template_defs(value, source_name, source_type, path=current_path)
            helpers.extend(sub_helpers)
            templates.extend(sub_templates)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            sub_helpers, sub_templates = walk_helper_template_defs(item, source_name, source_type, path=path + (str(idx),))
            helpers.extend(sub_helpers)
            templates.extend(sub_templates)
    return helpers, templates

def extract_helper_defs_from_storage_payload(data: Any, source_name: str) -> list[dict[str, Any]]:
    if source_name not in HELPER_DOMAINS or not isinstance(data, dict):
        return []
    payload = data.get("data", {})
    items: list[Any] = []
    if isinstance(payload, dict):
        if isinstance(payload.get("items"), list):
            items = payload.get("items") or []
        elif isinstance(payload.get(source_name), list):
            items = payload.get(source_name) or []
        elif source_name == "schedule" and isinstance(payload.get("schedules"), list):
            items = payload.get("schedules") or []
    definitions: list[dict[str, Any]] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        path = ("data", "items", str(idx))
        definitions.append({
            "source": source_name,
            "source_type": "storage",
            "helper_domain": source_name,
            "helper_id": item.get("id"),
            "name": item.get("name"),
            "path": "/".join(path),
            "definition": sanitize_data(item, context={"storage_name": source_name, "path_parts": path}),
        })
    return definitions


def extract_template_defs_from_storage_payload(data: Any, source_name: str) -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    if not isinstance(data, dict):
        return definitions
    if source_name == "template":
        payload = data.get("data", {})
        candidates = []
        if isinstance(payload, dict):
            for key in ("items", "templates", "entities"):
                value = payload.get(key)
                if isinstance(value, list):
                    candidates = value
                    break
        for idx, item in enumerate(candidates):
            if not isinstance(item, dict):
                continue
            path = ("data", "items", str(idx))
            definitions.append({
                "source": source_name,
                "source_type": "storage",
                "template_kind": item.get("template_type") or item.get("type"),
                "name": item.get("name") or item.get("friendly_name"),
                "path": "/".join(path),
                "definition": sanitize_data(item, context={"storage_name": source_name, "path_parts": path}),
            })
    if source_name == "core.config_entries":
        entries = data.get("data", {}).get("entries", []) if isinstance(data.get("data"), dict) else []
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict) or entry.get("domain") != "template":
                continue
            options = entry.get("options", {}) if isinstance(entry.get("options"), dict) else {}
            path = ("data", "entries", str(idx))
            definitions.append({
                "source": source_name,
                "source_type": "storage",
                "entry_id": sanitize_data(entry.get("entry_id"), "entry_id", context={"storage_name": source_name, "path_parts": path + ("entry_id",)}),
                "name": entry.get("title") or options.get("name"),
                "template_kind": options.get("template_type"),
                "path": "/".join(path),
                "definition": sanitize_data({"domain": entry.get("domain"), "title": entry.get("title"), "options": options}, context={"storage_name": source_name, "path_parts": path}),
            })
    return definitions


def copy_tree_sanitized_if_exists(src_root: Path, dst_root: Path, stats: ExportStats) -> bool:
    if not src_root.exists():
        stats.excluded_items.append(f"Fehlt: {src_root}")
        return False
    copy_tree_sanitized(src_root, dst_root, stats)
    return True

def copy_custom_components_sanitized(src_root: Path, dst_root: Path, stats: ExportStats, *, slim_hacs_assets: bool = True) -> bool:
    if not src_root.exists():
        stats.excluded_items.append(f"Fehlt: {src_root}")
        return False
    for src in iter_files(src_root):
        if should_skip_path(src):
            continue
        rel = src.relative_to(src_root)
        rel_parts = [part.lower() for part in rel.parts]
        if slim_hacs_assets and rel_parts and rel_parts[0] == 'hacs':
            suffix = src.suffix.lower()
            name_lower = src.name.lower()
            in_static_tree = any(part in {'frontend', 'frontend_latest', 'dist', 'www', 'static', 'assets'} for part in rel_parts[1:])
            is_compressed_or_map = suffix in {'.map', '.gz', '.br'}
            is_font_or_blob = suffix in {'.woff', '.woff2', '.ttf', '.eot', '.otf'}
            is_frontend_bundle = suffix in {'.js', '.mjs', '.css', '.svg'} and (in_static_tree or 'bundle' in name_lower or 'chunk' in name_lower or 'frontend' in '/'.join(rel_parts[1:]))
            if is_compressed_or_map or is_font_or_blob or is_frontend_bundle:
                continue
        dst = dst_root / rel
        ensure_dir(dst.parent)
        if is_text_file(src):
            try:
                content = src.read_text(encoding='utf-8', errors='ignore')
                dst.write_text(sanitize_text_file(content), encoding='utf-8')
                stats.included_files.append(str(dst))
                continue
            except Exception:
                pass
        shutil.copy2(src, dst)
        stats.included_files.append(str(dst))
    return True
def export_config_files(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    raw_root = export_dir / "source_sanitized" / "config"
    norm_root = export_dir / "normalized" / "config"
    details: dict[str, Any] = {"yaml_files": [], "directories": [], "theme_include": {}}
    helper_defs: list[dict[str, Any]] = []
    template_defs: list[dict[str, Any]] = []
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
        "climate.yaml",
        "template.yaml",
        "input_boolean.yaml",
        "input_number.yaml",
        "input_select.yaml",
        "input_datetime.yaml",
        "input_text.yaml",
        "input_button.yaml",
        "counter.yaml",
        "timer.yaml",
        "schedule.yaml",
    ]
    configuration_text = ""
    for name in top_level_files:
        src = HA_CONFIG_DIR / name
        if not src.exists():
            continue
        raw_dst = raw_root / name
        normalized_dst = norm_root / f"{name}.json"
        export_yaml(src, raw_dst, normalized_dst, stats)
        details["yaml_files"].append(name)
        try:
            parsed = parse_yaml_file(src)
            h, t = walk_helper_template_defs(parsed, name, "yaml")
            helper_defs.extend(h)
            template_defs.extend(t)
        except Exception:
            pass
        if name == "configuration.yaml":
            configuration_text = src.read_text(encoding="utf-8", errors="ignore")
    def export_directory_yaml(dir_name: str) -> None:
        src_root = HA_CONFIG_DIR / dir_name
        if not src_root.exists():
            return
        details["directories"].append(dir_name)
        for src in iter_files(src_root):
            if src.suffix.lower() not in YAML_EXTENSIONS:
                continue
            rel = src.relative_to(HA_CONFIG_DIR)
            raw_dst = raw_root / rel
            normalized_dst = norm_root / f"{rel.as_posix().replace('/', '__')}.json"
            export_yaml(src, raw_dst, normalized_dst, stats)
            try:
                parsed = parse_yaml_file(src)
                h, t = walk_helper_template_defs(parsed, rel.as_posix(), "yaml")
                helper_defs.extend(h)
                template_defs.extend(t)
            except Exception:
                pass
    if options.get("include_blueprints", True):
        export_directory_yaml("blueprints")
    export_directory_yaml("packages")
    if options.get("include_dashboards", True):
        export_directory_yaml("dashboards")
    if options.get("include_esphome", True):
        export_directory_yaml("esphome")
    if options.get("include_appdaemon", True):
        export_directory_yaml("appdaemon")
    theme_info = detect_theme_include(configuration_text) if configuration_text else {
        "declared": False,
        "directive": None,
        "include_target": None,
        "checked_path": None,
        "status": "not_declared",
        "yaml_files": [],
        "non_yaml_files": [],
        "note": None,
    }
    details["theme_include"] = theme_info
    if theme_info.get("declared"):
        note = theme_info.get("note")
        if note:
            stats.warnings.append(note)
        if theme_info.get("status") == "ok" and options.get("include_themes", True):
            theme_rel = str(theme_info["include_target"])
            src_root = HA_CONFIG_DIR / theme_rel
            details["directories"].append(theme_rel)
            copy_tree_sanitized(src_root, raw_root / theme_rel, stats)
            export_directory_yaml(theme_rel)
    if options.get("include_custom_components", True) and copy_custom_components_sanitized(HA_CONFIG_DIR / "custom_components", export_dir / "source_sanitized" / "custom_components", stats, slim_hacs_assets=bool(options.get("slim_hacs_assets", True))):
        details["directories"].append("custom_components")
    if options.get("include_python_scripts", True) and copy_tree_sanitized_if_exists(HA_CONFIG_DIR / "python_scripts", export_dir / "source_sanitized" / "python_scripts", stats):
        details["directories"].append("python_scripts")
    if options.get("include_pyscript", True) and copy_tree_sanitized_if_exists(HA_CONFIG_DIR / "pyscript", export_dir / "source_sanitized" / "pyscript", stats):
        details["directories"].append("pyscript")
    if options.get("include_appdaemon", True):
        copy_tree_sanitized_if_exists(HA_CONFIG_DIR / "appdaemon", export_dir / "source_sanitized" / "appdaemon", stats)
    # ESPHome source files are exported under source_sanitized/config/esphome to avoid duplicate trees.
    if options.get("include_helper_source_definitions", True):
        write_json(export_dir / "inventory" / "helper_source_definitions.json", helper_defs)
        stats.included_files.append(str(export_dir / "inventory" / "helper_source_definitions.json"))
    if options.get("include_template_source_definitions", True):
        write_json(export_dir / "inventory" / "template_source_definitions.json", template_defs)
        stats.included_files.append(str(export_dir / "inventory" / "template_source_definitions.json"))
    write_json(export_dir / "inventory" / "config_inventory.json", details)
    stats.included_files.append(str(export_dir / "inventory" / "config_inventory.json"))
    return details
def build_storage_exact(options: dict[str, Any]) -> set[str]:
    names = set(STORAGE_EXACT_BASE)
    if not options.get("include_security_storage", True):
        names -= {"http", "http.auth", "core.network", "auth", "auth_provider.homeassistant", "homeassistant.exposed_entities", "application_credentials"}
    if not options.get("include_backup_metadata", True):
        names -= {"backup"}
    if not options.get("include_frontend_storage", True):
        names -= {"frontend.system_data", "frontend_panels"}
    if not options.get("include_trace_storage", True):
        names -= {"trace.saved_traces", "repairs.issue_registry"}
    return names
def should_export_storage(name: str, options: dict[str, Any]) -> bool:
    exact = build_storage_exact(options)
    if name in exact:
        return True
    prefixes = list(STORAGE_PREFIX_BASE)
    if not options.get("include_frontend_storage", True):
        prefixes = [p for p in prefixes if not p.startswith("frontend.user_data_")]
    for prefix in prefixes:
        if name.startswith(prefix):
            return True
    for pattern in STORAGE_GLOB_BASE:
        if fnmatch.fnmatch(name, pattern):
            return True
    if not options.get("include_extended_storage", True):
        return name in STORAGE_EXACT_BASE or name.startswith("lovelace.")
    return False
def export_storage(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    storage_root = HA_CONFIG_DIR / ".storage"
    raw_root = export_dir / "source_sanitized" / "storage"
    norm_root = export_dir / "normalized" / "storage"
    info: dict[str, Any] = {"included": [], "available": [], "available_only": []}
    helper_defs: list[dict[str, Any]] = []
    template_defs: list[dict[str, Any]] = []
    if not storage_root.exists():
        stats.excluded_items.append(".storage fehlt")
        write_json(export_dir / "inventory" / "storage_inventory.json", info)
        return info
    for src in iter_files(storage_root):
        name = src.name
        info["available"].append(name)
        if should_export_storage(name, options):
            raw_dst = (raw_root / name) if options.get("include_raw_storage_files", True) else None
            normalized_dst = norm_root / f"{name}.json"
            export_json(src, raw_dst, normalized_dst, stats, storage_name=name)
            info["included"].append(name)
            try:
                data = json.loads(src.read_text(encoding="utf-8", errors="ignore"))
                helper_defs.extend(extract_helper_defs_from_storage_payload(data, name))
                template_defs.extend(extract_template_defs_from_storage_payload(data, name))
            except Exception:
                pass
        else:
            info["available_only"].append(name)
    write_json(export_dir / "inventory" / "storage_inventory.json", info)
    stats.included_files.append(str(export_dir / "inventory" / "storage_inventory.json"))
    if options.get("include_helper_source_definitions", True):
        helper_path = export_dir / "inventory" / "helper_source_definitions.storage.json"
        write_json(helper_path, helper_defs)
        stats.included_files.append(str(helper_path))
    if options.get("include_template_source_definitions", True):
        template_path = export_dir / "inventory" / "template_source_definitions.storage.json"
        write_json(template_path, template_defs)
        stats.included_files.append(str(template_path))
    return info
def export_api_inventory(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    ok, supervisor_info = try_api_json("http://supervisor/info", stats)
    if ok:
        write_json(export_dir / "inventory" / "supervisor_info.json", sanitize_data(supervisor_info))
        metadata["supervisor_info_exported"] = True
    ok, core_info = try_api_json("http://supervisor/core/info", stats)
    if ok:
        write_json(export_dir / "inventory" / "core_info.json", sanitize_data(core_info))
        metadata["core_info_exported"] = True
    ok, addons_info = try_api_json("http://supervisor/addons", stats)
    addon_slugs: list[str] = []
    if ok:
        write_json(export_dir / "inventory" / "addons.json", sanitize_data(addons_info))
        metadata["addons_exported"] = True
        addon_slugs = [a.get("slug") for a in addons_info.get("data", {}).get("addons", []) if isinstance(a, dict) and a.get("slug")]
    ok, api_config = try_api_json("http://supervisor/core/api/config", stats)
    if ok:
        write_json(export_dir / "inventory" / "api_config.json", sanitize_data(api_config))
        metadata["api_config_exported"] = True
    if options.get("include_service_catalog", True):
        ok, services = try_api_json("http://supervisor/core/api/services", stats)
        if ok:
            write_json(export_dir / "inventory" / "services.json", sanitize_data(services))
            metadata["services_exported"] = True
    if options.get("include_current_state_snapshot", True):
        ok, states = try_api_json("http://supervisor/core/api/states", stats)
        if ok and isinstance(states, list):
            redacted_states = redact_states_payload(states)
            write_ndjson(export_dir / "runtime" / "state_snapshot.ndjson", redacted_states)
            metadata["state_snapshot_count"] = len(redacted_states)
    if options.get("include_supervisor_logs", True):
        line_count = int(options.get("addon_log_lines", 250))
        log_targets = {
            "core": f"http://supervisor/core/logs/latest?{urlencode({'lines': line_count})}",
            "supervisor": f"http://supervisor/supervisor/logs/latest?{urlencode({'lines': line_count})}",
        }
        for label, url in log_targets.items():
            ok, text = try_api_text(url, stats, accept="text/x-log")
            if ok and text is not None:
                out = export_dir / "runtime" / f"{label}.latest.log.txt"
                ensure_dir(out.parent)
                out.write_text(sanitize_text_file(text), encoding="utf-8")
                stats.included_files.append(str(out))
                metadata[f"{label}_log_exported"] = True
    if options.get("include_addon_logs", True) and addon_slugs:
        addon_logs_dir = export_dir / "runtime" / "addon_logs"
        for slug in addon_slugs:
            url = f"http://supervisor/addons/{slug}/logs/latest?{urlencode({'lines': int(options.get('addon_log_lines', 250))})}"
            ok, text = try_api_text(url, stats, accept="text/x-log")
            if ok and text is not None:
                out = addon_logs_dir / f"{slug}.latest.log.txt"
                ensure_dir(out.parent)
                out.write_text(sanitize_text_file(text), encoding="utf-8")
                stats.included_files.append(str(out))
        metadata["addon_log_targets"] = addon_slugs
    return metadata
def timestamp_to_iso(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
    except Exception:
        return None
def get_table_columns(cursor: sqlite3.Cursor, table: str) -> list[str]:
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]
def table_exists(cursor: sqlite3.Cursor, table: str) -> bool:
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None
def parse_jsonish(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list, int, float, bool)):
        return value
    if isinstance(value, bytes):
        value = value.decode('utf-8', errors='ignore')
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return stripped
        if (stripped.startswith('{') and stripped.endswith('}')) or (stripped.startswith('[') and stripped.endswith(']')):
            try:
                return json.loads(stripped)
            except Exception:
                return value
    return value
def build_state_signature(item: dict[str, Any]) -> str:
    payload = {
        "state": item.get("state"),
        "last_changed": item.get("last_changed"),
        "last_updated": item.get("last_updated"),
        "attributes": item.get("attributes", {}),
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
def capture_state_snapshot(stats: ExportStats) -> tuple[bool, list[dict[str, Any]], str | None]:
    ok, states = try_api_json("http://supervisor/core/api/states", stats)
    captured_at = now_utc().isoformat()
    if ok and isinstance(states, list):
        return True, redact_states_payload(states), captured_at
    return False, [], captured_at
def export_multi_state_snapshots(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    info: dict[str, Any] = {"generated": False, "snapshots": []}
    if not options.get("include_multi_state_snapshots", True):
        return info
    count = max(2, int(options.get("multi_state_snapshot_count", 3)))
    interval = max(1, int(options.get("multi_state_snapshot_interval_seconds", 4)))
    snapshots_dir = export_dir / "runtime" / "state_snapshots"
    previous_map: dict[str, str] | None = None
    previous_capture: str | None = None
    deltas: list[dict[str, Any]] = []
    for idx in range(count):
        ok, states, captured_at = capture_state_snapshot(stats)
        if ok:
            filename = f"snapshot_{idx + 1:03d}.ndjson"
            path = snapshots_dir / filename
            write_ndjson(path, states)
            stats.included_files.append(str(path))
            current_map = {item.get("entity_id"): build_state_signature(item) for item in states if item.get("entity_id")}
            info["snapshots"].append({
                "index": idx + 1,
                "captured_at": captured_at,
                "file": f"runtime/state_snapshots/{filename}",
                "entity_count": len(states),
            })
            if previous_map is not None:
                changed_entities = sorted([eid for eid, sig in current_map.items() if previous_map.get(eid) != sig])
                disappeared = sorted([eid for eid in previous_map.keys() if eid not in current_map])
                appeared = sorted([eid for eid in current_map.keys() if eid not in previous_map])
                deltas.append({
                    "from_capture": previous_capture,
                    "to_capture": captured_at,
                    "changed_entity_count": len(changed_entities),
                    "appeared_entity_count": len(appeared),
                    "disappeared_entity_count": len(disappeared),
                    "sample_changed_entities": changed_entities[:100],
                    "sample_appeared_entities": appeared[:100],
                    "sample_disappeared_entities": disappeared[:100],
                })
            previous_map = current_map
            previous_capture = captured_at
        if idx < count - 1:
            time.sleep(interval)
    info["generated"] = bool(info["snapshots"])
    info["interval_seconds"] = interval
    info["requested_snapshot_count"] = count
    info["captured_snapshot_count"] = len(info["snapshots"])
    info["deltas"] = deltas
    out = export_dir / "runtime" / "state_snapshots_summary.json"
    write_json(out, info)
    stats.included_files.append(str(out))
    return info
def export_backup_context(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    info: dict[str, Any] = {"exported": False}
    if not options.get("include_backup_deep_context", True):
        return info
    ok_backups, backups = try_api_json("http://supervisor/backups", stats)
    ok_mounts, mounts = try_api_json("http://supervisor/mounts", stats)
    if ok_backups:
        sanitized_backups = sanitize_data(backups)
        write_json(export_dir / "inventory" / "backups.json", sanitized_backups)
        stats.included_files.append(str(export_dir / "inventory" / "backups.json"))
        backup_items = sanitized_backups.get("data", {}).get("backups", []) if isinstance(sanitized_backups, dict) else []
        slugs = [item.get("slug") for item in backup_items if isinstance(item, dict) and item.get("slug")]
        detail_rows: list[dict[str, Any]] = []
        for slug in slugs[:200]:
            ok_detail, detail = try_api_json(f"http://supervisor/backups/{slug}/info", stats)
            if ok_detail:
                detail_rows.append(sanitize_data(detail))
        if detail_rows:
            details_path = export_dir / "inventory" / "backup_details.json"
            write_json(details_path, detail_rows)
            stats.included_files.append(str(details_path))
        info["backup_count"] = len(backup_items)
        info["backup_slugs"] = slugs
        info["details_exported"] = len(detail_rows)
        locations = sorted({item.get("location") for item in backup_items if isinstance(item, dict) and item.get("location") is not None})
        info["backup_locations"] = locations
    if ok_mounts:
        sanitized_mounts = sanitize_data(mounts)
        write_json(export_dir / "inventory" / "mounts.json", sanitized_mounts)
        stats.included_files.append(str(export_dir / "inventory" / "mounts.json"))
        mounts_list = sanitized_mounts.get("data", {}).get("mounts", []) if isinstance(sanitized_mounts, dict) else []
        info["mount_count"] = len(mounts_list)
        info["default_backup_mount"] = sanitized_mounts.get("data", {}).get("default_backup_mount") if isinstance(sanitized_mounts, dict) else None
    storage_backup = export_dir / "normalized" / "storage" / "backup.json"
    if storage_backup.exists():
        try:
            parsed = json.loads(storage_backup.read_text(encoding="utf-8"))
            info["storage_backup_present"] = True
            info["storage_backup_keys"] = sorted(list(parsed.keys())) if isinstance(parsed, dict) else None
        except Exception:
            info["storage_backup_present"] = True
    else:
        info["storage_backup_present"] = False
    info["exported"] = bool(ok_backups or ok_mounts or info.get("storage_backup_present"))
    path = export_dir / "inventory" / "backup_context.json"
    write_json(path, info)
    stats.included_files.append(str(path))
    return info
def tail_lines(path: Path, count: int) -> str:
    dq: deque[str] = deque(maxlen=count)
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            dq.append(line)
    return "".join(dq)
def export_logs(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    details: dict[str, Any] = {"files": [], "tails": [], "api_logs": []}
    if not options.get("include_logs", True):
        return details
    for log_name in ["home-assistant.log", "home-assistant.log.1"]:
        log_file = HA_CONFIG_DIR / log_name
        if log_file.exists() and options.get("include_log_archives", True):
            out = export_dir / "runtime" / log_name
            export_raw_text(log_file, out, stats)
            details["files"].append(log_name)
        elif log_name == "home-assistant.log" and log_file.exists():
            try:
                text = tail_lines(log_file, int(options.get("max_log_lines", 500)))
                out = export_dir / "runtime" / "home-assistant.log.tail.txt"
                ensure_dir(out.parent)
                out.write_text(sanitize_text_file(text), encoding="utf-8")
                stats.included_files.append(str(out))
                details["tails"].append(out.name)
            except Exception as exc:
                stats.warnings.append(f"Log-Export fehlgeschlagen: {exc}")
    if not details["files"] and not details["tails"]:
        stats.excluded_items.append("home-assistant.log fehlt")
    return details
def query_one(cursor: sqlite3.Cursor, sql: str, params: tuple[Any, ...] = ()) -> Any:
    cursor.execute(sql, params)
    row = cursor.fetchone()
    if row is None:
        return None
    return row[0] if len(row) == 1 else row
def export_recorder_summary(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    summary: dict[str, Any] = {"exported": False, "deep_exported": False}
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
        days = int(options.get("recorder_days", 3))
        cutoff_dt = now_utc() - timedelta(days=days)
        cutoff = cutoff_dt.timestamp()
        summary["days"] = days
        summary["cutoff_utc"] = cutoff_dt.isoformat()
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
                    LIMIT ?
                    """,
                    (cutoff, int(options.get("recorder_entity_history_limit", 100))),
                )
                for entity_id, row_count, first_ts, last_ts, distinct_states in cursor.fetchall():
                    entity_rows.append(
                        {
                            "entity_id": entity_id,
                            "row_count": row_count,
                            "first_ts": first_ts,
                            "first_ts_iso": timestamp_to_iso(first_ts),
                            "last_ts": last_ts,
                            "last_ts_iso": timestamp_to_iso(last_ts),
                            "distinct_states": distinct_states,
                        }
                    )
            except sqlite3.DatabaseError as exc:
                stats.warnings.append(f"Recorder-Entity-Summary fehlgeschlagen: {exc}")
        summary["top_entities"] = entity_rows
        write_json(export_dir / "runtime" / "recorder_summary.json", summary)
        stats.included_files.append(str(export_dir / "runtime" / "recorder_summary.json"))
        if entity_rows:
            write_ndjson(export_dir / "runtime" / "recorder_top_entities.ndjson", entity_rows)
            stats.included_files.append(str(export_dir / "runtime" / "recorder_top_entities.ndjson"))
        if options.get("include_recorder_deep_export", True):
            deep_summary: dict[str, Any] = {"states_sample_count": 0, "events_sample_count": 0, "statistics_summary_count": 0}
            # State samples
            if table_exists(cursor, "states") and table_exists(cursor, "states_meta"):
                state_columns = set(get_table_columns(cursor, "states"))
                attr_columns = set(get_table_columns(cursor, "state_attributes")) if table_exists(cursor, "state_attributes") else set()
                select_parts = ["sm.entity_id AS entity_id"]
                join_parts = ["JOIN states_meta sm ON s.metadata_id = sm.metadata_id"]
                if "state" in state_columns:
                    select_parts.append("s.state AS state")
                if "last_changed_ts" in state_columns:
                    select_parts.append("s.last_changed_ts AS last_changed_ts")
                if "last_updated_ts" in state_columns:
                    select_parts.append("s.last_updated_ts AS last_updated_ts")
                if "old_state_id" in state_columns:
                    select_parts.append("s.old_state_id AS old_state_id")
                if "attributes_id" in state_columns and attr_columns:
                    join_parts.append("LEFT JOIN state_attributes sa ON s.attributes_id = sa.attributes_id")
                    if "shared_attrs" in attr_columns:
                        select_parts.append("sa.shared_attrs AS attributes_raw")
                    elif "attributes" in attr_columns:
                        select_parts.append("sa.attributes AS attributes_raw")
                state_sql = f"SELECT {', '.join(select_parts)} FROM states s {' '.join(join_parts)} WHERE s.last_updated_ts >= ? ORDER BY s.last_updated_ts DESC LIMIT ?"
                cursor.execute(state_sql, (cutoff, int(options.get("recorder_state_sample_limit", 2000))))
                state_samples: list[dict[str, Any]] = []
                for row in cursor.fetchall():
                    row_map = {desc[0]: row[idx] for idx, desc in enumerate(cursor.description)}
                    attrs = sanitize_data(parse_jsonish(row_map.get("attributes_raw")), "attributes") if row_map.get("attributes_raw") is not None else None
                    item = {
                        "entity_id": row_map.get("entity_id"),
                        "state": sanitize_data(row_map.get("state"), "state"),
                        "last_changed_ts": row_map.get("last_changed_ts"),
                        "last_changed": timestamp_to_iso(row_map.get("last_changed_ts")),
                        "last_updated_ts": row_map.get("last_updated_ts"),
                        "last_updated": timestamp_to_iso(row_map.get("last_updated_ts")),
                        "old_state_id": row_map.get("old_state_id"),
                    }
                    if attrs is not None:
                        item["attributes"] = attrs
                    state_samples.append(item)
                if state_samples:
                    path = export_dir / "runtime" / "recorder_state_samples.ndjson"
                    write_ndjson(path, state_samples)
                    stats.included_files.append(str(path))
                    deep_summary["states_sample_count"] = len(state_samples)
            # Event samples and event type counts
            if table_exists(cursor, "events"):
                event_columns = set(get_table_columns(cursor, "events"))
                join = ""
                event_type_expr = "e.event_type AS event_type" if "event_type" in event_columns else "NULL AS event_type"
                if "event_type_id" in event_columns and table_exists(cursor, "event_types"):
                    join = "LEFT JOIN event_types et ON e.event_type_id = et.event_type_id"
                    event_type_expr = "et.event_type AS event_type"
                data_expr = "NULL AS event_data"
                if "shared_data" in event_columns:
                    data_expr = "e.shared_data AS event_data"
                elif "event_data" in event_columns:
                    data_expr = "e.event_data AS event_data"
                time_expr = "e.time_fired_ts AS time_fired_ts" if "time_fired_ts" in event_columns else "NULL AS time_fired_ts"
                origin_expr = "e.origin AS origin" if "origin" in event_columns else "NULL AS origin"
                context_expr = "e.context_id AS context_id" if "context_id" in event_columns else "NULL AS context_id"
                event_sql = f"SELECT {event_type_expr}, {time_expr}, {origin_expr}, {context_expr}, {data_expr} FROM events e {join} WHERE ({'e.time_fired_ts >= ?' if 'time_fired_ts' in event_columns else '1=1'}) ORDER BY {'e.time_fired_ts DESC' if 'time_fired_ts' in event_columns else 'rowid DESC'} LIMIT ?"
                params = (cutoff, int(options.get("recorder_event_sample_limit", 1000))) if 'time_fired_ts' in event_columns else (int(options.get("recorder_event_sample_limit", 1000)),)
                cursor.execute(event_sql, params)
                event_rows: list[dict[str, Any]] = []
                for row in cursor.fetchall():
                    row_map = {desc[0]: row[idx] for idx, desc in enumerate(cursor.description)}
                    event_rows.append({
                        "event_type": row_map.get("event_type"),
                        "time_fired_ts": row_map.get("time_fired_ts"),
                        "time_fired": timestamp_to_iso(row_map.get("time_fired_ts")),
                        "origin": sanitize_data(row_map.get("origin"), "origin"),
                        "context_id": sanitize_data(row_map.get("context_id"), "context_id", context={"path_parts": ("event", "context_id")}),
                        "event_data": sanitize_data(parse_jsonish(row_map.get("event_data")), "event_data"),
                    })
                if event_rows:
                    path = export_dir / "runtime" / "recorder_event_samples.ndjson"
                    write_ndjson(path, event_rows)
                    stats.included_files.append(str(path))
                    deep_summary["events_sample_count"] = len(event_rows)
                try:
                    if 'time_fired_ts' in event_columns:
                        count_sql = f"SELECT {event_type_expr.split(' AS ')[0]}, COUNT(*) AS row_count FROM events e {join} WHERE e.time_fired_ts >= ? GROUP BY 1 ORDER BY row_count DESC LIMIT 200"
                        cursor.execute(count_sql, (cutoff,))
                    else:
                        count_sql = f"SELECT {event_type_expr.split(' AS ')[0]}, COUNT(*) AS row_count FROM events e {join} GROUP BY 1 ORDER BY row_count DESC LIMIT 200"
                        cursor.execute(count_sql)
                    type_counts = [{"event_type": row[0], "row_count": row[1]} for row in cursor.fetchall()]
                    if type_counts:
                        path = export_dir / "runtime" / "recorder_event_type_counts.json"
                        write_json(path, type_counts)
                        stats.included_files.append(str(path))
                except sqlite3.DatabaseError as exc:
                    stats.warnings.append(f"Recorder-Event-Type-Counts fehlgeschlagen: {exc}")
            # Statistics summaries
            if table_exists(cursor, "statistics_meta"):
                meta_columns = set(get_table_columns(cursor, "statistics_meta"))
                select_meta = ["m.id AS metadata_id"] if "id" in meta_columns else ["NULL AS metadata_id"]
                for col in ["statistic_id", "source", "unit_of_measurement", "has_mean", "has_sum", "name"]:
                    if col in meta_columns:
                        select_meta.append(f"m.{col} AS {col}")
                stats_counts = []
                count_exprs = []
                if table_exists(cursor, "statistics"):
                    count_exprs.append("(SELECT COUNT(*) FROM statistics s WHERE s.metadata_id = m.id) AS statistics_rows")
                if table_exists(cursor, "statistics_short_term"):
                    count_exprs.append("(SELECT COUNT(*) FROM statistics_short_term sst WHERE sst.metadata_id = m.id) AS statistics_short_term_rows")
                query = f"SELECT {', '.join(select_meta + count_exprs)} FROM statistics_meta m ORDER BY m.id LIMIT ?"
                cursor.execute(query, (int(options.get("recorder_statistics_limit", 500)),))
                for row in cursor.fetchall():
                    row_map = {desc[0]: row[idx] for idx, desc in enumerate(cursor.description)}
                    stats_counts.append(sanitize_data(row_map))
                if stats_counts:
                    path = export_dir / "runtime" / "recorder_statistics_summary.json"
                    write_json(path, stats_counts)
                    stats.included_files.append(str(path))
                    deep_summary["statistics_summary_count"] = len(stats_counts)
            if options.get("include_recorder_db_copy", False):
                out = export_dir / "runtime" / "home-assistant_v2.db"
                shutil.copy2(db_path, out)
                stats.included_files.append(str(out))
                deep_summary["recorder_db_copy_exported"] = True
            summary["deep_exported"] = any(v for v in deep_summary.values())
            summary["deep_summary"] = deep_summary
            deep_path = export_dir / "runtime" / "recorder_deep_export_summary.json"
            write_json(deep_path, deep_summary)
            stats.included_files.append(str(deep_path))
        summary["exported"] = True
        conn.close()
        return summary
    except Exception as exc:
        stats.warnings.append(f"Recorder-Export fehlgeschlagen: {exc}")
        return summary
def build_relationship_integrity_report(export_dir: Path, stats: ExportStats) -> dict[str, Any]:
    report: dict[str, Any] = {"generated": False}
    device_path = export_dir / "normalized" / "storage" / "core.device_registry.json"
    entity_path = export_dir / "normalized" / "storage" / "core.entity_registry.json"
    area_path = export_dir / "normalized" / "storage" / "core.area_registry.json"
    config_entries_path = export_dir / "normalized" / "storage" / "core.config_entries.json"
    try:
        devices = json.loads(device_path.read_text(encoding="utf-8")) if device_path.exists() else {}
        entities = json.loads(entity_path.read_text(encoding="utf-8")) if entity_path.exists() else {}
        areas = json.loads(area_path.read_text(encoding="utf-8")) if area_path.exists() else {}
        config_entries = json.loads(config_entries_path.read_text(encoding="utf-8")) if config_entries_path.exists() else {}
        device_ids = {item.get("id") for item in devices.get("data", {}).get("devices", []) if isinstance(item, dict) and item.get("id")}
        area_ids = {item.get("id") for item in areas.get("data", {}).get("areas", []) if isinstance(item, dict) and item.get("id")}
        entry_ids = set()
        for item in config_entries.get("data", {}).get("entries", []):
            if isinstance(item, dict):
                if item.get("entry_id"):
                    entry_ids.add(item.get("entry_id"))
                elif item.get("id"):
                    entry_ids.add(item.get("id"))
        entities_list = entities.get("data", {}).get("entities", [])
        linked_device_count = 0
        broken_device_refs: list[dict[str, Any]] = []
        broken_area_refs: list[dict[str, Any]] = []
        broken_config_entry_refs: list[dict[str, Any]] = []
        unique_entity_device_ids = set()
        for item in entities_list:
            if not isinstance(item, dict):
                continue
            entity_id = item.get("entity_id")
            device_id = item.get("device_id")
            if device_id:
                unique_entity_device_ids.add(device_id)
                if device_id in device_ids:
                    linked_device_count += 1
                else:
                    broken_device_refs.append({"entity_id": entity_id, "device_id": device_id})
            area_id = item.get("area_id")
            if area_id and area_id not in area_ids:
                broken_area_refs.append({"entity_id": entity_id, "area_id": area_id})
            config_entry_id = item.get("config_entry_id")
            if config_entry_id and config_entry_id not in entry_ids:
                broken_config_entry_refs.append({"entity_id": entity_id, "config_entry_id": config_entry_id})
        report = {
            "generated": True,
            "device_registry": {
                "device_count": len(device_ids),
                "unique_device_ids": len(device_ids),
            },
            "entity_registry": {
                "entity_count": len(entities_list),
                "entities_with_device_id": sum(1 for item in entities_list if isinstance(item, dict) and item.get("device_id")),
                "unique_device_ids_referenced": len(unique_entity_device_ids),
                "linked_device_refs": linked_device_count,
                "broken_device_refs": broken_device_refs[:50],
                "broken_area_refs": broken_area_refs[:50],
                "broken_config_entry_refs": broken_config_entry_refs[:50],
            },
            "integrity": {
                "device_linkage_preserved": len(device_ids) > 1 and len(unique_entity_device_ids) > 1 and not broken_device_refs,
                "area_linkage_preserved": not broken_area_refs,
                "config_entry_linkage_preserved": not broken_config_entry_refs,
            },
        }
        out = export_dir / "inventory" / "relationship_integrity_report.json"
        write_json(out, report)
        stats.included_files.append(str(out))
        return report
    except Exception as exc:
        stats.warnings.append(f"Relationship-Integrity-Report fehlgeschlagen: {exc}")
        return report
def create_checksums(export_dir: Path) -> None:
    checksum_path = export_dir / "metadata" / "checksums.sha256"
    ensure_dir(checksum_path.parent)
    with checksum_path.open("w", encoding="utf-8") as out:
        for path in sorted(p for p in export_dir.rglob("*") if p.is_file() and p != checksum_path):
            rel = path.relative_to(export_dir)
            out.write(f"{sha256_file(path)}  {rel.as_posix()}\n")
def create_archive(export_dir: Path, target_archive: Path | None = None) -> Path:
    archive_path = target_archive or export_dir.with_suffix(".tar.gz")
    ensure_dir(archive_path.parent)
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(export_dir, arcname=export_dir.name)
    return archive_path


def count_export_files(export_dir: Path) -> int:
    checksum_path = export_dir / "metadata" / "checksums.sha256"
    return sum(1 for path in export_dir.rglob("*") if path.is_file() and path != checksum_path)

def reconcile_logs_info(export_dir: Path, logs_info: dict[str, Any]) -> dict[str, Any]:
    info = dict(logs_info or {})
    files: list[str] = []
    runtime = export_dir / "runtime"
    for name in ("home-assistant.log", "home-assistant.log.1", "home-assistant.log.tail.txt", "core.latest.log.txt", "supervisor.latest.log.txt"):
        if (runtime / name).exists():
            files.append(name)
    addon_logs = runtime / "addon_logs"
    if addon_logs.exists():
        for path in sorted(addon_logs.glob("*.txt")):
            files.append(f"addon_logs/{path.name}")
    info["all_exported_logs"] = files
    info["has_any_logs"] = bool(files)
    return info

def reconcile_recorder_info(export_dir: Path, recorder_info: dict[str, Any]) -> dict[str, Any]:
    info = dict(recorder_info or {})
    runtime = export_dir / "runtime"
    info["exported"] = (runtime / "recorder_summary.json").exists()
    info["deep_exported"] = any((runtime / name).exists() for name in (
        "recorder_deep_export_summary.json",
        "recorder_state_samples.ndjson",
        "recorder_event_samples.ndjson",
        "recorder_statistics_summary.json",
    ))
    return info

def write_manifest(export_dir: Path, options: dict[str, Any], stats: ExportStats, manifest_data: dict[str, Any], *, output_report: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = dict(manifest_data)
    manifest["counts"] = {
        "included_files": count_export_files(export_dir),
        "warnings": len(stats.warnings),
        "api_calls": len(stats.api_calls),
    }
    if output_report is not None:
        manifest["output_report"] = output_report
    write_json(export_dir / "metadata" / "export_manifest.json", manifest)
    return manifest

def finalize_export_tree(export_dir: Path, export_name: str, options: dict[str, Any], stats: ExportStats, targets: OutputTargets, manifest_data: dict[str, Any], config_info: dict[str, Any], storage_info: dict[str, Any], api_info: dict[str, Any], runtime_info: dict[str, Any], recorder_info: dict[str, Any], backup_info: dict[str, Any], logs_info: dict[str, Any], relationship_info: dict[str, Any], security_info: dict[str, Any], operator_intent_info: dict[str, Any], addon_options_info: dict[str, Any], integration_profiles: dict[str, Any], uncertainty_info: dict[str, Any], *, include_output_report: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    reconciled_logs = reconcile_logs_info(export_dir, logs_info)
    reconciled_recorder = reconcile_recorder_info(export_dir, recorder_info)
    reconciled_operator = dict(operator_intent_info or {})
    reconciled_operator["imported"] = bool(reconciled_operator.get("imported"))
    output_report = None
    if include_output_report:
        output_report = {
            "primary": {
                "label": targets.primary.label,
                "root": str(targets.primary.root),
                "archive_path": str(targets.primary.archive_path) if targets.primary.archive_path else None,
                "ok": targets.primary.ok,
                "message": targets.primary.message,
            },
            "mirrors": [
                {
                    "label": m.label,
                    "root": str(m.root),
                    "archive_path": str(m.archive_path) if m.archive_path else None,
                    "ok": m.ok,
                    "message": m.message,
                } for m in targets.mirrors
            ],
        }
    manifest_payload = {
        **manifest_data,
        "logs_info": reconciled_logs,
        "recorder_info": reconciled_recorder,
        "operator_intent_info": reconciled_operator,
    }
    # First pass: materialize the files that must themselves be included in the final counts.
    write_manifest(export_dir, options, stats, manifest_payload, output_report=output_report)
    report = build_export_report(export_name, options, stats, targets, config_info, storage_info, api_info, runtime_info, reconciled_recorder, backup_info, reconciled_logs, relationship_info, security_info, reconciled_operator, addon_options_info, integration_profiles, uncertainty_info, export_dir=export_dir)
    write_json(export_dir / "metadata" / "export_report.json", report)
    generate_export_summary(export_dir, options, stats, config_info, storage_info, api_info, runtime_info, reconciled_recorder, backup_info, reconciled_logs, relationship_info, security_info, reconciled_operator, addon_options_info, integration_profiles, uncertainty_info, targets)
    create_checksums(export_dir)
    # Second pass: report/manifest are rewritten after they already exist, so counts stay stable and exact.
    report = build_export_report(export_name, options, stats, targets, config_info, storage_info, api_info, runtime_info, reconciled_recorder, backup_info, reconciled_logs, relationship_info, security_info, reconciled_operator, addon_options_info, integration_profiles, uncertainty_info, export_dir=export_dir)
    write_json(export_dir / "metadata" / "export_report.json", report)
    write_manifest(export_dir, options, stats, manifest_payload, output_report=output_report)
    create_checksums(export_dir)
    return report, {
        "logs_info": reconciled_logs,
        "recorder_info": reconciled_recorder,
        "operator_intent_info": reconciled_operator,
        "output_report": output_report,
    }

def copy_export_tree(source_dir: Path, target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)
def path_writable(path: Path) -> tuple[bool, str]:
    try:
        ensure_dir(path)
        probe = path / ".chatgpt_exporter_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True, "ok"
    except Exception as exc:
        return False, str(exc)
def determine_output_targets(export_name: str, options: dict[str, Any], stats: ExportStats) -> OutputTargets:
    ok, msg = path_writable(SHARE_DIR)
    if not ok:
        raise RuntimeError(f"/share ist nicht schreibbar: {msg}")
    primary = OutputTargetResult(label="share_archive", root=SHARE_DIR, export_dir=WORK_DIR / export_name, archive_path=SHARE_DIR / f"{export_name}.tar.gz", ok=True, message="archive-only")
    return OutputTargets(primary=primary, mirrors=[])
def mirror_output(source_dir: Path, source_archive: Path, target: OutputTargetResult, stats: ExportStats) -> None:
    if target.export_dir is None or target.archive_path is None:
        target.ok = False
        target.message = "Zielpfade fehlen"
        return
    try:
        if target.export_dir.exists():
            shutil.rmtree(target.export_dir)
        shutil.copytree(source_dir, target.export_dir)
        shutil.copy2(source_archive, target.archive_path)
        target.ok = True
        target.message = "gespiegelt"
    except Exception as exc:
        target.ok = False
        target.message = str(exc)
        stats.warnings.append(f"Spiegelung nach {target.label} fehlgeschlagen: {exc}")
def export_addon_options_profiles(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    info: dict[str, Any] = {
        "enabled": bool(options.get("include_addon_options_export", True)),
        "exported": False,
        "profiles": [],
        "stats": [],
        "stats_supported": [],
        "stats_unsupported": [],
        "stats_errors": [],
    }
    if not options.get("include_addon_options_export", True):
        return info
    addons_payload = read_export_json(export_dir / "inventory" / "addons.json") or {}
    addon_rows = addons_payload.get("data", {}).get("addons", []) if isinstance(addons_payload, dict) else []
    profiles: list[dict[str, Any]] = []
    stats_rows: list[dict[str, Any]] = []
    stats_supported: list[dict[str, Any]] = []
    stats_unsupported: list[dict[str, Any]] = []
    stats_errors: list[dict[str, Any]] = []
    for row in addon_rows[:200]:
        if not isinstance(row, dict):
            continue
        slug = row.get("slug")
        if not slug:
            continue
        ok, detail = try_api_json(f"http://supervisor/addons/{slug}/info", stats)
        if not ok or not isinstance(detail, dict):
            continue
        payload = detail.get("data", detail)
        if not isinstance(payload, dict):
            continue
        trimmed = trim_addon_info_payload(payload)
        sanitized = sanitize_data(trimmed)
        profile = {
            "slug": sanitized.get("slug") or slug,
            "name": sanitized.get("name"),
            "version": sanitized.get("version"),
            "version_latest": sanitized.get("version_latest"),
            "state": sanitized.get("state"),
            "boot": sanitized.get("boot"),
            "auto_update": sanitized.get("auto_update"),
            "watchdog": sanitized.get("watchdog"),
            "ingress": sanitized.get("ingress"),
            "ingress_panel": sanitized.get("ingress_panel"),
            "advanced": sanitized.get("advanced"),
            "build": sanitized.get("build"),
            "stage": sanitized.get("stage"),
            "repository": sanitized.get("repository"),
            "hassio_api": sanitized.get("hassio_api"),
            "hassio_role": sanitized.get("hassio_role"),
            "homeassistant_api": sanitized.get("homeassistant_api"),
            "host_network": sanitized.get("host_network"),
            "full_access": sanitized.get("full_access"),
            "protected": sanitized.get("protected"),
            "privileged": sanitized.get("privileged"),
            "services_role": sanitized.get("services_role"),
            "network": sanitized.get("network"),
            "network_description": sanitized.get("network_description"),
            "devices": sanitized.get("devices"),
            "usb": sanitized.get("usb"),
            "options": sanitized.get("options"),
            "schema_keys": summarize_schema_keys(sanitized.get("schema")),
            "option_key_count": len(sanitized.get("options", {})) if isinstance(sanitized.get("options"), dict) else 0,
            "schema_key_count": len(sanitized.get("schema", {})) if isinstance(sanitized.get("schema"), dict) else 0,
        }
        profiles.append(profile)
        if options.get("include_addon_stats", True):
            url = f"http://supervisor/addons/{slug}/stats"
            try:
                stats_payload = api_get_json(url, stats)
                if isinstance(stats_payload, dict):
                    stats_rows.append({"slug": slug, "stats": sanitize_data(stats_payload.get("data", stats_payload))})
                    stats_supported.append({"slug": slug, "status": "ok"})
                else:
                    stats_errors.append({"slug": slug, "reason": "non-dict-response"})
            except HTTPError as exc:
                code = getattr(exc, 'code', None)
                if code in {400, 404, 405, 422, 501}:
                    stats_unsupported.append({"slug": slug, "reason": f"http_{code}"})
                else:
                    stats.warnings.append(f"API-Aufruf fehlgeschlagen {url}: {exc}")
                    stats_errors.append({"slug": slug, "reason": f"http_{code or 'error'}"})
            except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
                stats.warnings.append(f"API-Aufruf fehlgeschlagen {url}: {exc}")
                stats_errors.append({"slug": slug, "reason": type(exc).__name__})
    out = export_dir / "inventory" / "addon_options_profiles.json"
    write_json(out, profiles)
    stats.included_files.append(str(out))
    if stats_rows:
        stats_path = export_dir / "inventory" / "addon_stats_profiles.json"
        write_json(stats_path, stats_rows)
        stats.included_files.append(str(stats_path))
    critical_patterns = ("esphome", "mosquitto", "mqtt", "samba", "backup", "google", "ssh", "studio-code-server")
    critical = [row for row in profiles if any(p in str(row.get("slug", "")).lower() or p in str(row.get("name", "")).lower() for p in critical_patterns)]
    critical_path = export_dir / "inventory" / "addon_options_profiles.critical.json"
    write_json(critical_path, critical)
    stats.included_files.append(str(critical_path))
    info.update({
        "exported": bool(profiles),
        "profile_count": len(profiles),
        "stats_count": len(stats_rows),
        "critical_profile_count": len(critical),
        "profiles": [{"slug": row.get("slug"), "name": row.get("name"), "state": row.get("state"), "option_key_count": row.get("option_key_count"), "schema_key_count": row.get("schema_key_count")} for row in profiles],
        "stats": [{"slug": row.get("slug")} for row in stats_rows],
        "stats_supported": stats_supported,
        "stats_unsupported": stats_unsupported,
        "stats_error_count": len(stats_errors),
        "stats_errors": stats_errors,
    })
    return info
def _load_registry_views(export_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    device_registry = read_export_json(export_dir / "normalized" / "storage" / "core.device_registry.json") or {}
    entity_registry = read_export_json(export_dir / "normalized" / "storage" / "core.entity_registry.json") or {}
    area_registry = read_export_json(export_dir / "normalized" / "storage" / "core.area_registry.json") or {}
    config_entries = read_export_json(export_dir / "normalized" / "storage" / "core.config_entries.json") or {}
    states = []
    snapshot_path = export_dir / "runtime" / "state_snapshot.ndjson"
    if snapshot_path.exists():
        try:
            states = [json.loads(line) for line in snapshot_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
        except Exception:
            states = []
    return device_registry, entity_registry, area_registry, config_entries, states
def _index_config_entries(config_entries: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_domain: dict[str, list[str]] = defaultdict(list)
    for entry in config_entries.get("data", {}).get("entries", []):
        if not isinstance(entry, dict):
            continue
        entry_id = entry.get("entry_id") or entry.get("id")
        if entry_id:
            by_id[entry_id] = entry
        domain = entry.get("domain")
        if isinstance(domain, str):
            by_domain[domain].append(entry_id)
    return by_id, by_domain
def _collect_entities_for_domain(entity_registry: dict[str, Any], config_by_id: dict[str, dict[str, Any]], domain_name: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entity in entity_registry.get("data", {}).get("entities", []):
        if not isinstance(entity, dict):
            continue
        entity_id = entity.get("entity_id")
        entity_domain = str(entity_id).split('.', 1)[0] if isinstance(entity_id, str) and '.' in entity_id else None
        config_entry_id = entity.get("config_entry_id")
        entry_domain = None
        if config_entry_id and config_entry_id in config_by_id:
            entry_domain = config_by_id[config_entry_id].get("domain")
        platform = entity.get("platform")
        if domain_name in {entity_domain, entry_domain, platform}:
            rows.append(entity)
    return rows


def find_yaml_mentions(export_dir: Path, keyword: str) -> list[str]:
    keyword_lower = keyword.lower()
    hits: list[str] = []
    root = export_dir / "source_sanitized" / "config"
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in YAML_EXTENSIONS:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue
        if keyword_lower in content:
            hits.append(path.relative_to(root).as_posix())
    return hits[:200]
def build_integration_profiles(export_dir: Path, options: dict[str, Any], stats: ExportStats, addon_options_info: dict[str, Any] | None = None) -> dict[str, Any]:
    info: dict[str, Any] = {"enabled": bool(options.get("include_integration_profiles", True)), "generated": False, "profiles": {}}
    if not options.get("include_integration_profiles", True):
        return info
    device_registry, entity_registry, area_registry, config_entries, states = _load_registry_views(export_dir)
    config_by_id, by_domain = _index_config_entries(config_entries)
    storage_inventory = read_export_json(export_dir / "inventory" / "storage_inventory.json") or {}
    services = read_export_json(export_dir / "inventory" / "services.json") or []
    addons_payload = read_export_json(export_dir / "inventory" / "addon_options_profiles.json") or []
    addons = addons_payload if isinstance(addons_payload, list) else addons_payload.get("profiles", []) if isinstance(addons_payload, dict) else []
    config_inventory = read_export_json(export_dir / "inventory" / "config_inventory.json") or {}
    def make_profile(domain_name: str, title: str) -> dict[str, Any]:
        entities = _collect_entities_for_domain(entity_registry, config_by_id, domain_name)
        entity_ids = [e.get("entity_id") for e in entities if isinstance(e, dict) and e.get("entity_id")]
        device_ids = sorted({e.get("device_id") for e in entities if isinstance(e, dict) and e.get("device_id")})
        areas = sorted({e.get("area_id") for e in entities if isinstance(e, dict) and e.get("area_id")})
        services_for_domain = []
        if isinstance(services, list):
            for service_block in services:
                if isinstance(service_block, dict) and service_block.get("domain") == domain_name:
                    services_for_domain = sorted((service_block.get("services") or {}).keys()) if isinstance(service_block.get("services"), dict) else []
        return {
            "title": title,
            "domain": domain_name,
            "config_entry_count": len(by_domain.get(domain_name, [])),
            "config_entries": sanitize_data([config_by_id[eid] for eid in by_domain.get(domain_name, []) if eid in config_by_id]),
            "entity_count": len(entity_ids),
            "entity_ids_sample": sorted(entity_ids)[:200],
            "device_count": len(device_ids),
            "device_ids_sample": device_ids[:200],
            "area_count": len(areas),
            "area_ids_sample": areas[:200],
            "service_names": services_for_domain,
            "state_snapshot_entity_count": sum(1 for row in states if isinstance(row, dict) and str(row.get("entity_id", "")).startswith(f"{domain_name}.")),
        }
    profiles: dict[str, Any] = {}
    esphome_profile = make_profile("esphome", "ESPHome")
    esphome_profile.update({
        "source_directories_present": {
            "esphome": (export_dir / "source_sanitized" / "config" / "esphome").exists(),
        },
        "storage_files": sorted([name for name in storage_inventory.get("included", []) if str(name).startswith("esphome.")]),
        "dashboard_storage_present": "esphome.dashboard" in storage_inventory.get("included", []),
        "candidate_addons": [row for row in addons if "esphome" in str(row.get("slug", "")).lower() or "esphome" in str(row.get("name", "")).lower()],
    })
    profiles["esphome"] = esphome_profile
    mqtt_profile = make_profile("mqtt", "MQTT")
    mqtt_yaml_mentions = find_yaml_mentions(export_dir, "mqtt")
    mqtt_candidate_addons = [row for row in addons if any(term in str(row.get("slug", "")).lower() or term in str(row.get("name", "")).lower() for term in ("mosquitto", "mqtt"))]
    mqtt_profile.update({
        "candidate_addons": mqtt_candidate_addons,
        "yaml_mentions": mqtt_yaml_mentions,
        "runtime_event_signal": [],
    })
    if mqtt_profile.get("config_entry_count") or mqtt_profile.get("entity_count") or mqtt_yaml_mentions:
        runtime_events = read_export_json(export_dir / "runtime" / "recorder_event_type_counts.json") or []
        if isinstance(runtime_events, list):
            mqtt_profile["runtime_event_signal"] = [row for row in runtime_events if str((row or {}).get('event_type', '')).lower().startswith('mqtt')][:20]
    profiles["mqtt"] = mqtt_profile
    broadlink_profile = make_profile("broadlink", "Broadlink")
    broadlink_profile.update({
        "storage_files": sorted([name for name in storage_inventory.get("included", []) if fnmatch.fnmatch(str(name), "broadlink_remote_*_codes") or fnmatch.fnmatch(str(name), "broadlink_remote_*_flags")]),
        "code_storage_count": len([name for name in storage_inventory.get("included", []) if fnmatch.fnmatch(str(name), "broadlink_remote_*_codes")]),
        "flag_storage_count": len([name for name in storage_inventory.get("included", []) if fnmatch.fnmatch(str(name), "broadlink_remote_*_flags")]),
    })
    profiles["broadlink"] = broadlink_profile
    hacs_storage_files = sorted([name for name in storage_inventory.get("included", []) if str(name).startswith("hacs.")])
    custom_components_root = export_dir / "source_sanitized" / "custom_components"
    custom_component_count = len([p for p in custom_components_root.iterdir() if p.is_dir()]) if custom_components_root.exists() else 0
    hacs_profile = {
        "title": "HACS",
        "domain": "hacs",
        "storage_files": hacs_storage_files,
        "storage_file_count": len(hacs_storage_files),
        "custom_components_present": custom_components_root.exists(),
        "custom_component_count": custom_component_count,
        "custom_component_names_sample": sorted([p.name for p in custom_components_root.iterdir() if p.is_dir()])[:200] if custom_components_root.exists() else [],
    }
    for hacs_name in hacs_storage_files[:4]:
        parsed = read_export_json(export_dir / "normalized" / "storage" / f"{hacs_name}.json")
        hacs_profile[f"{hacs_name}_item_count"] = count_mappingish_items(parsed)
    profiles["hacs"] = hacs_profile
    profile_dir = export_dir / "inventory" / "integration_profiles"
    for key, profile in profiles.items():
        out = profile_dir / f"{key}_profile.json"
        write_json(out, sanitize_data(profile))
        stats.included_files.append(str(out))
    index = {
        "generated_at": now_utc().isoformat(),
        "profiles": {key: {"file": f"inventory/integration_profiles/{key}_profile.json", "summary": {
            "config_entry_count": profile.get("config_entry_count"),
            "entity_count": profile.get("entity_count"),
            "device_count": profile.get("device_count"),
        }} for key, profile in profiles.items()},
    }
    idx_path = profile_dir / "index.json"
    write_json(idx_path, index)
    stats.included_files.append(str(idx_path))
    info.update({"generated": True, "profiles": {key: {"config_entry_count": value.get("config_entry_count"), "entity_count": value.get("entity_count"), "device_count": value.get("device_count")} for key, value in profiles.items()}})
    return info
def build_uncertainty_register(export_dir: Path, options: dict[str, Any], stats: ExportStats, config_info: dict[str, Any], storage_info: dict[str, Any], logs_info: dict[str, Any], recorder_info: dict[str, Any], backup_info: dict[str, Any], operator_intent_info: dict[str, Any], integration_profiles: dict[str, Any], addon_options_info: dict[str, Any]) -> dict[str, Any]:
    info: dict[str, Any] = {"enabled": bool(options.get("include_uncertainty_register", True)), "generated": False, "items": []}
    if not options.get("include_uncertainty_register", True):
        return info
    items: list[dict[str, Any]] = []
    def add_item(item_id: str, category: str, severity: str, title: str, summary: str, evidence: list[dict[str, Any]], mitigation: list[str]) -> None:
        items.append({
            "id": item_id,
            "category": category,
            "severity": severity,
            "title": title,
            "summary": summary,
            "evidence": evidence,
            "recommended_next_export": mitigation,
        })
    runtime_logs_present = any((export_dir / "runtime" / name).exists() for name in ("home-assistant.log", "home-assistant.log.1", "home-assistant.log.tail.txt", "core.latest.log.txt", "supervisor.latest.log.txt")) or (export_dir / "runtime" / "addon_logs").exists()
    if not logs_info.get("files") and not logs_info.get("tails") and not runtime_logs_present:
        add_item(
            "UNC-LOG-001", "hard_export_gap", "high", "Home Assistant logs missing", 
            "Keine home-assistant.log wurde im Export gefunden, obwohl Laufzeit- und Fehleranalyse davon stark profitieren.",
            [{"source": "logs_info", "fact": "weder volle Logdatei noch Tail exportiert"}],
            ["home-assistant.log und home-assistant.log.1 exportieren", "optional Core-/Supervisor-/Add-on-Logs aktiv lassen"],
        )
    theme_info = config_info.get("theme_include", {}) if isinstance(config_info, dict) else {}
    if theme_info.get("declared") and theme_info.get("status") != "ok":
        add_item(
            "UNC-THEME-001", "hard_export_gap", "medium", "Theme include unresolved", 
            "configuration.yaml referenziert Themes, aber das referenzierte Verzeichnis war im Export nicht nutzbar.",
            [{"source": "inventory/config_inventory.json", "fact": f"theme status={theme_info.get('status')} checked_path={theme_info.get('checked_path')}"}],
            ["referenziertes Theme-Verzeichnis lesbar exportieren", "bei Nichtnutzung den Include entfernen"],
        )
    for folder, item_id, title in (("python_scripts", "UNC-LOGIC-001", "python_scripts missing"), ("pyscript", "UNC-LOGIC-002", "pyscript missing"), ("appdaemon", "UNC-LOGIC-003", "appdaemon missing")):
        if options.get(f"include_{folder}", True):
            present = (export_dir / "source_sanitized" / folder).exists()
            if not present:
                add_item(item_id, "export_scope_gap", "medium", title, f"{folder}/ wurde nicht exportiert oder existierte nicht, wodurch ausgelagerte Logik unklar bleiben kann.", [{"source": "source_sanitized", "fact": f"{folder}/ fehlt"}], [f"{folder}/ vollständig exportieren, falls genutzt"])
    critical_storage = {
        "trace.saved_traces": "UNC-TRACE-001",
        "repairs.issue_registry": "UNC-TRACE-002",
        "http": "UNC-SEC-001",
        "http.auth": "UNC-SEC-002",
        "core.network": "UNC-SEC-003",
        "auth": "UNC-SEC-004",
        "auth_provider.homeassistant": "UNC-SEC-005",
        "homeassistant.exposed_entities": "UNC-SEC-006",
        "application_credentials": "UNC-SEC-007",
        "backup": "UNC-BACKUP-001",
        "frontend.system_data": "UNC-FRONTEND-001",
        "frontend_panels": "UNC-FRONTEND-002",
    }
    included = set(storage_info.get("included", [])) if isinstance(storage_info, dict) else set()
    available_only = set(storage_info.get("available_only", [])) if isinstance(storage_info, dict) else set()
    for name, item_id in critical_storage.items():
        if name in available_only:
            add_item(item_id, "export_scope_gap", "medium", f"Storage file not exported: {name}", f"{name} war im System sichtbar, wurde aber nicht in den Export aufgenommen.", [{"source": "inventory/storage_inventory.json", "fact": f"{name} in available_only"}], [f"{name} in den Export-Scope aufnehmen"])
        elif name not in included and name not in available_only:
            add_item(item_id, "hard_export_gap", "low", f"Storage file unavailable: {name}", f"{name} war im Export nicht vorhanden; entweder fehlt die Datei wirklich oder der Bereich ist in dieser Installation nicht aktiv.", [{"source": "inventory/storage_inventory.json", "fact": f"{name} nicht in included/available_only"}], [f"prüfen, ob {name} in dieser Installation existiert und relevant ist"])
    if not recorder_info.get("deep_exported"):
        add_item("UNC-RECORDER-001", "export_scope_gap", "high", "Recorder deep export missing", "Es gibt keine tieferen Recorder-Samples; Performance- und Ablaufanalyse bleiben dadurch grob.", [{"source": "runtime/recorder_deep_export_summary.json", "fact": "deep_exported=false oder Datei fehlt"}], ["include_recorder_deep_export aktivieren", "optional Recorder-DB-Kopie nur bei Bedarf exportieren"])
    if not operator_intent_info.get("imported"):
        add_item("UNC-INTENT-001", "principled_uncertainty", "medium", "Operator intent missing", "Betreiber-Absicht wurde nicht importiert; Zielarchitektur und No-Go-Bereiche bleiben dadurch prinzipiell unsicher.", [{"source": "metadata/operator_intent_import_manifest.json", "fact": "keine operator_intent-Datei importiert"}], ["operator_intent.md oder operator_intent.json hinzufügen"])
    esphome_profile = (integration_profiles or {}).get("profiles", {}).get("esphome", {})
    if esphome_profile and not (export_dir / "source_sanitized" / "config" / "esphome").exists() and (esphome_profile.get("config_entry_count") or esphome_profile.get("entity_count")):
        add_item("UNC-ESPHOME-001", "export_scope_gap", "high", "ESPHome source files missing", "ESPHome ist im System erkennbar, aber die Quell-YAMLs fehlen im Export.", [{"source": "inventory/integration_profiles/esphome_profile.json", "fact": "entities/config_entries vorhanden, source_directories_present.esphome=false"}], ["/config/esphome/*.yaml exportieren"])
    if addon_options_info.get("enabled") and not addon_options_info.get("exported"):
        add_item("UNC-ADDON-001", "export_scope_gap", "medium", "Addon options profiles missing", "Gezielte Add-on-Optionsprofile konnten nicht erzeugt werden, obwohl die Funktion aktiv ist.", [{"source": "inventory/addon_options_profiles.json", "fact": "nicht erzeugt oder leer"}], ["Supervisor-Zugriff auf /addons und /addons/<slug>/info prüfen"])
    severity_rank = {"high": 3, "medium": 2, "low": 1}
    items.sort(key=lambda row: (-severity_rank.get(row.get("severity", "low"), 0), row.get("id", "")))
    summary = {
        "generated_at": now_utc().isoformat(),
        "counts": {
            "total": len(items),
            "high": sum(1 for row in items if row.get("severity") == "high"),
            "medium": sum(1 for row in items if row.get("severity") == "medium"),
            "low": sum(1 for row in items if row.get("severity") == "low"),
        },
        "items": items,
    }
    out = export_dir / "inventory" / "uncertainty_register.json"
    write_json(out, summary)
    stats.included_files.append(str(out))
    md_lines = ["# Uncertainty Register", "", f"Generated: {summary['generated_at']}", "", "## Counts", f"- Total: {summary['counts']['total']}", f"- High: {summary['counts']['high']}", f"- Medium: {summary['counts']['medium']}", f"- Low: {summary['counts']['low']}", "", "## Items"]
    for row in items:
        md_lines.append(f"- [{row['severity']}] {row['id']} — {row['title']}: {row['summary']}")
    md_path = export_dir / "inventory" / "uncertainty_register.md"
    ensure_dir(md_path.parent)
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    stats.included_files.append(str(md_path))
    info.update({"generated": True, **summary})
    return info
def build_export_report(export_name: str, options: dict[str, Any], stats: ExportStats, targets: OutputTargets, config_info: dict[str, Any], storage_info: dict[str, Any], api_info: dict[str, Any], runtime_info: dict[str, Any], recorder_info: dict[str, Any], backup_info: dict[str, Any], logs_info: dict[str, Any], relationship_info: dict[str, Any], security_info: dict[str, Any], operator_intent_info: dict[str, Any], addon_options_info: dict[str, Any], integration_profiles: dict[str, Any], uncertainty_info: dict[str, Any], export_dir: Path | None = None) -> dict[str, Any]:
    def serialise_target(target: OutputTargetResult) -> dict[str, Any]:
        return {
            "label": target.label,
            "root": str(target.root),
            "archive_path": str(target.archive_path) if target.archive_path else None,
            "ok": target.ok,
            "message": target.message,
        }
    return {
        "exporter": {"name": "ChatGPT HA Exporter", "version": EXPORTER_VERSION, "created_at": now_utc().isoformat()},
        "export_name": export_name,
        "paths": {"homeassistant_config": str(HA_CONFIG_DIR), "share": str(SHARE_DIR), "data": str(DATA_DIR)},
        "targets": {"primary": serialise_target(targets.primary), "mirrors": [serialise_target(t) for t in targets.mirrors]},
        "options": options,
        "counts": {"included_files": count_export_files(export_dir) if export_dir else len(stats.included_files), "warnings": len(stats.warnings), "api_calls": len(stats.api_calls)},
        "config_info": config_info,
        "storage_info": storage_info,
        "api_info": api_info,
        "runtime_info": runtime_info,
        "recorder_info": recorder_info,
        "backup_info": backup_info,
        "logs_info": logs_info,
        "relationship_info": relationship_info,
        "security_info": security_info,
        "operator_intent_info": operator_intent_info,
        "addon_options_info": addon_options_info,
        "integration_profiles": integration_profiles,
        "uncertainty_info": {
            "generated": uncertainty_info.get("generated"),
            "counts": uncertainty_info.get("counts"),
        },
        "warnings": stats.warnings,
        "excluded_items": stats.excluded_items,
    }
def generate_export_summary(export_dir: Path, options: dict[str, Any], stats: ExportStats, config_info: dict[str, Any], storage_info: dict[str, Any], api_info: dict[str, Any], runtime_info: dict[str, Any], recorder_info: dict[str, Any], backup_info: dict[str, Any], logs_info: dict[str, Any], relationship_info: dict[str, Any], security_info: dict[str, Any], operator_intent_info: dict[str, Any], addon_options_info: dict[str, Any], integration_profiles: dict[str, Any], uncertainty_info: dict[str, Any], targets: OutputTargets) -> None:
    logs_info = reconcile_logs_info(export_dir, logs_info)
    recorder_info = reconcile_recorder_info(export_dir, recorder_info)
    operator_intent_import_manifest_exists = (export_dir / "metadata" / "operator_intent_import_manifest.json").exists()
    included_hint = [
        "Sanitisierte Konfigurationsdateien",
        "Normalisierte JSON/NDJSON-Dateien",
        "Entity-/Device-/Area-Registries mit stabiler Pseudonymisierung",
        "Config Entries (sanitisiert)",
        "Add-on- und System-Inventar",
        "Helper-Quelldefinitionen" if options.get("include_helper_source_definitions", True) else "Keine Helper-Quelldefinitionen",
        "Template-Quelldefinitionen" if options.get("include_template_source_definitions", True) else "Keine Template-Quelldefinitionen",
        "Aktueller States-Snapshot" if options.get("include_current_state_snapshot", True) else "Kein States-Snapshot",
        "Service-Katalog" if options.get("include_service_catalog", True) else "Kein Service-Katalog",
        "Recorder-Zusammenfassung" if options.get("include_recorder_summary", True) else "Keine Recorder-Zusammenfassung",
        "Recorder-Tiefenexport" if options.get("include_recorder_deep_export", True) else "Kein Recorder-Tiefenexport",
        "Mehrere States-Snapshots" if options.get("include_multi_state_snapshots", True) else "Nur ein Snapshot",
        "Backup-/Restore-Tiefenkontext" if options.get("include_backup_deep_context", True) else "Kein Backup-Tiefenkontext",
        "HA-/Core-/Supervisor-/Add-on-Logs" if options.get("include_logs", True) else "Keine Logs",
        "ESPHome-/python_scripts-/pyscript-/AppDaemon-Verzeichnisse, sofern vorhanden",
        "Security-/Exposure-Report" if options.get("include_security_exposure_report", True) else "Kein Security-/Exposure-Report",
        "Operator-Intent-Import" if options.get("include_operator_intent_import", True) else "Kein Operator-Intent-Import",
        "Gezielter Add-on-Options-Export" if options.get("include_addon_options_export", True) else "Kein Add-on-Options-Export",
        "Kritische Integrationsprofile" if options.get("include_integration_profiles", True) else "Keine Integrationsprofile",
        "Maschinenlesbares Unsicherheitsregister" if options.get("include_uncertainty_register", True) else "Kein Unsicherheitsregister",
    ]
    excluded_by_design = [
        "Echte Secret-Werte",
        "Roh-Tokens und Passwörter",
        "SSL-Schlüssel und Zertifikate",
        "Volle Recorder-Datenbank (außer include_recorder_db_copy=true)",
        "Medien-Dateien",
        "Nicht referenzierbare, zufällige IDs ohne Strukturbezug",
    ]
    lines = [
        "# ChatGPT Home Assistant Export Summary",
        "",
        f"Erstellt: {now_utc().isoformat()}",
        "",
        "## Ziel",
        "Dieser Export ist für eine andere ChatGPT-Instanz gedacht, damit sie dein Setup möglichst fehlerarm analysieren, verbessern, erweitern und refactoren kann.",
        "",
        "## Gespeicherte Ausgabepfade",
        f"- Nutzerrelevantes Archiv: {targets.primary.archive_path}",
    ]
    for mirror in targets.mirrors:
        lines.append(f"- Spiegel-Archiv: {mirror.archive_path} ({'ok' if mirror.ok else 'fehler'})")
    lines.extend(["", "## Enthalten"])
    lines.extend(f"- {item}" for item in included_hint)
    lines.extend(["", "## Bewusst ausgeschlossen"])
    lines.extend(f"- {item}" for item in excluded_by_design)
    lines.extend([
        "",
        "## Wichtige Einstiegsdateien für ChatGPT",
        "- metadata/export_manifest.json",
        "- metadata/export_report.json",
        "- metadata/export_summary.md",
        "- inventory/*.json",
        "- normalized/storage/*.json",
        "- normalized/config/*.json",
        "- runtime/state_snapshot.ndjson",
        "- runtime/state_snapshots_summary.json",
        "- runtime/recorder_summary.json",
        "- runtime/recorder_deep_export_summary.json",
        "- inventory/backup_context.json",
        "- inventory/security_exposure_report.json",
        "- inventory/addon_options_profiles.json",
        "- inventory/integration_profiles/*.json",
        "- inventory/uncertainty_register.json",
        "- metadata/operator_intent_template.md",
        *(["- metadata/operator_intent_import_manifest.json"] if operator_intent_import_manifest_exists else []),
        "",
        "## Beobachtungen",
        f"- Exportierte YAML-Dateien: {len(config_info.get('yaml_files', []))}",
        f"- Exportierte Verzeichnisse: {', '.join(config_info.get('directories', [])) or 'keine'}",
        f"- Exportierte .storage-Dateien: {len(storage_info.get('included', []))}",
        f"- Exportierte Log-Dateien: {', '.join(logs_info.get('all_exported_logs', [])) or 'keine'}",
        f"- API-Aufrufe: {len(stats.api_calls)}",
        f"- Recorder exportiert: {'ja' if recorder_info.get('exported') else 'nein'}",
        f"- Recorder-Tiefenexport: {'ja' if recorder_info.get('deep_exported') else 'nein'}",
        f"- Multi-Snapshot-Anzahl: {runtime_info.get('captured_snapshot_count', 0)}",
        f"- Backup-Kontext exportiert: {'ja' if backup_info.get('exported') else 'nein'}",
        f"- Theme-Status: {config_info.get('theme_include', {}).get('status', 'unbekannt')}",
        f"- Relationship-Integrity-Report: {'ja' if relationship_info.get('generated') else 'nein'}",
        f"- Security-/Exposure-Report: {'ja' if security_info.get('generated') else 'nein'}",
        f"- Operator-Intent importiert: {'ja' if operator_intent_info.get('imported') else 'nein'}",
        f"- Add-on-Optionsprofile: {'ja' if addon_options_info.get('exported') else 'nein'} ({addon_options_info.get('profile_count', 0)} Profile)",
        f"- Integrationsprofile: {'ja' if integration_profiles.get('generated') else 'nein'}",
        f"- Unsicherheitsregister: {'ja' if uncertainty_info.get('generated') else 'nein'} ({(uncertainty_info.get('counts') or {}).get('total', 0)} Einträge)",
        "",
        "## Warnungen",
    ])
    if stats.warnings:
        lines.extend(f"- {warning}" for warning in stats.warnings)
    else:
        lines.append("- Keine")
    out = export_dir / "metadata" / "export_summary.md"
    ensure_dir(out.parent)
    out.write_text("\n".join(lines), encoding="utf-8")
    stats.included_files.append(str(out))
def write_operator_intent_template(export_dir: Path, stats: ExportStats) -> None:
    content = """# operator_intent.md
## Zielarchitektur
- Welche Architektur willst du mittelfristig?
- Welche Integrationen/Add-ons sind strategisch gewollt?
## Kritische Automationen
- Welche Automationen dürfen nie unbeabsichtigt verändert werden?
- Welche Automationen sind sicherheitskritisch?
## Benennungsregeln
- Bevorzugte Sprache: deutsch / englisch / hybrid
- Regeln für entity_id, Helfer, Dashboards, Areas, Labels
## Backup-Strategie
- Führende Backup-Lösung
- Retention
- Externe Backup-Ziele
## Bewusst beibehaltene Altlasten
- Welche Legacy-Elemente sollen bewusst bleiben?
## Nie automatisch ändern
- Liste sensibler Geräte/Funktionen/Bereiche
"""
    path = export_dir / "metadata" / "operator_intent_template.md"
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    stats.included_files.append(str(path))
def parse_operator_intent_markdown(text: str) -> dict[str, Any]:
    sections: dict[str, list[str]] = {}
    current = "_root"
    sections[current] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        heading = re.match(r'^#{1,6}\s+(.*)$', line.strip())
        if heading:
            current = heading.group(1).strip() or current
            sections.setdefault(current, [])
            continue
        stripped = line.strip()
        if stripped:
            sections.setdefault(current, []).append(stripped)
    compact = {key: values for key, values in sections.items() if values}
    return {
        "format": "markdown",
        "sections": compact,
        "section_count": len(compact),
    }
def find_operator_intent_candidates() -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = []
    seen: set[str] = set()
    names = (
        'operator_intent.md', 'operator_intent.json', 'operator_intent.yaml', 'operator_intent.yml',
        'ha_operator_intent.md', 'ha_operator_intent.json', 'chatgpt_operator_intent.md',
    )
    roots = (('homeassistant', HA_CONFIG_DIR), ('share', SHARE_DIR))
    for label, root in roots:
        for name in names:
            path = root / name
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            if path.exists() and path.is_file():
                candidates.append((label, path))
    return candidates
def import_operator_intent(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    info: dict[str, Any] = {
        "enabled": bool(options.get("include_operator_intent_import", True)),
        "imported": False,
        "sources": [],
        "candidate_count": 0,
    }
    if not options.get("include_operator_intent_import", True):
        return info
    candidates = find_operator_intent_candidates()
    info["candidate_count"] = len(candidates)
    imported_rows: list[dict[str, Any]] = []
    import_root = export_dir / "metadata" / "operator_intent_import"
    for source_label, src in candidates:
        row: dict[str, Any] = {
            "source_label": source_label,
            "source_path": str(src),
            "filename": src.name,
            "format": src.suffix.lower().lstrip('.'),
            "imported": False,
            "parsed": False,
        }
        try:
            raw_text = src.read_text(encoding="utf-8", errors="ignore")
            sanitized_text = sanitize_text_file(raw_text)
            dst = import_root / f"{source_label}__{src.name}"
            ensure_dir(dst.parent)
            dst.write_text(sanitized_text, encoding="utf-8")
            stats.included_files.append(str(dst))
            row["imported"] = True
            parsed: Any = None
            if src.suffix.lower() == '.json':
                parsed = sanitize_data(json.loads(raw_text))
            elif src.suffix.lower() in {'.yaml', '.yml'}:
                parsed = sanitize_data(yaml.load(raw_text, Loader=IgnoreUnknownLoader))
            else:
                parsed = parse_operator_intent_markdown(sanitized_text)
            row["parsed"] = True
            row["normalized"] = parsed
            imported_rows.append(row)
        except Exception as exc:
            row["error"] = str(exc)
            imported_rows.append(row)
            stats.warnings.append(f"Operator-Intent-Import fehlgeschlagen für {src}: {exc}")
    summary = {
        "enabled": info["enabled"],
        "imported": any(row.get("imported") for row in imported_rows),
        "candidate_count": len(candidates),
        "sources": [
            {k: v for k, v in row.items() if k != 'normalized'}
            for row in imported_rows
        ],
        "normalized_sources": [
            {
                "source_label": row.get("source_label"),
                "filename": row.get("filename"),
                "format": row.get("format"),
                "normalized": row.get("normalized"),
            }
            for row in imported_rows if row.get("parsed")
        ],
    }
    manifest_path = export_dir / "metadata" / "operator_intent_import_manifest.json"
    write_json(manifest_path, summary)
    stats.included_files.append(str(manifest_path))
    normalized_path = export_dir / "metadata" / "operator_intent_context.json"
    write_json(normalized_path, summary.get("normalized_sources", []))
    stats.included_files.append(str(normalized_path))
    return summary
def build_security_exposure_report(export_dir: Path, options: dict[str, Any], stats: ExportStats) -> dict[str, Any]:
    info: dict[str, Any] = {"enabled": bool(options.get("include_security_exposure_report", True)), "generated": False}
    if not options.get("include_security_exposure_report", True):
        return info
    config = read_export_json(export_dir / "normalized" / "config" / "configuration.yaml.json") or {}
    api_config = read_export_json(export_dir / "inventory" / "api_config.json") or {}
    storage_http = read_export_json(export_dir / "normalized" / "storage" / "http.json") or {}
    storage_http_auth = read_export_json(export_dir / "normalized" / "storage" / "http.auth.json") or {}
    storage_network = read_export_json(export_dir / "normalized" / "storage" / "core.network.json") or {}
    storage_auth = read_export_json(export_dir / "normalized" / "storage" / "auth.json") or {}
    storage_auth_provider = read_export_json(export_dir / "normalized" / "storage" / "auth_provider.homeassistant.json") or {}
    storage_exposed = read_export_json(export_dir / "normalized" / "storage" / "homeassistant.exposed_entities.json") or {}
    storage_application_credentials = read_export_json(export_dir / "normalized" / "storage" / "application_credentials.json") or {}
    storage_mobile_app = read_export_json(export_dir / "normalized" / "storage" / "mobile_app.json") or {}
    storage_assist = read_export_json(export_dir / "normalized" / "storage" / "assist_pipeline.pipelines.json") or {}
    frontend_system = read_export_json(export_dir / "normalized" / "storage" / "frontend.system_data.json") or {}
    frontend_panels = read_export_json(export_dir / "normalized" / "storage" / "frontend_panels.json") or {}
    frontend_user_data_files = sorted([p.name for p in (export_dir / "normalized" / "storage").glob("frontend.user_data_*.json")])
    http_cfg = (config.get("http") or {}) if isinstance(config, dict) else {}
    cloud_cfg_present = isinstance(config, dict) and any(key in config for key in ("cloud", "google_assistant", "alexa"))

    auth_present = (export_dir / 'normalized' / 'storage' / 'auth.json').exists()
    provider_present = (export_dir / 'normalized' / 'storage' / 'auth_provider.homeassistant.json').exists()
    network_present = (export_dir / 'normalized' / 'storage' / 'core.network.json').exists()

    users_count = None
    owners = None
    active_users = None
    system_generated = None
    auth_users = recursive_find_key(storage_auth, "users")
    if auth_users:
        user_list = auth_users[0] if isinstance(auth_users[0], list) else []
        users_count = len(user_list)
        owners = 0
        active_users = 0
        system_generated = 0
        for user in user_list:
            if isinstance(user, dict):
                if user.get("is_owner") is True:
                    owners += 1
                if user.get("is_active") is not False:
                    active_users += 1
                if user.get("system_generated") is True:
                    system_generated += 1

    provider_count = None
    providers = recursive_find_key(storage_auth_provider, "providers")
    if providers:
        provider_count = len(providers[0]) if isinstance(providers[0], list) else count_mappingish_items(providers[0]) or 0
    elif storage_auth_provider:
        provider_count = 1

    exposed_entities = storage_exposed.get("data", {}).get("exposed_entities", {}) if isinstance(storage_exposed.get("data"), dict) else {}
    exposed_count = len(exposed_entities) if isinstance(exposed_entities, dict) else count_entities_in_structure(storage_exposed)
    app_cred_count = count_mappingish_items(storage_application_credentials) or 0
    mobile_app_count = count_mappingish_items(storage_mobile_app) or 0
    assist_pipeline_count = count_mappingish_items(storage_assist) or 0
    frontend_panel_count = count_mappingish_items(frontend_panels) or 0

    adapters = recursive_find_key(storage_network, "adapters")
    adapter_count = None
    if adapters:
        adapter_count = len(adapters[0]) if isinstance(adapters[0], list) else count_mappingish_items(adapters[0]) or 0
    elif isinstance(storage_network, dict) and isinstance(storage_network.get("data"), dict):
        configured_adapters = storage_network.get("data", {}).get("configured_adapters")
        if isinstance(configured_adapters, list):
            adapter_count = len(configured_adapters)

    http_summary = {
        "configured_in_yaml": isinstance(http_cfg, dict) and bool(http_cfg),
        "use_x_forwarded_for": bool(http_cfg.get("use_x_forwarded_for")) if isinstance(http_cfg, dict) else False,
        "trusted_proxies_count": len(http_cfg.get("trusted_proxies", [])) if isinstance(http_cfg.get("trusted_proxies"), list) else 0,
        "ip_ban_enabled": http_cfg.get("ip_ban_enabled") if isinstance(http_cfg, dict) else None,
        "login_attempts_threshold": http_cfg.get("login_attempts_threshold") if isinstance(http_cfg, dict) else None,
        "cors_allowed_origins_count": len(http_cfg.get("cors_allowed_origins", [])) if isinstance(http_cfg.get("cors_allowed_origins"), list) else 0,
        "ssl_certificate_configured": truthy_path(http_cfg.get("ssl_certificate")) if isinstance(http_cfg, dict) else False,
        "ssl_key_configured": truthy_path(http_cfg.get("ssl_key")) if isinstance(http_cfg, dict) else False,
        "storage_http_present": bool(storage_http),
        "storage_http_auth_present": bool(storage_http_auth),
    }
    api_payload = api_config.get("data", api_config) if isinstance(api_config, dict) else {}
    url_strings = flatten_strings({"api_config": api_payload, "storage_http": storage_http, "network": storage_network}, max_items=1000)
    external_like = [s for s in url_strings if isinstance(s, str) and ('http://' in s or 'https://' in s or '<host-' in s or '<ip-' in s)]
    findings: list[dict[str, Any]] = []
    def add_finding(fid: str, title: str, severity: str, evidence: dict[str, Any], summary: str) -> None:
        findings.append({"id": fid, "title": title, "severity": severity, "evidence": evidence, "summary": summary})
    if http_summary["use_x_forwarded_for"] or http_summary["trusted_proxies_count"]:
        add_finding("SEC-HTTP-001", "Reverse-Proxy-Kontext erkannt", "info", {"use_x_forwarded_for": http_summary["use_x_forwarded_for"], "trusted_proxies_count": http_summary["trusted_proxies_count"]}, "HTTP/Proxy-Kontext ist relevant und sollte bei Sicherheits- und Expositionsänderungen berücksichtigt werden.")
    if http_summary["ssl_certificate_configured"] or http_summary["ssl_key_configured"]:
        add_finding("SEC-HTTP-SSL-001", "Eigene SSL-Konfiguration in YAML erkannt", "info", {"ssl_certificate_configured": http_summary["ssl_certificate_configured"], "ssl_key_configured": http_summary["ssl_key_configured"]}, "Das Setup scheint direkten TLS-Kontext in Home Assistant zu führen oder zu referenzieren.")
    if (provider_count or 0) > 0 or (users_count or 0) > 0:
        add_finding("SEC-AUTH-001", "Authentifizierungs-Kontext exportiert", "info", {"provider_count": provider_count, "users_count": users_count, "owner_count": owners, "active_users": active_users}, "Benutzer- und Provider-Struktur ist zumindest teilweise sichtbar.")
    elif not auth_present or not provider_present:
        add_finding("SEC-AUTH-UNKNOWN", "Authentifizierungs-Kontext nur teilweise exportiert", "low", {"auth_present": auth_present, "provider_present": provider_present}, "Mindestens ein relevanter Auth-Kontext fehlt; Benutzer-/Provider-Zahlen sind daher nur eingeschränkt belastbar.")
    if exposed_count > 0 or cloud_cfg_present:
        add_finding("SEC-EXPOSE-001", "Expose-/Voice-Assistant-Kontext erkannt", "info", {"exposed_entities_count": exposed_count, "cloud_or_voice_config_present": cloud_cfg_present}, "Exponierte Entitäten bzw. Sprachassistent-Kontext sind Teil der Optimierungs- und Sicherheitsbewertung.")
    if app_cred_count > 0:
        add_finding("SEC-APPCREDS-001", "Application Credentials vorhanden", "info", {"application_credentials_count": app_cred_count}, "Integrationen mit externen Diensten sind wahrscheinlich vorhanden; Änderungen sollten Credential-Kontext berücksichtigen.")
    if mobile_app_count > 0:
        add_finding("SEC-MOBILE-001", "Mobile-App-Kontext vorhanden", "info", {"mobile_app_count": mobile_app_count}, "Mobile Geräte/Trigger/Notifications können Teil kritischer Abläufe sein.")
    if assist_pipeline_count > 0:
        add_finding("SEC-ASSIST-001", "Assist-Pipelines vorhanden", "info", {"assist_pipeline_count": assist_pipeline_count}, "Sprach-/Assist-Pipelines sind konfiguriert und sollten bei Umstrukturierungen berücksichtigt werden.")
    if (adapter_count or 0) > 0 or external_like:
        add_finding("SEC-NET-001", "Netzwerk-/Erreichbarkeits-Kontext vorhanden", "info", {"adapter_count": adapter_count, "url_like_values_count": len(external_like)}, "Netzwerk- und Erreichbarkeitsdaten sind teilweise sichtbar; Änderungen an HTTP/Cloud/Proxy nur mit Vorsicht.")
    if frontend_panel_count > 0 or frontend_user_data_files or frontend_system:
        add_finding("SEC-UI-001", "Frontend-/Panel-Kontext vorhanden", "info", {"frontend_panel_count": frontend_panel_count, "frontend_user_data_files": frontend_user_data_files[:20]}, "Zusätzliche Panels oder user-spezifische Frontend-Kontexte sind im Export sichtbar.")
    info = {
        "generated": True,
        "sources": {
            "configuration_yaml": bool(config),
            "api_config": bool(api_config),
            "http_storage": bool(storage_http),
            "http_auth_storage": bool(storage_http_auth),
            "network_storage": bool(storage_network),
            "auth_storage": bool(storage_auth),
            "auth_provider_storage": bool(storage_auth_provider),
            "exposed_entities_storage": bool(storage_exposed),
            "application_credentials_storage": bool(storage_application_credentials),
            "mobile_app_storage": bool(storage_mobile_app),
            "assist_pipeline_storage": bool(storage_assist),
            "frontend_system_storage": bool(frontend_system),
            "frontend_panels_storage": bool(frontend_panels),
            "frontend_user_data_files": frontend_user_data_files,
        },
        "http": http_summary,
        "auth": {
            "auth_present": auth_present,
            "provider_present": provider_present,
            "users_count": users_count,
            "owners_count": owners,
            "active_users_count": active_users,
            "system_generated_users_count": system_generated,
            "provider_count": provider_count,
        },
        "exposure": {
            "cloud_or_voice_config_present": cloud_cfg_present,
            "exposed_entities_count": exposed_count,
            "application_credentials_count": app_cred_count,
            "mobile_app_count": mobile_app_count,
            "assist_pipeline_count": assist_pipeline_count,
        },
        "network": {
            "network_present": network_present,
            "adapter_count": adapter_count,
            "url_like_values_count": len(external_like),
            "internal_url_present": bool(api_payload.get("internal_url")) or any('internal' in s.lower() for s in external_like),
            "external_url_present": bool(api_payload.get("external_url")) or any('external' in s.lower() for s in external_like),
        },
        "frontend": {
            "frontend_panel_count": frontend_panel_count,
            "frontend_user_data_file_count": len(frontend_user_data_files),
            "theme_declared": bool((read_export_json(export_dir / 'inventory' / 'config_inventory.json') or {}).get('theme_include', {}).get('declared')),
        },
        "operator_sensitive_domains": {
            "mobile_app": mobile_app_count > 0,
            "assist": assist_pipeline_count > 0,
            "voice_or_cloud_exposure": cloud_cfg_present or exposed_count > 0,
        },
        "findings": findings,
        "summary": {
            "finding_count": len(findings),
            "high_signal_context_present": bool(findings),
            "partial_confidence": (not auth_present) or (not provider_present) or (not network_present),
        },
    }
    json_path = export_dir / "inventory" / "security_exposure_report.json"
    write_json(json_path, info)
    stats.included_files.append(str(json_path))
    lines = [
        "# Security / Exposure Report",
        "",
        f"Generated: {now_utc().isoformat()}",
        "",
        "## Highlights",
        f"- HTTP YAML configured: {http_summary['configured_in_yaml']}",
        f"- Trusted proxies: {http_summary['trusted_proxies_count']}",
        f"- Auth users visible: {users_count if users_count is not None else 'unknown'}",
        f"- Auth providers visible: {provider_count if provider_count is not None else 'unknown'}",
        f"- Exposed entities visible: {exposed_count}",
        f"- Application credentials visible: {app_cred_count}",
        f"- Mobile app entries visible: {mobile_app_count}",
        f"- Assist pipelines visible: {assist_pipeline_count}",
        f"- Frontend panels visible: {frontend_panel_count}",
        "",
        "## Findings",
    ]
    if findings:
        for finding in findings:
            lines.append(f"- [{finding['severity']}] {finding['title']}: {finding['summary']}")
    else:
        lines.append("- No notable security/exposure signals could be derived from the exported data.")
    md_path = export_dir / "inventory" / "security_exposure_report.md"
    ensure_dir(md_path.parent)
    md_path.write_text("\n".join(lines), encoding="utf-8")
    stats.included_files.append(str(md_path))
    return info

def write_user_hint_files(report: dict[str, Any]) -> None:
    return

def main() -> int:
    options = load_options()
    prefix = str(options.get("export_name_prefix", "ha_chatgpt_export")).strip() or "ha_chatgpt_export"
    timestamp = now_utc().strftime("%Y%m%dT%H%M%SZ")
    export_name = f"{prefix}_{timestamp}"
    stats = ExportStats()
    targets = determine_output_targets(export_name, options, stats)
    work_export_dir = WORK_DIR / export_name
    if work_export_dir.exists():
        shutil.rmtree(work_export_dir)
    ensure_dir(work_export_dir)
    try:
        config_info = export_config_files(work_export_dir, options, stats)
        storage_info = export_storage(work_export_dir, options, stats)
        api_info = export_api_inventory(work_export_dir, options, stats)
        runtime_info = export_multi_state_snapshots(work_export_dir, options, stats)
        recorder_info = export_recorder_summary(work_export_dir, options, stats)
        backup_info = export_backup_context(work_export_dir, options, stats)
        logs_info = export_logs(work_export_dir, options, stats)
        relationship_info = build_relationship_integrity_report(work_export_dir, stats) if options.get("include_relationship_integrity_report", True) else {"generated": False}
        security_info = build_security_exposure_report(work_export_dir, options, stats)
        operator_intent_info = import_operator_intent(work_export_dir, options, stats)
        addon_options_info = export_addon_options_profiles(work_export_dir, options, stats)
        integration_profiles = build_integration_profiles(work_export_dir, options, stats, addon_options_info)
        uncertainty_info = build_uncertainty_register(work_export_dir, options, stats, config_info, storage_info, logs_info, recorder_info, backup_info, operator_intent_info, integration_profiles, addon_options_info)
        if options.get("include_operator_intent_template", True):
            write_operator_intent_template(work_export_dir, stats)
        manifest_data = {
            "exporter": {"name": "ChatGPT HA Exporter", "version": EXPORTER_VERSION, "created_at": now_utc().isoformat()},
            "paths": {"homeassistant_config": str(HA_CONFIG_DIR), "share": str(SHARE_DIR)},
            "options": options,
            "config_info": config_info,
            "storage_info": storage_info,
            "api_info": api_info,
            "runtime_info": runtime_info,
            "recorder_info": recorder_info,
            "backup_info": backup_info,
            "logs_info": logs_info,
            "relationship_info": relationship_info,
            "security_info": security_info,
            "operator_intent_info": operator_intent_info,
            "addon_options_info": addon_options_info,
            "integration_profiles": integration_profiles,
            "uncertainty_info": {"generated": uncertainty_info.get("generated"), "counts": uncertainty_info.get("counts")},
            "warnings": stats.warnings,
            "excluded_items": stats.excluded_items,
        }
        report, _ = finalize_export_tree(work_export_dir, export_name, options, stats, targets, manifest_data, config_info, storage_info, api_info, runtime_info, recorder_info, backup_info, logs_info, relationship_info, security_info, operator_intent_info, addon_options_info, integration_profiles, uncertainty_info, include_output_report=True)
        archive_path = create_archive(work_export_dir, targets.primary.archive_path)
        print(f"Archiv: {archive_path}")
        if stats.warnings:
            print("Warnungen:")
            for warning in stats.warnings:
                print(f"- {warning}")
        return 0
    finally:
        if work_export_dir.exists():
            shutil.rmtree(work_export_dir, ignore_errors=True)

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        print("UNBEHANDELTER FEHLER")
        traceback.print_exc()
        raise
