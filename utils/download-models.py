import sys
import tempfile

import huggingface_hub

if len(sys.argv) < 3:
    sys.exit("usage: python download.py REPO_ID LOCAL_DIR [REVISION]")

with tempfile.TemporaryDirectory() as cache_dir:
    huggingface_hub.snapshot_download(
        repo_id=sys.argv[1],
        local_dir=sys.argv[2],
        revision=sys.argv[3] if len(sys.argv) > 3 else None,
        cache_dir=cache_dir,
        local_dir_use_symlinks=False,
        resume_download=True,
    )