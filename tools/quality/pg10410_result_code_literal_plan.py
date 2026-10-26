"""Prepare9 exact immutable Test constants from actual PMD source-token locations."""
from pathlib import Path
import difflib
import json
import re
import sys
import g07_host_class_provenance_inputs as data
from pg10130_uid_oracle_preflight import tokens
from public_java_digest_provenance import LEX

OUT = data.BASE/'PG10410-result-code-literal-plan-v1'
NAMES = {'LogReplayServiceTest': ['FIXTURE_LOG_RESPONSE', 'FIXTURE_LAYOUT_VERSION', 'FIXTURE_SUCCESS_CODE', 'FIXTURE_REPLAY_CODE', 'FIXTURE_RESOURCE_CODE'], 'LoginReplayServiceTest': ['FIXTURE_LOGIN_RESPONSE', 'FIXTURE_LAYOUT_VERSION', 'FIXTURE_SUCCESS_CODE', 'FIXTURE_REPLAY_CODE']}



def class_marker(text,cls):
    matches = list(re.finditer(r'(?m)^(?:final )?class '+re.escape(cls)+r'(?: implements AutoCloseable)? \{$',text))
    assert len(matches) == 1
    return matches[0].group()


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
    static = data.read_checked(data.BASE/'PG10408-result-code-literal-static-v1/manifest.json',
        '6d2be81271bde4578c98e3f59be2a3c3ddc47881095a1d9a7c77889972c5d06a')
    changes = {}
    for cls,names in NAMES.items():
        path, = [p for p in static['sourceHashes'] if Path(p).stem == cls]
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
        marker = class_marker(updated,cls)
        declarations = ''.join('  private static final String '+n+' = '+v+';\n' for n,v in constants.items())
        assert updated.count(marker) == 1
        updated = updated.replace(marker,marker+'\n'+declarations,1)
        assert restored(updated,constants) == tokens(text)
        changes[path] = dict(beforeSha256=data.sha(text.encode()),plannedSha256=data.sha(updated.encode()),
            constantCount=len(constants),constants=constants,literalReferenceCount=len(spans),before=text,after=updated)
    assert sum(v['constantCount'] for v in changes.values()) == 9
    return changes


def main():
    assert not OUT.exists()
    for declaration in ('class Synthetic {','final class Synthetic {','final class Synthetic implements AutoCloseable {'):
        assert class_marker(declaration,'Synthetic') == declaration
    changes = plan()
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,baseSource='b98ab2b8a2e8868f07471a95530d1005b6121b10',
        sourceChanges={p:{k:v for k,v in r.items() if k not in ('before','after')} for p,r in changes.items()},
        exactTokenRestorationBeforeFormatting=True,constantCount=9,productTestsExecuted=0,externalActions=0,
        bug='BUG-1827',ykt='YKT-1578',newAccepted=0,formalUpdated=False))
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
