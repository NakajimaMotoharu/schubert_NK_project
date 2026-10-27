"""Eight same-value private fixture names/58 sites; current PMD and original-ID binding."""
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

OUT=data.BASE/'PG11470-api-web-gc-literal-plan-v2'
FILES=[f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.capitalize()}GcMetricRegistrationTest.java' for role in ('api','web')]
NAMES={'DEBUG':'DEBUG_MODE','STANDARD':'STANDARD_MODE','not own':'UNEXPECTED_OWNER_MESSAGE','fixture':'FAILURE_FIXTURE_MESSAGE'}


def inputs():
    normal=data.read_checked(data.BASE/'PG11444-gc-fake-guard-six-compile-v1/manifest.json',
        '0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb')
    sp=data.BASE/'PG11448-gc-fake-guard-static-v1/manifest.json'
    static=data.read_checked(sp,'4540e528ae063a80dfcdfa454da340a397e0449f006ee7692e95d19e8d86e185')
    assert normal['source']==static['source']=='495313cd8e724d5f1906fca64d9d9fd3516aae50' and normal['actualExit']==normal['testsExecuted']==0
    raw=(sp.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    index_path=data.BASE/"PG11460-current-gc-fake-guard-delta-v1/manifest.json"
    index=data.read_checked(index_path,"3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2")
    delta=data.read_checked(index_path.parent/"delta.json",index["deltaSha256"])
    assert index["source"]==normal["source"]
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
        matches=[r for r in delta["freshRows"] if r["path"]==path and r["attributes"]==dict(node.attrib)]
        assert len(matches)==1
        old=matches[0]
        assert any(r["id"]==old["id"] and r["path"]==path for r in original)
        table.setdefault(path,[]).append(dict(id=old['id'],name=name,literal=literal,references=len(found)))
    assert set(table)==set(FILES) and sum(len(v) for v in table.values())==8
    assert sum(r['references'] for v in table.values() for r in v)==58
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
    rejected=data.ROOT/"tools/quality/pg11470_api_web_gc_literal_plan.py"
    assert data.sha(rejected.read_bytes())=="b27922fb92334190253d8c9803cd2e502f637071f9e70a120dfa13b5f1f6fb0a"
    assert not (data.BASE/"PG11470-api-web-gc-literal-plan-v1").exists()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/"rejected-plan-v1.json",dict(actualExit=1,toolSha256=data.sha(rejected.read_bytes()),outNotCreated=True,reason="OLD_SNAPSHOT_ID_HELPER_READ_CURRENT_AFTER_PATCH",productTestsExecuted=0))
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,
        stringConstants=8,referencesReplaced=58,originalMethods=32,allMainAndOtherInputsPreserved=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
