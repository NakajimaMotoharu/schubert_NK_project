"""Current original16 tests and exact source/byte/counter/context/trace bindings, not whole acceptance."""
import datetime as dt
import platform
import subprocess
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='6c96b262e88d9863ffb1e883780a249eaa11be27'
OUT=data.BASE/'PG11746-mq-recorder-literal-completion-v1'
PINS={
 'normal':('PG11734-mq-recorder-literal-six-compile-v1','7d0f5f532b32896695e553c7ae886cdfef02595cbeb3c54c85c78b95b541505b'),
 'host':('PG11736-mq-recorder-literal-host-v1','2ec18eeb50b3f15baff545964708774faa1fae0945c222534daec42ac5cf5efa'),
 'post':('PG11740-mq-recorder-literal-post-v1','2438154224e144805d92fed133e10a46d2f96b24c40b6f370983a9c0ed93fa16'),
 'context':('PG11741-mq-recorder-owner-context-v1','0a1e03a22c825d6ea788a884e4c6e55104ac16abf41194b28bcc3193e5181245'),
 'contextPost':('PG11743-mq-recorder-owner-context-post-v1','ac920be8bcd0bd74e1edb9a2abb29fe73cef0be3be19f4133bbd58b195845f87'),
 'trace':('PG11742-mq-recorder-literal-trace-v1','c5a82030c8d64d3f0fb273f86fde3b03ac0da92fbb8643f728a47b10769b9801'),
 'tracePost':('PG11744-mq-recorder-literal-trace-post-v1','54a153bee1ad60938d4d27038e18c4f33b6a82dc3136214b8899a0f2309b58ff')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==16 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    sp=data.BASE/'PG11738-mq-recorder-literal-static-v1/manifest.json';static=data.read_checked(sp,'968d7e43a6d1a2aa9e21269e99899261afe481b90b5c96e8d4315bdd6958e5e1');assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==5
    measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);totals={k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for role,value in measures.items():
        assert role=='api' and value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100']
        assert len(value['selectedValueMain'])==3
        for unit in value['selectedValueMain'].values():
            for k,c in unit['counters'].items():
                for status in totals[k]:totals[k][status]+=c[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,76),'METHOD':(0,13),'CLASS':(0,3),'BRANCH':(0,42)}
    assert v['context']['sourceContexts']==5 and v['contextPost']['metadataNegativeVectors']==8
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2251_MQRecorder同値十一是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2252_MQRecorder同値十一是正_製造単体結果.md'
    record='dev/codex/schubert/nk/api/monitoring/MqPressureMetricRecorder$Snapshot.class'
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:record_bytes=jar.read(record)
    model=decode(record_bytes,record);generated={'toString','hashCode','equals','messages','queueBytes','addressMemoryBytes','addressPagedBytes','pagingActive','pageFiles'}
    assert {m['name'] for m in model['methods']}==generated|{'<init>'} and len(model['methods'])==10
    snapshot=measures['api']['selectedValueMain'][record];assert snapshot['counters']['METHOD']==dict(missed=0,covered=1)
    record_filter=dict(path=record,sha256=data.sha(record_bytes),compilerGeneratedMethods=sorted(generated),intrinsicJacocoFilter='DEFAULT_RECORD_FILTER_JACOCO_0_8_15_NO_CONFIG_EXCLUSION_ADDED',measuredHandwrittenMethods=1,generatedMethodsMeasured100Claim=False,independentCurrentCases=['mqPress004StandardRetainsNothingAndConfigurationOrNegativeSamplesAreNotNormalized','mqPress008GeneratedSnapshotContractsUseIndependentLongBooleanFoldAndFixedText'])
    assert all(any(c['name']==name and not c['nonPass'] for c in host['cases']) for name in record_filter['independentCurrentCases'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1931'],relatedYkt=['YKT-1680'],tests=host['begin']['cases'],actual=dict(tests=16,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainFourCounters=totals,generatedRecordFilter=record_filter,allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=10,referencesReplaced=57,orderConstants=2,comparisonReferences=2,rawStaticBefore=16,rawStatic=5,rawStaticGateExit=1,actualSecretCount=None,fullApiArtifactCoverage100=False,webArtifactMeasured=False,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
