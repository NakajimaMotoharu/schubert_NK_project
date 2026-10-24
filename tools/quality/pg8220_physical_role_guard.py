"""Actual physical trace retained; source-only namespace regression guards, no repeat architecture/PT."""
import inspect
import json
import subprocess
from pathlib import Path
import pg8218_counter_name_six_trace as trace
from host_tool_invocation import capture,verify

OUT=trace.host.BASE/'PG8220-physical-role-guard-v1'
TRACE=trace.host.BASE/'PG8219-counter-name-six-trace-v2/manifest.json'
TRACE_SHA='671663c32905d4e15ca0462f02d59d4759842a9e27ab908ee623d9f9850734af'
OLD='ca8c6f143'


def main():
    invocation=capture(Path(__file__))
    trace.require(not OUT.exists() and trace.host.sha(TRACE)==TRACE_SHA,'new-only immutable successful physical witness')
    raw=json.loads(TRACE.read_bytes())
    trace.require(raw['actualExit']==0 and raw['source']==trace.SOURCE and raw['allPhysicalClassCount']==1799
        and raw['originalPhysicalUnchanged']==1669 and raw['previousPhysicalUnchanged']==1798
        and set(raw['physicalChanged'])=={trace.CLASS},'true original full physical/source measurement')
    old_commit=subprocess.check_output(['git','rev-parse',OLD],cwd=trace.host.ROOT,text=True).strip()
    path='tools/quality/pg8218_counter_name_six_trace.py'
    old=subprocess.check_output(['git','show',old_commit+':'+path],cwd=trace.host.ROOT).decode()
    current=(trace.host.ROOT/path).read_text()
    inline="        require(all(p.startswith(role+':dev/') and not p.startswith(role+':'+role+':') for p in rows),\n                'prior witness uses explicit one-time role-qualified keys, not bare component entries')\n"
    restored=current.replace(inspect.getsource(trace.validate_role),'',1).replace('        validate_role(rows,role)\n',inline,1)
    canonical=lambda value:'\n'.join(line for line in value.splitlines() if line.strip())
    trace.require(canonical(restored)==canonical(old),'only pure guard extraction/nonempty tightening, measurement algorithm unchanged')
    prior=json.loads((trace.host.BASE/raw['witnesses']['previous']['path']).read_bytes())
    trace.require(trace.host.sha(trace.host.BASE/raw['witnesses']['previous']['path'])==raw['witnesses']['previous']['sha256'],'prior namespace original bytes')
    accepted=[]
    rejected=[]
    for role,key in (('web','currentWeb'),('api','historicalApi'),('batch','historicalBatch')):
        trace.validate_role(prior[key]['physicalClasses'],role)
        accepted.append(role)
        name=role+':dev/codex/schubert/nk/'+role+'/monitoring/OwnFixture.class'
        for label,rows in (('double-prefix',{role+':'+name:'0'*64}),('bare',{name.split(':',1)[1]:'0'*64}),
                           ('foreign',{'other:'+name.split(':',1)[1]:'0'*64}),('empty',{})):
            try:
                trace.validate_role(rows,role)
            except ValueError:
                rejected.append(role+':'+label)
            else:
                raise ValueError('bad namespace must never qualify')
    trace.require(len(accepted)==3 and len(rejected)==12,'every actual role and independent namespace negatives')
    verify(invocation)
    value=dict(actualExit=0,source=trace.SOURCE,invocation=invocation,originalTraceSha256=TRACE_SHA,
        originalExecutedToolCommit=old_commit,currentToolSha256=trace.host.sha(trace.host.ROOT/path),
        exactOtherSourceChanges=0,positiveActualRoleMaps=accepted,negativeNamespaceGuards=rejected,
        originalPhysicalCount=1799,originalPhysicalUnchanged=1669,sourceRows=155,
        productTestsExecuted=0,architectureJobsReplayed=0,actualVmActions=0,actualNetworkActions=0,
        actualDatabaseActions=0,newAccepted=0,formalUpdated=False)
    OUT.mkdir()
    trace.host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,actualRoles=len(accepted),negativeGuards=len(rejected),manifestSha256=trace.host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
