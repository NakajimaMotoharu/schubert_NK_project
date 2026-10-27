"""Bind actual same-source pure Main correction/21PT, retaining all tool failures and full-scope gaps."""
from pathlib import Path
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='fb1a22da2433c7909ceba05c7eeb07c879e52325'
OUT=data.BASE/'PG12566-monitoring-main-completion-v1'
PINS={
    'normal':('PG12551-monitoring-main-six-compile-v2','a51e4812b19c20f1ef673b35278a9c4ef75e08100e785360033bbd5c1afdc5e0'),
    'host':('PG12552-monitoring-main-host-v1','f8f5e46ed801d295b269f33e64e81881c6628af5ae4ba63cff692acb0978dfed'),
    'static':('PG12554-monitoring-main-static-v1','fb2fe41cab40003c4a052244dacd1d3036f48c0d6178066e4d576145ac08c812'),
    'post':('PG12560-monitoring-main-post-v3','4d3aa8a2243747ad1bd72ea6abc03df5edf377c6ee56d952d3258f292c97653c'),
    'trace':('PG12558-monitoring-main-trace-v1','e1078c4f13908f406ab9523bc41c9fa3a519cc2b1111c3b8e2f269e8b008f636'),
    'tracePost':('PG12559-monitoring-main-trace-post-v1','9d2c280e1b553163cd43621e9e1fdf17594b6f778c3d37db51faf7eba546b6f8'),
    'delta':('PG12562-current-monitoring-main-delta-v1','5ebe33e3a8cae2dd9addbd053e6df648c006bff06ca79f252e5671ac64489f40'),
    'deltaPost':('PG12564-current-monitoring-main-delta-post-v1','514d3b7b85b93b26709cffe4e59e01b0d6496fd3e17c25fd3e91419f48d51f7d')}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/name/'manifest.json',digest) for name,digest in PINS.values()],SOURCE)
    values={k:data.read_checked(data.BASE/name/'manifest.json',digest) for k,(name,digest) in PINS.items()}
    n,h,p,s=(values[k] for k in ['normal','host','post','static'])
    assert n['testsExecuted']==0 and h['observedTestExecutions']==p['observedTestExecutions']==21 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainPhysical']==1843 and len(p['changedMainPhysical'])==3 and p['otherMainUnchanged']==1840 and p['allTestPhysicalUnchanged']==1962
    assert p['selectedFiveMissedZero'] and not p['completeBatchCoverage100'] and p['spotbugsSixExit']==s['spotbugsSixExit']==0
    assert p['selectedFiveCounters']==dict(LINE=dict(missed=0,covered=85),METHOD=dict(missed=0,covered=19),CLASS=dict(missed=0,covered=5),BRANCH=dict(missed=0,covered=25))
    assert values['delta']['sourceDerivedRaw']==8520 and values['deltaPost']['totalPriorCorrections']==897
    assert values['tracePost']['oldRowsChangedShaOnly']==2 and values['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    plan=data.read_checked(data.BASE/'PG12548-monitoring-main-plan-v1/manifest.json','e1b73f8dda2d18379ba8edcf172709a520dab816d33a94458d90bffbd3157baf')
    assert plan['metadataNegativeVectors']==11 and plan['labelReferences']==13 and plan['allTestsAndOtherInputsUnchanged']
    assert all(n['begin']['inputHashes'][r['path']]==r['sha256'] for r in plan['sourceChanges'])
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2351_監視Main六件同値是正_単体テスト仕様書.md'
    result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2352_監視Main六件同値是正_製造単体結果.md'
    failures=[]
    for filename,session,bug,stage,code,digest in [
        ('pg12550_monitoring_main_six_compile.py','cbc446','BUG1981','CHECKED_ARGUMENT_REJECTION_BODY_NOT_STARTED',1,None),
        ('pg12556_monitoring_main_post.py','d1d17e','BUG1982','BODY_BEFORE_SLOT_AND_COVERAGE_READER',1,'cbafdfca4d16beaa9bbb0a9fbcc4d5e42c5b812c0a283e9e1e4360b592875d42'),
        ('pg12557_monitoring_main_post_v2.py','ced4d4','BUG1983','LINT_BODY_NOT_STARTED',1,'98bd5cf803f766b1efa3b7810773774120e88664e30b584d0a5ab8d489dc02a7')]:
        path=data.ROOT/'tools/quality'/filename;actual=data.sha(path.read_bytes());assert digest is None or digest==actual
        failures.append(dict(path=str(path.relative_to(data.ROOT)),sha256=actual,toolCallChunk=session,bug=bug,stage=stage,actualExit=code,productTestFailure=False,reexecuted=False))
    assert not list(Path(h['begin']['testCwd']).iterdir())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=21,suites=3,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG1980','BUG1981','BUG1982','BUG1983'],relatedYkt=['YKT1728','YKT1729','YKT1730','YKT1731'],implementationDecision='PG-D747',changedSourceFiles=2,changedMainPhysical=3,allOtherMainPhysicalUnchanged=1840,allTestPhysicalUnchanged=1962,selectedFiveCounters=p['selectedFiveCounters'],completeBatchCounters=p['completeBatchCounters'],completeBatchCoverage100=False,manualCoverageExclusionsAdded=False,rawStatic=0,spotbugsSixExit=0,sourceRawCorrections=6,sourceDerivedRaw=8520,totalCorrections=897,actualViolationCount=None,toolFailures=failures,implementedToolDefects=3,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
