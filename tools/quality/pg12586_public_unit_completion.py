"""Bind original13 public text PT, nine same-value corrections; no Main coverage or actual Unit credit."""
from pathlib import Path
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='2efcd4ac8e1b7681fdba0862f7392bbbba5d3f68'
OUT=data.BASE/'PG12586-public-unit-completion-v1'
PINS={
    'normal':('PG12572-public-unit-six-compile-v1','fe361f6c8fb14008feb760c5b0437f7fc68777a776eb39ca7febc8ec49a27c1a'),
    'host':('PG12575-public-unit-host-v2','52616e3280b26d21f53db04ac1ba1bc0ae5ffaaa5bb5ae8784b501a1d5a3e70d'),
    'static':('PG12576-public-unit-static-v1','7ab10e270524f200cf1bd53597127f4709f0df92fe0a26ee3211e0a4e62b3806'),
    'post':('PG12578-public-unit-post-v1','911bc75b7c886d101fe93b9d07cd465d4bcc348ee0aaad4f2adb62e52eed9517'),
    'trace':('PG12580-public-unit-trace-v1','0046165720eaf1f4074ba192f7b0b33a94ea1f29198aec6aa55eb1f0af714af7'),
    'tracePost':('PG12581-public-unit-trace-post-v1','604276bd909340b0625a130200add9dbe51ef42725af34320272d44e01127620'),
    'delta':('PG12582-current-public-unit-delta-v1','4f9e96e4bc92c480314194f3e5069cc62bec271bfb98decf1248c9187c0b2d3f'),
    'deltaPost':('PG12584-current-public-unit-delta-post-v1','21a137bd4faf4f0aed990a53e8dd05fabd03497089027be107f3338c57572c1f')}


def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/name/'manifest.json',digest) for name,digest in PINS.values()],SOURCE)
    values={k:data.read_checked(data.BASE/name/'manifest.json',digest) for k,(name,digest) in PINS.items()};n,h,p=(values[k] for k in ['normal','host','post'])
    assert n['testsExecuted']==0 and h['observedTestExecutions']==p['observedTestExecutions']==13 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainClassesUnchanged']==1843 and p['changedTestPhysical']==4 and p['otherTestPhysicalUnchanged']==1958 and p['actualProductMainClassesLoaded']==0
    assert p['productJarsInExecutionClasspath']==0 and p['coverage'] is None and p['mainCoverage']=='NOT_APPLICABLE_CONFIGURATION'
    assert all(v['findings']==v['processingErrors']==0 for v in values['static']['reports'].values())
    assert values['delta']['sourceDerivedRaw']==8511 and values['deltaPost']['totalPriorCorrections']==906
    assert values['tracePost']['oldRowsChangedShaOnly']==3 and values['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    plan=data.read_checked(data.BASE/'PG12570-public-unit-plan-v1/manifest.json','5ec7235434a5c8ce0c379da9decc85975dd2db1e7c60a2252e56eb6f121ae9e4')
    assert plan['metadataNegativeVectors']==29 and plan['literalReferences']==82 and plan['allMainAndOtherInputsUnchanged']
    assert all(n['begin']['inputHashes'][r['path']]==r['sha256'] for r in plan['sourceChanges'])
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2354_公開Unit三Test九同値是正_単体テスト仕様書.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2355_公開Unit三Test九同値是正_製造単体結果.md'
    failed=data.ROOT/'tools/quality/pg12574_public_unit_host.py';assert data.sha(failed.read_bytes())=='44dc7e94ea890008923abbe52a677afd1b4b8302c2b23f233a350cb1cd9d78b7'
    assert not list(Path(h['begin']['testCwd']).iterdir())
    verify(invocation);OUT.mkdir();value=dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=13,suites=3,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG1984','BUG1985'],relatedYkt=['YKT1732','YKT1733'],implementationDecision='PG-D748',allMainClassesUnchanged=1843,changedTestPhysical=4,allOtherTestPhysicalUnchanged=1958,coverage=None,mainCoverage='NOT_APPLICABLE_CONFIGURATION',productMainClassesLoaded=0,productJarsInExecutionClasspath=0,rawStatic=0,sourceRawCorrections=9,sourceDerivedRaw=8511,totalCorrections=906,actualViolationCount=None,toolFailures=[dict(path=str(failed.relative_to(data.ROOT)),sha256=data.sha(failed.read_bytes()),toolCallChunk='695ab3',bug='BUG1985',actualExit=1,stage='BODY_PRE_RESOURCE_BEFORE_SLOT_JVM_PT',productTestFailure=False,reexecuted=False)],implementedToolDefects=1,whole451Accepted=False,wholeF03Accepted=False,wholeC02Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
