"""Safe provisional collection. Fixed actual exit/source and independent SQL postconditions.
Never exports raw credentials, cookies, sessions, original/Backup contents or DB rows.
"""
import collections,datetime,hashlib,json,pathlib,subprocess
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
TREE=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='d3bba6db6eb9fec13e4847a10541cf337f575731'
OUT=TREE/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG469-parent-log-native-v1'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    assert not OUT.exists()
    assert (WORK/'pg469-six-full-v1.source').read_text().strip()==SOURCE
    assert subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml'],cwd=TREE)==b''
    executions={}
    for stem in ['pg469-parent-observer-v1','pg469-readback-native-v1','pg469-l01-native-v1','pg469-log-outage-native-v1']:
        assert (WORK/(stem+'.exit')).read_text().strip()=='0'
        executions[stem]={'actualExit':0,'started':(WORK/(stem+'.started')).read_text().strip(),'completed':(WORK/(stem+'.completed')).read_text().strip()}
    done=[json.loads(l) for l in (WORK/'pg469-parent-journal-private-v1.jsonl').read_text().splitlines()]
    done=[r for r in done if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf' and r.get('JOB_RESULT')=='done' and r.get('INVOCATION_ID')=='aabcc2c3ef1444a7bb07b3183b220c14' and r.get('JOB_ID')=='162935' and r.get('_PID')=='1' and r.get('_UID')=='0']
    assert len(done)==1 and 1791218060000000<=int(done[0]['_SOURCE_REALTIME_TIMESTAMP'])<=1791219861000000
    readback=(WORK/'pg469-readback-native-v1.private.log').read_text()
    for marker in ['rows361Old351Full14Preserved=true','allPreviousBackupPreserved=true','namespace45Intent0=true','unchangedBusinessTables=19','newReadOnlyMAAndDatabaseScopesReturnedNormally=true']:assert marker in readback
    diag=(WORK/'pg469-parent-diagnostic-v1.txt').read_text()
    for marker in ['SESSION count=1','DIAG mismatch=0','EXITPATH 540 status=2','EXITPATH 542 status=2','EXITPATH 47 status=1','EXITPATH 543 status=1']:assert marker in diag
    assert 'Exception ' not in diag
    l01=json.loads((WORK/'pg469-l01-v1/L01-observed.private.json').read_bytes())
    assert l01['productionSource']==SOURCE and l01['status']=='OBSERVED_NOT_ACCEPTED'
    actions=collections.Counter(l01['databaseActions']);categories=collections.Counter(l01['databaseTypes'])
    assert actions==dict(LOGIN_SUCCEEDED=1,SCENARIO_SEARCHED=1,HTTP_REQUEST_COMPLETED=11)
    assert categories==dict(SECURITY=1,ACTION=1,REQUEST=11)
    normal=json.loads((WORK/'pg469-d3-log-readback-v1.safe.json').read_bytes());assert normal['productionSource']==SOURCE
    assert normal['localEventIdMatchedRows']==337 and normal['missing']==normal['duplicates']==normal['fieldMismatch']==0
    outage=json.loads((WORK/'pg469-log-outage-native-v1.private.log').read_text().strip())
    assert outage['source']==SOURCE and all(outage[k]==5 for k in ['events','http200','blockedErrors','afterSent','afterDbExactOnce']) and outage['dbBeforeRecovery']==0
    assert outage['firewallRestored'] and outage['samePeers'] and not outage['brokerProcessStopped']
    sql="""select json_build_object('scenarioActions',count(*),'matchedCommittedInbox',count(*) filter(where i.processing_state='COMPLETED' and i.request_layout_id='SRCREQ01' and i.correlation_id=a.correlation_id and i.owner_user_id=a.actor_user_id),'uniqueMessages',count(distinct a.message_id),'fixedActionFields',count(*) filter(where a.service='API' and a.category='ACTION' and a.level='INFO' and a.message='SCENARIO_SEARCHED' and a.details->>'layout'='SRCREQ01' and (a.details->>'resultCount')::bigint>=0 and a.details-'layout'-'resultCount'='{}'::jsonb)) from schubert.app_logs a left join schubert.request_inbox i on i.message_id=a.message_id where a.action='SCENARIO_SEARCHED' and a.logged_at>='2026-10-05T17:07:48Z' and a.logged_at<='2026-10-05T17:08:11Z';"""
    ssh=['ssh','-i',str(PRIVATE/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(PRIVATE/'known_hosts'),'ubuntu@127.0.0.1']
    r=subprocess.run(ssh+['sudo -n -u postgres /usr/bin/psql -X -qAt -v ON_ERROR_STOP=1 -d schubert_nk'],input=('begin read only; set local statement_timeout=\'5s\';\n'+sql+'\ncommit;').encode(),capture_output=True,timeout=15)
    assert r.returncode==0
    audit=json.loads(r.stdout);assert audit==dict(scenarioActions=1,matchedCommittedInbox=1,uniqueMessages=1,fixedActionFields=1)
    assert subprocess.check_output(ssh+['sudo -n nft list ruleset'],timeout=10)==b''
    hashes={n:digest(WORK/n) for n in ['pg469-parent-journal-private-v1.jsonl','pg469-parent-native-v1.exec','pg469-readback-native-v1.private.log','pg469-readback-oracle-v1.private.log','pg469-l01-v1/L01-observed.private.json','pg469-log-outage-native-v1.private.log','pg469-log-outage-oracle-v1.log']}
    tools={p.name:digest(p) for p in (TREE/'tools/quality/vm/050_s1').glob('pg469_*') if p.is_file()}
    for n in ['Pg469CompletedReadback.java','Pg469CompletedReadbackTest.java']:tools[n]=digest(TREE/'tools/quality/vm/050_s1'/n)
    manifest={'schema':1,'classification':'PROVISIONAL_NATIVE_NOT_FORMAL','created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','productionSource':SOURCE,'toolsBaseHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=TREE,text=True).strip(),'toolsDirtyAtExecution':True,'release':'PG469','manifestSha256':'cc5e4dd7ca70d3a21e1145dd35b9f047856c4ab83bfac6f11722663ba7744462','environment':{'guest':'Ubuntu26.04','JDK':'25.0.4','PostgreSQL':'18.6'},'executions':executions,'parent':{'invocation':'aabcc2c3ef1444a7bb07b3183b220c14','job':162935,'pid1DoneMicros':done[0]['_SOURCE_REALTIME_TIMESTAMP'],'rows':361,'oldFull14RowsPreserved':351,'startupEntries':45,'oldStartupByteMetadataPreserved':40,'intent':0,'unchangedBusinessTables':19,'allBackupPreserved':True,'allNewOwnedScopesReturned':True},'nativeCoverage':{'singleParentSession':True,'sameFrozenSixModuleBytes':True,'noMatch':0,'partialLines':[47,543],'qualified100':False,'ordinaryWebAgent':False},'chrA01':{'actualExit':0,'approvedDIF':'001','artifactSha256':digest(TREE/'program/characterization/reports/nk/PG469-native-a01-v1/artifacts/CHR-A01.json')},'l01':{'status':'OBSERVED_NOT_ACCEPTED','QA':'QA-051','actionCounts':dict(actions),'categoryCounts':dict(categories),'displayedRows':l01['displayedRows'],'detailsElements':l01['detailsElements'],'auditInboxPostconditions':audit,'sqlActualExit':r.returncode,'sqlSha256':hashlib.sha256(sql.encode()).hexdigest(),'earlierDraftSqlExit':3,'earlierDraftSqlNotPassed':True},'webLocalProjection':normal,'webBrokerLinkOutage':outage,'independentToolAssertions':{'readback':374,'projectionNegative':17,'outage':102},'privateHashes':hashes,'toolsSha256':tools,'BUG':['BUG-742','BUG-749','BUG-750'],'YKT':['YKT-523','YKT-527','YKT-530'],'SSC':['SSC-190','SSC-191'],'rawSecretExported':False,'fullProductionRegression':{'source':SOURCE,'passed':3301,'suites':489,'failed':0,'errors':0,'skipped':0,'staticModulesZero':6,'existingSafeManifestSha256':digest(TREE/'evidence/01_PT/008_NK-SCN-001/evidence/provisional/PG469-scenario-audit-full/manifest.json')},'formal':{'unchanged':True,'run':'PT-WEB-20260925-24','productionPTCount':1964,'scopes':53},'notAccepted':['allCHR','BrokerProcessStop','ApiProcessStop','allNativeCoverage100','allPGPT','ITST']}
    OUT.mkdir(parents=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'manifestSha256':digest(OUT/'manifest.json'),'source':SOURCE,'formalUpdated':False,'rawExported':False}))
if __name__=='__main__':main()
