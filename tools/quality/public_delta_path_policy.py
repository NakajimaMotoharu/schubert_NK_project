"""Pure public committed-delta path/schema policy. No filesystem or authorization operations."""
import hashlib
import json
import re
from pathlib import PurePosixPath

PROTECTED = frozenset({
    'tools/quality/architecture/SnapshotKeyCloseWitness.java',
    'tools/quality/pg9892_snapshot_key_close_witness.py',
})
PUBLIC_NAMESPACE_METADATA = ('evidence/01_PT/018_NK-OPS-001/evidence/'
    'PG37538-range-namespace5-source-v1/private-noarg-source-candidates.json')
PREFIXES = ('src/', 'documents/', 'evidence/01_PT/', 'tools/quality/',
            'program/characterization/src/main/java/',
            'program/characterization/tests/java/')
SOURCE = re.compile(r'src/schubert-nk-(protocol|storage|bootstrap|api|web|batch)/src/main/java/[A-Za-z0-9_/$]+\.java\Z')
HEX = re.compile(r'[0-9a-f]{64}\Z')
STATUSES = frozenset({
    'INTENTIONAL_FACTORY_CANDIDATE_REQUIRES_SPEC_AND_RAW',
    'SOURCE_ONLY_HOLD_NO_INSTANTIATION_OR_CLASSFILE_ACTION',
    'PRIVATE_NAMESPACE_CANDIDATE_NOT_QUALIFIED',
    'CURRENT_RANGE_GROUP_GUARD_AND_NEW1_PENDING',
})
KNOWN_PROOFS = frozenset({
    'PG37348 current raw5Code100; separate parser5 source proof',
    'PG37286 current raw53Code100 target6; no replay',
})


def require(condition):
    if not condition:
        raise ValueError('public delta policy rejected input')


def validate_path(name):
    require(isinstance(name, str))
    # Deny before any possible exception or content access.
    require(name not in PROTECTED)
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in name
            and str(p) == name and name.startswith(PREFIXES))
    if name == PUBLIC_NAMESPACE_METADATA:
        return 'PUBLIC_NAMESPACE_METADATA_REQUIRES_PIN_AND_SCHEMA'
    require('/private' not in name.lower() and not name.endswith('.private.log')
            and 'raw' not in p.parts and not name.endswith(('.raw.json', '.raw.log')))
    return 'ORDINARY_PUBLIC_TRACKED_BLOB'


def validate_metadata(raw, expected_sha256):
    require(isinstance(raw, bytes) and len(raw) <= 1_048_576)
    require(isinstance(expected_sha256, str) and HEX.fullmatch(expected_sha256)
            and hashlib.sha256(raw).hexdigest() == expected_sha256)
    data = json.loads(raw)
    require(type(data) is dict and set(data) == {'rows', 'excludedHeldSourceNotRead', 'wholeScopeAccepted'}
            and data['wholeScopeAccepted'] is False)
    rows = data['rows']; skipped = data['excludedHeldSourceNotRead']
    require(type(rows) is list and len(rows) == 63 and type(skipped) is list
            and all(type(n) is str and SOURCE.fullmatch(n) for n in skipped))
    seen = set()
    fields = {'path', 'sha256', 'line', 'emptyBody', 'sameClassNewFactoryCandidate',
              'status', 'knownLimitedProof', 'actualTestOrInstantiation', 'formalAccepted'}
    for row in rows:
        require(type(row) is dict and set(row) == fields)
        name = row['path']
        require(type(name) is str and SOURCE.fullmatch(name) and name not in seen)
        seen.add(name)
        require(type(row['sha256']) is str and HEX.fullmatch(row['sha256'])
                and type(row['line']) is int and row['line'] > 0)
        require(type(row['emptyBody']) is bool and type(row['sameClassNewFactoryCandidate']) is bool
                and row['actualTestOrInstantiation'] is False and row['formalAccepted'] is False)
        require(row['status'] in STATUSES and (row['knownLimitedProof'] is None
                or row['knownLimitedProof'] in KNOWN_PROOFS))
    return 'PINNED_PUBLIC_SOURCE_CANDIDATES_ONLY_NOT_RAW_OR_RUNTIME_PROOF'
