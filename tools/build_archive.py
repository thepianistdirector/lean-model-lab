#!/usr/bin/env python3
"""Build a deterministic standard-library zipapp; does not publish or bundle weights."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from lean_model_lab import __version__
from lean_model_lab.artifacts import write_new
from lean_model_lab.llama_adapter import BACKEND_PATCH_FILENAME


def build(output: Path) -> dict:
    files = {str(p.relative_to(ROOT/'src')):p.read_bytes()
             for p in sorted((ROOT/'src'/'lean_model_lab').glob('*.py'))}
    files['__main__.py'] = b'from lean_model_lab.cli import main\nraise SystemExit(main())\n'
    files['LICENSE'] = (ROOT/'LICENSE').read_bytes()
    files['THIRD_PARTY_NOTICES.md'] = (ROOT/'THIRD_PARTY_NOTICES.md').read_bytes()
    files['patches/'+BACKEND_PATCH_FILENAME] = (ROOT/'patches'/BACKEND_PATCH_FILENAME).read_bytes()
    manifest = {'version':__version__, 'artifact_class':'LOCAL_DEVELOPMENT_CANDIDATE',
                'runtime':'Python 3.12+ standard library; admitted external backend needed for inference',
                'files':{name:hashlib.sha256(data).hexdigest() for name,data in files.items()}}
    files['BUILD-MANIFEST.json'] = (json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,contents in sorted(files.items()):
            item=zipfile.ZipInfo(name,date_time=(2026,9,7,0,0,0))
            item.compress_type=zipfile.ZIP_DEFLATED
            item.external_attr=0o644 << 16
            archive.writestr(item,contents)
    write_new(output,data.getvalue())
    return {'version':__version__, 'sha256':hashlib.sha256(data.getvalue()).hexdigest(),
            'bytes':len(data.getvalue()), 'status':'LOCAL_CANDIDATE_NOT_PUBLISHED'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(build(args.output)))
