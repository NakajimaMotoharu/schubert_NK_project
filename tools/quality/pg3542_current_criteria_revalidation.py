"""Criterion-level bridge for17 existing acceptances; never grants new leaves."""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from pg1446_current_cold_stage import W
from pg3520_outbox_owned_sources_v2 import SOURCE
from pg3282_wbs_current_source_apply import group_coverage
from pg3390_broker_config_oracle import self_check

ROOT=Path(__file__).resolve().parents[2]
PMO=ROOT/'documents/400_PGPT/470_PMO'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3542-current-criteria-revalidation'
SLOT='pg3542-current-criteria-revalidation-v1'
PREVIOUS='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
LATEST='evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG3356-current-file-media-witness/manifest.json'
WITNESS='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3540-current-common-xml-witness/manifest.json'
MEASUREMENT='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3532-current-native-measurement-v3/manifest.json'
EXPECTED={*[f'WBS-P001-0{i}'for i in range(1,4)],*[f'WBS-P002-0{i}'for i in range(1,5)],
          *[f'WBS-P003-0{i}'for i in range(1,9)],'WBS-F01','WBS-C04'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def read(path):return json.loads(path.read_bytes())


def require(value,message):
    if not value:raise ValueError(message)


def git_file(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT)


def cleanup_only(old,current,path):
    allowed={
      'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/media/MediaApplicationServiceTest.java':'database',
      'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioApplicationServiceTest.java':'database',
      'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/MediaRepositoryTest.java':'database',
      'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/MediaControllerTest.java':'db',
    }
    if old==current:return 'EXACT_BYTES'
    require(path in allowed,'unreviewed Test oracle/input/body change')
    name=allowed[path];before=('    '+name+'.stop();').encode()
    after=('    if ('+name+' != null) '+name+'.stop();').encode()
    require(old.count(before)==1 and old.replace(before,after,1)==current,'only exact reviewed AfterAll guard allowed')
    return 'AFTERALL_NULL_GUARD_ONLY_EXPECTATIONS_INPUT_ASSERTIONS_UNCHANGED'


def prepend_only(old,current,heading):
    header,body=old.split(b'\n\n',1)
    require(current.startswith(header+b'\n\n')and current.endswith(body),'old normative content must remain byte-exact')
    addition=current[len(header)+2:-len(body)]
    require(addition.startswith(heading.encode())and addition.endswith(b'\n\n'),'one explicitly reviewed prepend required')
    require(addition.count(b'\n## ')==0,'no other normative section append')
    return sha(addition)


def revalidate():
    master=read(PMO/'481_PGPT詳細WBS.json');budget=read(PMO/'484_WBSコスト枠・細分化.json')
    inventory=read(PMO/'485_WBS網羅性・受入対応.json');snapshot=read(PMO/'486_WBS現行実績.json')
    accepted={r['id']:r for r in master['tasks']+budget['children']if r['acceptance']['status']=='ACCEPTED'}
    require(set(accepted)==EXPECTED and inventory['source']==snapshot['source']==PREVIOUS,'exact historical17 source required')
    full=read(W/'pg3414-outbox-full-qualified-v1/manifest.safe.json');f=full['result']
    require(full['actualExit']==f['actualExit']==f['FESFlakyNotRun']==f['staticSixModules']==0 and f['productionSource']==SOURCE and(f['tests'],f['suites'],f['mainClasses'])==(3712,545,1643),'current3712 qualification required')
    witness=read(ROOT/WITNESS);latest=read(ROOT/LATEST);measurement=read(ROOT/MEASUREMENT)
    require(witness['productionSource']==SOURCE and witness['wholeManifestSha256']==f['serverManifestSha256']and witness['sourceSnapshot']==f['sourceSnapshot'],'original current witness authority required')
    coverage=group_coverage(measurement)
    for module in ['protocol','storage']:
        require(all(measurement['moduleCounters'][module][k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']),'common entire module four100 required')
    artifacts=inventory['artifacts'];require(len(artifacts)==941,'exact physical ownership941 required')
    changed=[]
    for artifact in artifacts:
        path=artifact['path'];raw=(ROOT/path).read_bytes()
        require(sha(git_file(PREVIOUS,path))==artifact['sha256'],'old inventory must still match genuine old Git blob')
        require(git_file(SOURCE,path)==raw,'current physical artifact must equal qualified Production source')
        if sha(raw)!=artifact['sha256']:changed.append({'path':path,'owner':artifact['owner'],'oldSha256':artifact['sha256'],'newSha256':sha(raw)})
    require(len(changed)==1 and changed[0]['owner']=='WBS-P006-02'and changed[0]['path'].endswith('/OutboxJmsSender.java'),'only independently registered unaccepted Outbox change')
    test_reviews={}
    for path,digest in latest['testSourceHashes'].items():
        old=git_file(latest['sourceSnapshot'],path);require(sha(old)==digest,'original independent oracle Test hash required')
        current=(ROOT/path).read_bytes();require(witness['testSourceHashes'][path]==sha(current),'same actual current Test witness required')
        test_reviews[path]=cleanup_only(old,current,path)
    for module,suites in latest['modules'].items():
        actual={s['class']:s for s in witness['modules'][module]}
        for old in suites:
            require(old['class']in actual and old['counts']==actual[old['class']]['counts'],'all prior corrected oracle suite cases retained and passed')
            require(collections.Counter(old['tests'])==collections.Counter(actual[old['class']]['tests']),'same independently named cases/method ordinal counts required')
    docs={};evidence={};reviews={}
    for rid,row in accepted.items():
        a=row['acceptance'];checks={c['id']for c in row['acceptanceChecks']}
        require(a['source']==PREVIOUS and set(a['criteriaSatisfied'])==checks and len(checks)==3,'historical per-criterion approval complete')
        for dep in row.get('dependencies',[])+row.get('externalDependencies',[])+row.get('children',[]):
            require(dep in accepted,'every exit dependency must be revalidated in this exact group')
        for prerequisite in row.get('externalPrerequisites',[]):
            require(prerequisite in a.get('resolvedPrerequisites',[]),'unresolved external approval')
        for old in a['evidence']:
            require(sha((ROOT/old['path']).read_bytes())==old['sha256']and old['source']==PREVIOUS,'preserved independent historical evidence hash')
            evidence[old['path']]=old['sha256']
        owned=[x for x in artifacts if x['owner']==rid]
        require(len(owned)==len(row['ownedArtifacts']),'all owned scope matched')
        for path in row['evidencePlan']['designFiles']:
            raw=git_file('origin/main',path);require(raw==(ROOT/path).read_bytes(),'canonical design byte agreement required')
            docs[path]=sha(raw)
        for path in row['evidencePlan']['candidateTestFiles']:
            require(path in witness['testSourceHashes'],'all candidate Test files must be actual current XML witness')
        for item in owned:
            require(sha((ROOT/item['path']).read_bytes())==item['sha256'],'accepted owned artifact byte changed')
            if item['kind']=='JAVA':
                counters=coverage[item['module']].get(item['class']);require(counters is not None,'owned family missing from current coverage')
                require(all(v[0]==0 for v in counters.values()),'owned executable family must have four missed0')
        shared=[]
        for reference in row['sharedClassReferences']:
            matches=[a for a in artifacts if a.get('class')==reference]
            require(len(matches)==1,'one physical shared-reference owner required')
            item=matches[0]
            require(item['owner']in accepted and item['costOwner']==item['owner'],'accepted sole cost owner for shared reference required')
            require(sha((ROOT/item['path']).read_bytes())==item['sha256'],'shared class byte changed')
            counter=coverage[item['module']].get(item['class'])
            require(counter is not None and all(v[0]==0 for v in counter.values()),'shared referenced family four100 required')
            shared.append({'class':reference,'path':item['path'],'sha256':item['sha256'],'owner':item['owner'],'referenceCost':0,'fourCountersMissed0':True})
        reviews[rid]={'status':'REVALIDATED','source':SOURCE,'priorSource':PREVIOUS,'verifiedChecks':sorted(checks),
                      'ownedArtifactCount':len(owned),'ownedArtifactSha256':{x['path']:x['sha256']for x in owned},
                      'dependencies':row.get('dependencies',[]),'sharedReferences':shared,'criteria':{c['id']:{'expected':c['expected'],'result':'SATISFIED','basis':['unchanged individually reviewed contract/oracle evidence','complete unchanged owned scope and canonical designs','actual current3712 XML/source and applicable common four100; separately reviewed F01/C04']}for c in row['acceptanceChecks']},
                      'historicalEvidencePaths':[e['path']for e in a['evidence']],'currentTestFiles':row['evidencePlan']['candidateTestFiles'],
                      'formalUpdated':False,'newLeafCredit':0}
    foundation=read(ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3378-foundation-contract/manifest.json')
    for path,digest in foundation['pomSha256'].items():require(sha((ROOT/path).read_bytes())==digest,'all seven POMs unchanged')
    require(len(foundation['pomSha256'])==7,'complete seven POMs')
    foundation_docs={}
    for path,digest in foundation['documentSha256'].items():
        raw=(ROOT/path).read_bytes()
        if sha(raw)!=digest:
            require(path=='documents/400_PGPT/440_判断/441_実装判断記録.md','unreviewed policy document change')
            old=git_file(SOURCE+'^',path);require(sha(old)==digest,'original decision normative hash required')
            foundation_docs[path]={'newSha256':sha(raw),'additionSha256':prepend_only(old,raw,'## PG-D419'),'reason':'BUG1299 internal graph repair only; old policy byte-exact'}
    for path,digest in foundation['canonicalDocumentSha256'].items():
        old=git_file(foundation['canonicalMain'],path);require(sha(old)==digest,'historical canonical design hash required')
        raw=git_file('origin/main',path);require(raw==(ROOT/path).read_bytes(),'current canonical policy agreement')
        if sha(raw)!=digest:
            require(path.endswith('/354_PT・IT試験観点詳細設計.md'),'unreviewed canonical policy change')
            foundation_docs[path]={'newSha256':sha(raw),'additionSha256':prepend_only(old,raw,'## SSC-285'),'reason':'published SSC285 bounded recovery supplements only; all prior quality rules unchanged'}
    reviews['WBS-F01']['specificQuality']={'sevenPomsSame':True,'reviewedMandatoryTopics':foundation['reviewedMandatoryTopics'],'changedDocumentReview':foundation_docs,'F03Accepted':False,'globalFour100Claim':False}
    broker=read(ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3392-broker-config-contract/manifest.json')
    for path,digest in broker['documentSha256'].items():require(sha(git_file('origin/main',path))==digest,'Broker RD/SS unchanged')
    config=ROOT/broker['ownedArtifact'];require(sha(config.read_bytes())==broker['artifactSha256'],'Broker single physical artifact unchanged')
    policy=self_check(config);require(policy==broker['independentPolicy'],'independent Broker policy and mutation negatives unchanged')
    canary=broker['schemaCanary'];private=W/'pg3390-broker-schema-v1'
    require(canary['compileExit']==canary['actualExit']==0 and canary['originalAcceptedBeforeAndAfter']and canary['independentInvalidFourRejected'],'complete existing schema canary success required')
    require(sha((ROOT/'tools/quality/vm/050_s1/ArtemisConfigurationSchemaCanary.java').read_bytes())==canary['sourceSha256'],'independent schema canary source unchanged')
    require(sha((private/'run.private.log').read_bytes())==canary['runLogSha256']and(private/'compile.private.log').read_bytes()==b'','actual unchanged original schema verdict required')
    jar=ROOT.parent/'toolchain/m2/repository/org/apache/artemis/artemis-server/2.56.0/artemis-server-2.56.0.jar'
    with zipfile.ZipFile(jar)as archive:
        for name,digest in canary['officialSchemaSha256'].items():
            require(sha(archive.read('schema/'+name))==sha((private/name).read_bytes())==digest,'same official Artemis schema and independent fixture required')
    suite=next(s for s in witness['modules']['api']if s['class']=='dev.codex.schubert.nk.api.messaging.config.ArtemisBrokerConfigurationTest')
    require(suite['counts']=={'tests':4,'failures':0,'errors':0,'skipped':0},'actual current Broker four XML cases')
    reviews['WBS-C04']['specificQuality']={'nonJavaCoverage':'NOT_APPLICABLE_XML_SCHEMA_POLICY_CONTRACT','policy':policy,'currentOriginalXmlSha256':suite['xmlSha256'],'historicalSchemaCanary':broker['schemaCanary'],'unchangedIndependentSchemaProof':True,'runtimeBrokerStartedByReview':False,'ITSTClaim':False}
    return {'actualExit':0,'productionSource':SOURCE,'previousSource':PREVIOUS,'acceptedIds':sorted(EXPECTED),
            'criteriaRevalidated':sum(len(v['verifiedChecks'])for v in reviews.values()),'rows':reviews,'historicalIndependentEvidence':evidence,
            'canonicalMain':subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip(),'canonicalDesignSha256':docs,
            'onlyPhysicalChange':changed,'testSourceReviews':test_reviews,'newWholeWitness':{'path':WITNESS,'sha256':sha((ROOT/WITNESS).read_bytes())},
            'currentMeasurement':{'path':MEASUREMENT,'sha256':sha((ROOT/MEASUREMENT).read_bytes())},
            'beforeFileHashes':{p.name:sha(p.read_bytes())for p in [PMO/'481_PGPT詳細WBS.json',PMO/'484_WBSコスト枠・細分化.json',PMO/'485_WBS網羅性・受入対応.json',PMO/'486_WBS現行実績.json']},
            'newLeafCredit':0,'formalUpdated':False,'effortCompletionRate':None,'WbsSourceSwitchApplied':False,
            'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}


def main():
    result=revalidate();PUBLIC.mkdir(parents=True)
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'source':SOURCE,'revalidated':len(result['rows']),'criteria':result['criteriaRevalidated'],'changedPhysicalArtifacts':len(result['onlyPhysicalChange']),'newLeafCredit':0,'sourceSwitchApplied':False,'publicManifestSha256':sha((PUBLIC/'manifest.json').read_bytes())}));return 0


if __name__=='__main__':raise SystemExit(main())
