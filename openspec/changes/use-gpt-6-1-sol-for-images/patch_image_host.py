"""Apply the Images host-model change to the verified deployed 1.22.0 module."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

DEPLOYED_API_SHA256 = "3ff71a3c6377eba45ab42c564f95dc54e4b66feb80ac2ec358bc020760059598"
OLD_HOST = '_IMAGES_HOST_MODEL = "gpt-5.5"'
NEW_HOST = '_IMAGES_HOST_MODEL = "gpt-6.1-sol"'
OLD_COMMENT = """# responses) and is fixed (issue #1340 / PRINCIPLES.md P2): it tracks the
# registry bootstrap catalog's stable ``gpt-5.5`` slug and changes only in
# lockstep with catalog maintenance.
"""
NEW_COMMENT = """# responses). Use the current GPT 6.1 Sol catalog entry for account routing;
# native Images requests retain their requested public image model.
"""


def patch_api(path: Path) -> None:
    original = path.read_bytes()
    if hashlib.sha256(original).hexdigest() != DEPLOYED_API_SHA256:
        raise ValueError("Deployed API checksum differs; review the source before applying this patch.")
    source = original.decode("utf-8")
    if source.count(OLD_HOST) != 1 or source.count(OLD_COMMENT) != 1:
        raise ValueError("Expected exactly one Images host constant and comment.")
    updated = source.replace(OLD_HOST, NEW_HOST).replace(OLD_COMMENT, NEW_COMMENT)
    compile(updated, str(path), "exec")
    path.write_bytes(updated.encode("utf-8"))


if __name__ == "__main__":
    patch_api(Path(sys.argv[1]))
