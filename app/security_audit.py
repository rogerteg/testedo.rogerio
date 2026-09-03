"""Auditoria de segredos nos registros persistidos (T042 / SC-005).

Varre o banco SQLite em busca de valores que contenham sinais de
segredos/credenciais nos campos de texto do catálogo — defesa em profundidade
além da validação de entrada (FR-013, aplicada em app/schemas.py).
"""
import sqlite3
from pathlib import Path

from app.schemas import CAMPOS_TEXTO, contem_segredo


def auditar_segredos(db_path: Path | str) -> list[dict]:
    """Retorna as violações encontradas: ``[{id, campo, valor_resumo}]``.

    Cada item indica o registro (``id``), o campo violado e um resumo curto
    do valor (para inspeção humana sem expor o conteúdo completo).
    """
    campos = ", ".join(CAMPOS_TEXTO)
    violacoes: list[dict] = []

    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f"SELECT id, {campos} FROM environment_setup").fetchall()

    for row in rows:
        for campo in CAMPOS_TEXTO:
            valor = row[campo]
            if isinstance(valor, str) and contem_segredo(valor):
                resumo = valor if len(valor) <= 40 else f"{valor[:37]}..."
                violacoes.append({"id": row["id"], "campo": campo, "valor_resumo": resumo})

    return violacoes


def main(db_path: Path | str | None = None) -> int:
    """CLI: retorna 0 se nenhuma violação; 1 caso contrário (para CI)."""
    if db_path is None:
        db_path = Path(__file__).resolve().parent.parent / "data" / "setups.db"

    violacoes = auditar_segredos(db_path)

    if violacoes:
        print(f"[audit-secrets] {len(violacoes)} violação(ões) em {db_path}:")
        for v in violacoes:
            print(f"  - id={v['id']} campo={v['campo']} valor={v['valor_resumo']}")
        return 1

    print(f"[audit-secrets] OK — nenhum segredo detectado em {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
