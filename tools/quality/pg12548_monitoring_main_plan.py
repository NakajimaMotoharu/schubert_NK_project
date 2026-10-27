"""Pure Main six same-value naming corrections; independent inverse, no product execution."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12548-monitoring-main-plan-v1'
BEFORE='03ffd8803faf780d872d002426c599a2a0a3814f'
PREFIX='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/'
PATHS=[PREFIX+'MetricContract.java',PREFIX+'MonitoringModePolicy.java']
LABELS={'SERVICE_LABEL':'service','ADDRESS_LABEL':'address','STATUS_LABEL':'status'}
FIELDS={'configuredDetailMetrics':'detailedMetricsEnabled','configuredRetentionDays':'retentionDays','configuredRetentionBytes':'retentionBytes'}


def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def before():
    n=data.read_checked(data.BASE/'PG12528-public-record-six-compile-v1/manifest.json','59a22edd2c2584134bb3f2d4a5bc3de042d007afee84f6aa8e0bd17e8a24c735')
    assert n['source']==BEFORE and n['actualExit']==n['testsExecuted']==0
    snapshot=Path(n['jars']['batch']['path']).parent.parent.parent.parent
    return n,{p:(snapshot/p).read_text() for p in PATHS}


def intended(old):
    result=dict(old)
    t=result[PATHS[0]]
    for name,value in LABELS.items():
        assert t.count('"'+value+'"')=={'service':4,'address':5,'status':4}[value]
        t=t.replace('"'+value+'"','MetricContract.'+name)
    declarations=''.join('  private static final String '+k+' = "'+v+'";\n' for k,v in LABELS.items())
    result[PATHS[0]]=t.replace('  public enum Kind {',declarations+'\n  public enum Kind {',1)
    t=result[PATHS[1]]
    for new,oldname in FIELDS.items():
        t=re.sub(r'(private final (?:boolean|int|long) )'+oldname+r'\b',r'\g<1>'+new,t)
        t=t.replace('this.'+oldname+' =','this.'+new+' =')
        t=t.replace('return '+oldname+';','return '+new+';')
    t=t.replace('enabled != detailedMetricsEnabled','enabled != configuredDetailMetrics')
    t=t.replace('configuration.days() != retentionDays','configuration.days() != configuredRetentionDays')
    t=t.replace('configuration.bytes() != retentionBytes','configuration.bytes() != configuredRetentionBytes')
    result[PATHS[1]]=t
    return result


def require_equivalent(old,new):
    t=new[PATHS[0]]
    for name,value in LABELS.items():
        declaration='  private static final String '+name+' = "'+value+'";\n'
        assert t.count(declaration)==1
        t=t.replace(declaration,'')
        assert t.count('MetricContract.'+name)=={'service':4,'address':5,'status':4}[value]
        t=t.replace('MetricContract.'+name,'"'+value+'"')
    assert raw(t)==raw(old[PATHS[0]])
    t=new[PATHS[1]]
    for name,oldname in FIELDS.items():t=re.sub(r'\b'+name+r'\b',oldname,t)
    assert raw(t)==raw(old[PATHS[1]])


def emit():
    _,old=before();new=intended(old)
    require_equivalent(old,new)
    patch='*** Begin Patch\n'
    for p in PATHS:
        assert (data.ROOT/p).read_text()==old[p]
        patch+='*** Update File: '+str(data.ROOT/p)+'\n'
        patch+='\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(old[p].splitlines(),new[p].splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__);assert not OUT.exists();n,old=before()
    new={p:(data.ROOT/p).read_text() for p in PATHS};require_equivalent(old,new)
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in n['begin']['inputHashes'].items() if p not in PATHS)
    vectors=[]
    for name,value in LABELS.items():
        for bad in (new[PATHS[0]].replace(' = "'+value+'";',' = "WRONG-'+value+'";',1),new[PATHS[0]].replace('MetricContract.'+name,'MetricContract.UNKNOWN_LABEL',1)):
            assert bad!=new[PATHS[0]];vectors.append({**new,PATHS[0]:bad})
    for name in FIELDS:
        bad=re.sub(r'\b'+name+r'\b','incorrectField',new[PATHS[1]],count=1)
        assert bad!=new[PATHS[1]];vectors.append({**new,PATHS[1]:bad})
    for path,oldword,newword in [(PATHS[0],'return wireName;','return "wrong";'),(PATHS[1],'enabled != configuredDetailMetrics','enabled == configuredDetailMetrics')]:
        bad=new[path].replace(oldword,newword,1);assert bad!=new[path];vectors.append({**new,path:bad})
    for bad in vectors:
        try:require_equivalent(old,bad)
        except AssertionError:pass
        else:raise AssertionError('nonvacuous inverse negative accepted')
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2351_監視Main六件同値是正_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,sourceBefore=BEFORE,invocation=invocation,sourceChanges=[dict(path=p,beforeSha256=data.sha(old[p].encode()),sha256=data.sha(new[p].encode())) for p in PATHS],metadataNegativeVectors=len(vectors),mainCorrections=6,labelReferences=13,newExecutableClasses=0,allTestsAndOtherInputsUnchanged=True,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
