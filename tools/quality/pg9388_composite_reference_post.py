"""Independent JDK class/source/CP metadata and literal responsibility47 oracle; never PT."""
from collections import defaultdict
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg9360_static_companion_javap_metadata as disassembly
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SUBJECT=BASE/'PG9386-composite-reference-graph-v3'
OUT=BASE/'PG9388-composite-reference-post-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9388-composite-reference-post-v1'
TC=ROOT.parent/'toolchain'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
PREFIX='dev/codex/schubert/nk/'
# Literal reviewed responsibility table, independent of graph resolution/mapper.
ORACLE={
 'api/bootstrap/BootstrapClosingBoundaryTest':'WBS-P010-05',
 'api/bootstrap/BootstrapEntryBoundaryTest':'WBS-P010-05',
 'api/error/ApiStartupGraph330Test':'WBS-P018-05',
 'api/error/TemporaryFailureGraph329Test':'WBS-P018-05',
 'api/idempotency/ExceptionValueContractTest':'WBS-P006-01',
 'api/idempotency/InboxBoundaryFailureFixture':'WBS-P006-01',
 'api/idempotency/InboxModelTest':'WBS-P006-01',
 'api/idempotency/SecretBufferTest':'WBS-P006-01',
 'api/maintenance/InspectorEntryBoundaryTest':'WBS-P004-04',
 'api/messaging/config/ApiFactoryOwnershipTest':'WBS-P005-04',
 'api/messaging/outbound/OutboxModelTest':'WBS-P006-02',
 'api/messaging/outbound/OutboxPolicyTest':'WBS-P006-02',
 'api/security/AuthenticationFailureGraphTest':'WBS-P007-03',
 'api/security/AuthenticationJdbcGraph328Test':'WBS-P007-03',
 'batch/cleanup/ExceptionValueContractTest':'WBS-P017-07',
 'batch/file/CaddyAddressBoundaryTest':'WBS-P018-01',
 'batch/file/CaddyParentRemainingBudgetTest':'WBS-P017-12',
 'batch/file/CaddyPublicCaMetadataTest':'WBS-P018-01',
 'batch/file/CaddyPublicMetadataTest':'WBS-P018-01',
 'batch/file/MorningBackupCatalogTest':'WBS-P017-03',
 'batch/file/MorningBackupInputModeTest':'WBS-P017-03',
 'batch/file/MorningStartupRetainOwnerTest':'WBS-P017-12',
 'batch/file/UnsupportedOriginalProofTest':'WBS-P017-02',
 'batch/platform/ExceptionValueContractTest':'WBS-P018-04',
 'batch/platform/LegacyReceiptValueTest':'WBS-P017-06',
 'batch/platform/RootContextNoIoFixture':'WBS-P018-03',
 'batch/repository/JdbcResourceCases':'WBS-P017-02',
 'bootstrap/ChildMaintenanceParentTest':'WBS-P018-03',
 'bootstrap/FixedCaddyIdentityTest':'WBS-P018-04',
 'bootstrap/FixedNativeCoverageStopHoldProbe':'WBS-P018-08',
 'bootstrap/MaintenanceParentGuardTest':'WBS-P018-03',
 'web/bootstrap/WebRuntimeExecutionRetentionTest':'WBS-P018-06',
 'web/bootstrap/WebRuntimePendingFailureRetentionTest':'WBS-P018-06',
 'web/bootstrap/WebStartupGraph330Test':'WBS-P018-06',
 'web/bootstrap/WebStartupRetentionTest':'WBS-P006-04',
 'web/bootstrap/WebUnknownRetentionTest':'WBS-P018-06',
 'web/logging/ExceptionValueContractTest':'WBS-P006-04',
 'web/media/ExceptionValueContractTest':'WBS-P009-04',
 'web/messaging/WebBrokerFactoryOwnershipTest':'WBS-P005-02',
 'web/revocation/ExceptionValueContractTest':'WBS-P015-05',
 'web/revocation/RevocationJdbcGraph328Test':'WBS-P015-05',
 'web/security/ExceptionValueContractTest':'WBS-P015-02',
 'web/security/WebSecurityHeaderTest':'WBS-P015-02',
 'web/session/ExceptionValueContractTest':'WBS-P015-01',
 'web/session/SessionFailureGraphTest':'WBS-P015-01',
 'web/session/SessionJdbcGraph328Test':'WBS-P015-01',
 'web/storage/ScenarioFileFixture':'WBS-P003-01'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def short(path):return path.split('/schubert/nk/')[1].removesuffix('.java')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    subject_raw=(SUBJECT/'manifest.json').read_bytes();assert sha(subject_raw)=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    subject=json.loads(subject_raw);assert subject['actualExit']==0 and subject['source']==SOURCE
    for name,key in (('candidates.json','candidatesSha256'),('unresolved.json','unresolvedSha256'),('main-class-sources.json','mainMapSha256'),('test-class-metadata.json','testMetadataSha256')):
        assert sha((SUBJECT/name).read_bytes())==subject[key]
    candidates=json.loads((SUBJECT/'candidates.json').read_bytes());unknown=json.loads((SUBJECT/'unresolved.json').read_bytes())
    classes=json.loads((SUBJECT/'test-class-metadata.json').read_bytes());mains=json.loads((SUBJECT/'main-class-sources.json').read_bytes())
    assert len(candidates)==47 and len(unknown)==291 and {short(row['path']) for row in candidates}==set(ORACLE)
    assert all(row['owner']==row['costOwner']==ORACLE[short(row['path'])] for row in candidates)
    by_source=defaultdict(list)
    for row in classes:by_source[row['path']].append(row)
    test_lookup=defaultdict(set)
    for row in classes:test_lookup[row['className']].add(row['path'])
    needed={row['path'] for row in candidates};pending=list(needed)
    while pending:
        path=pending.pop()
        for source_class in by_source[path]:
            for name in source_class['references']:
                if not name.startswith(PREFIX) or name in mains:continue
                same={row['path'] for row in classes if row['module']==source_class['module'] and row['className']==name}
                dependencies=same or test_lookup[name]
                assert len(dependencies)==1
                dep=next(iter(dependencies))
                if dep not in needed:needed.add(dep);pending.append(dep)
    by_module=defaultdict(list)
    for path in sorted(needed):
        for row in by_source[path]:by_module[row['module']].append(row)
    os.umask(0o077);SLOT.mkdir();receipts=[];independent={};selected_main=set()
    fixture_vectors=disassembly.vectors()
    for module,rows in sorted(by_module.items()):
        directory=next(Path(path) for path in subject['treePins'] if '/schubert-nk-'+module+'/' in path)
        for offset in range(0,len(rows),48):
            batch=rows[offset:offset+48]
            argv=[str(TC/'jdk-25.0.4/bin/javap'),'-v','-p','-classpath',str(directory)]+[row['className'].replace('/','.') for row in batch]
            begin=dt.datetime.now(dt.timezone.utc).isoformat()
            process=subprocess.Popen(argv,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
            write(SLOT/(module+'-'+str(offset)+'-process.safe.json'),dict(pid=process.pid,ownerPid=os.getpid(),startUTC=begin,command=argv))
            timed_out=False
            try:stdout,stderr=process.communicate(timeout=120)
            except subprocess.TimeoutExpired:
                timed_out=True;process.kill();stdout,stderr=process.communicate(timeout=15)
            receipt=dict(command=argv,actualExit=process.returncode,timedOut=timed_out,startUTC=begin,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),stdoutSha256=sha(stdout),stderrSha256=sha(stderr),rawOutputPersisted=False)
            write(SLOT/(module+'-'+str(offset)+'-exit.safe.json'),receipt);receipts.append(receipt)
            assert process.returncode==0 and not stderr and not timed_out
            metadata=disassembly.parse_metadata(stdout.decode());by_class={row['className']:row for row in metadata}
            assert set(by_class)=={row['className'] for row in batch}
            for row in batch:
                current=by_class[row['className']];expected={name for name in row['references'] if name.startswith(PREFIX)}
                actual={name for name,_ in current['refs'] if name.startswith(PREFIX)}
                assert actual==expected and current['sourceFile']==row['sourceFile']
                assert sha((directory/row['entry']).read_bytes())==row['sha256']
                independent[row['key']]=dict(path=row['path'],sourceFile=current['sourceFile'],projectClassOwners=sorted(actual))
                selected_main.update(actual & mains.keys())
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    assert sha(normal_path.read_bytes())==subject['inputs']['normal'][1]
    normal=json.loads(normal_path.read_bytes());main_rows=defaultdict(list)
    for name in sorted(selected_main):main_rows[mains[name]['module']].append(name)
    for module,names in sorted(main_rows.items()):
        jar=normal['jars'][module];assert sha(Path(jar['path']).read_bytes())==jar['sha256']
        argv=[str(TC/'jdk-25.0.4/bin/javap'),'-p','-classpath',jar['path']]+[name.replace('/','.') for name in names]
        result=subprocess.run(argv,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120,check=False)
        assert result.returncode==0 and not result.stderr
        # Each -p class declaration is preceded by its exact compiled SourceFile;
        # full CP mapping above uses distinct Main Jar and SourceFile provenance.
        compiled_sources=[line.removeprefix('Compiled from "').removesuffix('"') for line in result.stdout.decode().splitlines() if line.startswith('Compiled from "')]
        assert compiled_sources==[Path(mains[name]['path']).name for name in names]
        receipts.append(dict(command=argv,actualExit=0,stdoutSha256=sha(result.stdout),stderrSha256=sha(result.stderr),rawOutputPersisted=False))
    assert set(independent)=={row['key'] for path in needed for row in by_source[path]}
    # Independent source graph: compare every class CP reference, then collect
    # all finite helper dependencies, never rely on a candidate's cached owners.
    observed={};unproven=[]
    for candidate in candidates:
        stack=[candidate['path']];seen=set();owners=set()
        while stack:
            path=stack.pop()
            if path in seen:continue
            seen.add(path)
            assert path in needed
            for source_class in by_source[path]:
                proof=independent[source_class['key']]
                assert not source_class['reflectiveOrDynamicLookup']
                for name in proof['projectClassOwners']:
                    if name in mains:owners.add(mains[name]['owner']);continue
                    same={row['path'] for row in classes if row['module']==source_class['module'] and row['className']==name}
                    dependencies=same or test_lookup[name]
                    assert len(dependencies)==1
                    dep=next(iter(dependencies))
                    if dep!=path:stack.append(dep)
        if owners!={ORACLE[short(candidate['path'])]}:unproven.append(candidate['path'])
        observed[candidate['path']]=dict(owner=ORACLE[short(candidate['path'])],helperClosure=sorted(seen),verifiedMainOwners=sorted(owners))
    assert not unproven
    verify(invocation);OUT.mkdir();write(OUT/'responsibility-proofs.json',observed)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      subjectManifestSha256=sha(subject_raw),candidatesSha256=subject['candidatesSha256'],literalOwnerTable=ORACLE,
      confirmedCandidates=47,keptUnregistered=291,independentClassMetadata=len(independent),independentMainSourceFiles=len(selected_main),
      verifiedSourceClosure=len(needed),javapFormatVectors=fixture_vectors,receipts=receipts,proofsSha256=sha((OUT/'responsibility-proofs.json').read_bytes()),
      rawOutputPersisted=False,targetRuntimeClassLoading=0,productTestsExecuted=0,newAccepted=0,coverage=None,formalUpdated=False)
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,confirmedCandidates=47,independentClassMetadata=len(independent),mainSources=len(selected_main),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
