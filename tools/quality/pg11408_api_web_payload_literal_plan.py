"""Eight same-value private fixture names/72 sites; current PMD and original-ID binding."""
import difflib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11408-api-web-payload-literal-plan-v1'
FILES=[f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.capitalize()}CustomMetricPayloadTest.java' for role in ('api','web')]
NAMES={'DEBUG':'DEBUG_MODE','STANDARD':'STANDARD_MODE','not read':'UNEXPECTED_PROVIDER_MESSAGE','fixture':'FAILURE_FIXTURE_MESSAGE'}


def inputs():
    normal=data.read_checked(data.BASE/'PG11380-full-payload-guard-six-compile-v1/manifest.json',
        'f9691978776defaba64743818d99b493a80ab4f36b1cd30bae3eee542ab55be2')
    sp=data.BASE/'PG11384-full-payload-guard-static-v1/manifest.json'
    static=data.read_checked(sp,'075bc441fc602c77dfa0b6d7cb6eadcbf4c570893655850f6cb6140c47841a09')
    assert normal['source']==static['source']=='4aee5c4b73ffae5426e0cc5d15fc928e06ece7b8' and normal['actualExit']==normal['testsExecuted']==0
    raw=(sp.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    table={}
    for path,node in actual:
        if path not in FILES or node.get('rule')!='AvoidDuplicateLiterals':
            continue
        before=(snapshot/path).read_text()
        assert data.sha(before.encode())==static['sourceHashes'][path]==normal['begin']['inputHashes'][path]
        message=''.join(node.itertext()).strip()
        match=re.fullmatch(r'The String literal "(.*)" appears ([0-9]+) times in this file; the first occurrence is on line [0-9]+',message)
        assert match and match[1] in NAMES
        literal=json.dumps(match[1]);found=[m for m in LEX.finditer(before) if m.group()==literal]
        assert len(found)==int(match[2]) and before[:found[0].start()].count('\n')+1==int(node.get('beginline'))
        name=NAMES[match[1]]
        assert not any(m.group()==name for m in LEX.finditer(before))
        old=original_match(path,node,original,actual)
        table.setdefault(path,[]).append(dict(id=old['id'],name=name,literal=literal,references=len(found)))
    assert set(table)==set(FILES) and sum(len(v) for v in table.values())==8
    assert sum(r['references'] for v in table.values() for r in v)==72
    return normal,snapshot,table


def emit():
    _,snapshot,table=inputs()
    patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text()
        assert (data.ROOT/path).read_text()==before
        after=transformed(before,Path(path).stem,rows)
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'
        patch+='\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text()
        assert canonical(after)==canonical(transformed(before,Path(path).stem,rows))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,
        stringConstants=8,referencesReplaced=72,originalMethods=52,allMainAndOtherInputsPreserved=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
