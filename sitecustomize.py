"""CI-only repair for a legacy binary corruption in eventbild1.

A previous image replacement damaged the otherwise valid JPEG stream stored as
``images/eventbild1.png``. GitHub Pages builds execute Python from the repository
root, so this module can repair the ephemeral Actions checkout before Pillow
reads the source. The repository image itself is not rewritten by this helper.
"""

from __future__ import annotations

import os
from pathlib import Path


if os.environ.get("GITHUB_PAGES", "").lower() == "true":
    source = Path(__file__).resolve().parent / "images" / "eventbild1.png"
    print("Reitanlage CI image repair hook loaded.")

    if source.exists():
        data = source.read_bytes()
        # Decoded form of the connector truncation sentinel observed in the
        # damaged JPEG stream. A 14-byte prefix also covers suffix variants.
        prefix = bytes.fromhex("b6bba771ab5e75fa2b762b2995ac")
        pos = data.find(prefix)
        print(f"eventbild1 bytes={len(data)} corruption_marker_offset={pos}")
        if pos >= 0:
            # The observed sentinel carried one suffix byte (display2). Remove
            # the 15-byte injection while preserving all authentic JPEG bytes.
            repaired = data[:pos] + data[pos + 15 :]
            source.write_bytes(repaired)
            print(f"Repaired eventbild1 in CI checkout; bytes={len(repaired)}")
