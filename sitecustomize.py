"""CI-only repair for a legacy binary corruption in eventbild1.

A previous image replacement accidentally injected the decoded bytes of the
connector truncation marker ``truncatedfordisplay2`` into the otherwise valid
JPEG stream stored as ``images/eventbild1.png``.  GitHub Pages builds execute
Python from the repository root, so Python imports this module automatically.
We repair only that exact byte signature, only in the ephemeral Actions
checkout, before Pillow reads the image.  The public source file is otherwise
left untouched until the original clean photograph can be replaced directly.
"""

from __future__ import annotations

import os
from pathlib import Path


if os.environ.get("GITHUB_PAGES", "").lower() == "true":
    source = Path(__file__).resolve().parent / "images" / "eventbild1.png"
    injected = bytes.fromhex("b6bba771ab5e75fa2b762b2995acb6")

    if source.exists():
        data = source.read_bytes()
        if injected in data:
            repaired = data.replace(injected, b"", 1)
            source.write_bytes(repaired)
            print("Repaired legacy eventbild1 binary corruption in CI checkout.")
