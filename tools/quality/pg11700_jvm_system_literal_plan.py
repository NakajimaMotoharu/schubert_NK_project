"""Four exact first-order comparisons and14 same-value strings; source-only transformation."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11700-jvm-system-literal-plan-v1'
FILES=[f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.capitalize()}{kind}MetricsTest.java' for role in ('api','web') for kind in ('Jvm','System')]
NAMES={'"DEBUG"':'DEBUG_MODE','"STANDARD"':'STANDARD_MODE','"fixture"':'FAILURE_FIXTURE','"process.cpu.time"':'PROCESS_CPU_TIME'}
ORDER='FIRST_BINDER_ORDER'

def inputs():
    normal=data.read_checked(data.BASE/'PG11674-standard-composition-literal-six-compile-v1/manifest.json','15a6eeb057afdb021d0403af21625b84664c7df00c9da343954cfe02762a4ce1');assert normal['source']=='5a16139a752e2404cd6c26504760f4568ac413fd' and normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path];ts=list(LEX.finditer(text));rows=[]
        for r in root:
            if r['path']!=path or r['rule'] not in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition'):continue
            assert r['inputSha256']==normal['begin']['inputHashes'][path];a=r['attributes'];lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;i=next(i for i,m in enumerate(ts) if m.start()==point);literal=ts[i].group()
            if r['rule']=='AvoidDuplicateLiterals':
                count=int(re.search(r' appears ([0-9]+) times',r['message'])[1]);assert literal in NAMES and sum(m.group()==literal for m in ts)==count
                rows.append(dict(id=r['id'],kind='STRING',literal=literal,name=NAMES[literal],references=count))
            else:
                assert literal=='1' and ''.join(m.group() for m in ts[i-3:i])=='order==' and ts[i+1].group()==')'
                rows.append(dict(id=r['id'],kind='ORDER_INT',literal='1',name=ORDER,references=1,point=point))
        assert len([x for x in rows if x['kind']=='ORDER_INT'])==1 and not any(m.group() in {x['name'] for x in rows} for m in ts);table[path]=rows
    assert sum(r['kind']=='STRING' for rs in table.values() for r in rs)==14 and sum(r['references'] for rs in table.values() for r in rs if r['kind']=='STRING')==100
    return normal,snapshot,table

def transformed(text,stem,rows):
    row=next(r for r in rows if r['kind']=='ORDER_INT');i=row['point'];assert text[i:i+1]=='1';result=text[:i]+ORDER+text[i+1:];result=strings(result,stem,[r for r in rows if r['kind']=='STRING']);header='class '+stem+' {\n';assert result.count(header)==1
    return result.replace(header,header+'  private static final int '+ORDER+' = 1;\n',1)

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before;after=transformed(before,Path(path).stem,rows);patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table);changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert canonical(after)==canonical(transformed(before,Path(path).stem,rows));changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=14,stringReferences=100,orderConstants=4,comparisonReferences=4,originalMethods=56,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
