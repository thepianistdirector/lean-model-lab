"""Reviewed model profiles: exact lawful GGUF shards, never arbitrary remote code."""
from __future__ import annotations
import copy
import re
from pathlib import Path
from .contracts import ContractError, digest, file_digest
from .llama_adapter import MODEL_COMMIT,MODEL_FILENAME,MODEL_SHA256,render_prompt

LARGE_PROFILE = {'profile_id': 'qwen2.5-14b-instruct-fp16-v1',
 'repository': 'Qwen/Qwen2.5-14B-Instruct-GGUF',
 'revision': 'b466e1f8c07172155743e8e1307507d8a4f91fbd',
 'precision': 'FP16',
 'license': 'Apache-2.0',
 'license_sha256': '832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e',
 'architecture': 'qwen2',
 'entrypoint': 'qwen2.5-14b-instruct-fp16-00001-of-00008.gguf',
 'files': [{'filename': 'qwen2.5-14b-instruct-fp16-00001-of-00008.gguf',
            'sha256': '18ccd380458642716373134dd9aeb194bf11b97085c5ce78aaec768f0f2a51aa',
            'bytes': 3891239200},
           {'filename': 'qwen2.5-14b-instruct-fp16-00002-of-00008.gguf',
            'sha256': 'd55f0a9808ebe5fde158e904884dd3f227e10d36df3598c9582f1bd8a84d0523',
            'bytes': 3995566912},
           {'filename': 'qwen2.5-14b-instruct-fp16-00003-of-00008.gguf',
            'sha256': 'db6e3e4466ece09a65577a1611ff569f751d2677dd4ae4b21c2156e6db8e3513',
            'bytes': 3995566976},
           {'filename': 'qwen2.5-14b-instruct-fp16-00004-of-00008.gguf',
            'sha256': 'bf402e7f26ed075863a2cf1c203f6f81a88224a8dc27f3a1e12c07f4a15716ff',
            'bytes': 3995608064},
           {'filename': 'qwen2.5-14b-instruct-fp16-00005-of-00008.gguf',
            'sha256': 'f17a7615d7518b93072e6cde7b382e47dc142a81e59a4595d4b00104dce78f8a',
            'bytes': 3979867360},
           {'filename': 'qwen2.5-14b-instruct-fp16-00006-of-00008.gguf',
            'sha256': 'dbbaf1f47f920ad0aab9e1e17cd3d40e5f7b0815e584e7992766b5f3180f776f',
            'bytes': 3995566976},
           {'filename': 'qwen2.5-14b-instruct-fp16-00007-of-00008.gguf',
            'sha256': '62bd5a129ed80ffdab24158e8db4ac54f72f8fbef0283c2cc3eb05a3be6f8a08',
            'bytes': 3995546432},
           {'filename': 'qwen2.5-14b-instruct-fp16-00008-of-00008.gguf',
            'sha256': '4a5e06a3d286001c3cfc95aa2fe991db58062f8775bfaeca7a66e43d980b51b6',
            'bytes': 1698754944}]}

LEGACY_PROFILE = {
    'profile_id':'qwen2.5-0.5b-instruct-fp16-v1',
    'repository':'Qwen/Qwen2.5-0.5B-Instruct-GGUF','revision':MODEL_COMMIT,
    'precision':'FP16','license':'Apache-2.0','architecture':'qwen2',
    'entrypoint':MODEL_FILENAME,
    'files':[{'filename':MODEL_FILENAME,'sha256':MODEL_SHA256,'bytes':1266425774}],
}

# Keep the old declaration byte-for-byte for historical recipe validation.
# Its size mistakenly used acquisition-phase directory growth (78 extra bytes).
# The official pinned repository tree and retained GGUF inventory both report
# 1,266,425,696 bytes for the model itself; SHA-256 and weights are unchanged.
SMALL_PROFILE = copy.deepcopy(LEGACY_PROFILE)
SMALL_PROFILE['profile_id']='qwen2.5-0.5b-instruct-fp16-v2'
SMALL_PROFILE['files'][0]['bytes']=1266425696

def get_model_profile(profile_id: str) -> dict:
    for profile in (LEGACY_PROFILE,SMALL_PROFILE,LARGE_PROFILE):
        if profile_id==profile['profile_id']:
            value=copy.deepcopy(profile)
            value['template_sha256']=digest(render_prompt('{PROMPT}'))
            return value
    raise ContractError('unknown or unreviewed model profile')


def profile_sha256(profile_id: str) -> str:
    return digest(get_model_profile(profile_id))


def model_files(entrypoint: Path, profile_id: str) -> list[Path]:
    profile=get_model_profile(profile_id)
    if entrypoint.name!=profile['entrypoint']:
        raise ContractError('model entrypoint differs from reviewed shard filename')
    if entrypoint.is_symlink() or not entrypoint.is_file():
        raise ContractError('model entrypoint must be a regular non-symlink file')
    paths=[]
    for artifact in profile['files']:
        p=entrypoint.parent/artifact['filename']
        if p.is_symlink() or not p.is_file():
            raise ContractError('reviewed model shard is missing or symlinked: '+artifact['filename'])
        if p.stat().st_size!=artifact['bytes']:
            raise ContractError('model shard size differs: '+artifact['filename'])
        paths.append(p)
    return paths


def verify_model_files(entrypoint: Path, profile_id: str, *, check=None) -> dict:
    if check is not None: check()
    profile=get_model_profile(profile_id)
    paths=model_files(entrypoint,profile_id)
    for path,artifact in zip(paths,profile['files']):
        observed=file_digest(path,check=check) if check is not None else file_digest(path)
        if observed!=artifact['sha256']:
            raise ContractError('model shard SHA-256 differs: '+artifact['filename'])
    return {'profile_id':profile_id,'profile_sha256':digest(profile),
            'files':copy.deepcopy(profile['files']),
            'total_bytes':sum(a['bytes'] for a in profile['files'])}
