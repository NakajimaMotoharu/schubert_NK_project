"""Explicit public query-oracle change delta only; held witness files are not read."""
import hashlib
import json
import subprocess
from pg9898_g07_enum_public_delta import ROOT, RULES, HELD

OUT = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10524-constructor-review-public-delta-v1'
BEFORE = '38cafd4fe'


def main():
    assert not OUT.exists()
    raw = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,'--'],cwd=ROOT)
    raw += subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT)
    assert raw.endswith(b'\0')
    names = set(raw.decode().split('\0')[:-1])-HELD
    rows, findings = [], []
    for name in sorted(names):
        assert name.startswith(('documents/','evidence/01_PT/','src/','tools/quality/pg102','tools/quality/pg103','tools/quality/pg104','tools/quality/pg105','tools/quality/architecture/RoleLiteralView','tools/quality/architecture/PublicTemplate14','tools/quality/architecture/QuestionQueryWireOracleMetadata','tools/quality/architecture/UserQueryWireOracleMetadata'))
        path = ROOT/name
        assert '/private' not in name and not path.is_symlink() and path.is_file()
        content = path.read_bytes()
        assert b'\0' not in content
        content.decode('utf-8')
        rows.append(dict(path=name,sha256=hashlib.sha256(content).hexdigest()))
        for rule,pattern in RULES.items():
            findings.extend(dict(path=name,rule=rule,line=content[:m.start()].count(b'\n')+1) for m in pattern.finditer(content))
    assert rows
    value = dict(actualExit=1 if findings else 0,before=BEFORE,files=rows,findings=findings,
        scope='EXPLICIT_QUERY_ORACLE_PUBLIC_TEXT_DELTA_THREE_FORMAT_PATTERNS_NOT_WHOLE_G07',
        heldFilesNotRead=sorted(HELD),actualSecretCount=None,wholeWorktreeCleanClaim=False,
        productTestsExecuted=0,externalActions=0,formalUpdated=False)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=value['actualExit'],files=len(rows),findings=len(findings),
        manifestSha256=hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest())))
    raise SystemExit(value['actualExit'])


if __name__ == '__main__':
    main()
