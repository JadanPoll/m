"""Compact offline next-word lookup for Firefly.

Data is generated from independently licensed Leipzig bigram counts; its
values are *observed counts*, not calibrated neural probabilities. A pruned
row provides conditional ordering only; omitted mass is unknown. This module
uses only the standard library and never accesses the network.
"""

from __future__ import annotations


class StaticNextWords:
    def __init__(self, rows: dict[str, tuple[tuple[str, int], ...]] | None = None):
        self.rows = rows or {}

    @classmethod
    def load(cls, path: str) -> "StaticNextWords":
        rows: dict[str, tuple[tuple[str, int], ...]] = {}
        try:
            with open(path, "r", encoding="utf-8") as stream:
                for line in stream:
                    if line.startswith("#") or not line.strip():
                        continue
                    try:
                        previous, entries = line.rstrip("\n").split("\t", 1)
                        if not previous.isalpha() or previous != previous.lower():
                            continue
                        candidates = []
                        for entry in entries.split():
                            word, count = entry.rsplit(":", 1)
                            if not word.replace("'", "").isalpha():
                                continue
                            frequency = int(count, 36)
                            if frequency > 0:
                                candidates.append((word, frequency))
                        if candidates:
                            rows[previous] = tuple(candidates[:8])
                    except (ValueError, OverflowError):
                        continue  # Malformed optional data must not disable typing.
        except (OSError, UnicodeError):
            pass  # Keep the original predictor working with no static asset.
        return cls(rows)

    def candidates(self, previous: str, prefix: str = "") -> tuple[tuple[str, int], ...]:
        row = self.rows.get(previous.casefold(), ())
        prefix = prefix.casefold()
        return tuple((word, count) for word, count in row
                     if word.startswith(prefix) and word != prefix)

    def strength(self, previous: str, word: str) -> float:
        """Relative association within one pruned context, not a true P(word|prev)."""
        row = self.rows.get(previous.casefold(), ())
        if not row:
            return 0.0
        peak = max(count for _, count in row)
        for candidate, count in row:
            if candidate == word.casefold():
                return (count / peak) ** 0.5
        return 0.0
