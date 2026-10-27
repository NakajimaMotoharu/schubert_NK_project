"""Independent saved measurement boundary contract; synthetic metadata only, no Product execution."""
import copy
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='442441c83f73935eb2bd33cd40a7b9884eb7dfe3'
OUT=data.BASE/'PG12321-readiness-boundary-contract-v1'
TYPES={'dev.codex.schubert.nk.api.application.question.AnswerProvider','dev.codex.schubert.nk.api.messaging.inbound.InternalEventProcessor','dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor','dev.codex.schubert.nk.storage.NonSecretConfigSource'}

def require(v):
    if v.get('source')!=SOURCE or set(v.get('resolvedTypes',[]))!=TYPES or v.get('outsideProductProbeHits')!=0 or v.get('nonPredicateMethodInstructionHits')!=0 or v.get('interfaceExecutionPermission') is not False:
        raise ValueError('exact interface resolution without executable permission; all outside/predicate isolation counts zero')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    post=data.read_checked(data.BASE/'PG12319-readiness-dependency-post-v2/manifest.json','4637b7fae4f42b67a7db0a04dd67c82513fd499b0f9287b67a43dde169604783')
    assert post['source']==SOURCE and post['actualExit']==0
    headers={}
    for role in ('api','web'):
        p=data.ROOT.parent/'pgpt-runs/PG379/pg12319-readiness-dependency-post-v2'/('measure-'+role+'.stdout')
        lines=p.read_text().splitlines()[:3]
        assert lines[1:]==['FORBIDDEN_PROBE_HITS\t0','FORBIDDEN_METHOD_HITS\t0']
        headers[role]=dict(path=str(p),sha256=data.sha(p.read_bytes()),sessionHeader=lines[0])
    interfaces=post['resolvedInterfaceMetadata'];assert set(interfaces)==TYPES
    assert all(not r['executionPermission'] and not r['staticInitializer'] for r in interfaces.values())
    assert sum(len(r['executableDefaultMethods']) for r in interfaces.values())==1
    v=dict(source=post['source'],resolvedTypes=sorted(interfaces),outsideProductProbeHits=int(lines[1].split('\t')[1]),nonPredicateMethodInstructionHits=post['artifactMeasurements']['api']['nonPredicateApiMainInstructionHits'],interfaceExecutionPermission=False)
    require(v);labels=[]
    for k,value in [('source','0'*40),('resolvedTypes',sorted(TYPES|{'foreign'})),('outsideProductProbeHits',1),('nonPredicateMethodInstructionHits',1),('interfaceExecutionPermission',True)]:
        bad=copy.deepcopy(v);bad[k]=value
        try:require(bad)
        except ValueError:labels.append(k)
        else:raise AssertionError('wrong boundary metadata accepted')
    assert len(labels)==5
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,boundary=v,measurementHeaders=headers,metadataNegativeLabels=labels,metadataNegativeVectors=len(labels),oldPostEntrySha256=data.sha((data.ROOT/'tools/quality/pg12318_readiness_dependency_post.py').read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
