"""Explicit operator admission for the exact reviewed dependency/resource envelope."""
from __future__ import annotations

from .config import LIMITS
from .contracts import ContractError, canonical_bytes, keys
from .llama_adapter import BACKEND_COMMIT, MODEL_SHA256


def proposal() -> dict:
    return {'schema_version':1,'approved':False,'backend_revision':BACKEND_COMMIT,
            'model_sha256':MODEL_SHA256,'limits':dict(LIMITS),
            'approval_reference':'PENDING: exact operator dependency/model/resource decision'}


def validate_admission(value: dict) -> dict:
    keys(value,{'schema_version','approved','backend_revision','model_sha256','limits','approval_reference'},'admission')
    expected=proposal()
    for key in ('schema_version','backend_revision','model_sha256','limits'):
        if canonical_bytes(value[key])!=canonical_bytes(expected[key]):
            raise ContractError(f'admission changed reviewed {key}')
    if value['approved'] is not True:
        raise ContractError('dependency/model/resource admission is pending; no acquisition or inference permitted')
    if type(value['approval_reference']) is not str or not value['approval_reference'].strip() or value['approval_reference'].startswith('PENDING'):
        raise ContractError('admission needs the actual operator approval reference')
    return value
