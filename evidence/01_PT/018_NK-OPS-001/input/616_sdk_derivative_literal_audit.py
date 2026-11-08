"""Verify non-count string constants were preserved in scoped SDK tools; parse only."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

B = Path('evidence/01_PT/018_NK-OPS-001')
I = B / 'input'
O = B / 'evidence/PG24012-sdk-derivative-literal-audit-v1'


def strings(text, added_source=False):
    tree = ast.parse(text)
    if added_source:
        removed = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for keyword in list(node.keywords):
                    if keyword.arg == 'source':
                        assert ast.dump(keyword.value) == ast.dump(ast.parse("cfg['source']", mode='eval').body)
                        node.keywords.remove(keyword)
                        removed += 1
        assert removed == 1
    return [v.value for v in ast.walk(tree) if isinstance(v, ast.Constant) and type(v.value) is str]


def verify(old, new, allowed, added_source=False):
    left, right = strings(old), strings(new, added_source)
    assert len(left) == len(right)
    changes = []
    for a, b in zip(left, right):
        if a != b:
            assert allowed.get(a) == b
            changes.append((a, b))
    assert set(changes) == set(allowed.items())
    return len(changes)


def main():
    assert not O.exists()
    producer_allowed = {
        'Nine exact existing SDK JARs are opaque public code artifact data; never load/execute.':
        'One exact existing SDK JAR are opaque public code artifact data; never load/execute.',
        'input/516_g07_sdk_alias_scope.json': 'input/611_g07_slf4j_two_scope.json',
        'evidence/PG23742-g07-sdk-alias-provenance-v1': 'evidence/PG24002-g07-slf4j-two-provenance-v1',
    }
    post_allowed = {
        'evidence/PG23742-g07-sdk-alias-provenance-v1': 'evidence/PG24002-g07-slf4j-two-provenance-v1',
        'evidence/PG23744-g07-sdk-alias-independent-v1': 'evidence/PG24004-g07-slf4j-two-independent-v1',
        '5ea3a94a74689182c86b2cd703db172f0ef26cd3105d500770b608bf57eda93a':
        '89d3ae0f1dad8900922f98173544d03aeb9d649436f2f31c91c3735f5faaf186',
    }
    before = I / '518_g07_sdk_alias_post.py'
    after = I / '614_g07_slf4j_two_independent.py'
    producer_changes = verify((I / '517_g07_sdk_alias_provenance.py').read_text(),
                              (I / '613_g07_slf4j_two_provenance.py').read_text(), producer_allowed, added_source=True)
    post_changes = verify(before.read_text(), after.read_text(), post_allowed)
    bad = B / 'evidence/PG24010-slf4j-post-draft-before-v1/614_g07_slf4j_two_independent.py'
    try:
        verify(before.read_text(), bad.read_text(), post_allowed)
    except AssertionError:
        bad_rejected = True
    else:
        raise AssertionError('actual pre-fix regex change was not rejected')
    O.mkdir()
    paths = [before, after, I / '517_g07_sdk_alias_provenance.py', I / '613_g07_slf4j_two_provenance.py', bad]
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(),
                  producerStringChanges=producer_changes, postStringChanges=post_changes,
                  originalRegexAndOtherStringsPreserved=True, actualBeforeFixRejected=bad_rejected,
                  productTestsExecuted=0, newAcceptance=0, formalUpdated=False, effortRate=None,
                  bugs=['BUG-2516'], ykts=['YKT-2254'],
                  inputHashes={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  verifier={'path': str(Path(__file__)), 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    (O / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['actualExit', 'producerStringChanges', 'postStringChanges',
                                          'originalRegexAndOtherStringsPreserved', 'actualBeforeFixRejected']}))


if __name__ == '__main__':
    main()
