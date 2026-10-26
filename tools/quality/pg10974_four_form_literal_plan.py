"""Same-value fixture constants for exactly four existing form tests; no target execution."""
import difflib
import json
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed

OUT = data.BASE/'PG10974-four-form-literal-plan-v1'
NAMES = {"question":"QUESTION_FIELD","operation_token":"OPERATION_TOKEN_FIELD","CANCEL":"CANCEL_OPERATION","operation":"OPERATION_FIELD","confirm":"CONFIRM_FIELD","DELETE":"DELETE_OPERATION","username":"USERNAME_FIELD","user1":"SYNTHETIC_USERNAME","password":"PASSWORD_FIELD","password_confirmation":"PASSWORD_CONFIRMATION_FIELD","role":"ROLE_FIELD","USER":"USER_ROLE_TEXT","enabled":"ENABLED_FIELD","STATUS":"STATUS_OPERATION","ROLE":"ROLE_OPERATION","PASSWORD":"PASSWORD_OPERATION","UNLOCK":"UNLOCK_OPERATION","expected_version":"EXPECTED_VERSION_FIELD","true":"TRUE_TEXT","target":"SYNTHETIC_TARGET_USERNAME"}
FILES = ['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/form/'+n+'Test.java' for n in ('UserCreateForm','UserMutationForm','TargetOperationForm','QuestionSubmitForm')]


def inputs():
    normal = data.read_checked(data.BASE/'PG10950-form-literal-six-compile-v1/manifest.json',
        '4cd53877ce16c93b44af747c29afdace410d2dc1ce7fec7eb5ebd48a67093baf')
    assert normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    records = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows = [r for r in records if r['path'] in FILES and r['rule'] == 'AvoidDuplicateLiterals']
    assert len(rows) == 27
    table = {}
    for row in rows:
        path = row['path']
        before = (snapshot/path).read_text()
        assert data.sha(before.encode()) == row['inputSha256'] == normal['begin']['inputHashes'][path]
        match = re.fullmatch(r'The String literal "(.*)" appears ([0-9]+) times in this file; the first occurrence is on line [0-9]+',row['message'])
        assert match is not None and match[1] in NAMES
        literal = json.dumps(match[1],ensure_ascii=False)
        found = [m for m in LEX.finditer(before) if m.group() == literal]
        assert len(found) == int(match[2]) and before[:found[0].start()].count('\n')+1 == row['line']
        name = NAMES[match[1]]
        assert not any(m.group() == name for m in LEX.finditer(before))
        table.setdefault(path,[]).append(dict(id=row['id'],name=name,literal=literal,references=len(found)))
    assert set(table) == set(FILES)
    return normal,snapshot,table


def emit():
    _,snapshot,table = inputs()
    patch = '*** Begin Patch\n'
    for path,rows in table.items():
        before = (snapshot/path).read_text()
        assert (data.ROOT/path).read_text() == before
        after = transformed(before,Path(path).stem,rows)
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'
        patch += '\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal,snapshot,table = inputs()
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes = []
    for path,rows in table.items():
        before,after = (snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert canonical(after) == canonical(transformed(before,Path(path).stem,rows))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=changes,constantsAdded=27,referencesReplaced=sum(r['references'] for rows in table.values() for r in rows),
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
