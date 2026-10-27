"""Pure metadata advisory, never an execution/safety qualification or HOLD release."""
import hashlib
import re
from public_java_digest_provenance import LEX

JAVA = re.compile(r'src/schubert-nk-(?:api|batch|bootstrap|protocol|storage|web)/src/(?:main|test)/java/dev/codex/schubert/nk/(?:[A-Za-z_$][\w$]*/)*[A-Za-z_$][\w$]*\.java\Z', re.ASCII)
HEX = re.compile(r'[0-9a-f]{64}\Z')
LIMITATIONS = ['RAW_LEXER_NOT_JAVA_UNICODE_PREPROCESSOR', 'SAME_PACKAGE_AND_INHERITED_REFERENCES_NOT_CLOSED', 'REFLECTION_TRANSITIVE_CALL_AND_INITIALIZATION_NOT_PROVEN', 'PARENT_MUST_REVIEW_WHOLE_FIXTURE_OPERATIONS_AND_ORACLE']


def java_path(path):
    if not isinstance(path, str) or JAVA.fullmatch(path) is None:
        raise ValueError('explicit canonical NK Java source path required')
    return path


def direct_imports(text):
    tokens = [m.group() for m in LEX.finditer(text)
              if not m.group().startswith(('//', '/*', '"', "'"))]
    found = []
    for pos, token in enumerate(tokens):
        if token != 'import':
            continue
        index = pos + 1
        static = index < len(tokens) and tokens[index] == 'static'
        index += int(static)
        end = index
        while end < len(tokens) and tokens[end] != ';':
            end += 1
        if end == len(tokens):
            raise ValueError('terminated explicit import required')
        parts = tokens[index:end]
        name = ''.join(parts)
        if name.startswith('dev.codex.schubert.nk.'):
            if not re.fullmatch(r'[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*(?:\.\*)?', name, re.ASCII):
                raise ValueError('unambiguous raw import tokens required')
            found.append(dict(name=name, static=static))
    return found


def audit(texts, reviewed_main, changed_paths, frozen_hashes, registry_rows,
          known_wbs, expected_owners=None):
    """No filesystem/process access. The caller supplies only independently allowed data."""
    if not texts or len(reviewed_main) != len(set(reviewed_main)) or len(changed_paths) != len(set(changed_paths)):
        raise ValueError('nonempty texts and unique scope required')
    for path in [*texts, *reviewed_main, *changed_paths]:
        java_path(path)
    if not set(reviewed_main) <= set(texts) or not set(changed_paths) <= set(texts):
        raise ValueError('all reviewed and changed source texts required')
    if any('/src/main/' not in p for p in reviewed_main):
        raise ValueError('reviewed Main list cannot contain Test')
    for path, text in texts.items():
        digest = frozen_hashes.get(path)
        if not isinstance(text, str) or not isinstance(digest, str) or HEX.fullmatch(digest) is None:
            raise ValueError('typed source and frozen sha256 required')
        if hashlib.sha256(text.encode()).hexdigest() != digest:
            raise ValueError('source bytes differ from frozen input')
    # Metadata index only; never read any additional source from these paths.
    binary = {}
    for path in frozen_hashes:
        if isinstance(path, str) and JAVA.fullmatch(path) and '/src/main/' in path:
            name = path.split('/java/', 1)[1][:-5].replace('/', '.')
            binary.setdefault(name, []).append(path)
    rows = {}
    for row in registry_rows:
        path = row['path']
        if path in rows:
            raise ValueError('duplicate original registry path')
        rows[path] = row
    issues, imports, owners = [], {}, []
    expectations = {} if expected_owners is None else expected_owners
    if not set(expectations) <= set(changed_paths):
        raise ValueError('owner expectation outside changed scope')
    for path, text in sorted(texts.items()):
        imports[path] = []
        if re.search(r'\\u+[0-9a-fA-F]{4}', text):
            issues.append(dict(kind='JAVA_UNICODE_PREPROCESSING_UNREVIEWED', path=path))
        for item in direct_imports(text):
            name = item['name']
            candidate = name
            if name.endswith('.*'):
                issues.append(dict(kind='WILDCARD_UNRESOLVED', path=path, imported=name))
                continue
            while candidate not in binary and '.' in candidate:
                candidate = candidate.rpartition('.')[0]
            matches = binary.get(candidate, [])
            if len(matches) != 1:
                issues.append(dict(kind='IMPORT_UNRESOLVED_OR_AMBIGUOUS', path=path, imported=name))
                continue
            resolved = matches[0]
            imports[path].append(dict(**item, outerSourceCandidate=resolved))
            if resolved not in reviewed_main:
                issues.append(dict(kind='DIRECT_IMPORT_NOT_REVIEWED', path=path, imported=name, target=resolved))
    for path in sorted(changed_paths):
        row = rows.get(path)
        if row is None:
            issues.append(dict(kind='ORIGINAL_REGISTRY_ROW_MISSING', path=path))
            continue
        if row.get('sha256') != frozen_hashes[path]:
            issues.append(dict(kind='REGISTRY_SOURCE_HASH_MISMATCH', path=path))
        owner, cost = row.get('canonicalOwner'), row.get('canonicalCostOwner')
        if owner not in known_wbs or cost not in known_wbs:
            issues.append(dict(kind='CANONICAL_OWNER_UNKNOWN', path=path))
        owners.append(dict(path=path, canonicalOwner=owner, canonicalCostOwner=cost))
        if path in expectations and expectations[path] != (owner, cost):
            issues.append(dict(kind='EXPECTED_OWNER_DIFFERS_FROM_ORIGINAL', path=path))
    return dict(metadataIssues=issues, metadataConsistent=not issues,
                directImports=imports, originalOwners=owners,
                executionQualified=False, holdReleased=False,
                limitations=list(LIMITATIONS), productTestsExecuted=0,
                newAccepted=0, coverage=None)
