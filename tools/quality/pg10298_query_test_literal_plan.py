"""Prepare exact compile-time fixture constants from19 existing PMD source-token locations."""
from collections import Counter
from pathlib import Path
import difflib
import json
import re
import sys
import g07_host_class_provenance_inputs as data
from pg10130_uid_oracle_preflight import tokens
from public_java_digest_provenance import LEX

BASE = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/'
OUT = data.BASE/'PG10298-query-test-literal-plan-v1'
NAMES = {
    'QuestionQueryApplicationServiceTest': ['QSS_REQUEST','QSD_REQUEST','NTS_REQUEST','SUCCESS_CODE',
        'PROMOTE_USER_SQL','DEMOTE_USER_SQL','FORBIDDEN_CODE','NOT_FOUND_CODE','INBOX_COUNT_SQL',
        'CLOSE_METHOD','COUNT_METHOD','ROLLBACK_METHOD'],
    'QuestionQueryReplayServiceTest': ['KEY_FIXTURE_ID','QSD_REQUEST','NTD_REQUEST','SUCCESS_CODE',
        'REPLAY_CODE','LAYOUT_VERSION','QUESTION_TEXT']}


def restored(text,constants):
    result = tokens(text)
    for name,literal in constants.items():
        declaration = tokens('private static final String '+name+' = '+literal+';')
        indices = [i for i in range(len(result)) if result[i:i+len(declaration)] == declaration]
        assert len(indices) == 1
        i, = indices
        result[i:i+len(declaration)] = []
        result = [part for value in result for part in (tokens(literal) if value == name else [value])]
    return result


def plan():
    static = data.read_checked(data.BASE/'PG10281-query-wire-oracle-static-v2/manifest.json',
        '8e68da33c559ef0de554823e6db8e0a03724dffa85619616a7e5e5be8188d626')
    changes = {}
    for cls,names in NAMES.items():
        path = BASE+cls+'.java'
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == static['sourceHashes'][path]
        findings = [r for r in static['reports']['pmd']['details'] if r['class'] == cls and r['rule'] == 'AvoidDuplicateLiterals']
        assert len(findings) == len(names)
        constants = {}
        for finding,name in zip(findings,names):
            assert name not in tokens(text)
            matches = [m for m in LEX.finditer(text) if m.group().startswith('"') and
                text.count('\n',0,m.start())+1 == int(finding['beginline']) and
                m.start()-text.rfind('\n',0,m.start()) == int(finding['begincolumn'])]
            literal, = [m.group() for m in matches]
            constants[name] = literal
        reverse = {literal:name for name,literal in constants.items()}
        assert len(reverse) == len(constants)
        spans = [(m.start(),m.end(),reverse[m.group()]) for m in LEX.finditer(text) if m.group() in reverse]
        updated = text
        for low,high,value in reversed(spans): updated = updated[:low]+value+updated[high:]
        marker = 'final class '+cls+' {'
        declarations = ''.join('  private static final String '+n+' = '+v+';\n' for n,v in constants.items())
        assert updated.count(marker) == 1
        updated = updated.replace(marker,marker+'\n'+declarations,1)
        assert restored(updated,constants) == tokens(text)
        changes[path] = dict(beforeSha256=data.sha(text.encode()),plannedSha256=data.sha(updated.encode()),
            constantCount=len(constants),constants=constants,literalReferenceCount=len(spans),before=text,after=updated)
    assert sum(v['constantCount'] for v in changes.values()) == 19
    return changes


def main():
    assert not OUT.exists()
    changes = plan()
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source='21228608b9defca3eb6fac7e0485f28a56925246',
        sourceChanges={p:{k:v for k,v in r.items() if k not in ('before','after')} for p,r in changes.items()},
        exactTokenRestorationBeforeFormatting=True,constantCount=19,productTestsExecuted=0,externalActions=0,
        bug='BUG-1812',ykt='YKT-1563',newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    value = json.loads((OUT/'manifest.json').read_bytes())
    changes = plan()
    assert value['sourceChanges'] == {p:{k:v for k,v in r.items() if k not in ('before','after')} for p,r in changes.items()}
    patch = '*** Begin Patch\n'
    for p,r in changes.items():
        change = ''.join(list(difflib.unified_diff(r['before'].splitlines(True),r['after'].splitlines(True)))[2:])
        change = re.sub(r'^@@.*@@\s*$', '@@',change,flags=re.M)
        patch += '*** Update File: '+str(data.ROOT/p)+'\n'+change
    return patch+'*** End Patch\n'


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
