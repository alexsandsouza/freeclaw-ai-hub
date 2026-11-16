"""Review-only extraction of Python files from an AI-written Markdown proposal.

Expected format:
### Arquivo: src/main.py
```python
print("example")
```

No paths are ever written into a project tree. The caller may export an isolated ZIP.
"""
from __future__ import annotations
import io
import re
import zipfile
from pathlib import PurePosixPath

MAX_FILES = 20
MAX_TOTAL_CHARS = 200_000
MAX_FILE_CHARS = 70_000
HEADER = re.compile(r"^#{2,4}\s*(?:Arquivo|File)\s*:\s*(\S+)\s*$", re.I | re.M)
BLOCK = re.compile(r"^\s*```(?:python|py)\s*\n(.*?)^\s*```\s*$", re.I | re.M | re.S)
SUSPICIOUS = re.compile(
    r"(?:nvapi-[A-Za-z0-9_-]{8,}|sk-[A-Za-z0-9_-]{12,}|AIza[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)",
    re.I,
)

def safe_path(raw: str) -> str:
    if not raw or "\\" in raw or ":" in raw or raw.startswith(("/", "~")) or "%" in raw:
        raise ValueError("Caminho inseguro na proposta.")
    path = PurePosixPath(raw)
    if (
        path.is_absolute()
        or any(part in ("", ".", "..") for part in raw.split("/"))
        or len(path.parts) < 2
        or path.parts[0] not in ("src", "tests")
        or path.suffix != ".py"
        or len(raw) > 150
    ):
        raise ValueError("Somente arquivos .py dentro de src/ ou tests/ são aceitos.")
    return path.as_posix()

def extract_files(markdown: str) -> dict[str, str]:
    if not isinstance(markdown, str) or len(markdown) > MAX_TOTAL_CHARS:
        raise ValueError("Resposta inválida ou maior que 200 mil caracteres.")
    matches = list(HEADER.finditer(markdown))
    if len(matches) > MAX_FILES:
        raise ValueError("Excesso de arquivos propostos (limite 20).")
    result = {}
    for index, match in enumerate(matches):
        name = safe_path(match.group(1))
        if name in result:
            raise ValueError("Arquivo duplicado na proposta: " + name)
        segment = markdown[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(markdown)]
        block = BLOCK.search(segment)
        if block is None:
            raise ValueError("Falta bloco de código Python após " + name)
        source = block.group(1)
        if not source.strip() or len(source) > MAX_FILE_CHARS:
            raise ValueError("Código vazio ou muito grande em " + name)
        if SUSPICIOUS.search(source):
            raise ValueError("Possível chave ou segredo no código de " + name)
        result[name] = source.rstrip() + "\n"
    if not result:
        raise ValueError("Nenhum arquivo identificado. Use '### Arquivo: src/nome.py' seguido de bloco ```python.")
    return result

def build_zip(files: dict[str, str]) -> bytes:
    if not files or len(files) > MAX_FILES:
        raise ValueError("Número de arquivos inválido.")
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("REVIEW_REQUIRED.md",
            "# FreeClaw - revisão obrigatória\n\n"
            "Arquivos gerados por IA, não executados e não aprovados.\n"
            "Analise dependências, permissões, vulnerabilidades, requisitos RF/AC e dados sensíveis.\n"
            "Não execute nem copie diretamente para produção.\n")
        total = 0
        for raw, source in files.items():
            name = safe_path(raw)
            if not isinstance(source, str) or SUSPICIOUS.search(source):
                raise ValueError("Código inválido ou com possível segredo.")
            total += len(source)
            if len(source) > MAX_FILE_CHARS or total > MAX_TOTAL_CHARS:
                raise ValueError("Limite de tamanho dos arquivos excedido.")
            archive.writestr(name, source)
    return output.getvalue()
