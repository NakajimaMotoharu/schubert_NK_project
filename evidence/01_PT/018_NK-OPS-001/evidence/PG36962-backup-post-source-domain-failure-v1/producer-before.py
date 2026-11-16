"""Verify fixed Path local, unchanged ABI/1100 other class bytes and full static terminal."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
from pmo_group_context import build_context
b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
bp=b/'evidence/PG36872-ssc450-four-main-compile-v1/manifest.json';old=load(bp)
cp=b/'evidence/PG36956-backup-path-four-main-compile-v1/manifest.json';current=load(cp)
sp=b/'evidence/PG36958-backup-path-fresh-sibling-spotbugs-v1/manifest.json';sb=load(sp)
pm=b/'evidence/PG36960-current287-root-pmd-v1/manifest.json';pmd=load(pm)
assert current['actualExit']==sb['actualExit']==pmd['actualExit']==0
assert current['sourceCore']==sb['sourceCore']==pmd['sourceCore']
for module in ['bootstrap','batch']:
    x=sb['reports'][module];assert sb['stages'][module]['actualExit']==0
    assert not x['bugs'] and not x['errors'] and not x['missingClasses']
    assert set(x['classStats'])=={n[:-6].replace('/','.') for n in current['physicalClassHashes'][module]}
changed=[];total=0
for module,before in old['physicalClassHashes'].items():
    after=current['physicalClassHashes'][module];assert set(before)==set(after)
    total+=len(after);changed.extend((module,n) for n,h in before.items() if after[n]!=h)
assert total==1101 and changed==[('batch','dev/codex/schubert/nk/batch/file/BackupStartIntentFiles.class')]
path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/BackupStartIntentFiles.java'
before=subprocess.check_output(['git','show',old['sourceCore']+':'+path],text=True);after=(r/path).read_text()
inverse=after.replace('    context.recheck(morning);\n    Path path = Path.of("/run/schubert-nk/startup");','    context.recheck(morning);').replace('        () -> OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), path),','        () ->\n            OwnedTransferDirectory.open(\n                LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup")),')
assert inverse==before
assert all(current['inputHashes'][p]==h for p,h in old['inputHashes'].items() if p!=path)
diff=subprocess.check_output(['git','diff','--name-only',old['sourceCore'],current['sourceCore'],'--','src'],text=True).splitlines();assert diff==[path]
out=b/'evidence/PG36962-backup-static-independent-v1';assert not out.exists();out.mkdir()
javap=r.parent/'toolchain/jdk-25.0.4/bin/javap';outputs=[];commands=[]
name='dev.codex.schubert.nk.batch.file.BackupStartIntentFiles'
for label,manifest in [('before',old),('after',current)]:
    folder=Path(manifest['cwd'])/'src/schubert-nk-batch/target/classes'
    command=[str(javap),'-public','-classpath',str(folder),name]
    result=subprocess.run(command,capture_output=True,timeout=30);assert result.returncode==0 and not result.stderr
    p=out/(label+'-public.txt');p.open('xb').write(result.stdout);outputs.append(result.stdout);commands.append(dict(command=command,actualExit=0,output=ref(p)))
assert outputs[0]==outputs[1]
folder=Path(current['cwd'])/'src/schubert-nk-batch/target/classes'
command=[str(javap),'-p','-c','-classpath',str(folder),name]
result=subprocess.run(command,capture_output=True,timeout=30);assert result.returncode==0
(out/'after-bytecode.txt').open('xb').write(result.stdout)
text=result.stdout.decode();start=text.index('public static dev.codex.schubert.nk.batch.file.BackupStartIntentFiles createService(')
body=text[start:text.index('\n  dev.codex.schubert.nk.batch.file.BackupStartIntentFiles(',start)]
assert body.index('java/nio/file/Path.of:')<body.index('InvokeDynamic')<body.index('storage/ResourceScope.handoff:')
assert 'LinuxDirectoryCalls.create' not in body and 'OwnedTransferDirectory.open' not in body
spec=b/'4457_F03固定Path静的是正仕様.md';report=b/'evidence/PG36848-ssc449-fresh-sibling-spotbugs-v1/manifest.json'
context=dict(group_id='STATIC-REFERENCE-SELF',category='REVIEW',kind='TOOL_FIX',scope='No operation; validate oracle reference schema only.',oracle_refs=[ref(spec),ref(report)])
build_context(**context)
try:build_context(**dict(context,oracle_refs=[ref(report.parent/'batch-spotbugs.xml')]))
except ValueError as failure:assert str(failure)=='public reference'
else:raise AssertionError('XML must remain rejected before external operations')
value=dict(actualExit=0,source=current['sourceCore'],sourceCore=current['sourceCore'],
    terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourcePath=path,
    mainCount=477,physical=1101,other1100PhysicalByteExact=True,changedPhysical=changed,
    sourceInverseByteExact=True,publicAbiExact=True,abiMeasurements=commands,
    pathBeforeAcquireLambdaCapture=True,existingAnnotationsByteExact=True,newSuppressions=0,
    canonicalArtifactOwner='WBS-P017-06',staticGateWorkOwner='WBS-F03',historicalCostsReassigned=False,
    compile=ref(cp),fullBootstrapBatchSpotbugs=ref(sp),full287Pmd=ref(pm),
    spotbugsBootstrapClassStats=200,spotbugsBatchClassStats=646,spotbugsBugsMissingErrors=0,
    pmdRaw=971,pmdStillUnclassified=True,normalCreateServicePt='NOT_RUN_HOLD_NOT_PASS',
    actualNativeServiceIntentActions=0,newProductTests=0,coverageMeasuredByThisRun=False,
    factoryHorizontal=dict(create='closed-target path unchanged',createPublication='already outer fixed Path unchanged',createService='outer fixed Path inverse exact / old annotations now apply to the actual Path method'),
    referenceSchemaNegative=1,referenceSchemaPositive=1,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,source=current['sourceCore'],spotbugs=0,otherPhysicalExact=1100,publicAbiExact=True,pmdRawPending=971,newAcceptance=0)))
