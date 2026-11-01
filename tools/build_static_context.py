"""Build Firefly's compact English static next-word table from an open dataset.

Input: synth-inc/predictive-bigrams data/en_bigrams_50k.txt, derived from
Leipzig Corpora Collection (CC BY 4.0). Not fetched automatically: download
the pinned source yourself and run:

  python tools/build_static_context.py upstream_en_bigrams_50k.txt data/en_context_bigrams.tsv

Output: at most eight continuations per predecessor, sorted deterministically;
base-36 frequencies retain useful relative evidence without shipping 50k
unfiltered pair rows. No third-party dependencies or runtime model download.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
from pathlib import Path
import re

UPSTREAM_BLOB = "208514436252cbb3834207d562f36773227e682d"
VALID_WORD = re.compile(r"[a-z]+(?:'[a-z]+)?\Z")
HEADER = (
    "# Firefly context bigrams v1; prev<TAB>next:base36-count ...\n"
    "# Source: synth-inc/predictive-bigrams data/en_bigrams_50k.txt @ "
    + UPSTREAM_BLOB + "\n"
    "# Original counts: Leipzig Corpora Collection, CC BY 4.0; "
    "top 8 per predecessor, aggregated duplicates, count >= 50.\n"
)


def base36(value: int) -> str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    if value < 1:
        raise ValueError("Expected a positive frequency")
    chars = []
    while value:
        value, rem = divmod(value, 36)
        chars.append(alphabet[rem])
    return "".join(reversed(chars))


def build(raw: bytes) -> str:
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if blob != UPSTREAM_BLOB:
        raise ValueError(f"Unpinned input: git blob sha={blob}; expected {UPSTREAM_BLOB}")
    groups: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for line in raw.decode("utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        prev, word, number = parts
        if not VALID_WORD.fullmatch(prev) or not VALID_WORD.fullmatch(word):
            continue
        try:
            frequency = int(number)
        except ValueError:
            continue
        if frequency >= 50:
            groups[prev][word] += frequency
    output = [HEADER]
    for previous in sorted(groups):
        best = sorted(groups[previous].items(), key=lambda x: (-x[1], x[0]))[:8]
        if best:
            output.append(previous + "\t" + " ".join(
                f"{word}:{base36(count)}" for word, count in best) + "\n")
    return "".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(build(args.source.read_bytes()), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
