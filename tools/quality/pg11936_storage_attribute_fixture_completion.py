"""Bind current7, raw33 corrections, own-temp post and measured coverage with constructor filter explicit."""
import datetime as dt
from pathlib import Path
import platform
import re
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
from classfile_code_metadata import decode

SOURCE='fd113e37b0783ae86d50696c9d3844e80b258d8a'
OUT=data.BASE/'PG11936-storage-attribute-fixture-completion-v1'
PINS={
 'normal':('PG11924-storage-attribute-fixture-six-compile-v1','6c9f579aa08c720ce523423efa8ca7dc64a941dac559a548927259f09f28555c'),
 'host':('PG11926-storage-attribute-fixture-host-v1','e90717c76ced572401417d0a4515c79d5c82fb2cbbe3bd445bdc55f8cac1aa01'),
 'post':('PG11930-storage-attribute-fixture-post-v1','1bf9eba710e500037a4dd7e1eb008151cc1c389d24726ba2481765fca200b86b'),
 'context':('PG11931-storage-attribute-map-context-v1','953bad12f2072ba6ae09f3462526b080dd06c6064dda06df73e3670ae17a462b'),
 'contextPost':('PG11933-storage-attribute-map-context-post-v1','1b1656e75eafa77239ce41445e0ef7883d2901c8dcc7a37dca064a4d59c0ce26'),
 'trace':('PG11932-storage-attribute-fixture-trace-v1','4e2e5dbf16f884e0b6285e12d06ebc293c9177b003d62eb34825d0c4a4f5672c'),
 'tracePost':('PG11934-storage-attribute-fixture-trace-post-v1','9d1b40c981e322be9fdf23afa1e3ac434560a4c63fadf36a7cc40160a70012de')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE);v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'));assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items());assert host['observedTestExecutions']==7 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    static=data.read_checked(data.BASE/'PG11928-storage-attribute-fixture-static-v1/manifest.json','1518ae6f87ba5342038fb964354e8f0ab34525ba2e76af5fabbb88a969f4933d');assert static['source']==SOURCE and static['actualExit']==1 and static['reports']['pmd']['findings']==1 and all(r['processingErrors']==0 for r in static['reports'].values());measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);assert set(measures)=={'storage'};m=measures['storage'];assert m['selectedValueFourCounters100'] and not m['wholeArtifactCoverage100'] and len(m['selectedValueMain'])==1;counts=next(iter(m['selectedValueMain'].values()))['counters'];assert {k:(c['missed'],c['covered']) for k,c in counts.items()}=={'LINE':(0,44),'METHOD':(0,8),'CLASS':(0,1),'BRANCH':(0,42)}
    entry='dev/codex/schubert/nk/storage/StorageAttributeGuard.class'
    with zipfile.ZipFile(normal['jars']['storage']['path']) as jar:model=decode(jar.read(entry),entry)
    constructor=[x for x in model['methods'] if x['name']=='<init>'];assert len(model['methods'])==9 and constructor==[dict(name='<init>',descriptor='()V',flags=2,hasCode=True,codeLength=5)]
    core=data.ROOT.parent/'toolchain/m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar';core_sha=data.sha(core.read_bytes());assert core_sha=='ade1e0fdb4cd80d8537b57c6edb70a1360c47fdc518c20c65314517479bc4d0d';filter_name='org/jacoco/core/internal/analysis/filter/PrivateEmptyNoArgConstructorFilter.class'
    with zipfile.ZipFile(core) as jar:assert filter_name in jar.namelist()
    assert host['temporaryCreatedAndRemoved']==post['temporaryCreatedAndRemoved']==7 and host['temporaryParentAfter']==post['temporaryParentPost'] and host['temporaryReceiptSha256']==post['temporaryReceiptSha256'];closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==3 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items());run=Path(host['begin']['testCwd']).parent;raw=(run/'classload-metadata.log').read_bytes();assert data.sha(raw)==host['classloadSha256'];loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',raw.decode()));product={x for x in loaded if x.startswith('dev.codex.schubert.nk.')};assert product and all(x.startswith('dev.codex.schubert.nk.storage.') for x in product) and not any('Native' in x or 'Linux' in x for x in product)
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2275_Storage属性三十三是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2276_Storage属性三十三是正_製造単体結果.md';verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1938'],relatedYkt=['YKT-1687'],tests=host['begin']['cases'],actual=dict(tests=7,suites=1,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredFourCounters=counts,privateEmptyConstructor=dict(physicalMethodCount=9,measuredMethodCount=8,structuralModel=constructor[0],defaultFilter=filter_name,jacocoCoreSha256=core_sha,executed=False,noManualExclusions=True,noPrivateReflection=True),eligibilityClosureSourceHashes=closure,temporaryCreatedAndRemoved=7,temporaryParentPost=post['temporaryParentPost'],temporaryReceiptSha256=post['temporaryReceiptSha256'],codeDebugSha256=post['codeDebugSha256'],allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=5,referencesReplaced=55,modeLiteralPoints=27,boundConstants=1,rawStaticBefore=34,rawStatic=1,rawStaticGateExit=1,actualSecretCount=None,fullStorageArtifactCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
