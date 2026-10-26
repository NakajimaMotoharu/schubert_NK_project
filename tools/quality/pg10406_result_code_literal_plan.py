"""Prepare independent UI232 result literals in six existing Tests, no target loading."""
import difflib
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10406-result-code-literal-plan-v1'
SOURCE = 'b98ab2b8a2e8868f07471a95530d1005b6121b10'
OLD = 'code.wireValue()'
NEW = 'oracleResultCode(code)'
CODES = {
    'SUCCESS':'0000','VALIDATION_ERROR':'0100','AUTHENTICATION_FAILED':'0101',
    'SESSION_INVALID':'0102','FORBIDDEN':'0103','NOT_FOUND':'0104','CONFLICT':'0105',
    'LOCKED':'0106','NOT_CANCELLABLE':'0107','IDEMPOTENT_SUCCESS':'0200',
    'TEMPORARY_FAILURE':'9000','RESOURCE_LIMIT':'9001'}
METHOD = ('  /** UI232 section7 literal oracle; never call Production wireValue. */\n'
    '  private static String oracleResultCode(ResultCode code) {\n'
    '    return switch (code) {\n'+''.join('      case '+k+' -> "'+v+'";\n' for k,v in CODES.items())+
    '    };\n  }\n')


def transformed(text):
    assert 'oracleResultCode' not in text and text.endswith('\n}\n')
    result = text.replace(OLD,NEW)
    close = result.rfind('\n}')
    return result[:close]+'\n\n'+METHOD+result[close:]


def changes():
    review = data.read_checked(data.BASE/'PG10390-role-code-hash-context-v1/manifest.json',
        'e00358550a71829c81d338ed84bc8ddd0be803ee67af14866bf203629a03ba5a')
    rows = {}
    for p,row in review['horizontalSourceMatches'][OLD].items():
        text = (data.ROOT/p).read_text()
        assert data.sha(text.encode()) == row['sha256'] and text.count(OLD) == row['count']
        after = transformed(text)
        rows[p] = dict(before=text,after=after,beforeSha256=row['sha256'],
            afterUnformattedSha256=data.sha(after.encode()),replacements=row['count'])
    assert len(rows) == 6 and sum(r['replacements'] for r in rows.values()) == 15
    return rows


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    ui = 'documents/200_UI/230_インターフェース/232_固定長電文共通仕様.md'
    approved = subprocess.check_output(['git','show','origin/main:'+ui],cwd=data.ROOT)
    assert (data.ROOT/ui).read_bytes() == approved and all('| `'+v+'` |' in approved.decode() for v in CODES.values())
    rows = changes()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        approvedUi=ui,approvedUiSha256=data.sha(approved),independentTestLiterals=CODES,
        sourceChanges={p:{k:v for k,v in r.items() if k not in {'before','after'}} for p,r in rows.items()},
        replacements=15,localLiteralHelpers=6,newJavaSourcePaths=0,bug='BUG-1826',ykt='YKT-1577',
        productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    print('*** Begin Patch')
    for p,row in changes().items():
        print('*** Update File: '+str(data.ROOT/p))
        for line in list(difflib.unified_diff(row['before'].splitlines(),row['after'].splitlines(),n=3))[2:]:
            print('@@' if line.startswith('@@') else line)
    print('*** End Patch')


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['--emit-patch']: emit()
    else:
        assert not sys.argv[1:]
        main()
