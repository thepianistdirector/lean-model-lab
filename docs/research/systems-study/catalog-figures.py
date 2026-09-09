#!/usr/bin/env python3
"""Catalog reviewed standalone binary figure assets for the root distribution builder."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--review-record', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--builder-output', type=Path,
                    help='Optional source-relative path-to-SHA mapping for the distribution builder')
args = parser.parse_args()
base = Path(__file__).resolve().parent
review = json.loads(args.review_record.read_text())
assert review['status'] == 'VISUAL_REVIEW_COMPLETE'
assets = []
for stem in review['reviewed_figure_stems']:
    assert '/' not in stem and '..' not in stem
    for extension in ('png', 'pdf'):
        path = base/'figures'/f'{stem}.{extension}'
        assets.append({'source_relative_path':str(Path('docs/research/systems-study')/path.relative_to(base)),
                       'relative_path':str(path.relative_to(base)),
                       'bytes':path.stat().st_size, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                       'media_type':'image/png' if extension=='png' else 'application/pdf'})
record = {'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope':'Explicit binary PNG/PDF asset manifest after visual figure review; source SVG variants retained separately.',
          'plot_source_sha256':hashlib.sha256((base/'plot.py').read_bytes()).hexdigest(),
          'analysis_source_sha256':hashlib.sha256((base/'analyze.py').read_bytes()).hexdigest(),
          'analysis_summary_sha256':hashlib.sha256((base/'tables/summary.json').read_bytes()).hexdigest(),
          'review_record':args.review_record.name,
          'review_record_sha256':hashlib.sha256(args.review_record.read_bytes()).hexdigest(),
          'assets':assets}
args.output.write_text(json.dumps(record,indent=2)+'\n')
assert {row['relative_path'] for row in assets} == {
    str(path.relative_to(base)) for path in (base/'figures').iterdir()
    if path.suffix in {'.png','.pdf'}}, 'Every binary figure must have a recorded visual review'
if args.builder_output:
    args.builder_output.write_text(json.dumps({row['source_relative_path']:row['sha256'] for row in assets},indent=2)+'\n')
print(json.dumps({'assets':len(assets),'output':str(args.output)},indent=2))
