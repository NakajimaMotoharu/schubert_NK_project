"""Bind current48 and static12 corrections; retain measured direct/whole coverage gaps."""
import datetime as dt
from pathlib import Path
import platform
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='06685adcf32c8583c80cb9c3e4d06d547ada486c'
OUT=data.BASE/'PG11876-web-exporter-fixture-completion-v1'
PINS={
 'normal':('PG11864-web-exporter-fixture-six-compile-v1','920dd983970da239050bc75e2f736650e4d5a6349aa5bff3d05e5203a40d2f2d'),
 'host':('PG11866-web-exporter-fixture-host-v1','66bf7c6847d32dfba0dda4c6423562d5eae973f93c7268996bd6b00540e9317a'),
 'static':('PG11868-web-exporter-fixture-static-v1','3b08df0c3b89baf7b636f007498c861760492ed0b95056d9b324060fb2178ca5'),
 'post':('PG11870-web-exporter-fixture-post-v1','09a7fe7901e7832873c0cd37af1ee250619e7f04ce2b8656e64aac6e6116e3e8'),
 'trace':('PG11872-web-exporter-fixture-trace-v1','5991784004057fddac7cfe1825f611c2d63520fe1f433427219d183a266d7148'),
 'tracePost':('PG11874-web-exporter-fixture-trace-post-v1','d51707eb7978377de81d90f0752d20cc682cd7a143999449bbc486eb42348e74')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE);v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items());assert host['observedTestExecutions']==48 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    assert all(r['findings']==r['processingErrors']==0 for r in v['static']['reports'].values());measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);assert set(measures)=={'web'};m=measures['web'];assert len(m['selectedValueMain'])==3 and not m['selectedValueFourCounters100'] and not m['wholeArtifactCoverage100'];totals={k:{status:sum(u['counters'][k][status] for u in m['selectedValueMain'].values()) for status in ('missed','covered')} for k in ('LINE','METHOD','CLASS','BRANCH')}
    assert {k:(x['missed'],x['covered']) for k,x in totals.items()}=={'LINE':(18,118),'METHOD':(3,19),'CLASS':(0,3),'BRANCH':(3,55)}
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==6 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items());run=Path(host['begin']['testCwd']).parent;raw=(run/'classload-metadata.log').read_bytes();assert data.sha(raw)==host['classloadSha256'];loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',raw.decode()));assert not any(n.startswith(('dev.codex.schubert.nk.api.','dev.codex.schubert.nk.web.bootstrap.','org.postgresql.','org.apache.activemq.')) for n in loaded)
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2267_Web三Exporter十二是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2268_Web三Exporter十二是正_製造単体結果.md';verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1935'],relatedYkt=['YKT-1684'],tests=host['begin']['cases'],actual=dict(tests=48,suites=3,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainFourCounters=totals,selectedMainFourCounters100=False,eligibilityClosureSourceHashes=closure,heldErrorBootstrapClassesLoaded=0,allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=11,referencesReplaced=94,fieldBindingTokensRenamed=3,rawStaticBefore=12,rawStatic=0,rawStaticGateExit=0,actualSecretCount=None,fullWebArtifactCoverage100=False,apiArtifactMeasured=False,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
