"""Prepare only independent literal USER/ADMIN expectations in existing Tests."""
import difflib
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10392-role-literal-plan-v1'
OLD = 'role.wireValue()'
NEW = 'switch (role) { case USER -> "USER"; case ADMIN -> "ADMIN"; }'


def changes():
    review = data.read_checked(data.BASE/'PG10390-role-code-hash-context-v1/manifest.json',
        'e00358550a71829c81d338ed84bc8ddd0be803ee67af14866bf203629a03ba5a')
    result = {}
    for p,row in review['horizontalSourceMatches'][OLD].items():
        before = (data.ROOT/p).read_text()
        assert data.sha(before.encode()) == row['sha256'] and before.count(OLD) == row['count']
        after = before.replace(OLD,NEW)
        result[p] = dict(before=before,after=after,beforeSha256=row['sha256'],
            afterUnformattedSha256=data.sha(after.encode()),replacements=row['count'])
    assert len(result) == 13 and sum(r['replacements'] for r in result.values()) == 18
    return result


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    rows = changes()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source='3d9f1d9fd395e8cb9456b0a540e1f29bcb87876e',invocation=invocation,
        sourceChanges={p:{k:v for k,v in r.items() if k not in {'before','after'}} for p,r in rows.items()},
        replacement=NEW,replacements=18,bug='BUG-1825',ykt='YKT-1576',productTestsExecuted=0,
        externalActions=0,newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    rows = changes()
    print('*** Begin Patch')
    for p,row in rows.items():
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
