"""Static source/resource responsibilities only; never execute SQL, fixtures, services or scripts."""
from collections import Counter,defaultdict
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import explicit_primary_source_metadata as select
import pg9360_static_companion_javap_metadata as jdk
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9422-resource33-source-metadata-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9422-resource33-source-metadata-v1'
TC=ROOT.parent/'toolchain'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
TABLE=[
 ('api','api/database/DatabaseMigrationTest','WBS-P004-01','SQL_ALL'),
 ('api','api/database/MigrationInventory','WBS-P004-01','SQL_ALL'),
 ('api','api/database/NotificationStateMigrationTest','WBS-P004-01','V024'),
 ('api','api/database/QuestionDlqMigrationTest','WBS-P004-01','V025'),
 ('api','api/database/StartupSchemaProjectionTest','WBS-P004-01','V023'),
 ('api','api/logging/MessageStoreCleanupTest','WBS-P004-01','V006'),
 ('api','api/maintenance/BackupRerunBoundaryTest','WBS-P004-01','V017'),
 ('api','api/maintenance/CleanupSafetyBoundaryTest','WBS-P004-01','V013'),
 ('api','api/maintenance/InboxInspectionProgressBoundaryTest','WBS-P004-01','V012'),
 ('api','api/maintenance/InboxMaintenanceBoundaryTest','WBS-P004-01','V010'),
 ('api','api/maintenance/InspectionParentBoundaryTest','WBS-P004-01','V019'),
 ('api','api/maintenance/LogCleanupProgressBoundaryTest','WBS-P004-01','V014'),
 ('api','api/maintenance/OutboxCleanupBoundaryTest','WBS-P004-01','V011'),
 ('api','api/maintenance/RunReferenceBoundaryTest','WBS-P004-01','V018'),
 ('api','api/maintenance/StepCleanupBoundaryTest','WBS-P004-01','V020'),
 ('batch','batch/repository/SuccessProgressSealTest','WBS-P004-01','V028'),
 ('api','api/database/PostgresDeploymentTest','WBS-C03','PG_CONFIG'),
 ('api','api/maintenance/ApplicationServiceUnitTest','WBS-C02','API_WEB_UNITS'),
 ('api','api/maintenance/UnitSyntaxFixture','WBS-C02','ALL_UNITS'),
 ('batch','batch/platform/ArtemisServiceUnitTest','WBS-C02','ARTEMIS_UNIT'),
 ('batch','batch/platform/CleanupServiceUnitTest','WBS-C02','CLEANUP_UNIT'),
 ('batch','batch/platform/MorningServiceUnitTest','WBS-C02','MORNING_UNITS'),
 ('batch','batch/platform/RootServiceUnitTest','WBS-C02','API_WEB_UNITS'),
 ('api','api/maintenance/InspectorDeploymentTest','WBS-C08','INSPECTOR_SCRIPT'),
 ('api','api/messaging/config/ArtemisBrokerConfigurationTest','WBS-C04','BROKER'),
 ('api','api/messaging/config/ArtemisSecurityTest','WBS-C04','BROKER'),
 ('batch','batch/mq/ArtemisExpiryManagementAuthorizationTest','WBS-C04','BROKER'),
 ('batch','batch/bootstrap/BatchRuntimeDependencyTest','WBS-F02','BATCH_POM'),
 ('web','web/bootstrap/WebRuntimeDependencyTest','WBS-F02','WEB_POM'),
 ('web','web/view/LogSearchScriptTest','WBS-P016-25','log-search-validation.js'),
 ('web','web/view/OperationPostScriptTest','WBS-P016-25','operation-post-submit.js'),
 ('web','web/view/QuestionInputScriptTest','WBS-P016-25','question-input-validation.js'),
 ('web','web/view/ScenarioSearchScriptTest','WBS-P016-25','search-speaker-submit.js')]

def source_path(module,name):return 'src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk/'+name+'.java'
PRIMARY={source_path(module,name):owner for module,name,owner,_ in TABLE}
PROFILE={source_path(module,name):profile for module,name,_,profile in TABLE}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def wbs_scope(value,identifier):
    found=[]
    def visit(item):
        if isinstance(item,dict):
            if item.get('id')==identifier:found.append(item)
            for child in item.values():visit(child)
        elif isinstance(item,list):
            for child in item:visit(child)
    visit(value)
    assert len(found)==1;return found[0]

def artifacts(profile,logical):
    unit='src/deployment/systemd/'
    if profile=='SQL_ALL':return sorted(p for p in logical if '/resources/db/' in p and p.endswith('.sql'))
    if profile.startswith('V'):
        result=[p for p in logical if '/db/migration/'+profile+'__' in p];assert len(result)==1;return result
    if profile=='PG_CONFIG':return sorted(p for p in logical if p.startswith('src/deployment/postgresql/'))
    if profile=='ALL_UNITS':return sorted(p for p in logical if logical[p]['owner']=='WBS-C02')
    if profile=='API_WEB_UNITS':return [unit+'schubert-nk-api.service.template',unit+'schubert-nk-web.service.template']
    if profile=='ARTEMIS_UNIT':return [unit+'artemis.service']
    if profile=='CLEANUP_UNIT':return [unit+'schubert-nk-cleanup.service.template']
    if profile=='MORNING_UNITS':return [unit+'schubert-nk-morning-controller.service.template',unit+'schubert-nk-morning.target.template']
    if profile=='INSPECTOR_SCRIPT':return ['src/deployment/operations/inbox-inspector.sh.template',unit+'schubert-nk-inbox-inspector.service','src/deployment/config/inbox-inspector.env.template']
    if profile=='BROKER':return ['src/deployment/artemis/etc/broker.xml']
    if profile in ('BATCH_POM','WEB_POM'):return ['src/schubert-nk-'+('batch' if profile=='BATCH_POM' else 'web')+'/pom.xml']
    if profile.endswith('.js'):return ['src/schubert-nk-web/src/main/resources/static/js/'+profile]
    raise ValueError('closed literal resource profile required')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists() and len(PRIMARY)==len(TABLE)==33
    graph_dir=BASE/'PG9386-composite-reference-graph-v3';graph_raw=(graph_dir/'manifest.json').read_bytes()
    assert sha(graph_raw)=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(graph_raw)
    for name,key in (('unresolved.json','unresolvedSha256'),('test-class-metadata.json','testMetadataSha256')):assert sha((graph_dir/name).read_bytes())==graph[key]
    original=json.loads((graph_dir/'unresolved.json').read_bytes());classes=json.loads((graph_dir/'test-class-metadata.json').read_bytes())
    prior_raw=(BASE/'PG9414-reflective25-source-join-v1/manifest.json').read_bytes();assert sha(prior_raw)=='c9d1ddfbf5a0766430221a57e837278155289d39fe5c2d64b076972345125b46'
    prior=json.loads(prior_raw);known={row['path'] for row in prior['sourceRows']}
    selected=select.exact_selection(original,known,PRIMARY);selection_vectors=select.selection_vectors()
    assert all(row['mainOwners']==[] for row in selected)
    normal_raw=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes();assert sha(normal_raw)=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    normal=json.loads(normal_raw);hashes=normal['begin']['inputHashes']
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());logical={row['path']:row for row in inventory['artifacts']}
    wbs_path=ROOT/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json';wbs=json.loads(wbs_path.read_bytes())
    f02=wbs_scope(wbs,'WBS-F02');assert f02['title']=='JDK/Maven/toolchain・6module build・依存境界'
    candidates=[];witnesses={};by_module=defaultdict(list)
    for row in sorted(selected,key=lambda r:r['path']):
        path=row['path'];primary=PRIMARY[path];profile=PROFILE[path]
        assert row['sha256']==hashes[path]==sha((ROOT/path).read_bytes())
        saved=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'/path;assert sha(saved.read_bytes())==hashes[path]
        current_witnesses=[]
        for artifact in artifacts(profile,logical):
            raw=(ROOT/artifact).read_bytes();assert sha(raw)==hashes[artifact]
            saved_artifact=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'/artifact
            assert sha(saved_artifact.read_bytes())==hashes[artifact]
            if artifact in logical:
                owner=logical[artifact]['owner'];assert owner==logical[artifact]['costOwner'];mode='ORIGINAL941_ARTIFACT_OWNER'
            else:
                assert profile in ('BATCH_POM','WEB_POM') and artifact.endswith('/pom.xml')
                tree=ET.fromstring(raw);ns={'m':'http://maven.apache.org/POM/4.0.0'}
                dependencies=[d for d in tree.findall('m:dependencies/m:dependency',ns) if d.findtext('m:groupId',namespaces=ns)=='org.postgresql' and d.findtext('m:artifactId',namespaces=ns)=='postgresql']
                assert len(dependencies)==1 and dependencies[0].findtext('m:scope',namespaces=ns)=='runtime'
                owner='WBS-F02';mode='EXPLICIT_481_F02_BUILD_DEPENDENCY_SCOPE_NOT_ORIGINAL941_ENTRY'
            witness=dict(path=artifact,sha256=hashes[artifact],owner=owner,basis=mode)
            current_witnesses.append(witness);witnesses[artifact]=witness
        assert current_witnesses and primary in {v['owner'] for v in current_witnesses}
        candidates.append(dict(path=path,sha256=hashes[path],owner=primary,costOwner=primary,profile=profile,
          relatedOwners=sorted({v['owner'] for v in current_witnesses}-{primary}),originalReferenceOwners=[],
          reviewedArtifactWitnesses=current_witnesses,witnessScope='PRIMARY_RESPONSIBILITY_REVIEW_ONLY_NOT_EXHAUSTIVE_DEPENDENCIES',
          unresolvedRuntimeReasons=row['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='EXACT_LITERAL_RESOURCE_SQL_UNIT_JS_BUILD_PRIMARY_1914_NOT_RUNTIME_PT'))
        own=[item for item in classes if item['path']==path];assert own
        for item in own:by_module[item['module']].append(item)
    os.umask(0o077);SLOT.mkdir();receipts=[];proofs={}
    for module,rows in sorted(by_module.items()):
        directory=next(Path(p) for p in graph['treePins'] if '/schubert-nk-'+module+'/' in p)
        for offset in range(0,len(rows),40):
            batch=rows[offset:offset+40]
            argv=[str(TC/'jdk-25.0.4/bin/javap'),'-v','-p','-classpath',str(directory)]+[row['className'].replace('/','.') for row in batch]
            process=subprocess.Popen(argv,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
            write(SLOT/(module+'-'+str(offset)+'-process.safe.json'),dict(pid=process.pid,ownerPid=os.getpid(),command=argv,startUTC=dt.datetime.now(dt.timezone.utc).isoformat()))
            timed_out=False
            try:stdout,stderr=process.communicate(timeout=120)
            except subprocess.TimeoutExpired:timed_out=True;process.kill();stdout,stderr=process.communicate(timeout=15)
            receipt=dict(command=argv,actualExit=process.returncode,timedOut=timed_out,stdoutSha256=sha(stdout),stderrSha256=sha(stderr),rawOutputPersisted=False)
            write(SLOT/(module+'-'+str(offset)+'-exit.safe.json'),receipt);receipts.append(receipt)
            assert process.returncode==0 and not stderr and not timed_out
            parsed={item['className']:item for item in jdk.parse_metadata(stdout.decode())};assert set(parsed)=={row['className'] for row in batch}
            for row in batch:
                item=parsed[row['className']];refs=sorted({name for name,_ in item['refs'] if name.startswith('dev/codex/schubert/nk/')})
                assert item['sourceFile']==row['sourceFile'] and refs==[name for name in row['references'] if name.startswith('dev/codex/schubert/nk/')]
                assert sha((directory/row['entry']).read_bytes())==row['sha256']
                proofs[row['key']]=dict(path=row['path'],className=row['className'],sourceFile=item['sourceFile'],classSha256=row['sha256'],projectClassReferences=refs)
    verify(invocation);OUT.mkdir();write(OUT/'candidates.json',candidates);write(OUT/'artifact-proofs.json',witnesses);write(OUT/'class-proofs.json',proofs)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      graphManifestSha256=sha(graph_raw),normalManifestSha256=sha(normal_raw),priorManifestSha256=sha(prior_raw),wbsSha256=sha(wbs_path.read_bytes()),
      frozenPrimaryOwners=PRIMARY,candidates=33,sourceSelectionVectors=selection_vectors,independentTestClassDeclarations=len(proofs),
      uniqueSourceFiles=33,uniqueArtifactWitnessFiles=len(witnesses),profileCounts=dict(Counter(row['profile'] for row in candidates)),receipts=receipts,
      candidatesSha256=sha((OUT/'candidates.json').read_bytes()),artifactProofsSha256=sha((OUT/'artifact-proofs.json').read_bytes()),
      classProofsSha256=sha((OUT/'class-proofs.json').read_bytes()),primaryWitnessesNotExhaustiveDependencies=True,
      targetCompile=0,targetRuntimeClassLoading=0,productTestsExecuted=0,newAccepted=0,newTestIds=0,newMain=0,coverage=None,formalUpdated=False,effortPercent=None)
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,candidates=33,testClassDeclarations=len(proofs),uniqueArtifactWitnessFiles=len(witnesses),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
