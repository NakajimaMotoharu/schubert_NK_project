"""Fifteen exact same-value typed pure resource/profile/value fixture constants; no Main or independent-oracle changes."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10840_web_view_duplicate_plan import transformed

OUT=data.BASE/'PG12496-pure-resource-profile-plan-v1'
NORMAL='b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe'
FILES=['src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/ResourceScopeTest.java', 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/FactoryResourceScopeTest.java', 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfileTest.java', 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest.java']
COUNTS={'ResourceScopeTest': 8, 'FactoryResourceScopeTest': 18, 'FixedNativeCoverageProfileTest': 5, 'ObservationValueRedactionTest': 2}
NAMES={'"body"': 'BODY_EVENT', '"open"': 'OPEN_EVENT', '"close"': 'CLOSE_EVENT', '"PUBLIC_CLOSE"': 'PUBLIC_CLOSE_MARKER', '"API-"': 'API_ROLE_PREFIX', '"-root"': 'ROOT_PHASE_SUFFIX', '"public"': 'PUBLIC_FIELD'}
NUMBERS={'PMD-07117': ('int', 'CLOSE_FAILURE_MODE', '1'), 'PMD-07118': ('int', 'SUCCESSFUL_BODY_MODE', '1'), 'PMD-06943': ('char', 'SANITIZED_IO_WINNER', "'S'"), 'PMD-06944': ('int', 'ONE_SANITIZED_SUPPRESSION', '1'), 'PMD-06945': ('int', 'IO_CLOSE_MODE', '1'), 'PMD-06946': ('int', 'RUNTIME_CLOSE_MODE', '2'), 'PMD-06947': ('int', 'ERROR_CLOSE_MODE', '3')}

def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inputs():
    normal=data.read_checked(data.BASE/'PG12476-enum-catalog-six-compile-v1/manifest.json',NORMAL);assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for p in FILES:
        text=(snapshot/p).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][p]
        ts=list(LEX.finditer(text));lines=text.splitlines(keepends=True);rows=[]
        for r in original:
            if r['path']!=p or (r['rule']!='AvoidDuplicateLiterals' and r['id'] not in NUMBERS):continue
            assert r['inputSha256']==normal['begin']['inputHashes'][p]
            a=r['attributes'];start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
            if r['rule']=='AvoidDuplicateLiterals':
                literal=next(m.group() for m in ts if m.start()==start);count=int(re.search(r' appears ([0-9]+) times',r['message'])[1]);name=NAMES[literal]
                assert sum(m.group()==literal for m in ts)==count
                rows.append(dict(id=r['id'],type='String',name=name,literal=literal,references=count))
            else:
                typ,name,literal=NUMBERS[r['id']];assert r['rule']=='AvoidLiteralsInIfCondition' and text[start:start+len(literal)]==literal
                rows.append(dict(id=r['id'],type=typ,name=name,literal=literal,references=1,originalStart=start))
            assert name not in raw(text)
        assert len(rows)==dict(ResourceScopeTest=3,FactoryResourceScopeTest=9,FixedNativeCoverageProfileTest=2,ObservationValueRedactionTest=1)[Path(p).stem]
        assert len(re.findall(r'@Test\s+void ',text))==COUNTS[Path(p).stem];table[p]=rows
    assert sum(len(rs) for rs in table.values())==15 and sum(r['references'] for rs in table.values() for r in rs if r['type']=='String')==48
    return normal,snapshot,table

def changed(before,path,rows):
    after=before;numbers=[r for r in rows if r['type']!='String']
    for r in sorted(numbers,key=lambda r:r['originalStart'],reverse=True):
        start=r['originalStart'];assert after[start:start+len(r['literal'])]==r['literal'];after=after[:start]+r['name']+after[start+len(r['literal']):]
    after=transformed(after,Path(path).stem,[r for r in rows if r['type']=='String'])
    header='class '+Path(path).stem+' {\n';assert after.count(header)==1
    return after.replace(header,header+''.join('  private static final '+r['type']+' '+r['name']+' = '+r['literal']+';\n' for r in numbers),1)

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for p,rows in table.items():
        before=(snapshot/p).read_text();assert (data.ROOT/p).read_text()==before;after=changed(before,p,rows)
        patch+='*** Update File: '+str(data.ROOT/p)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes=[]
    for p,rows in table.items():
        before=(snapshot/p).read_text();after=(data.ROOT/p).read_text();assert raw(after)==raw(changed(before,p,rows))
        changes.append(dict(path=p,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],sourceChanges=changes,stringConstants=8,stringReferences=48,numericConstants=7,numericReferences=7,rawDiagnosticsCorrected=15,originalMethods=33,additionalUnchangedCompanionMethods=1,expectedExecutedMethods=34,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
