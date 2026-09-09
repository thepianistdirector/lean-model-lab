#!/usr/bin/env python3
"""Package verified research exports separately, with exact source and producer bytes.

Creates a local review candidate only. Large studies have separate ZIPs and
workbenches so opening the landing page does not load every request into one DOM.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_recipe_review_bundle as verified
from build_review_bundle import SOURCE_DIRS, SOURCE_FILES, SUFFIXES, sha, write_zip
from lean_model_lab.contracts import canonical_bytes, parse_json
from lean_model_lab.workbench import build_catalog, render_workbench

ROOT = verified.ROOT
FIGURE_ROOT = 'docs/research/'
TEXT_SUFFIXES = SUFFIXES | {'.csv', '.svg'}
BINARY_SUFFIXES = {'.png', '.pdf'}


def validate_figure(name: str, data: bytes) -> None:
    """Conservative format checks, not a general hostile-document sanitizer."""
    research_figure = name.startswith(FIGURE_ROOT) and '/figures/' in name
    product_screenshot = name.startswith('docs/release/screenshots/') and name.endswith('.png')
    if not (research_figure or product_screenshot):
        raise ValueError('binary assets must be research figures or product PNG screenshots')
    if len(data) > verified.MAX_FILE_BYTES:
        raise ValueError('oversized research figure')
    if re.search(rb'/(?:home|Users|tmp)/[^\s<>]+', data):
        raise ValueError('private path in figure metadata')
    if name.endswith('.png'):
        if not data.startswith(b'\x89PNG\r\n\x1a\n') or not data.endswith(b'IEND\xaeB`\x82'):
            raise ValueError('invalid PNG figure')
    elif name.endswith('.pdf'):
        if not data.startswith(b'%PDF-') or not data.rstrip().endswith(b'%%EOF'):
            raise ValueError('invalid PDF figure')
        if re.search(rb'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|URI|GoToR)\b', data):
            raise ValueError('active or externally linked PDF refused')
    else:
        raise ValueError('unreviewed binary figure type')


def validate_svg(data: bytes) -> None:
    if b'<!ENTITY' in data or b'<!DOCTYPE' in data and b'<!DOCTYPE svg PUBLIC' not in data:
        raise ValueError('unreviewed SVG declaration')
    root = ElementTree.fromstring(data)
    if root.tag.rsplit('}', 1)[-1] != 'svg':
        raise ValueError('invalid SVG root')
    for node in root.iter():
        if node.tag.rsplit('}', 1)[-1] in {'script', 'foreignObject', 'iframe', 'image'}:
            raise ValueError('active or embedded SVG refused')
        for key, value in node.attrib.items():
            local = key.rsplit('}', 1)[-1]
            if local.lower().startswith('on') or local == 'href' and not value.startswith('#'):
                raise ValueError('active or externally linked SVG refused')


def source_snapshot(asset_manifest: Path | None) -> dict[str, bytes]:
    assets = {} if asset_manifest is None else parse_json(
        verified.read_text(asset_manifest, 'reviewed-assets.json'))
    if not isinstance(assets, dict):
        raise ValueError('asset manifest must map source-relative figure names to SHA-256')
    for name, value in assets.items():
        verified.safe_member(name)
        if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
            raise ValueError('invalid reviewed asset digest')
    files, seen = {}, set()
    paths = [ROOT / name for name in SOURCE_FILES]
    for directory in SOURCE_DIRS:
        paths.extend(sorted((ROOT / directory).rglob('*')))
    for path in paths:
        verified.checked_path(path)
        name = path.relative_to(ROOT).as_posix()
        if '__pycache__' in path.parts or path.is_dir():
            continue
        if not path.is_file():
            raise ValueError('nonregular source file')
        if name in SOURCE_FILES or path.suffix in TEXT_SUFFIXES:
            data = verified.read_text(path, name, source=True)
            if path.suffix == '.svg':
                validate_svg(data)
        elif path.suffix in BINARY_SUFFIXES:
            if name not in assets:
                raise ValueError('research binary lacks reviewed digest: ' + name)
            if path.stat().st_size > verified.MAX_FILE_BYTES:
                raise ValueError('oversized research figure')
            data = path.read_bytes()
            validate_figure(name, data)
            if sha(data) != assets[name]:
                raise ValueError('reviewed figure digest differs: ' + name)
            seen.add(name)
        else:
            if name.startswith(FIGURE_ROOT):
                raise ValueError('unsupported research file would be omitted: ' + name)
            continue
        files['lean-model-lab-source/' + name] = data
    if seen != set(assets):
        raise ValueError('asset manifest has unused entries')
    if len({name.casefold() for name in files}) != len(files):
        raise ValueError('case-colliding source files')
    return files


def landing_page(summaries: dict, research: dict | None = None, *, flattened=False,
                 entrypoint: str | None = None) -> bytes:
    rows = []
    for name, item in summaries.items():
        label = html.escape(name)
        finding = html.escape(item['finding'])
        evidence = html.escape(item['evidence_class'])
        evidence_link = (f'evidence/{name}/EXPORT-READY.json' if flattened else name + '-evidence.zip')
        evidence_label = 'Export receipt' if flattened else 'Evidence ZIP'
        rows.append(f'<tr><th scope="row"><a href="{name}.html">{label}</a></th>'
                    f'<td>{evidence}</td><td>{finding}</td><td>'
                    f'<a href="{evidence_link}">{evidence_label}</a> · '
                    f'<a href="{name}.json">Workbench JSON</a></td></tr>')
    manifest_name = 'RESEARCH-PACKAGE.json' if flattened else 'CANDIDATE-MANIFEST.json'
    source_link = 'lean-model-lab-source/README.md' if flattened else 'lean-model-lab-source.zip'
    packages = ''.join(f'<li><a href="{name}-research.zip">{html.escape(item["title"])}</a>'
                       f' — {html.escape(item["classification"])}</li>'
                       for name, item in (research or {}).items())
    packages = '<h2>Complete research packages</h2><ul>' + packages + '</ul>' if packages else ''
    manuscript = ('<p><a href="lean-model-lab-source/' + quote(entrypoint, safe='/') +
                  '">Read the primary manuscript</a></p>') if entrypoint else ''
    return ('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lean Model Lab · Research evidence</title>
<style>body{font:1rem/1.6 system-ui,sans-serif;max-width:76rem;margin:auto;padding:2rem;color:#18212d;background:#f6f8fb}a{color:#0753a5}a:focus-visible{outline:3px solid #9d4700;outline-offset:4px}h1{line-height:1.2}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;vertical-align:top;padding:.85rem;border-bottom:1px solid #cad3df}caption{text-align:left;font-weight:700;padding:1rem 0}.scroll{overflow:auto}footer{margin-top:2rem} @media(max-width:40rem){body{padding:1rem}th,td{padding:.55rem}}</style>
<main><h1>Lean Model Lab research evidence</h1>
<p>Local review candidate. Each study includes its observed quality gates, complete attempt costs,
retained failures, and exact producer identity. Open one study at a time.</p>
<p><a href="''' + source_link + '''">Source and research manuscripts</a> ·
<a href="lean-model-lab.pyz">Portable CLI</a> ·
<a href="''' + manifest_name + '''">Artifact hashes and release gates</a></p>
''' + manuscript + packages + '''
<div class="scroll" role="region" aria-label="Research studies" tabindex="0"><table>
<caption>Verified evidence packages</caption><thead><tr><th scope="col">Study</th>
<th scope="col">Evidence</th><th scope="col">Finding</th><th scope="col">Downloads</th></tr></thead><tbody>
''' + ''.join(rows) + '''</tbody></table></div>
<footer>Hash consistency does not establish producer authentication or independent execution.
This candidate has not been published or reviewed by external researchers.</footer></main></html>''').encode()


def build(output: Path, archive: Path, producers: list[Path],
          studies: list[tuple[str, Path]], asset_manifest: Path | None = None,
          research_packages: list[tuple[str, Path]] | None = None) -> dict:
    output, archive = map(verified.checked_path, (output, archive))
    producers = [verified.checked_path(path) for path in producers]
    studies = [(name, verified.checked_path(path)) for name, path in studies]
    if not studies or any(not verified.NAME.fullmatch(name) for name, _ in studies):
        raise ValueError('provide studies with safe unique names')
    if len({name.casefold() for name, _ in studies}) != len(studies):
        raise ValueError('study name collision')
    if any(name.casefold() in {'index', 'candidate-manifest'} for name, _ in studies):
        raise ValueError('study name is reserved for a distribution artifact')
    if asset_manifest is not None:
        asset_manifest = verified.checked_path(asset_manifest)
    paths = [output, archive, *producers, *(path for _, path in studies)]
    if asset_manifest is not None:
        paths.append(asset_manifest)
    research_specs = {}
    for name, path in research_packages or []:
        if (not verified.NAME.fullmatch(name) or
                name.casefold() in {key.casefold() for key in research_specs}):
            raise ValueError('research package name invalid or duplicate')
        path = verified.checked_path(path)
        paths.append(path)
        specification = parse_json(verified.read_text(path, name + '-research-specification.json'))
        required = {'title', 'classification', 'source_directory', 'studies'}
        if (not isinstance(specification, dict) or not required <= set(specification)
                or not set(specification) <= required | {'entrypoint', 'supplementary_files'}):
            raise ValueError('invalid research package specification')
        if (not isinstance(specification['title'], str) or not 1 <= len(specification['title']) <= 240 or
                specification['classification'] not in {'BENCHMARK', 'NEGATIVE_ENGINEERING_STUDY',
                    'CANDIDATE_MECHANISM_STUDY', 'REPRODUCTION', 'INCONCLUSIVE_STUDY'}):
            raise ValueError('invalid research title or classification')
        directory = specification['source_directory']
        verified.safe_member(directory)
        if not directory.startswith(FIGURE_ROOT) or not (ROOT / directory).is_dir():
            raise ValueError('research source directory missing or out of scope')
        if 'entrypoint' in specification:
            entrypoint = specification['entrypoint']
            verified.safe_member(entrypoint)
            if (not entrypoint.startswith(directory + '/') or
                    Path(entrypoint).suffix not in {'.md', '.html'} or not (ROOT / entrypoint).is_file()):
                raise ValueError('research manuscript entrypoint missing or outside its source directory')
        names = specification['studies']
        if (not isinstance(names, list) or not names or any(not isinstance(n, str) for n in names)
                or len(set(names)) != len(names) or not set(names) <= {n for n, _ in studies}):
            raise ValueError('research package references missing or duplicate studies')
        research_specs[name] = specification
        supplements = specification.get('supplementary_files', {})
        if not isinstance(supplements, dict):
            raise ValueError('supplementary files must map archive names to source-relative text files')
        for destination, relative in supplements.items():
            verified.safe_member(destination)
            verified.safe_member(relative)
            if Path(destination).suffix not in TEXT_SUFFIXES or Path(relative).suffix not in TEXT_SUFFIXES:
                raise ValueError('supplementary file must be supported text')
            input_file = verified.checked_path(ROOT / relative)
            if not input_file.is_file() or input_file.is_relative_to(output):
                raise ValueError('supplementary source missing or overlaps output')
    for index, path in enumerate(paths):
        if any(path.is_relative_to(other) or other.is_relative_to(path) for other in paths[index + 1:]):
            raise ValueError('input or output paths overlap')
    if output.exists():
        raise ValueError('output already exists; no overwrite')
    if any(output.is_relative_to(ROOT / directory) for directory in SOURCE_DIRS):
        raise ValueError('output overlaps source allowlist')
    final = verified.verify_archive(archive)
    source = source_snapshot(asset_manifest)
    prefix = 'lean-model-lab-source/src/'
    runtime = {name[len(prefix):]: data for name, data in source.items()
               if name.startswith(prefix + 'lean_model_lab/') and name.endswith('.py')}
    if runtime != final['runtime']:
        raise ValueError('source runtime differs from final CLI')
    base = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()
    source['lean-model-lab-source/BASE-REVISION.txt'] = (
        base + '\nUncommitted source snapshot; FILE-MANIFEST.json is its exact inventory.\n').encode()
    payloads = {'lean-model-lab.pyz': final['data']}
    implementations = {final['implementation_sha256']: ['lean-model-lab.pyz']}
    producer_records = []
    for path in producers:
        producer = verified.verify_archive(path)
        name = 'producer-' + producer['sha256'] + '.pyz'
        if name in payloads:
            raise ValueError('duplicate producer archive')
        payloads[name] = producer['data']
        implementations.setdefault(producer['implementation_sha256'], []).append(name)
        producer_records.append({key: producer[key] for key in
            ('sha256', 'bytes', 'version', 'implementation_sha256')} | {'artifact': name})
    # No ready manifest is written until every independently packaged study passes.
    # A failed build may retain a partial local directory; it is never a candidate.
    output.mkdir(parents=True, exist_ok=False)
    artifacts = {'lean-model-lab-source.zip': write_zip(output / 'lean-model-lab-source.zip', source)}
    summaries = {}
    for name, path in studies:
        summary, files, directories = verified.verify_export(path, implementations)
        summaries[name] = summary
        catalog = build_catalog([path / 'study'])
        catalog['studies'][0]['label'] = name
        page = render_workbench(catalog).encode()
        document = canonical_bytes(catalog) + b'\n'
        verified.check_text(name + '.html', page, workbench=True)
        verified.check_text(name + '.json', document, workbench=True)
        evidence_name = name + '-evidence.zip'
        artifacts[evidence_name] = write_zip(output / evidence_name,
            {'evidence/' + name + '/' + key: value for key, value in files.items()},
            ['evidence/' + name + '/' + entry for entry in directories])
        for suffix, data in (('.html', page), ('.json', document)):
            with (output / (name + suffix)).open('xb') as stream:
                stream.write(data)
            artifacts[name + suffix] = {'sha256': sha(data), 'bytes': len(data)}
        del files, catalog, page, document
    research_records = {}
    for name, specification in research_specs.items():
        selected = {key: summaries[key] for key in specification['studies']}
        package = dict(source)
        directories = []
        for study_name in selected:
            evidence_name = study_name + '-evidence.zip'
            with zipfile.ZipFile(output / evidence_name) as evidence:
                for entry in evidence.infolist():
                    if entry.filename == 'FILE-MANIFEST.json':
                        package['manifests/' + study_name + '-evidence.json'] = evidence.read(entry)
                    elif entry.is_dir():
                        directories.append(entry.filename)
                    else:
                        package[entry.filename] = evidence.read(entry)
            for suffix in ('.html', '.json'):
                package[study_name + suffix] = (output / (study_name + suffix)).read_bytes()
        required_producers = {'lean-model-lab.pyz'} | {
            artifact for item in selected.values() for artifact in item['producer_artifacts']}
        package.update({key: payloads[key] for key in sorted(required_producers)})
        package['index.html'] = landing_page(selected, flattened=True, entrypoint=specification.get('entrypoint'))
        supplements = {}
        for destination, relative in specification.get('supplementary_files', {}).items():
            if destination.casefold() in {'file-manifest.json', 'research-package.json'} or any(
                    destination.casefold() == existing.casefold() or
                    destination.casefold().startswith(existing.casefold() + '/') or
                    existing.casefold().startswith(destination.casefold() + '/')
                    for existing in package):
                raise ValueError('supplementary file collides with package: ' + destination)
            data = verified.read_text(ROOT / relative, destination)
            if Path(destination).suffix == '.svg':
                validate_svg(data)
            package[destination] = data
            supplements[destination] = {'sha256': sha(data), 'bytes': len(data)}
        record = {'schema_version': 1, 'status': 'LOCAL_REVIEW_CANDIDATE_NOT_PUBLISHED',
                  **specification, 'source_base_revision': base,
                  'supplementary_files': supplements,
                  'final_cli_implementation_sha256': final['implementation_sha256'], 'study_evidence': selected,
                  'producer_artifacts': {key: {'sha256': sha(payloads[key]), 'bytes': len(payloads[key])}
                                         for key in sorted(required_producers)},
                  'layout': 'Complete source in lean-model-lab-source; selected exports in evidence; exact producers and workbenches at root.',
                  'integrity_limit': 'Local consistency only; not independent execution, publisher authentication, peer review or public release.'}
        package['RESEARCH-PACKAGE.json'] = canonical_bytes(record) + b'\n'
        research_name = name + '-research.zip'
        artifacts[research_name] = write_zip(output / research_name, package, directories)
        research_records[name] = record | {'artifact': research_name}
        del package
    payloads['index.html'] = landing_page(summaries, research_specs)
    for name, data in payloads.items():
        with (output / name).open('xb') as stream:
            stream.write(data)
        artifacts[name] = {'sha256': sha(data), 'bytes': len(data)}
    for name, metadata in artifacts.items():
        if sha((output / name).read_bytes()) != metadata['sha256']:
            raise ValueError('artifact readback differs')
    result = {'schema_version': 1, 'status': 'LOCAL_REVIEW_CANDIDATE_NOT_PUBLISHED',
        'version': final['version'], 'source_base_revision': base,
        'source_snapshot': 'Exact allowlisted uncommitted bytes in source ZIP FILE-MANIFEST.json',
        'artifacts': artifacts, 'final_cli_implementation_sha256': final['implementation_sha256'],
        'source_runtime_matches_final_cli': True, 'producer_archives': producer_records,
        'studies': summaries, 'workbench_matches_included_exports': True,
        'research_packages': research_records,
        'workbench_layout': 'One generated workbench and evidence ZIP per study; index contains only summaries.',
        'privacy_scope': 'UTF-8 source/evidence path and credential checks; explicit SHA-256 reviewed PNG/PDF research figures with bounded format checks. No weights, native backend or browser binaries. Binary checks are not a general sanitizer or independent privacy attestation.',
        'integrity_limit': 'Hash consistency is not producer authentication, independent execution or proof against omitted evidence.',
        'missing_release_gates': ['explicit public release authorization and author identity',
            'supported authenticated native Tanduna publication and actual review/decision',
            'external execution and recovery from the public artifact',
            'qualified researcher observations', 'independent browser accessibility review']}
    (output / 'CANDIDATE-MANIFEST.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--producer', type=Path, action='append', default=[])
    parser.add_argument('--study', type=verified.study_argument, action='append', required=True)
    parser.add_argument('--asset-manifest', type=Path)
    parser.add_argument('--research', type=verified.study_argument, action='append', default=[],
                        help='SAFE_NAME=JSON_SPECIFICATION for a self-contained investigation ZIP')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output, args.archive, args.producer, args.study,
                               args.asset_manifest, args.research), indent=2))
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        print('v1 candidate refused: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
