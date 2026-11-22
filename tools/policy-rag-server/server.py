#!/usr/bin/env python3
"""Keyword search over shelter policy documents — no embedding API key required."""

import math
import os
import re
from collections import Counter
from pathlib import Path

from mcp.server.mcpserver import (
    MCPServer,
)  # mcp 1.x: from mcp.server.fastmcp import FastMCP

POLICY_DIR = Path(os.environ.get("POLICY_DIR", "policies"))
MAX_POLICY_CHARS = 20_000
mcp = MCPServer("policy-rag")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def load_corpus() -> list[dict]:
    docs = []
    for path in sorted(POLICY_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        tokens = tokenize(raw)
        docs.append(
            {
                "file": path.name,
                "raw": raw,
                "freq": Counter(tokens),
                "size": len(tokens),
            }
        )
    return docs


def score(query_tokens: list[str], doc: dict) -> float:
    hits = sum(doc["freq"][t] for t in query_tokens)
    return hits / math.sqrt(doc["size"] or 1)


def excerpt(raw: str) -> str:
    """Return the policy text, marking it clearly if it had to be cut."""
    if len(raw) <= MAX_POLICY_CHARS:
        return raw
    return f"{raw[:MAX_POLICY_CHARS]}\n\n[TRUNCATED: read the full policy file]"


@mcp.tool()
def rag_query(question: str) -> str:
    """Answers a question using the shelter's screening and adoption policies."""
    q = tokenize(question)
    ranked = sorted(
        ((score(q, d), d) for d in load_corpus()), key=lambda p: p[0], reverse=True
    )
    hits = [(s, d) for s, d in ranked[:3] if s > 0]
    if not hits:
        return f'No policy matched "{question}".'
    return "\n\n".join(f"### {d['file']}\n{excerpt(d['raw'])}" for _, d in hits)


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
