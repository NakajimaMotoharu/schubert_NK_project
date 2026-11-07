"""Two fixed JSON physical-class references, lexical positions and Java declarations only."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

R = Path(__file__).resolve().parents[4]
B = R/'evidence/01_PT/018_NK-OPS-001/evidence'
O = B/'PG22184-g07-two-public-class-references-v2'
TARGETS = {
 'PG5970-api-sql1021-v1': (166,'dfea096010f76ff0ec5fee6f89b403319252d763e26cdfdf3f442436484be7c3'),
 'PG6010-api15-1021-v1': (40,'10e2544454a0137d7ca737d85b6207d6b8aac0b033a43ceac6179595b22a3514'),
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_bytes())


def main():
    assert not O.exists()
    origin = B/'provisional/PG9888-g07-capture-shape-v1'
    assert sha(origin/'manifest.json') == '6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb'
    assert sha(origin/'residual-metadata-shapes.json') == load(origin/'manifest.json')['residualMetadataSha256']
    pending = load(origin/'residual-metadata-shapes.json')
    rule = B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json'
    assert sha(rule) == '97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a'
    regex = re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII)
    proofs = []
    hashes = {}
    for slot,(line,digest) in TARGETS.items():
        path = B/'provisional'/slot/'manifest.json'
        assert sha(path) == digest
        name = str(path.relative_to(R))
        rows = [row for row in pending if row['path'] == name and row['startLine'] == row['endLine'] == line]
        assert len(rows) == 1 and rows[0]['inputSha256'] == digest and rows[0]['ruleId'] == 'generic-api-key'
        text = path.read_text()
        value = json.loads(text)
        # BUG2420: the actual finding is a targetCounters object KEY, not an array value.
        field = re.search(r'"targetCounters"\s*:\s*\{',text)
        assert field
        opening = field.end()-1
        depth = 0
        tokens = []
        closing = None
        for lexical in re.finditer(r'"(?:\\.|[^"\\])*"|[{}]',text[opening:]):
            symbol = lexical.group()
            if symbol == '{':
                depth += 1
            elif symbol == '}':
                depth -= 1
                if depth == 0:
                    closing = opening+lexical.end()
                    break
            elif depth == 1:
                after = text[opening+lexical.end():]
                assert re.match(r'\s*:',after)
                tokens.append((opening+lexical.start(),opening+lexical.end(),json.loads(symbol)))
        assert closing is not None and json.loads(text[opening:closing]) == value['targetCounters']
        captures = [match for match in regex.finditer(text)
                    if text.count('\n',0,match.start(1))+1 == line
                    == text.count('\n',0,match.end(1))+1]
        assert len(captures) == 1
        match = captures[0]
        candidates = [token for token in tokens if token[0]+1 <= match.start(1)
                      <= match.end(1) <= token[1]-1]
        assert len(candidates) == 1
        token_start,token_end,literal = candidates[0]
        counters = value['targetCounters'][literal]
        assert set(counters) == {'LINE','METHOD','CLASS','BRANCH'}
        assert all(set(v) == {'covered','missed'} and
                   all(type(n) is int and n >= 0 for n in v.values()) for v in counters.values())
        parsed = re.fullmatch(r'(api|web|batch|bootstrap|protocol|storage):([A-Za-z_$][\w$]*(?:/[A-Za-z_$][\w$]*)*)',literal)
        assert parsed
        module,relative = parsed.groups()
        assert relative.startswith(module+'/')
        internal = 'dev/codex/schubert/nk/'+relative
        assert module+':'+internal+'.class' in value['changedPhysicalClasses']
        outer,*nested = internal.split('$')
        assert len(nested) <= 1
        source_path = 'src/schubert-nk-'+module+'/src/main/java/'+outer+'.java'
        assert not any(x in source_path for x in ('RootFailedStart','SnapshotKeyCloseWitness','pg9892','private'))
        java = (R/source_path).read_text()
        hashes[source_path] = sha(R/source_path)
        package,simple = outer.replace('/','.').rsplit('.',1)
        assert re.search(r'^package\s+'+re.escape(package)+r';',java,re.M)
        declaration = re.search(r'^public\s+final\s+class\s+'+re.escape(simple)+r'\b',java,re.M)
        assert declaration
        declaration_lines = [java.count('\n',0,declaration.start())+1]
        for child in nested:
            declared = re.search(r'^\s*(?:private\s+)?(?:static\s+)?(?:final\s+)?(?:record|class)\s+'+re.escape(child)+r'\b',java,re.M)
            assert declared
            declaration_lines.append(java.count('\n',0,declared.start())+1)
        proofs.append(dict(**{k:rows[0][k] for k in ('path','ruleId','startLine','endLine','inputSha256')},
                           disposition='FALSE_POSITIVE_PROVEN_PUBLIC_CLASS_REFERENCE',
                           proofKind='TYPED_TARGET_COUNTER_KEY_BOUND_TO_NORMAL_CLASS_AND_DECLARED_OWNER',
                           fullExactCaptureClosure=True,capturesProven=1,
                           tokenCharacterSpan=[token_start,token_end],
                           jsonRole='TARGET_COUNTERS_OBJECT_KEY',
                           captureCharacterSpan=[match.start(1),match.end(1)],
                           declarationPath=source_path,declarationSourceSha256=hashes[source_path],
                           declarationLines=declaration_lines))
    O.mkdir()
    write = lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    write(O/'updates.json',proofs)
    result = dict(atJST=datetime.datetime.now().astimezone().isoformat(),actualExit=0,
                  command=[sys.executable,'-B',str(Path(__file__).relative_to(R))],
                  os=platform.platform(),python=platform.python_version(),scriptSha256=sha(Path(__file__)),
                  historicalScanSource='fb9fce0f91de3d9fdfa634fe277592700f915e45',
                  contentCommit='05d73a7974da8df92228160b96d91e7a006768f3',
                  originalMetadataSha256=sha(origin/'residual-metadata-shapes.json'),
                  sourceHashes=hashes,updatesSha256=sha(O/'updates.json'),
                  previousUnclassified=4486,additionalFalsePositives=2,remainingUnclassified=4484,
                  actualSecretCount=None,binaryClosed=0,binaryTotal=22,
                  productTestsExecuted=0,scannerExecuted=False,targetsExecuted=False,
                  valuesOrValueHashesWritten=False,newAccepted=0,currentWholeG07Qualified=False)
    write(O/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,classified=2,remaining=4484,manifestSha256=sha(O/'manifest.json'))))


if __name__ == '__main__':
    main()
