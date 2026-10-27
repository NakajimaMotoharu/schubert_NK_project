"""Bind current12, actual17 corrections, source/CRC/Code-debug and measured record-filter counters."""
import datetime as dt
from pathlib import Path
import platform
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts,selftest
SOURCE='5672593199b6b4e9cbfcc9bc01b26bdcda87a638'
OUT=data.BASE/'PG11966-jms-proxy-fixture-completion-v1'
PINS={
 'normal':('PG11954-jms-proxy-fixture-six-compile-v1','9914ca39739520420fbad05428dbf20ef4c776998175713a838b4ca0ab1b6824'),
 'host':('PG11956-jms-proxy-fixture-host-v1','a1ef69cbd52dc7f8fbedbe2538a09ed341d122fb5496a2561f7caaa2445cbbd9'),
 'post':('PG11960-jms-proxy-fixture-post-v1','b5278ba9730fcdb5b641fc8b80bed43733a4c2f29b846ba2f710fc17bb2aeb60'),
 'context':('PG11961-jms-proxy-fixture-context-v1','7cbf809203b90adaaecf34e04284f6c925070806ff2ddd2560de7ad436b82591'),
 'contextPost':('PG11963-jms-proxy-fixture-context-post-v1','fe7a5f6b189e9f17c6afa5b101c69f5157e1f339d2d59ad9ec543bca379e2e67'),
 'trace':('PG11962-jms-proxy-fixture-trace-v1','014615fac61be63e1f39ef6232a6eec11b0f891d57b18d1c0a712eb007451feb'),
 'tracePost':('PG11964-jms-proxy-fixture-trace-post-v1','73001516d61164fa6eb0d0bd236a075af19daacc413441f0b12e737b3955e32f')}
def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE);v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'));assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items()) and host['observedTestExecutions']==12 and not host['oldExecUnion'];assert all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG11924-storage-attribute-fixture-six-compile-v1/manifest.json','6c9f579aa08c720ce523423efa8ca7dc64a941dac559a548927259f09f28555c');old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962;changed=[key for key in old if old[key]!=new[key]];assert len(changed)==5;detail=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry);b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry);detail.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],rawCodeRepresentationChanged=a['rawCodeRepresentationSha256']!=b['rawCodeRepresentationSha256'],debugTablesChanged=a['debugTablesSha256']!=b['debugTablesSha256'],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in detail}=={'JmsMessageGuardTest.java','JmsReplyDecoderTest.java'};vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);counts={}
    for role in ('api','web'):
        m=measure[role];assert m['selectedValueFourCounters100'] and not m['wholeArtifactCoverage100'];counts[role]={kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    assert {k:c['covered'] for k,c in counts['api'].items()}==dict(LINE=70,METHOD=13,CLASS=2,BRANCH=40) and {k:c['covered'] for k,c in counts['web'].items()}==dict(LINE=74,METHOD=13,CLASS=2,BRANCH=38) and all(c['missed']==0 for values in counts.values() for c in values.values());static=data.read_checked(data.BASE/'PG11958-jms-proxy-fixture-static-v1/manifest.json','fec45644accf3140542a82a3b8189f4205796b7c5edbccbcca159ae0b84895f6');assert static['actualExit']==1 and static['reports']['pmd']['findings']==10
    run=Path(host['begin']['testCwd']).parent;loadedraw=(run/'classload-metadata.log').read_bytes();assert data.sha(loadedraw)==host['classloadSha256'];loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()));assert not any(n.startswith(('org.postgresql.','dev.codex.schubert.nk.api.error.','dev.codex.schubert.nk.web.bootstrap.')) or 'ConnectionFactory' in n for n in loaded);closure=host['begin']['eligibilityClosureSourceHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items());assert not list(Path(host['begin']['testCwd']).iterdir())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2279_JMS代理field十七是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2280_JMS代理field十七是正_製造単体結果.md';verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=detail,structuralReaderVectors=vectors,meaningProof='strict raw inverse40 negatives plus original12 actual PT, raw constant pool indices not semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1939'],relatedYkt=['YKT-1688'],tests=host['begin']['cases'],actual=dict(tests=12,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,recordDefaultFilters=True,zeroBranchRecordCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1957,testClassesChanged=5,stringConstants=17,referencesReplaced=102,rawStaticBefore=27,rawStatic=10,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
