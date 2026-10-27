"""Two same-value integer constants for exactly eight current diagnostic points; no target execution."""
import difflib
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11640-db-pool-binding-fatal-case-plan-v1'
NAME='FATAL_SUPPLIER_CASE'
DECL='private static final int '+NAME+' = 1;'

def inputs():
    normal=data.read_checked(data.BASE/'PG11614-db-pool-binding-literal-six-compile-v1/manifest.json','da1fa15da3656d99970d1bd3afe64efee9a7fe5e153d2144af2f79c69662f16f')
    assert normal['source']=='b2790ba78d8876c058dfcebf46e25805ac0bf56e' and normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    sp=data.BASE/'PG11618-db-pool-binding-literal-static-v1';st=data.read_checked(sp/'manifest.json','5a3585696589d6307496597bc5672bde35d35d71dddc2db09962b48c353bc334');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    table={}
    for path,node in actual:
        if node.get('rule')!='AvoidLiteralsInIfCondition':continue
        assert Path(path).stem in ('ApiDbPoolMetricBindingTest','WebDbPoolMetricBindingTest')
        before=(snapshot/path).read_text();assert data.sha(before.encode())==normal['begin']['inputHashes'][path]
        lines=before.splitlines(keepends=True);point=sum(map(len,lines[:int(node.get('beginline'))-1]))+int(node.get('begincolumn'))-1
        ts=list(LEX.finditer(before));index=next(i for i,m in enumerate(ts) if m.start()==point)
        assert ts[index].group()=='1' and ''.join(m.group() for m in ts[index-2:index])=='==' and ts[index+1].group()==')'
        assert not any(m.group()==NAME for m in ts)
        row=original_match(path,node,root,actual)
        table.setdefault(path,[]).append(dict(id=row['id'],point=point,attributes=dict(node.attrib),literal='1',name=NAME))
    assert len(table)==2 and sorted(len(v) for v in table.values())==[4,4]
    return normal,snapshot,table

def transformed(before,stem,points):
    after=before
    for row in sorted(points,key=lambda r:r['point'],reverse=True):
        p=row['point'];assert after[p:p+1]=='1';after=after[:p]+NAME+after[p+1:]
    header='class '+stem+' {\n';assert after.count(header)==1
    return after.replace(header,header+'  '+DECL+'\n',1)

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before
        after=transformed(before,Path(path).stem,rows);patch+='*** Update File: '+str(data.ROOT/path)+'\n'
        patch+='\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert canonical(after)==canonical(transformed(before,Path(path).stem,rows))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),name=NAME,literal='1',references=4,points=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,integerConstants=2,comparisonReferences=8,originalMethods=30,
        allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:
        assert not sys.argv[1:];main()
