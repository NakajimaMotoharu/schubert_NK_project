"""Test-only explicit result identity expectations; no target methods/classes are executed."""
from pathlib import Path
import difflib
import json
import re
import sys
import g07_host_class_provenance_inputs as data
from pg10130_uid_oracle_preflight import tokens

OUT = data.BASE/'PG10332-result-profile-oracle-plan-v1'
PREDICATE = '(code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)'
CALL = 'code.usesSuccessProfile()'


def restore(values,count):
    pattern = tokens(PREDICATE)
    result = list(values)
    indices = [i for i in range(len(result)) if result[i:i+len(pattern)] == pattern]
    if len(indices) != count: raise ValueError('all explicit Test profile predicates required')
    for i in reversed(indices): result[i:i+len(pattern)] = tokens(CALL)
    return result


def plan():
    review = data.read_checked(data.BASE/'PG10330-wire-helper-context-v1/manifest.json',
        '3adecef2effbdf4d4940ff60e130491f08de3db773f677ec0d1acf0bdd46021d')
    changes = {}
    for path,item in review['positiveProfileSharedClassifierSources'].items():
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == item['sha256'] and text.count(CALL) == item['count']
        assert 'import dev.codex.schubert.nk.protocol.header.ResultCode;' in text
        updated = text.replace(CALL,PREDICATE)
        assert restore(tokens(updated),item['count']) == tokens(text)
        changes[path] = dict(beforeSha256=item['sha256'],plannedSha256=data.sha(updated.encode()),
            replacementCount=item['count'],before=text,after=updated)
    assert len(changes) == 5 and sum(r['replacementCount'] for r in changes.values()) == 12
    return changes


def main():
    assert not OUT.exists()
    changes = plan()
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source='8788668513552ce50862797cb700d2b7a4162ac1',
        sourceChanges={p:{k:v for k,v in r.items() if k not in ('before','after')} for p,r in changes.items()},
        replacementCount=12,exactTokenRestorationBeforeFormatting=True,
        predicate=PREDICATE,independentSpecification='UI232 sections5/7; only0000 and0200 use success fields',
        productTestsExecuted=0,externalActions=0,bug='BUG-1817',ykt='YKT-1568',newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    value = json.loads((OUT/'manifest.json').read_bytes())
    changes = plan()
    assert value['sourceChanges'] == {p:{k:v for k,v in r.items() if k not in ('before','after')} for p,r in changes.items()}
    patch = '*** Begin Patch\n'
    for path,r in changes.items():
        delta = ''.join(list(difflib.unified_diff(r['before'].splitlines(True),r['after'].splitlines(True)))[2:])
        delta = re.sub(r'^@@.*@@\s*$','@@',delta,flags=re.M)
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'+delta
    return patch+'*** End Patch\n'


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
