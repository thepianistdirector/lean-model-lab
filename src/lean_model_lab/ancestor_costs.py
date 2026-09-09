"""Retain historical preparation scopes without double-counting current time."""
import hashlib
import json
from .contracts import ContractError, parse_json
from .session import validate_setup_records


def preparation_ancestors(records):
    found={}
    for record in records:
        try: detail=json.loads(record['details'])
        except (ValueError,TypeError):continue
        if not isinstance(detail,dict) or detail.get('operation')!='reuse-and-verification' or 'ancestor' not in detail:
            continue
        ancestor=detail['ancestor']
        if not isinstance(ancestor,dict) or type(ancestor.get('source_receipt_raw_utf8')) is not str:
            raise ContractError('historical preparation lacks its retained source receipt')
        raw=ancestor['source_receipt_raw_utf8'].encode('utf-8')
        sha=hashlib.sha256(raw).hexdigest()
        if sha!=ancestor.get('source_receipt_sha256'):
            raise ContractError('historical preparation receipt hash differs')
        source=parse_json(raw)
        if not isinstance(source,dict) or 'records' not in source:
            raise ContractError('historical preparation source has no ledger')
        prior=validate_setup_records(source['records'])
        if not prior:
            raise ContractError('historical preparation source ledger is empty')
        start=min(r['started_ns'] for r in prior);end=max(r['finished_ns'] for r in prior)
        if end>record['started_ns']:
            raise ContractError('historical preparation overlaps current reuse verification')
        attributed=sum(r['finished_ns']-r['started_ns'] for r in prior)
        found[sha]={'source_receipt_sha256':sha,'attributed_setup_ns':attributed,
            'historical_setup_span_ns':end-start,'historical_unattributed_gap_ns':end-start-attributed,
            'known_acquired_bytes':sum(r['bytes_acquired'] for r in prior if r['bytes_acquired'] is not None),
            'unknown_byte_records':sum(r['bytes_acquired'] is None for r in prior),
            'failed_phases':sum(r['status']=='FAILED' for r in prior),
            'interrupted_phases':sum(r['status']=='INTERRUPTED' for r in prior),
            'phase_count':len(prior),
            'scope':'Separate historical source preparation only. Already incurred costs are not zero; do not add overlapping ancestor scopes or infer all historical experiment costs. Current allocation totals exclude these old intervals.'}
    return [found[k] for k in sorted(found)]
