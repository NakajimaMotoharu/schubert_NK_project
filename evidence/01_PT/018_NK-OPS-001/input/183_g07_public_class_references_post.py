"""Independent fixed JSON key positions, declaration and multiset proof; source data only."""
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

R = Path(__file__).resolve().parents[4]
B = R/'evidence/01_PT/018_NK-OPS-001/evidence'
O = B/'PG22186-g07-two-public-class-references-independent-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_bytes())
key = lambda v: tuple(v[k] for k in ('path','ruleId','startLine','endLine','inputSha256'))


def actual_key(text, line):
    """Independent fixed two-space JSON profile + standard decoder, no target data emitted."""
    fields = list(re.finditer(r'^  "targetCounters": ',text,re.M))
    if len(fields) != 1:
        return None
    start = fields[0].end()
    value,end = json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(value,dict):
        return None
    lines = text.splitlines(keepends=True)
    raw = lines[line-1]
    prefix = sum(len(v) for v in lines[:line-1])
    token = re.fullmatch(r'    ("(?:\\.|[^"\\])*"): \{\n?',raw)
    if not token or not start <= prefix < start+end:
        return None
    name = json.loads(token[1])
    if name not in value:
        return None
    return name,prefix+token.start(1),prefix+token.end(1)


def main():
    assert not O.exists()
    # Target-key/array/nested/other-field disambiguation recurrence checks, no Product test.
    valid = '{\n  "targetCounters": {\n    "api:api/Foo": {\n      "LINE": 0\n    }\n  }\n}'
    assert actual_key(valid,3)[0] == 'api:api/Foo'
    assert actual_key(valid.replace('targetCounters','otherCounters'),3) is None
    assert actual_key('{\n  "targetCounters": [\n    "api:api/Foo"\n  ]\n}',3) is None
    assert actual_key(valid,4) is None
    nested = '{\n  "targetCounters": {\n    "outer": {\n      "api:api/Foo": {}\n    }\n  }\n}'
    assert actual_key(nested,4) is None
    assert actual_key(valid+'\n  "targetCounters": {}',3) is None
    producer = B/'PG22184-g07-two-public-class-references-v2'
    assert sha(producer/'manifest.json') == 'cc46d63442a941dfbfe229b8287776cfd5f1fd1a0a1899729f03ba5974892905'
    pm = load(producer/'manifest.json')
    assert pm['actualExit'] == 0 and sha(producer/'updates.json') == pm['updatesSha256']
    updates = load(producer/'updates.json')
    original = B/'provisional/PG9888-g07-capture-shape-v1'
    assert sha(original/'manifest.json') == '6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb'
    assert sha(original/'residual-metadata-shapes.json') == load(original/'manifest.json')['residualMetadataSha256']
    pending = Counter(key(v) for v in load(original/'residual-metadata-shapes.json'))
    prior = []
    for slot in ['PG22160-g07-three-public-test-symbols-v1','PG22170-g07-four-selector-symbols-v1']:
        p=B/slot
        assert sha(p/'updates.json') == load(p/'manifest.json')['updatesSha256']
        prior.extend(load(p/'updates.json'))
    old = Counter(key(v) for v in prior)
    new = Counter(key(v) for v in updates)
    assert len(old) == 7 and len(new) == len(updates) == 2 and not old.keys() & new.keys()
    assert all(n == 1 and pending[k] == 1 for k,n in new.items())
    rules = B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json'
    assert sha(rules) == '97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a'
    rx = re.compile(load(rules)['rules']['generic-api-key']['regex'],re.ASCII)
    for v in updates:
        path = R/v['path']
        assert sha(path) == v['inputSha256']
        text = path.read_text()
        line = v['startLine']
        assert line == v['endLine']
        name,begin,end = actual_key(text,line)
        assert [begin,end] == v['tokenCharacterSpan'] and v['jsonRole'] == 'TARGET_COUNTERS_OBJECT_KEY'
        matches = [m for m in rx.finditer(text) if text.count('\n',0,m.start(1))+1 == line == text.count('\n',0,m.end(1))+1]
        assert len(matches) == 1 and begin < matches[0].start(1) < matches[0].end(1) < end
        assert list(matches[0].span(1)) == v['captureCharacterSpan']
        module,relative = name.split(':')
        assert module == 'api' and relative.startswith('api/') and re.fullmatch(r'[A-Za-z_$][\w$]*(?:/[A-Za-z_$][\w$]*)*',relative)
        full = 'dev/codex/schubert/nk/'+relative
        doc = json.loads(text)
        assert module+':'+full+'.class' in doc['changedPhysicalClasses']
        assert set(doc['targetCounters'][name]) == {'LINE','METHOD','CLASS','BRANCH'}
        java_path = 'src/schubert-nk-api/src/main/java/'+full+'.java'
        assert java_path == v['declarationPath'] and sha(R/java_path) == v['declarationSourceSha256'] == pm['sourceHashes'][java_path]
        assert not any(x in java_path for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892','private'])
        java_lines = (R/java_path).read_text().splitlines()
        package,simple = full.replace('/','.').rsplit('.',1)
        assert 'package '+package+';' in java_lines
        declarations = [i+1 for i,s in enumerate(java_lines) if re.fullmatch(r'public final class '+re.escape(simple)+r'[^\n]*\{',s)]
        assert declarations == v['declarationLines'] and len(declarations) == 1
        assert v['fullExactCaptureClosure'] is True and v['capturesProven'] == 1
    assert sum((pending-old-new).values()) == pm['remainingUnclassified'] == 4484
    O.mkdir()
    result = dict(atJST=datetime.datetime.now().astimezone().isoformat(),actualExit=0,
                  command=[sys.executable,'-B',str(Path(__file__).relative_to(R))],
                  os=platform.platform(),python=platform.python_version(),scriptSha256=sha(Path(__file__)),
                  producerSha256=sha(producer/'manifest.json'),originalMetadataSha256=sha(original/'residual-metadata-shapes.json'),
                  previousUnclassified=4486,additionalFalsePositives=2,remainingUnclassified=4484,
                  originalMultiplicityPreserved=True,priorSevenOverlap=False,targetKeyRoleVerified=True,
                  toolPositionRecurrenceChecks=6,productTestsExecuted=0,targetsExecuted=False,
                  scannerExecuted=False,actualSecretCount=None,binaryClosed=0,binaryTotal=22,
                  newAccepted=0,valuesOrValueHashesWritten=False)
    (O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,classified=2,remaining=4484,manifestSha256=sha(O/'manifest.json'))))


if __name__ == '__main__':
    main()
