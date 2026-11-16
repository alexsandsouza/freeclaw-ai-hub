"""Read-only comparison of AI-proposed Python files with an existing project.

The project directory is never modified. Approved selections are exported as
an isolated ZIP, not applied automatically.
"""
from __future__ import annotations

import difflib
import io
import zipfile
from pathlib import Path
from proposal_parser import build_zip, safe_path

MAX_EXISTING_FILE_BYTES = 100_000
MAX_ZIP_BYTES = 2_000_000

def _safe_existing(project_root: Path, filename: str) -> Path:
    relative = safe_path(filename)
    root = project_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("A origem deve ser uma pasta existente.")
    path = root.joinpath(*relative.split("/"))
    # Reject symbolic-link components, including final symlink, to avoid file
    # disclosure through an existing project symlink.
    cursor = root
    for part in relative.split("/"):
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("Links simbólicos não são permitidos.")
    resolved = path.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise ValueError("Caminho fora da pasta do projeto.")
    return path

def compare_files(project_root: Path, proposed: dict[str, str]) -> dict[str, dict[str,str]]:
    if not isinstance(proposed, dict) or not proposed:
        raise ValueError("Nenhum arquivo proposto para comparação.")
    # Build ZIP once to validate path, content, size and suspicious secrets.
    build_zip(proposed)
    result = {}
    for filename, source in proposed.items():
        target = _safe_existing(project_root, filename)
        if target.exists():
            if not target.is_file() or target.stat().st_size > MAX_EXISTING_FILE_BYTES:
                raise ValueError("Arquivo existente inválido ou muito grande: " + filename)
            old = target.read_text(encoding="utf-8-sig")
            status = "alterado" if old != source else "idêntico"
        else:
            old, status = "", "novo"
        diff = "".join(difflib.unified_diff(
            old.splitlines(keepends=True), source.splitlines(keepends=True),
            fromfile="original/" + filename, tofile="proposto/" + filename,
        ))
        result[filename] = {"status":status, "diff":diff or "(sem alterações)\n"}
    return result

def export_selected(proposed: dict[str,str], selected: list[str]) -> bytes:
    if not selected or not isinstance(selected, list):
        raise ValueError("Selecione ao menos um arquivo revisado.")
    if len(selected) != len(set(selected)):
        raise ValueError("Seleção duplicada.")
    if any(name not in proposed for name in selected):
        raise ValueError("Seleção contém arquivo desconhecido.")
    return build_zip({name: proposed[name] for name in selected})

def read_proposal_zip(data: bytes) -> dict[str,str]:
    if len(data) > MAX_ZIP_BYTES:
        raise ValueError("ZIP de proposta muito grande.")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > 24:
            raise ValueError("ZIP com arquivos em excesso.")
        result = {}
        for member in members:
            if member.is_dir() or member.filename == "REVIEW_REQUIRED.md":
                continue
            name = safe_path(member.filename)
            if name in result:
                raise ValueError("Caminho duplicado no ZIP.")
            if member.file_size > MAX_EXISTING_FILE_BYTES or member.compress_size > MAX_ZIP_BYTES:
                raise ValueError("Arquivo no ZIP excede limite.")
            # Disallow symlinks encoded as Unix ZIP entries
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("ZIP contém link simbólico.")
            text = archive.read(member).decode("utf-8-sig")
            result[name] = text
        if not result:
            raise ValueError("ZIP sem arquivos Python de projeto.")
        build_zip(result)  # re-validate contents and paths
        return result
