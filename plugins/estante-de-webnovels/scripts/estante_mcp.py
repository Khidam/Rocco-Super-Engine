#!/usr/bin/env python3
"""Servidor MCP sem dependencias para dados locais da Estante de Webnovels."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("ESTANTE_DATA_DIR", "~/.local/share/estante-de-webnovels")).expanduser()
KINDS = {"profiles", "works", "reading"}


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    if not clean:
        clean = hashlib.sha256(value.encode()).hexdigest()[:16]
    return clean[:96]


def _path(kind: str, key: str) -> Path:
    if kind not in KINDS:
        raise ValueError("tipo de registro invalido")
    return ROOT / kind / f"{slug(key)}.json"


def load(kind: str, key: str) -> dict[str, Any] | None:
    path = _path(kind, key)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def save(kind: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    path = _path(kind, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {**value, "id": key, "updated_at": datetime.now(timezone.utc).isoformat()}
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
    return record


TOOLS = [
    ("save_profile", "Salva perfil e fontes sem capitulos integrais", {"title": "string", "profile": "object"}),
    ("get_profile", "Le um perfil pelo titulo", {"title": "string"}),
    ("save_work", "Salva original ou versao sem sobrescrever outras versoes", {"work_id": "string", "work": "object"}),
    ("get_work", "Le original e versoes", {"work_id": "string"}),
    ("list_works", "Lista obras do usuario", {}),
    ("set_reading_progress", "Salva ponto de leitura e anotacoes", {"title": "string", "progress": "object"}),
    ("get_reading_progress", "Le ponto de leitura", {"title": "string"}),
]


def schema(fields: dict[str, str]) -> dict[str, Any]:
    return {"type": "object", "properties": {k: {"type": v} for k, v in fields.items()}, "required": list(fields), "additionalProperties": False}


def call(name: str, args: dict[str, Any]) -> Any:
    if name == "save_profile":
        return save("profiles", args["title"], args["profile"])
    if name == "get_profile":
        return load("profiles", args["title"])
    if name == "save_work":
        current = load("works", args["work_id"]) or {"original": None, "versions": []}
        incoming = args["work"]
        if incoming.get("kind") == "original":
            if current.get("original") is not None:
                raise ValueError("o original ja existe; crie uma versao")
            current["original"] = incoming
        else:
            current.setdefault("versions", []).append(incoming)
        return save("works", args["work_id"], current)
    if name == "get_work":
        return load("works", args["work_id"])
    if name == "list_works":
        folder = ROOT / "works"
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))] if folder.exists() else []
    if name == "set_reading_progress":
        return save("reading", args["title"], args["progress"])
    if name == "get_reading_progress":
        return load("reading", args["title"])
    raise ValueError(f"ferramenta desconhecida: {name}")


def response(message: dict[str, Any]) -> dict[str, Any] | None:
    if "id" not in message:
        return None
    rid = message["id"]
    try:
        method = message.get("method")
        if method == "initialize":
            result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "estante-storage", "version": "0.1.0"}}
        elif method == "tools/list":
            result = {"tools": [{"name": n, "description": d, "inputSchema": schema(s)} for n, d, s in TOOLS]}
        elif method == "tools/call":
            params = message.get("params", {})
            data = call(params.get("name", ""), params.get("arguments", {}))
            result = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}], "isError": False}
        elif method == "ping":
            result = {}
        else:
            raise ValueError(f"metodo desconhecido: {method}")
        return {"jsonrpc": "2.0", "id": rid, "result": result}
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": str(exc)}}


def main() -> None:
    for line in sys.stdin:
        try:
            outgoing = response(json.loads(line))
        except json.JSONDecodeError as exc:
            outgoing = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        if outgoing is not None:
            print(json.dumps(outgoing, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
