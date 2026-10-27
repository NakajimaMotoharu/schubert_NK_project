"""Current28 selected supplied value/related generated tests tests and exact source/byte/counter/context/trace bindings, not whole acceptance."""
import datetime as dt
import platform
import subprocess
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='60f62bd5dffb11e9943fc7578d9bddf380f8003c'
OUT=data.BASE/'PG11816-job-outbox-value-literal-completion-v1'
PINS={
 'normal':('PG11804-job-outbox-value-literal-six-compile-v1','cfa574ea833d73ee31adfb96fba25fb5909890a2fb1fe32413049618b4ca58ea'),
 'host':('PG11806-job-outbox-value-literal-host-v1','89a9ea21cc85b393ae250b02a92b4d5fb76fc1682a053c2d03e175fa62ad1e98'),
 'post':('PG11810-job-outbox-value-literal-post-v1','c5378e66859ab942a09b9bad4dc74dea3cd7568b06a369db6306626f19130298'),
 'context':('PG11811-job-outbox-value-owner-context-v1','cafc772777dea065b2c37ceeb582cda3418475ea2efed811bd28f21fcdca1eac'),
 'contextPost':('PG11813-job-outbox-value-owner-context-post-v1','d729d2e4d2a8834d864b2f9efe8ab26e5cd9f95edae97e72dae505972f07056c'),
 'trace':('PG11812-job-outbox-value-literal-trace-v1','85472122436148adf180f0e0f7e09667d35b3ff211bdb9de003eb517256c70c6'),
 'tracePost':('PG11814-job-outbox-value-literal-trace-post-v1','099735cbb6b45656bcb370bc0ab3f0c875402b8876e698dcbc738e1d09e00dc4')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==28 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    sp=data.BASE/'PG11808-job-outbox-value-literal-static-v1/manifest.json';static=data.read_checked(sp,'c7d692599949d97030a84d4612b8110171dcaeb21d4786808de6180d7218f2af');assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==12
    measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);totals={k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for role,value in measures.items():
        assert role=='api' and value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100']
        assert len(value['selectedValueMain'])==8
        for unit in value['selectedValueMain'].values():
            for k,c in unit['counters'].items():
                for status in totals[k]:totals[k][status]+=c[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,122),'METHOD':(0,33),'CLASS':(0,8),'BRANCH':(0,61)}
    assert v['context']['sourceContexts']==12 and v['contextPost']['metadataNegativeVectors']==8
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2259_JobOutbox供給値十命名_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2260_JobOutbox供給値十命名_製造単体結果.md'
    units=measures['api']['selectedValueMain'];filters=[];prefix='dev/codex/schubert/nk/api/monitoring/'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for base,record in [('OutboxRowsMetricRecorder$Counts',True),('OutboxAgeMetricRecorder$Ages',True),('AsyncJobMetricRecorder$State',False),('OutboxRowsMetricRecorder$Status',False)]:
            path=prefix+base+'.class';raw=jar.read(path);model=decode(raw,path);names={m['name'] for m in model['methods']}
            generated={'toString','hashCode','equals','pending','sent','error'} if record else {'values','valueOf','<init>','$values'}
            assert names==generated|({'<init>','value'} if record else {'<clinit>'}) and len(model['methods'])==(8 if record else 5)
            assert units[path]['counters']['METHOD']==dict(missed=0,covered=2 if record else 1)
            if not record:assert units[path]['counters']['BRANCH']==dict(missed=0,covered=0)
            filters.append(dict(path=path,sha256=data.sha(raw),classfileMethods=sorted(names),defaultFilteredCompilerGeneratedMethods=sorted(generated),measuredMethods=2 if record else 1,zeroBranchDenominatorNA=not record,generatedCoverage100Claim=False,explicitExclusionAdded=False))
    generated_cases=[c for c in host['cases'] if c['classname'].endswith('.GeneratedMetricValueContractTest')]
    assert len(generated_cases)==4 and {c['name'][:len('genMetric003')] for c in generated_cases}=={'genMetric003','genMetric004','genMetric005','genMetric008'}
    assert all(not c['nonPass'] for c in generated_cases)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1933'],relatedYkt=['YKT-1682'],tests=host['begin']['cases'],actual=dict(tests=28,suites=4,changedRecorderMethods=24,selectedUnchangedGeneratedMethods=4,unselectedGeneratedMethodsNotPassed=[1,2,6,7],newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainFourCounters=totals,defaultGeneratedFilters=filters,relatedGeneratedCases=generated_cases,allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=10,referencesReplaced=73,orderConstants=3,comparisonReferences=3,rawStaticBefore=22,rawStatic=12,rawStaticGateExit=1,actualSecretCount=None,fullApiArtifactCoverage100=False,webArtifactMeasured=False,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
