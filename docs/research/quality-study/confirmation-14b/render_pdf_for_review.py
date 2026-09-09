"""Render standalone figure PDFs for local visual review; no native inference."""
from pathlib import Path
import argparse
import json
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--figure-directory', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--dependency-directory', type=Path)
args = parser.parse_args()
if args.dependency_directory:
    sys.path.insert(0, str(args.dependency_directory.resolve()))
import pypdfium2 as pdfium
if args.output.exists():
    raise ValueError('visual-review output must be new')
args.output.mkdir(parents=True)
for path in sorted(args.figure_directory.glob('*.pdf')):
    with pdfium.PdfDocument(path) as doc:
        if len(doc) != 1:
            raise ValueError('expected a standalone one-page figure PDF')
        page = doc[0]
        bitmap = page.render(scale=1.8)
        bitmap.to_pil().save(args.output / (path.stem + '.png'))
        bitmap.close()
        page.close()
(args.output / 'renderer.json').write_text(json.dumps({
    'renderer': 'pypdfium2', 'version': str(pdfium.PYPDFIUM_INFO),
    'scope': 'Local visual QA only; rendered output still requires visual inspection. No model execution.'
}, indent=2) + '\n')
