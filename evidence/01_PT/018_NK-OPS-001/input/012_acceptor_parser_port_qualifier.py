"""Reusable owned host port qualification. Business backend operations excluded; SDK metadata activity reviewed separately."""
from pathlib import Path
import sys,os,json,hashlib,subprocess,datetime,zipfile,re,shutil
import xml.etree.ElementTree as E
import pg9666_pagination_static as r
root=Path.cwd();runs=root.parent/'pgpt-runs/PG379';tc=root.parent/'toolchain';jdk=tc/'jdk-25.0.4/bin';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();phase=sys.argv[1];profile=sys.argv[2];external=profile.endswith('.json');assert phase in {'prepare','static','run','post'} and (external or profile in {'range','verified','audit','receipt','login_audit','login_attempt','inbound','snapshot','run_reference','metadata','expiry','backup','batch_run','cleanup_step','cleanup_query','inspection_summary','pressure','topology','acceptor'})
loginFailureExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/097_login_failure_http.json'
outboxJdbcExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/096_outbox_jdbc.json'
stateParserExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/089_unit_state_parser_bytes.json'
authVerifierExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/090_authentication_verifier_jdbc.json'
adminPreludeExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/091_admin_prelude_jdbc.json'
sessionIssueExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/092_session_issue_jdbc.json'
sessionRevocationExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/093_session_revocation_jdbc.json'
javaStaticCrossSource=stateParserExternal or authVerifierExternal or adminPreludeExternal or sessionIssueExternal or sessionRevocationExternal
errorRestoreExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/080_error_dispatch_restore.json'
routerExternal=external and profile in {'evidence/01_PT/018_NK-OPS-001/input/077_internal_error_router.json','evidence/01_PT/018_NK-OPS-001/input/078_internal_error_router_style.json'}
securityAuditExternal=external and profile in {'evidence/01_PT/018_NK-OPS-001/input/072_web_security_audit.json','evidence/01_PT/018_NK-OPS-001/input/073_web_security_audit_style.json','evidence/01_PT/018_NK-OPS-001/input/074_web_security_audit_logger.json'}
csrfExternal=external and profile in {'evidence/01_PT/018_NK-OPS-001/input/069_form_csrf_request.json','evidence/01_PT/018_NK-OPS-001/input/070_form_csrf_request_style.json'}
formExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/068_login_form_converter.json'
sessionExternal=external and profile=='evidence/01_PT/018_NK-OPS-001/input/067_web_session_snapshot.json'
requestExternal=external and profile in {'evidence/01_PT/018_NK-OPS-001/input/064_question_submit_request.json','evidence/01_PT/018_NK-OPS-001/input/065_question_submit_request_style.json','evidence/01_PT/018_NK-OPS-001/input/066_question_submit_request_boundary_style.json'}
observationExternal=external and profile in {'evidence/01_PT/018_NK-OPS-001/input/052_api_observation_publication.json','evidence/01_PT/018_NK-OPS-001/input/053_api_observation_publication_style.json'}
viewProfiles={
 'evidence/01_PT/018_NK-OPS-001/input/063_question_list_projection_style.json':('QuestionListViewModel','QuestionListProjectionPortTest'),
 'evidence/01_PT/018_NK-OPS-001/input/062_question_list_projection.json':('QuestionListViewModel','QuestionListProjectionPortTest'),
 'evidence/01_PT/018_NK-OPS-001/input/054_question_detail_projection.json':('QuestionDetailViewModel','QuestionDetailProjectionPortTest'),
 'evidence/01_PT/018_NK-OPS-001/input/055_question_detail_projection_style.json':('QuestionDetailViewModel','QuestionDetailProjectionPortTest'),
 'evidence/01_PT/018_NK-OPS-001/input/056_notification_detail_projection.json':('NotificationDetailViewModel','NotificationDetailProjectionPortTest'),
 'evidence/01_PT/018_NK-OPS-001/input/057_notification_detail_projection_style.json':('NotificationDetailViewModel','NotificationDetailProjectionPortTest'),
 'evidence/01_PT/018_NK-OPS-001/input/059_notification_list_projection.json':('NotificationListViewModel','NotificationListProjectionPortTest'),
 'evidence/01_PT/018_NK-OPS-001/input/060_notification_list_projection_frozen.json':('NotificationListViewModel','NotificationListProjectionPortTest'),
 'evidence/01_PT/018_NK-OPS-001/input/061_notification_list_projection_fixture.json':('NotificationListViewModel','NotificationListProjectionPortTest')}
viewExternal=external and profile in viewProfiles
if external:
 assert loginFailureExternal or outboxJdbcExternal or sessionRevocationExternal or sessionIssueExternal or adminPreludeExternal or authVerifierExternal or stateParserExternal or errorRestoreExternal or routerExternal or securityAuditExternal or csrfExternal or formExternal or sessionExternal or requestExternal or viewExternal or observationExternal or re.fullmatch(r'evidence/01_PT/017_NK-BAT-001/input/[0-9]{3}_log_transaction_[a-z]+\.json',profile)
 externalCfg=json.loads((root/profile).read_text())
 assert externalCfg['preflightDecision']=='PT_DEFAULT' and externalCfg['actualBackendActions']==0
 if loginFailureExternal:
  assert externalCfg['module']=='web' and externalCfg['main']=='MqLoginFailureHandler' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['MqLoginFailurePortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==6
 elif outboxJdbcExternal:
  assert externalCfg['module']=='api' and externalCfg['main']=='JdbcOutboxRepository' and externalCfg['mainPackage']=='messaging/outbound'
  assert externalCfg['tests']==['JdbcOutboxPortTest','OutboxReturningIdContractTest'] and externalCfg['testPackages']==['messaging/outbound','messaging/outbound']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==9
 elif sessionRevocationExternal:
  assert externalCfg['module']=='api' and externalCfg['main']=='AuthSessionRevocationService' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['SessionRevocationJdbcPortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==8
 elif sessionIssueExternal:
  assert externalCfg['module']=='api' and externalCfg['main']=='AuthSessionService' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['SessionIssueJdbcPortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==8
 elif adminPreludeExternal:
  assert externalCfg['module']=='api' and externalCfg['main']=='AdminCommandAuthenticator' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['AdminPreludeJdbcPortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==2 and externalCfg['abstract']==0 and externalCfg['expected']==8
 elif authVerifierExternal:
  assert externalCfg['module']=='api' and externalCfg['main']=='AuthenticationContextVerifier' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['AuthenticationVerifierJdbcPortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==2 and externalCfg['abstract']==0 and externalCfg['expected']==6
 elif stateParserExternal:
  assert externalCfg['module']=='batch' and externalCfg['main']=='UnitStateParser' and externalCfg['mainPackage']=='platform'
  assert externalCfg['tests']==['UnitStateParserBytePortTest'] and externalCfg['testPackages']==['platform']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==6
 elif viewExternal:
  assert externalCfg['module']=='web' and externalCfg['main']==viewProfiles[profile][0] and externalCfg['mainPackage']=='view'
  assert externalCfg['tests']==[viewProfiles[profile][1]] and externalCfg['testPackages']==['view']
  assert externalCfg['abstract']==0
  assert (externalCfg['physical'],externalCfg['expected'],externalCfg['syntheticNoCode'])==((1,16,[]) if externalCfg['main']=='QuestionListViewModel' else (2,14 if externalCfg['main']=='NotificationListViewModel' else 8,['dev/codex/schubert/nk/web/view/'+viewProfiles[profile][0]+'$1']))
 elif errorRestoreExternal:
  assert externalCfg['module']=='web' and externalCfg['main']=='WebErrorDispatchFilter' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['ErrorDispatchRestorePortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==8
 elif routerExternal:
  assert externalCfg['module']=='web' and externalCfg['main']=='InternalErrorDispatchRouter' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['InternalErrorRouterPortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==10
 elif securityAuditExternal:
  assert externalCfg['module']=='web' and externalCfg['main']=='WebSecurityAudit' and externalCfg['mainPackage']=='logging'
  assert externalCfg['tests']==['WebSecurityAuditPortTest'] and externalCfg['testPackages']==['logging']
  assert externalCfg['physical']==3 and externalCfg['abstract']==0 and externalCfg['expected']==10
 elif csrfExternal:
  assert externalCfg['module']=='web' and externalCfg['main']=='FormCsrfTokenRequestHandler' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['FormCsrfRequestPortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==9
 elif formExternal:
  assert externalCfg['module']=='web' and externalCfg['main']=='LoginFormAuthenticationConverter' and externalCfg['mainPackage']=='security'
  assert externalCfg['tests']==['LoginFormConverterPortTest'] and externalCfg['testPackages']==['security']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==13
 elif sessionExternal:
  assert externalCfg['module']=='web' and externalCfg['main']=='WebSessionSnapshot' and externalCfg['mainPackage']=='session'
  assert externalCfg['tests']==['WebSessionSnapshotPortTest'] and externalCfg['testPackages']==['session']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==8
 elif requestExternal:
  assert externalCfg['module']=='api' and externalCfg['main']=='QuestionSubmitRequest' and externalCfg['mainPackage']=='application/question'
  assert externalCfg['tests']==['QuestionSubmitRequestPortTest'] and externalCfg['testPackages']==['application/question']
  assert externalCfg['physical']==1 and externalCfg['abstract']==0 and externalCfg['expected']==8
 elif observationExternal:
  assert externalCfg['module']=='api' and externalCfg['main']=='ApiOutboxObservationSource' and externalCfg['mainPackage']=='monitoring'
  assert externalCfg['tests']==['ApiOutboxPublicationPortTest'] and externalCfg['testPackages']==['monitoring']
  assert externalCfg['physical']==2 and externalCfg['abstract']==0 and externalCfg['expected']==8
 else:
  assert externalCfg['module']=='batch' and externalCfg['main']=='LogCleanupService' and externalCfg['mainPackage']=='cleanup'
  assert externalCfg['tests']==['LogCleanupTransactionPortTest'] and externalCfg['testPackages']==['cleanup']
  assert externalCfg['physical']==5 and externalCfg['abstract']==2 and externalCfg['expected']==19
 assert re.fullmatch('[0-9a-f]{40}',externalCfg['coreSource'])
 for key in ['normalCompileSlot','sixStaticSlot','prepare','static','unit']:
  assert re.fullmatch(r'pg[0-9]+-[a-z0-9-]+-v[0-9]+',externalCfg[key])
cfg={
 'acceptor':dict(module='batch',program='018_NK-OPS-001',main='ArtemisAcceptorReadinessClient',mainPackage='mq',tests=['AcceptorObjectBoundaryTest','AcceptorPolicyPortTest'],testPackages=['mq','mq'],prepare='pg19292-mq-acceptor-port-compile-v1',static='pg19294-mq-acceptor-port-static-v1',unit='pg19298-mq-acceptor-port-fifteen-unit-v1',public='PG19298-mq-acceptor-port-fifteen-v1',physical=2,abstract=1,expected=15,session='PG19298-MQ-ACCEPTOR-PORT-15',sdkReview='evidence/01_PT/018_NK-OPS-001/input/011_acceptor_parser_port_sdk_review.json',sdkReviewSha256='658d8823beb8001ade2a83418d7f787ab53cc63267c50782bf7e6d3484b480ec',resourceScopeNote='MemoryJSON fixture; SDK may read classpath services/default JVM properties. Business backend operation count0, not globalSDK syscall0'),
 'topology':dict(module='batch',program='018_NK-OPS-001',main='ArtemisReadinessClient',mainPackage='mq',tests=['TopologyQueryPortTest'],testPackages=['mq'],prepare='pg19210-mq-topology-port-compile-v1',static='pg19212-mq-topology-port-static-v1',unit='pg19218-mq-topology-port-six-unit-v1',public='PG19218-mq-topology-port-six-v1',physical=1,abstract=0,expected=6,session='PG19218-MQ-TOPOLOGY-PORT-6',sdkReview='evidence/01_PT/018_NK-OPS-001/input/004_mq_topology_sdk_static_review.json',sdkReviewSha256='78c04314faae4343166bc69d434ea5584294df09e5ce175d10df4aebda32c50e'),
 'pressure':dict(module='batch',program='018_NK-OPS-001',main='ArtemisQueuePressureClient',mainPackage='mq',tests=['QueuePressurePolicyTest'],testPackages=['mq'],prepare='pg19180-mq-pressure-port-compile-v1',static='pg19182-mq-pressure-port-static-v1',unit='pg19178-mq-pressure-port-six-unit-v1',public='PG19178-mq-pressure-port-six-v1',physical=5,abstract=1,expected=6,session='PG19178-MQ-PRESSURE-PORT-6',sdkReview='evidence/01_PT/018_NK-OPS-001/input/001_mq_pressure_sdk_static_review.json',sdkReviewSha256='ad4b2e32bd9a784eedca09b804dac58a12d1e21b2da1b1978b733de7d8782eb6'),
 'inspection_summary':dict(module='batch',program='017_NK-BAT-001',main='InspectionSummaryRepository',mainPackage='repository',tests=['InspectionSummaryPortTest'],testPackages=['repository'],prepare='pg19140-inspection-summary-port-compile-v1',static='pg19142-inspection-summary-port-static-v1',unit='pg19148-inspection-summary-port-eight-unit-v1',public='PG19148-inspection-summary-port-eight-v1',physical=1,abstract=0,expected=8,session='PG19148-INSPECTION-SUMMARY-PORT-8'),
 'cleanup_query':dict(module='batch',program='017_NK-BAT-001',main='CleanupRepository',mainPackage='repository',tests=['CleanupQueryPortTest'],testPackages=['repository'],prepare='pg19120-cleanup-query-port-compile-v1',static='pg19122-cleanup-query-port-static-v1',unit='pg19128-cleanup-query-port-nine-unit-v1',public='PG19128-cleanup-query-port-nine-v1',physical=2,abstract=0,syntheticNoCode=['dev/codex/schubert/nk/batch/repository/CleanupRepository$1'],expected=9,session='PG19128-CLEANUP-QUERY-PORT-9'),
 'cleanup_step':dict(module='batch',program='017_NK-BAT-001',main='CleanupStepRepository',mainPackage='repository',tests=['CleanupStepPortTest'],testPackages=['repository'],prepare='pg19100-cleanup-step-port-compile-v1',static='pg19102-cleanup-step-port-static-v1',unit='pg19108-cleanup-step-port-nine-unit-v1',public='PG19108-cleanup-step-port-nine-v1',physical=1,abstract=0,expected=9,session='PG19108-CLEANUP-STEP-PORT-9'),
 'batch_run':dict(module='batch',program='017_NK-BAT-001',main='BatchRunRepository',mainPackage='repository',tests=['BatchRunAuditPortTest'],testPackages=['repository'],prepare='pg19080-batch-run-audit-compile-v1',static='pg19082-batch-run-audit-static-v1',unit='pg19088-batch-run-audit-fourteen-unit-v1',public='PG19088-batch-run-audit-fourteen-v1',physical=2,abstract=0,expected=14,session='PG19088-BATCH-RUN-AUDIT-14'),
 'backup':dict(module='batch',program='017_NK-BAT-001',main='BackupStepRepository',mainPackage='repository',tests=['BackupTerminalObservationTest','BackupPairPortTest'],testPackages=['repository','repository'],prepare='pg19048-backup-pair-port-compile-v1',static='pg19050-backup-pair-port-static-v1',unit='pg19052-backup-pair-thirteen-unit-v1',public='PG19052-backup-pair-thirteen-v1',physical=2,abstract=0,expected=13,session='PG19052-BACKUP-PAIR-PORT-13'),
 'range':dict(main='MediaRangeService',tests=['MediaRangePortTest'],prepare='pg18794-media-range-port-compile-v1',static='pg18796-media-range-port-static-v1',unit='pg18802-media-range-port-eight-unit-v1',public='PG18802-media-range-port-eight-v1',physical=4,abstract=3,session='PG18802-MEDIA-RANGE-PORT-8'),
 'verified':dict(main='MediaResponseDecoder',tests=['MediaResponseDecoderTest','MediaVerifiedProjectionTest'],prepare='pg18808-media-verified-projection-compile-v1',static='pg18810-media-verified-projection-static-v1',unit='pg18814-media-verified-projection-eight-unit-v1',public='PG18814-media-verified-projection-eight-v1',physical=3,abstract=0,session='PG18814-MEDIA-VERIFIED-PROJECTION-8'),
 'audit':dict(program='015_NK-WEB-001',main='WebSecurityAudit',mainPackage='logging',additionalMain=['security/CaddyTransportContextFilter'],tests=['WebSecurityAuditTest','CaddyTransportPortTest'],testPackages=['logging','security'],prepare='pg18838-web-transport-audit-compile-v1',static='pg18840-web-transport-audit-static-v1',unit='pg18844-web-transport-audit-eleven-unit-v1',public='PG18844-web-transport-audit-eleven-v1',physical=4,abstract=0,expected=11,session='PG18844-WEB-TRANSPORT-AUDIT-11'),
 'expiry':dict(module='batch',program='017_NK-BAT-001',main='ExpiryAuditRepository',mainPackage='repository',tests=['ExpirySuccessfulScopeTest','ExpiryAuditPredicateContractTest','ExpiryAuditPortTest'],testPackages=['repository','repository','repository'],formatNewTests=2,prepare='pg19020-expiry-audit-port-compile-v1',static='pg19022-expiry-audit-port-static-v1',unit='pg19028-expiry-audit-port-thirtyeight-unit-v1',public='PG19028-expiry-audit-port-thirtyeight-v1',physical=7,abstract=3,expected=38,session='PG19028-EXPIRY-AUDIT-PORT-38'),
 'metadata':dict(module='api',program='011_NK-QST-001',main='QuestionCommandMetadata',mainPackage='application/question',tests=['QuestionCommandTimeBoundaryTest','QuestionCommandMetadataContractTest'],testPackages=['application/question','application/question'],prepare='pg19000-command-metadata-compile-v1',static='pg19002-command-metadata-static-v1',unit='pg19008-command-metadata-five-unit-v1',public='PG19008-command-metadata-five-v1',physical=1,abstract=0,expected=5,session='PG19008-COMMAND-METADATA-5'),
 'run_reference':dict(module='batch',program='017_NK-BAT-001',main='RunReferenceRepository',mainPackage='repository',tests=['RunReferencePortTest'],testPackages=['repository'],prepare='pg18980-run-reference-port-compile-v1',static='pg18982-run-reference-port-static-v1',unit='pg18984-run-reference-port-eight-unit-v1',public='PG18984-run-reference-port-eight-v1',physical=1,abstract=0,expected=8,session='PG18984-RUN-REFERENCE-PORT-8'),
 'snapshot':dict(module='api',program='008_NK-SCN-001',main='ScenarioDetailSnapshot',mainPackage='persistence',tests=['ScenarioDetailSnapshotBoundaryTest','ScenarioSnapshotShapeTest'],testPackages=['persistence','persistence'],prepare='pg18960-scenario-snapshot-shape-compile-v1',static='pg18958-scenario-snapshot-shape-static-v1',unit='pg18964-scenario-snapshot-shape-six-unit-v1',public='PG18964-scenario-snapshot-shape-six-v1',physical=1,abstract=0,expected=6,session='PG18964-SCENARIO-SNAPSHOT-SHAPE-6'),
 'inbound':dict(module='api',program='005_NK-MSG-001',main='InboundTransactions',mainPackage='messaging/inbound',tests=['InboundTransactionsPrimaryContractTest','InboundTransactionPortTest'],testPackages=['messaging/inbound','messaging/inbound'],prepare='pg18940-inbound-transaction-port-compile-v1',static='pg18942-inbound-transaction-port-static-v1',unit='pg18948-inbound-transaction-port-eleven-unit-v1',public='PG18948-inbound-transaction-port-eleven-v1',physical=1,abstract=0,expected=11,session='PG18948-INBOUND-TRANSACTION-PORT-11'),
 'login_attempt':dict(module='api',program='007_NK-AUT-001',main='LoginAttemptRepository',mainPackage='security',tests=['LoginAttemptPortTest'],testPackages=['security'],prepare='pg18924-login-attempt-port-compile-v1',static='pg18926-login-attempt-port-static-v1',unit='pg18932-login-attempt-port-ten-unit-v1',public='PG18932-login-attempt-port-ten-v1',physical=1,abstract=0,expected=10,session='PG18932-LOGIN-ATTEMPT-PORT-10'),
 'login_audit':dict(module='api',program='007_NK-AUT-001',main='LoginAuditWriter',mainPackage='security',tests=['LoginAuditPortTest'],testPackages=['security'],prepare='pg18900-login-audit-port-compile-v1',static='pg18898-login-audit-port-static-v1',unit='pg18904-login-audit-port-seven-unit-v1',public='PG18904-login-audit-port-seven-v1',physical=1,abstract=0,expected=7,session='PG18904-LOGIN-AUDIT-PORT-7'),
 'receipt':dict(program='016_NK-WEB-002',main='ReceiptReferenceRepository',mainPackage='receipt',tests=['ReceiptReferencePortTest'],testPackages=['receipt'],prepare='pg18884-receipt-jdbc-port-compile-v1',static='pg18886-receipt-jdbc-port-static-v1',unit='pg18888-receipt-jdbc-port-nine-unit-v1',public='PG18888-receipt-jdbc-port-nine-v1',physical=2,abstract=1,expected=9,session='PG18888-RECEIPT-JDBC-PORT-9')
}[profile] if not external else externalCfg
module=cfg.get('module','web');mainNames=[cfg.get('mainPackage','media')+'/'+cfg['main'],*cfg.get('additionalMain',[])];mains=['src/schubert-nk-'+module+'/src/main/java/dev/codex/schubert/nk/'+module+'/'+n+'.java' for n in mainNames];main=mains[0];testPackages=cfg.get('testPackages',['media']*len(cfg['tests']));tests=['src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk/'+module+'/'+pkg+'/'+n+'.java' for n,pkg in zip(cfg['tests'],testPackages)];selected=['dev.codex.schubert.nk.'+module+'.'+pkg.replace('/','.')+'.'+n for n,pkg in zip(cfg['tests'],testPackages)];expectedCount=cfg.get('expected',8);core=cfg.get('coreSource','7d2c2fb64711531db8898d49b4b377670b58ff87');comp=runs/cfg.get('normalCompileSlot','pg19270-acceptor-parser-six-main-compile-v1');base=json.loads((comp/'manifest.safe.json').read_text());assert base['actualExit']==0 and base['source']==core
if javaStaticCrossSource:assert sha(comp/'manifest.safe.json')==cfg['normalCompileManifestSha256']
for n,h in base['begin']['inputHashes'].items():assert sha(root/n)==h
for j in base['jars'].values():assert sha(j['path'])==j['sha256']
console=tc/'junit-platform-console-standalone-1.13.4.jar';assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892';deps=[Path(base['jars'][n]['path']) for n in ['protocol',module]]
if external:
 if not loginFailureExternal and not outboxJdbcExternal and not observationExternal and not viewExternal and not requestExternal and not sessionExternal and not formExternal and not csrfExternal and not securityAuditExternal and not routerExternal and not errorRestoreExternal and not stateParserExternal and not authVerifierExternal and not adminPreludeExternal and not sessionIssueExternal and not sessionRevocationExternal:deps.append(Path(base['jars']['bootstrap']['path']))
 deps.append(tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar')
 if loginFailureExternal or securityAuditExternal or sessionIssueExternal or sessionRevocationExternal:
  assert len(cfg['gsonDependencies'])==2
  for name,h in cfg['gsonDependencies'].items():
   assert '/toolchain/m2/repository/' in name and any(v in name for v in ['/gson/2.14.0/','/error_prone_annotations/2.50.0/']) and sha(name)==h;deps.append(Path(name))
 if loginFailureExternal or formExternal or csrfExternal or routerExternal or errorRestoreExternal:
  assert len(cfg['converterDependencies'])==6
  for name,h in cfg['converterDependencies'].items():
   assert '/toolchain/m2/repository/' in name and any(v in name for v in ['/commons-logging/1.4.0/','/spring-core/7.0.9/','/spring-web/7.0.9/','/jakarta.servlet-api/6.1.0/','/spring-security-core/7.1.1/','/spring-security-web/7.1.1/']) and sha(name)==h;deps.append(Path(name))
 if observationExternal:
  dependency=tc/'m2/repository/io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar';assert sha(dependency)==cfg['micrometerCoreSha256'];deps.append(dependency)
 if viewExternal and cfg['main'] in {'NotificationListViewModel','QuestionListViewModel'}:
  reference=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13218-spotbugs-fresh-aux-plan-recovery-v1/manifest.json';assert sha(reference)=='a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564';aux=json.loads(reference.read_text())['auxiliaryClasspathHashes']
  assert len(cfg['uriLibraryDependencies'])==3 and all('/toolchain/m2/repository/' in name and any(v in name for v in ['/spring-core/7.0.9/','/spring-web/7.0.9/','/commons-logging/1.4.0/']) for name in cfg['uriLibraryDependencies'])
  for name,h in cfg['uriLibraryDependencies'].items():assert aux[name]==h==sha(name);deps.append(Path(name))

if profile in {'inbound','pressure','topology','acceptor'}:
 sdkManifest=root/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18622-dlq-sender-unit-v1/manifest.json';assert sha(sdkManifest)=='e643b92d0553c4b0b76413381d39d7cf6e2cf6509510ab0798492300eafb6404';sdkPrior=json.loads(sdkManifest.read_text());sdkDeps=sdkPrior['inputProvenance']['sdkDependencies'];assert all(sha(f)==h for f,h in sdkDeps.items());deps.extend([tc/'m2/repository/jakarta/jms/jakarta.jms-api/3.1.0/jakarta.jms-api-3.1.0.jar',*map(Path,sdkDeps)])
if profile in {'expiry','pressure'}:deps.extend([Path(base['jars']['bootstrap']['path']),tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar'])
if profile in {'topology','acceptor'}:deps.append(tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar')
if profile=='login_audit':deps.extend([tc/'m2/repository/com/google/code/gson/gson/2.14.0/gson-2.14.0.jar',tc/'m2/repository/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar'])
if profile=='verified':deps.append(tc/'m2/repository/jakarta/jms/jakarta.jms-api/3.1.0/jakarta.jms-api-3.1.0.jar')
if profile=='audit':deps.extend([tc/'m2/repository/jakarta/servlet/jakarta.servlet-api/6.1.0/jakarta.servlet-api-6.1.0.jar',tc/'m2/repository/com/google/code/gson/gson/2.14.0/gson-2.14.0.jar',tc/'m2/repository/com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar',tc/'m2/repository/org/springframework/security/spring-security-core/7.1.1/spring-security-core-7.1.1.jar'])
if profile in {'pressure','topology','acceptor'}:
 assert sha(root/cfg['sdkReview'])==cfg['sdkReviewSha256'];sdkReview=json.loads((root/cfg['sdkReview']).read_text());assert sdkReview['decision']=='STATIC_PASS_BEFORE_ANY_FIXTURE_OR_PRODUCT_RUN'
assert all(p.is_file() for p in deps);classpath=os.pathsep.join(map(str,[*deps,console]));prepared=runs/cfg['prepare'];cfgHash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
if sessionRevocationExternal:
 # BUG2364/YKT2109: expected values come from immutable approved design, never
 # from a Product enum/method or the observed failed run's actual value.
 oracleRelative='evidence/01_PT/007_NK-AUT-001/input/016_revocation_expected_code_oracle.json'
 assert cfg['expectedCodeOracle']==oracleRelative and sha(root/oracleRelative)==cfg['expectedCodeOracleSha256']
 codeOracle=json.loads((root/oracleRelative).read_text());assert codeOracle['designSource']=='8deb209723494008cad46b6649194a3b7b30e0da'
 assert codeOracle['subjectExpected']==dict(freshLogout='0000',alreadyRevoked='0200',expired='0102')
 for name,binding in codeOracle['designDocuments'].items():
  assert name.startswith(('documents/200_UI/230_インターフェース/','documents/300_SS/350_運用・品質/')) and '..' not in Path(name).parts and name.endswith('.md')
  blob=subprocess.check_output(['git','show',codeOracle['designSource']+':'+name]);assert hashlib.sha256(blob).hexdigest()==binding['sha256']
  lines=blob.decode().splitlines()
  for row in binding['selectedLines']:assert lines[row['line']-1]==row['text']
 assert '0200' in codeOracle['approvedCodes'] and '0001' not in codeOracle['approvedCodes']
 expectedLiterals=set(re.findall(r'"([0-9]{4})"',(root/tests[0]).read_text().replace('\\"','"')))
 assert expectedLiterals<=set(codeOracle['approvedCodes']),sorted(expectedLiterals-set(codeOracle['approvedCodes']))
 if phase in {'run','post'}:assert hashlib.sha256(subprocess.check_output(['git','show',sys.argv[3]+':'+oracleRelative])).hexdigest()==cfg['expectedCodeOracleSha256']
if phase=='prepare':
 slot=prepared;assert not slot.exists();slot.mkdir();r.SLOT=slot;stages={};formatNew=cfg.get('formatNewTests',1);assert 1<=formatNew<=len(tests);oldTestHashes={n:sha(root/n) for n in tests[:-formatNew]};stages['format']=r.step('format',[str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),*(['--dry-run','--set-exit-if-changed'] if cfg.get('formatFrozen',False) else ['--replace']),*[str(root/n) for n in tests[-formatNew:]]],root);assert stages['format']['actualExit']==0
 inputs={n:sha(root/n) for n in [*mains,*tests]};classes=slot/'test-classes';classes.mkdir();stages['test-compile']=r.step('test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',classpath,'-d',str(classes),*[str(root/n) for n in tests]],root)
 assert all(sha(root/n)==h for n,h in oldTestHashes.items());value={'actualExit':stages['test-compile']['actualExit'],'source':core,'gitHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'testUncommitted':True,'inputHashes':inputs,'normalCompileManifest':{'path':str(comp/'manifest.safe.json'),'sha256':sha(comp/'manifest.safe.json')},'normalMainInputCount':len(base['begin']['inputHashes']),'jars':{str(p):sha(p) for p in deps},'consoleSha256':sha(console),'classpath':classpath,'stages':stages,'classHashes':{str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')},'testExecution':False,'actualBackendOperations':0,'profile':profile,'configHash':cfgHash,'driverSha256':sha(__file__)};(slot/'manifest.safe.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'actualExit':value['actualExit'],'manifestSha256':sha(slot/'manifest.safe.json'),'mainRecompiled':False,'testsExecuted':0}));raise SystemExit(value['actualExit'])
producerHash=sha(__file__);producerGitArtifact=None;verifierGitArtifact=None;sdkExtension=None;sdkExtensionGitArtifact=None;authJdkReview=None;authJdkReviewBinding=None
if phase=='post' and len(sys.argv) in {6,7}:
 producerRelative=sys.argv[4];verifierRelative=sys.argv[5];allowedInput='evidence/01_PT/'+cfg.get('program','009_NK-MED-001')+'/input/'
 assert all((n.startswith(allowedInput) or external and n=='evidence/01_PT/018_NK-OPS-001/input/012_acceptor_parser_port_qualifier.py') and n.endswith('.py') and '..' not in Path(n).parts for n in [producerRelative,verifierRelative])
 # The producer is the immutable Git version that actually ran; a later verifier may
 # occupy the same path. Compile/run receipts below must match that exact old byte hash.
 producerHash=hashlib.sha256(subprocess.check_output(['git','show',sys.argv[3]+':'+producerRelative])).hexdigest();verifierHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 assert sha(root/verifierRelative)==sha(__file__) and hashlib.sha256(subprocess.check_output(['git','show',verifierHead+':'+verifierRelative])).hexdigest()==sha(__file__)
 producerGitArtifact={'source':sys.argv[3],'path':producerRelative,'sha256':producerHash};verifierGitArtifact={'source':verifierHead,'path':verifierRelative,'sha256':sha(__file__)}
if phase=='post' and len(sys.argv)==7 and (outboxJdbcExternal or authVerifierExternal or adminPreludeExternal or sessionIssueExternal or sessionRevocationExternal):
 reviewRelative=sys.argv[6];assert reviewRelative==('evidence/01_PT/006_NK-MSG-002/input/001_outbox_jdbc_jdk_static_review.json' if outboxJdbcExternal else 'evidence/01_PT/007_NK-AUT-001/input/014_session_revocation_jdk_static_review.json' if sessionRevocationExternal else 'evidence/01_PT/007_NK-AUT-001/input/011_session_issue_jdk_static_review.json' if sessionIssueExternal else 'evidence/01_PT/007_NK-AUT-001/input/009_admin_prelude_jdk_static_review.json' if adminPreludeExternal else 'evidence/01_PT/007_NK-AUT-001/input/007_auth_jdbc_jdk_static_review.json') and producerGitArtifact is not None
 reviewHash=sha(root/reviewRelative);assert hashlib.sha256(subprocess.check_output(['git','show',verifierHead+':'+reviewRelative])).hexdigest()==reviewHash
 authJdkReview=json.loads((root/reviewRelative).read_text());assert authJdkReview['decision']=='STATIC_JDK_EXCEPTION_LOG_WRITER_CLOSURE' and authJdkReview['source']==sys.argv[3] and authJdkReview['originalRun']==('PG21014' if outboxJdbcExternal else 'PG20958' if sessionRevocationExternal else 'PG20914' if sessionIssueExternal else 'PG20874' if adminPreludeExternal else 'PG20840')
 assert authJdkReview['originalProducerSha256']==producerHash and authJdkReview['originalConfigSha256']==cfgHash and authJdkReview['testsReexecuted']==0 and authJdkReview['actualBackendActions']==0 and not authJdkReview['formalUpdated']
 assert sha(jdk.parent/'lib/modules')==authJdkReview['jdkModulesSha256'] and sha(jdk/'javap')==authJdkReview['jdkJavapSha256']
 assert authJdkReview['classpathDriverProviderEntries'] and all(not v for v in authJdkReview['classpathDriverProviderEntries'].values())
 assert authJdkReview['forbiddenObservedInitialization']==[] and authJdkReview['ordinaryJdbcQualificationOnly'] is True
 for name,h in authJdkReview['staticArtifacts'].items():
  assert name.startswith(('evidence/01_PT/007_NK-AUT-001/evidence/PG20846-auth-jdbc-jdk-static-review-v1/','evidence/01_PT/007_NK-AUT-001/evidence/PG20876-admin-prelude-jdk-static-review-v1/','evidence/01_PT/007_NK-AUT-001/evidence/PG20916-session-issue-jdk-static-review-v1/','evidence/01_PT/007_NK-AUT-001/evidence/PG20960-session-revocation-jdk-static-review-v1/','evidence/01_PT/006_NK-MSG-002/evidence/PG21016-outbox-jdbc-jdk-static-review-v1/')) and '..' not in Path(name).parts
  assert sha(root/name)==h and hashlib.sha256(subprocess.check_output(['git','show',verifierHead+':'+name])).hexdigest()==h
 authJdkReviewBinding={'source':verifierHead,'path':reviewRelative,'sha256':reviewHash,'testsReexecuted':0}
elif phase=='post' and len(sys.argv)==7:
 assert profile=='topology' and producerGitArtifact is not None
 extensionRelative=sys.argv[6];allowedExtension='evidence/01_PT/'+cfg['program']+'/input/006_topology_sdk_method_extension.json';assert extensionRelative==allowedExtension and '..' not in Path(extensionRelative).parts
 extensionHash=sha(root/extensionRelative);assert hashlib.sha256(subprocess.check_output(['git','show',verifierHead+':'+extensionRelative])).hexdigest()==extensionHash
 sdkExtension=json.loads((root/extensionRelative).read_text());assert sdkExtension['decision']=='STATIC_METHOD_CLOSURE_PASS_HOST_VALUE_COMPARISON' and sdkExtension['source']==sys.argv[3] and sdkExtension['originalRun']=='PG19218'
 assert sdkExtension['parentReview']=={'path':cfg['sdkReview'],'sha256':cfg['sdkReviewSha256']} and sdkExtension['sdkDependencies']==sdkReview['sdkDependencies']
 assert sdkExtension['additionalInitializedSdkClasses']==['org/apache/activemq/artemis/utils/ByteUtil'] and sdkExtension['testsReexecuted']==0 and not sdkExtension['formalUpdated']
 artifactPrefix='evidence/01_PT/'+cfg['program']+'/evidence/PG19224-topology-sdk-static-v1/'
 for name,h in sdkExtension['staticArtifacts'].items():
  assert name.startswith(artifactPrefix) and '..' not in Path(name).parts and name.endswith(('.json','.stdout','.stderr'))
  assert sha(root/name)==h and hashlib.sha256(subprocess.check_output(['git','show',verifierHead+':'+name])).hexdigest()==h
 sdkExtensionGitArtifact={'source':verifierHead,'path':extensionRelative,'sha256':extensionHash}
pm=json.loads((prepared/'manifest.safe.json').read_text());assert pm['actualExit']==0 and pm.get('configHash')==cfgHash and pm['driverSha256']==producerHash
for f,h in pm['inputHashes'].items():assert sha(root/f)==h
for f,h in pm['classHashes'].items():assert sha(prepared/'test-classes'/f)==h
if phase=='static':
 slot=runs/cfg['static'];assert not slot.exists();slot.mkdir();r.SLOT=slot;files=[root/f for f in pm['inputHashes']];(slot/'source-list.txt').write_text(''.join(str(p)+'\n' for p in files));static=tc/'static-gates-20261015';rules=root/'tools/quality/static';pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))];stages={};stages['pmd']=r.step('pmd',[str(jdk/'java'),'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(slot/'source-list.txt'),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',classpath,'--no-cache','--format','xml','--report-file',str(slot/'pmd.xml')],slot);stages['checkstyle']=r.step('checkstyle',[str(jdk/'java'),'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(slot/'checkstyle.xml'),'@'+str(slot/'source-list.txt')],slot);reports={}
 for key,path,tag in [('pmd',slot/'pmd.xml','violation'),('checkstyle',slot/'checkstyle.xml','error')]:
  x=E.parse(path).getroot();nodes=[n for n in x.iter() if n.tag.rsplit('}',1)[-1]==tag];errors=[n for n in x.iter() if n.tag.rsplit('}',1)[-1] in (('error','configerror') if key=='pmd' else ())];reports[key]={'path':str(path),'sha256':sha(path),'findings':len(nodes),'processingErrors':len(errors),'items':[dict(n.attrib,message=' '.join(''.join(n.itertext()).split())[:300]) for n in nodes]}
 old=runs/cfg.get('sixStaticSlot','pg19272-acceptor-parser-six-static-reactor-v1')/'manifest.safe.json';sb=json.loads(old.read_text());assert sb['actualExit']==0
 if javaStaticCrossSource:
  assert sb['source']==cfg['staticJavaReferenceSource'];ref=json.loads((runs/cfg['staticJavaReferenceNormalSlot']/'manifest.safe.json').read_text());assert ref['actualExit']==0 and ref['source']==sb['source']
  oldInputs=ref['begin']['inputHashes'];newInputs=base['begin']['inputHashes'];javaPom=lambda n:n.endswith('.java') or n.endswith('/pom.xml') or n=='pom.xml'
  assert {n:h for n,h in oldInputs.items() if javaPom(n)}=={n:h for n,h in newInputs.items() if javaPom(n)}
  classMaps=[]
  for bm in [ref,base]:
   values={}
   for module,j in bm['jars'].items():
    assert sha(j['path'])==j['sha256']
    with zipfile.ZipFile(j['path']) as archive:
     for n in archive.namelist():
      if n.endswith('.class'):values[module+':'+n]=hashlib.sha256(archive.read(n)).hexdigest()
   classMaps.append(values)
  assert classMaps[0]==classMaps[1] and len(classMaps[0])==1844
  staticBinding={'referenceSource':sb['source'],'currentSource':core,'allJavaPomInputHashesEqual':True,'all1844CodeDebugClassBytesEqual':True,'onlyStaticProofReused':True,'oldRuntimeOrTestSuccessTransferred':False}
 else:assert sb['source']==core
 if external:assert sha(old)==cfg['sixStaticManifestSha256']
 for n,x in sb['reports'].items():
  assert sha(x['path'])==x['sha256'];tree=E.parse(x['path']).getroot();assert not tree.findall('.//BugInstance') and not tree.findall('.//MissingClass') and not tree.findall('.//Error')
 assert all(sha(root/f)==h for f,h in pm['inputHashes'].items());value={'coreSource':core,'compileManifestSha256':sha(prepared/'manifest.safe.json'),'inputHashes':pm['inputHashes'],'stages':stages,'reports':reports,'sameSourceSixMainSpotBugs':{'manifest':str(old),'sha256':sha(old),'reports':sb['reports'],'currentAllMainInputsEqualPinnedNormalBuild':True,'javaOnlyCrossSourceBinding':staticBinding if javaStaticCrossSource else None},'rules':{str(f):sha(f) for f in [rules/'pmd.xml',rules/'checkstyle.xml']},'suppressionAdded':False,'testsExecuted':0,'formalUpdated':False,'driverSha256':sha(__file__),'configHash':cfgHash};(slot/'manifest.safe.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'manifestSha256':sha(slot/'manifest.safe.json'),'findings':{k:[v['findings'],v['processingErrors']] for k,v in reports.items()},'stages':{k:v['actualExit'] for k,v in stages.items()}}));raise SystemExit(0)
head=sys.argv[3];slot=runs/cfg['unit'];session=cfg['session'];prefixes=['dev/codex/schubert/nk/'+module+'/'+n for n in mainNames]
if phase=='run':
 assert not slot.exists();assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head;slot.mkdir();r.SLOT=slot
 for f,h in pm['inputHashes'].items():assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+f])).hexdigest()==h
 agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar';assert sha(cli)=='d2b74b20b415163c1f53261e7c5ef4445b788327094208ff821e0c2baf9bc8f1';(slot/'tmp').mkdir();cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(slot/'tmp'),'-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(slot/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(slot/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',os.pathsep.join([str(prepared/'test-classes'),*map(str,deps)]),'--reports-dir',str(slot/'xml'),'--fail-if-no-tests','--details','summary']
 if routerExternal:cmd.insert(1,'-Dspring.security.strategy=MODE_THREADLOCAL')
 for cls in selected:cmd+=['--select-class',cls]
 begin={'coreSource':core,'source':head,'session':session,'compileManifestSha256':sha(prepared/'manifest.safe.json'),'mainCompileManifestSha256':sha(comp/'manifest.safe.json'),'inputHashes':pm['inputHashes'],'classHashes':pm['classHashes'],'dependencies':{str(p):sha(p) for p in deps},'tools':{str(p):sha(p) for p in [console,agent,cli]},'selectedClasses':selected,'expectedTests':expectedCount,'onlyMemoryCallbackFixtures':True,'actualNativeFsDbVmNetworkActions':None if formExternal or csrfExternal or securityAuditExternal or routerExternal or errorRestoreExternal else 0,'actualBusinessBackendOperations':0,'actionCountScope':'BUSINESS_BACKEND_NOT_JVM_SDK_SYSCALL_COUNTS','resourceScopeNote':cfg.get('resourceScopeNote','No actual business backend operations; SDK/JVM activity reviewed separately'),'startUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'driverSha256':sha(__file__),'configHash':cfgHash};(slot/'begin.safe.json').write_text(json.dumps(begin,indent=2)+'\n');stages={'unit':r.step('unit',cmd,root,timeout=120)};component=slot/'component';component.mkdir();physical={}
 with zipfile.ZipFile(deps[1]) as z:
  for n in z.namelist():
   if any(n==prefix+'.class' or n.startswith(prefix+'$') and n.endswith('.class') for prefix in prefixes):
    p=component/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n));physical[n[:-6]]=sha(p)
 assert len(physical)==cfg['physical']
 for number,name in enumerate(cfg.get('syntheticNoCode',[])):
  assert name in physical;stages['synthetic-metadata-'+str(number)]=r.step('synthetic-metadata-'+str(number),[str(jdk/'javap'),'-v','-p',str(component/(name+'.class'))],root)
 for label,args in [('coverage',['report',str(slot/'jacoco.exec'),'--classfiles',str(component),'--sourcefiles',str(root/('src/schubert-nk-'+module+'/src/main/java')),'--xml',str(slot/'coverage.xml'),'--csv',str(slot/'coverage.csv')]),('classinfo',['classinfo',str(component)]),('execinfo',['execinfo',str(slot/'jacoco.exec')])]:stages[label]=r.step(label,[str(jdk/'java'),'-jar',str(cli),*args],root)
 cases=[]
 for p in (slot/'xml').glob('TEST-*.xml'):
  for c in E.parse(p).getroot().findall('testcase'):cases.append({'class':c.get('classname'),'name':c.get('name'),'failure':bool(c.findall('failure')),'error':bool(c.findall('error')),'skipped':bool(c.findall('skipped'))})
 assert all(sha(root/p)==h for p,h in pm['inputHashes'].items());value={'actualExit':stages['unit']['actualExit'],'begin':begin,'stages':stages,'cases':cases,'tests':len(cases),'failures':sum(x['failure'] for x in cases),'errors':sum(x['error'] for x in cases),'skipped':sum(x['skipped'] for x in cases),'physical':physical,'noOldExecUnion':True,'formalUpdated':False,'newAccepted':0};(slot/'manifest.safe.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value[k] for k in ['actualExit','tests','failures','errors','skipped']}|{'manifestSha256':sha(slot/'manifest.safe.json')}));raise SystemExit(value['actualExit'])
assert phase=='post';out=root/'evidence/01_PT'/cfg.get('program','009_NK-MED-001')/'evidence'/cfg['public'];assert not out.exists();m=json.loads((slot/'manifest.safe.json').read_text());b=m['begin'];assert b['source']==head and b['coreSource']==core and b['driverSha256']==producerHash and b['configHash']==cfgHash;assert m['actualExit']==0 and m['tests']==expectedCount and all(m[k]==0 for k in ['failures','errors','skipped']);assert sha(prepared/'manifest.safe.json')==b['compileManifestSha256'] and sha(comp/'manifest.safe.json')==b['mainCompileManifestSha256']
for f,h in b['inputHashes'].items():assert sha(root/f)==h and hashlib.sha256(subprocess.check_output(['git','show',head+':'+f])).hexdigest()==h
for f,h in {**b['dependencies'],**b['tools']}.items():assert sha(f)==h
for n,x in m['stages'].items():
 assert x['actualExit']==0 and not x['timedOut'] and x['startUTC']<=x['endUTC'];assert sha(slot/(n+'.stdout'))==x['stdoutSha256'] and sha(slot/(n+'.stderr'))==x['stderrSha256']
expected=set()
for file,cls in zip(tests,selected):expected.update((cls,n) for n in re.findall(r'@Test\s+void\s+(\w+)\s*\(', (root/file).read_text()))
assert len(expected)==expectedCount;actual=[];xmlPins={}
for f in sorted((slot/'xml').glob('TEST-*.xml')):
 xmlPins[str(f)]=sha(f)
 for c in E.parse(f).getroot().findall('testcase'):
  assert not any(c.findall(tag) for tag in ['failure','error','skipped']);n=c.get('name');assert n.endswith('()') and n.count('(')==1;actual.append((c.get('classname'),n[:-2]))
assert len(actual)==expectedCount and len(set(actual))==expectedCount and set(actual)==expected;cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==len(selected) and {cmd[i+1] for i,v in enumerate(cmd[:-1]) if v=='--select-class'}==set(selected) and '--select-method' not in cmd;assert any('append=false' in v and 'sessionid='+session in v for v in cmd)
for text in [f'{expectedCount} tests found',f'{expectedCount} tests started',f'{expectedCount} tests successful','0 tests failed','0 tests aborted','0 tests skipped','0 containers aborted']:assert text in (slot/'unit.stdout').read_text()
cp=cmd[cmd.index('--class-path')+1].split(os.pathsep);assert cp==[str(prepared/'test-classes'),*map(str,deps)];assert not any('storage' in v or 'playwright' in v or 'postgresql' in v for v in cp)
if profile not in {'inbound','pressure','topology','acceptor'}:assert not any('artemis' in v for v in cp)
else:
 assert cp==[str(prepared/'test-classes'),*map(str,deps)] and not any('artemis-server' in v or 'artemis-jakarta-server' in v or 'artemis-jms-server' in v for v in cp)
 initializedSdk=set(re.findall(r'Initializing \'(org/apache/activemq/artemis/[^\']+)',(slot/'class-init.log').read_text()))
 if profile=='inbound':
  allowedSdk={n.replace('.','/') for n in sdkPrior['initializedSdkValueClasses']};assert initializedSdk and initializedSdk<=allowedSdk,sorted(initializedSdk-allowedSdk)
 else:
  generatedSdk={n for n in initializedSdk if any(n.startswith(prefix) for prefix in sdkReview['allowedGeneratedLambdaPrefixes'])};allowedSdk={n.replace('.','/') for n in sdkReview['allowedInitializedClasses']};allowedSdk.update(sdkExtension['additionalInitializedSdkClasses'] if sdkExtension else []);assert initializedSdk-generatedSdk<=allowedSdk,sorted(initializedSdk-generatedSdk-allowedSdk)
  assert '-Xlog:class+init=info:file='+str(slot/'class-init.log') in cmd and re.search("Initializing '"+re.escape("dev/codex/schubert/nk/"+module+"/"+mainNames[0])+"'",(slot/'class-init.log').read_text())
  if profile in {'topology','acceptor'}:assert set(sdkReview['requiredPositiveInitialization'])<=initializedSdk
  for prefix,maximum in sdkReview['allowedGeneratedLambdaPrefixes'].items():assert sum(n.startswith(prefix) for n in generatedSdk)<=maximum
  initializedAll=set(re.findall(r'Initializing \'([^\']+)',(slot/'class-init.log').read_text()));assert not any(n.startswith('io/netty/channel/') or 'NativeLibraryLoader' in n or n.startswith('com/sun/jna/') for n in initializedAll),sorted(n for n in initializedAll if 'NativeLibrary' in n)

if sdkExtension:
 assert sha(slot/'manifest.safe.json')==sdkExtension['originalManifestSha256'] and sha(slot/'class-init.log')==sdkExtension['classInitializationLogSha256']
 nettyActual={n for n in initializedAll if n.startswith('io/netty/')};assert nettyActual==set(sdkExtension['reviewedInitializedNettyClasses'])
 assert all(not n.startswith('io/netty/channel/') and 'NativeLibraryLoader' not in n for n in nettyActual)
 for file,binding in sdkExtension['originalXmlEnvironmentBindings'].items():
  assert str(Path(file).parent)==str(slot/'xml') and Path(file).name.startswith('TEST-') and Path(file).suffix=='.xml' and '..' not in Path(file).parts
  assert sha(file)==binding['sha256']
  props={x.get('name'):x.get('value') for x in E.parse(file).getroot().findall('properties/property')};checks={'javaIoTmpdirEqualsOwnedSlot':props.get('java.io.tmpdir')==str(slot/'tmp'),'noNettyTmpOverride':'io.netty.tmpdir' not in props,'noJulConfigFile':'java.util.logging.config.file' not in props,'noJulConfigClass':'java.util.logging.config.class' not in props};assert checks==binding['checks'] and all(checks.values())

if profile in {'expiry','backup','batch_run','cleanup_step','cleanup_query','inspection_summary','pressure','topology','acceptor'}:
 initializedApp=set(re.findall(r'Initializing \'(dev/codex/schubert/nk/[^\']+)',(slot/'class-init.log').read_text()));assert not any(n.startswith('dev/codex/schubert/nk/storage/') or n in {'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame','dev/codex/schubert/nk/batch/repository/MorningDatabaseSession'} for n in initializedApp),sorted(initializedApp)
if observationExternal:
 initializedApp=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));assert not any(n.startswith(('io/micrometer/','dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/')) for n in initializedApp),sorted(initializedApp)
 assert 'dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttempt' in initializedApp
if viewExternal and cfg['main'] in {'NotificationListViewModel','QuestionListViewModel'}:
 formClass='dev/codex/schubert/nk/web/form/'+('QuestionSearchForm' if cfg['main']=='QuestionListViewModel' else 'NotificationSearchForm')
 initializedPure=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));unexpected={n for n in initializedPure if n.startswith('dev/codex/schubert/nk/') and not (n.startswith(('dev/codex/schubert/nk/protocol/','dev/codex/schubert/nk/web/view/')) or n in {formClass,'dev/codex/schubert/nk/web/session/SessionPrincipal'} or n.startswith((formClass+'$$Lambda','dev/codex/schubert/nk/web/session/SessionPrincipal$$Lambda')))};assert not unexpected,sorted(unexpected)
 for owner,maximum in [(formClass+'$$Lambda',2),('dev/codex/schubert/nk/web/session/SessionPrincipal$$Lambda',1)]:assert sum(n.startswith(owner) for n in initializedPure)<=maximum
 assert not any(n.startswith(('org/springframework/context/','org/springframework/beans/','org/springframework/web/client/','org/springframework/jdbc/','org/apache/activemq/','io/netty/','com/zaxxer/')) for n in initializedPure)
if requestExternal:
 initializedRequest=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowedRequest={'dev/codex/schubert/nk/api/application/question/QuestionSubmitRequest','dev/codex/schubert/nk/api/domain/Role','dev/codex/schubert/nk/api/security/AuthenticatedActor','dev/codex/schubert/nk/api/idempotency/CanonicalRequest','dev/codex/schubert/nk/api/idempotency/CanonicalField'}
 unexpectedRequest={n for n in initializedRequest if n.startswith('dev/codex/schubert/nk/') and not (n.startswith('dev/codex/schubert/nk/protocol/') or n in allowedRequest or n.startswith(('dev/codex/schubert/nk/api/application/question/QuestionSubmitRequestPortTest','dev/codex/schubert/nk/api/idempotency/CanonicalRequest$$Lambda')))};assert not unexpectedRequest,sorted(unexpectedRequest)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','io/netty/','com/zaxxer/','io/micrometer/')) for n in initializedRequest)
if sessionExternal:
 initializedSession=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowedSession={'dev/codex/schubert/nk/web/session/'+n for n in ['WebSessionSnapshot','WebSessionId','WebSessionRow','SessionPayloadIdentity','EncryptedSessionPayload','SessionAttributes']}
 unexpectedSession={n for n in initializedSession if n.startswith('dev/codex/schubert/nk/') and not (n in allowedSession or n.startswith(('dev/codex/schubert/nk/web/session/WebSessionSnapshotPortTest','dev/codex/schubert/nk/web/session/SessionAttributes$$Lambda')))};assert not unexpectedSession,sorted(unexpectedSession)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','io/netty/','com/zaxxer/','io/micrometer/','javax/crypto/Cipher')) for n in initializedSession)
if formExternal:
 initializedForm=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowedForm={'dev/codex/schubert/nk/web/security/'+n for n in ['LoginFormAuthenticationConverter','CaddyClientAddressResolver','LoginClientAddress','LoginFormRejectedException','CaddyRequestRejectedException']}
 unexpectedForm={n for n in initializedForm if n.startswith('dev/codex/schubert/nk/') and not (n in allowedForm or n.startswith('dev/codex/schubert/nk/web/security/LoginFormConverterPortTest'))};assert not unexpectedForm,sorted(unexpectedForm)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','io/netty/','com/zaxxer/','io/micrometer/','org/springframework/security/core/context/SecurityContextHolder')) for n in initializedForm)
if csrfExternal:
 initializedCsrf=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowedCsrf={'dev/codex/schubert/nk/web/security/FormCsrfTokenRequestHandler','dev/codex/schubert/nk/web/security/WebCsrfToken'}
 unexpectedCsrf={n for n in initializedCsrf if n.startswith('dev/codex/schubert/nk/') and not (n in allowedCsrf or n.startswith('dev/codex/schubert/nk/web/security/FormCsrfRequestPortTest'))};assert not unexpectedCsrf,sorted(unexpectedCsrf)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','io/netty/','com/zaxxer/','io/micrometer/','org/springframework/security/core/context/SecurityContextHolder','javax/crypto/Cipher')) for n in initializedCsrf)
if errorRestoreExternal:
 initializedRestore=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowedRestore={'dev/codex/schubert/nk/web/'+n for n in ['security/WebErrorDispatchFilter','security/WebDisplayContext','security/WebCsrfToken','session/SessionPrincipal','session/SessionStoreException','view/TopBarViewModel']}
 unexpectedRestore={n for n in initializedRestore if n.startswith('dev/codex/schubert/nk/') and not(n in allowedRestore or n.startswith(('dev/codex/schubert/nk/protocol/','dev/codex/schubert/nk/web/session/SessionPrincipal$$Lambda','dev/codex/schubert/nk/web/security/ErrorDispatchRestorePortTest')))};assert not unexpectedRestore,sorted(unexpectedRestore)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','io/netty/','com/zaxxer/','io/micrometer/','javax/crypto/Cipher','org/springframework/security/core/context/SecurityContextHolder')) for n in initializedRestore)
if routerExternal:
 initializedRouter=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowedRouter={'dev/codex/schubert/nk/web/security/'+n for n in ['InternalErrorDispatchRouter','WebRequestContext','LoginClientAddress']}
 unexpectedRouter={n for n in initializedRouter if n.startswith('dev/codex/schubert/nk/') and not(n in allowedRouter or n.startswith('dev/codex/schubert/nk/web/security/InternalErrorRouterPortTest'))};assert not unexpectedRouter,sorted(unexpectedRouter)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','io/netty/','com/zaxxer/','io/micrometer/','javax/crypto/Cipher')) for n in initializedRouter)
if securityAuditExternal:
 initializedAudit=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));unexpectedAudit={n for n in initializedAudit if n.startswith('dev/codex/schubert/nk/') and not (n.startswith(('dev/codex/schubert/nk/protocol/','dev/codex/schubert/nk/web/logging/WebSecurityAudit')) or n=='dev/codex/schubert/nk/web/session/SessionPrincipal' or n.startswith('dev/codex/schubert/nk/web/session/SessionPrincipal$$Lambda'))};assert not unexpectedAudit,sorted(unexpectedAudit)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','io/netty/','com/zaxxer/','io/micrometer/','org/springframework/security/core/context/SecurityContextHolder','javax/crypto/Cipher')) for n in initializedAudit)
if stateParserExternal:
 initializedState=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowedState={'dev/codex/schubert/nk/batch/platform/'+n for n in ['UnitStateParser','ApplicationUnit','StopGateException','StopGateFailure']}
 unexpectedState={n for n in initializedState if n.startswith('dev/codex/schubert/nk/') and not (n in allowedState or n.startswith('dev/codex/schubert/nk/batch/platform/UnitStateParserBytePortTest'))};assert not unexpectedState,sorted(unexpectedState)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','io/netty/','com/zaxxer/','io/micrometer/')) for n in initializedState)
if authVerifierExternal or adminPreludeExternal or sessionIssueExternal or sessionRevocationExternal:
 initializedAuth=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowedAuth={'dev/codex/schubert/nk/api/'+n for n in ['security/AuthenticationContextVerifier','security/AuthenticationContextVerifier$VerifiedSession','security/ContextHash','security/AuthenticationInfrastructureException','security/AuthenticationContextException','security/AuthenticatedActor','domain/Role','database/RequiredColumn']}
 if adminPreludeExternal:allowedAuth.update({'dev/codex/schubert/nk/api/security/'+n for n in ['AdminCommandAuthenticator','AdminCommandAuthenticator$Mutation','AuthorizationService','AuthorizationException']});allowedAuth.add('dev/codex/schubert/nk/protocol/header/ResultCode')
 if sessionIssueExternal:allowedAuth.update({'dev/codex/schubert/nk/api/security/'+n for n in ['AuthSessionService','AuthContextCodec','AuthContextIdentity','EncryptedAuthContext','IssuedContext','SessionAuditWriter','SessionRevocationReason','AuthContextCryptoException','AuthContextCryptoException$Reason']});allowedAuth.add('dev/codex/schubert/nk/protocol/header/ResultCode')
 if sessionRevocationExternal:allowedAuth.update({'dev/codex/schubert/nk/api/security/'+n for n in ['AuthSessionRevocationService','AuthContextIdentity','RevokedContext','SessionAuditWriter','SessionRevocationReason','AuthorizationService','AuthorizationException']});allowedAuth.add('dev/codex/schubert/nk/protocol/header/ResultCode')
 testPrefix='dev/codex/schubert/nk/api/security/'+('SessionRevocationJdbcPortTest' if sessionRevocationExternal else 'SessionIssueJdbcPortTest' if sessionIssueExternal else 'AdminPreludeJdbcPortTest' if adminPreludeExternal else 'AuthenticationVerifierJdbcPortTest')
 # The public session-service constructor prepares one UUID supplier call site;
 # its invalid-transaction test never invokes that supplier or issues a real session.
 sessionSupplierPrefix='dev/codex/schubert/nk/api/security/AuthSessionService$$Lambda'
 if sessionIssueExternal:assert sum(n.startswith(sessionSupplierPrefix) for n in initializedAuth)<=1
 unexpectedAuth={n for n in initializedAuth if n.startswith('dev/codex/schubert/nk/') and not (n in allowedAuth or n=='dev/codex/schubert/nk/protocol/header/AuthenticationContext' or n.startswith(testPrefix) or sessionIssueExternal and n.startswith(sessionSupplierPrefix))};assert not unexpectedAuth,sorted(unexpectedAuth)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','org/postgresql/','io/netty/','com/zaxxer/','io/micrometer/','java/sql/DriverInfo','java/net/Socket','sun/nio/ch/SocketChannelImpl')) for n in initializedAuth)
 if 'java/sql/DriverManager' in initializedAuth:
  assert authJdkReview is not None and authJdkReviewBinding is not None
  assert sha(slot/'manifest.safe.json')==authJdkReview['originalManifestSha256'] and sha(slot/'class-init.log')==authJdkReview['originalInitializationSha256']
  assert b['inputHashes']==authJdkReview['originalInputHashes']
  for file,binding in authJdkReview['originalXmlEnvironmentBindings'].items():
   assert Path(file).parent==slot/'xml' and sha(file)==binding['sha256'] and all(binding['checks'].values())
if outboxJdbcExternal:
 initializedOutbox=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));prefix='dev/codex/schubert/nk/api/messaging/outbound/'
 allowedOutbox={prefix+n for n in ['JdbcOutboxRepository','OutboxRequest','OutboxEntry','OutboxDlqMetadata','OutboxDestination','OutboxRetrySchedule','OutboxIntegrityException']};allowedOutbox.add('dev/codex/schubert/nk/api/database/RequiredColumn')
 lambdaPrefixes={prefix+'JdbcOutboxRepository$$Lambda':4,prefix+'OutboxDestination$$Lambda':2,prefix+'OutboxDlqMetadata$$Lambda':1}
 for p,maximum in lambdaPrefixes.items():assert sum(n.startswith(p) for n in initializedOutbox)<=maximum
 unexpectedOutbox={n for n in initializedOutbox if n.startswith('dev/codex/schubert/nk/') and not (n in allowedOutbox or n.startswith(prefix+'JdbcOutboxPortTest') or n.startswith(prefix+'OutboxReturningIdContractTest') or any(n.startswith(p) for p in lambdaPrefixes))};assert not unexpectedOutbox,sorted(unexpectedOutbox)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','org/postgresql/','io/netty/','com/zaxxer/','io/micrometer/','java/sql/DriverInfo','java/net/Socket','sun/nio/ch/SocketChannelImpl')) for n in initializedOutbox)
 if 'java/sql/DriverManager' in initializedOutbox:
  assert authJdkReview is not None and authJdkReviewBinding is not None
  assert sha(slot/'manifest.safe.json')==authJdkReview['originalManifestSha256'] and sha(slot/'class-init.log')==authJdkReview['originalInitializationSha256']
  assert b['inputHashes']==authJdkReview['originalInputHashes']
  for file,binding in authJdkReview['originalXmlEnvironmentBindings'].items():
   assert Path(file).parent==slot/'xml' and sha(file)==binding['sha256'] and all(binding['checks'].values())


if loginFailureExternal:
 initializedLogin=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));securityPrefix='dev/codex/schubert/nk/web/security/';loggingPrefix='dev/codex/schubert/nk/web/logging/'
 allowedLogin={securityPrefix+n for n in ['MqLoginFailureHandler','WebRequestContext','LoginClientAddress','MqLoginLockedException','LoginFormRejectedException','CaddyRequestRejectedException']};allowedLogin.update(loggingPrefix+n for n in ['WebSecurityAudit','WebSecurityAudit$Event','WebSecurityAudit$Route'])
 loginLambdas={securityPrefix+'WebRequestContext$$Lambda':1,loggingPrefix+'WebSecurityAudit$$Lambda':3}
 for p,maximum in loginLambdas.items():assert sum(n.startswith(p) for n in initializedLogin)<=maximum
 unexpectedLogin={n for n in initializedLogin if n.startswith('dev/codex/schubert/nk/') and not (n in allowedLogin or n.startswith(securityPrefix+'MqLoginFailurePortTest') or any(n.startswith(p) for p in loginLambdas))};assert not unexpectedLogin,sorted(unexpectedLogin)
 assert not any(n.startswith(('dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/apache/activemq/','org/postgresql/','io/netty/','com/zaxxer/','io/micrometer/','org/springframework/security/core/context/SecurityContextHolder','java/sql/DriverManager','java/sql/DriverInfo','java/net/Socket','sun/nio/ch/SocketChannelImpl')) for n in initializedLogin)

physical=m['physical'];assert len(physical)==cfg['physical']
with zipfile.ZipFile(deps[1]) as z:
 for n,h in physical.items():assert sha(slot/'component'/(n+'.class'))==h and hashlib.sha256(z.read(n+'.class')).hexdigest()==h
ids={n:crc for crc,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(slot/'classinfo.stdout').read_text())};assert set(ids)==set(physical);execText=(slot/'execinfo.stdout').read_text();assert execText.count('Session "')==1 and 'Session "'+session+'"' in execText;execIds={n:(crc,int(hit),int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',execText,re.M)};coverage={};abstract=[];generated=[]
held={'dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/web/bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec'};heldHits={name:execIds.get(name,('',0,0))[1] for name in held};assert sum(heldHits.values())==0
for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class'):
 n=c.get('name');assert n in physical;cs={x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))} for x in c.findall('counter')};coverage[n]=cs
 if cs:assert all(x['missed']==0 for x in cs.values()) and n in execIds and execIds[n][0]==ids[n]
 else:
  assert '$' in n and not c.findall('method')
  if n in cfg.get('syntheticNoCode',[]):
   number=cfg['syntheticNoCode'].index(n);metadata=(slot/('synthetic-metadata-'+str(number)+'.stdout')).read_text();flags=re.search(r'^  flags: \(0x([0-9a-f]+)\)',metadata,re.M);assert flags and int(flags.group(1),16)&0x1000 and '$SwitchMap$' in metadata and 'static {};' in metadata;generated.append(n)
  else:abstract.append(n)
assert len(coverage)==cfg['physical'] and len(abstract)==cfg['abstract'] and set(generated)==set(cfg.get('syntheticNoCode',[]));out.mkdir(parents=True)
for name in ['manifest.safe.json','begin.safe.json','unit.stdout','unit.stderr','coverage.xml','coverage.csv','classinfo.stdout','execinfo.stdout','jacoco.exec']:shutil.copyfile(slot/name,out/name)
for number in range(len(generated)):
 for suffix in ['stdout','stderr']:shutil.copyfile(slot/('synthetic-metadata-'+str(number)+'.'+suffix),out/('synthetic-metadata-'+str(number)+'.'+suffix))
for n in m['stages']:
 for suffix in ['begin.safe.json','process.safe.json','exit.safe.json']:shutil.copyfile(slot/(n+'-'+suffix),out/(n+'-'+suffix))
suite=E.Element('testsuite',tests=str(expectedCount),failures='0',errors='0',skipped='0')
for cls,n in sorted(actual):E.SubElement(suite,'testcase',classname=cls,name=n+'()')
E.ElementTree(suite).write(out/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);value={'actualExit':0,'atJST':datetime.datetime.now().astimezone().isoformat(),'source':head,'productionCoreMain':core,'originalManifest':{'path':str(slot/'manifest.safe.json'),'sha256':sha(slot/'manifest.safe.json')},'originalXmlPins':xmlPins,'tests':expectedCount,'testClasses':len(selected),'failures':0,'errors':0,'skipped':0,'aborted':0,'selectedTestMethods':sorted(actual),'normalMainCompileSourceInputsChecked':True,'allNormalJarHashesChecked':True,'inputHashes':b['inputHashes'],'physicalHashes':physical,'physicalClassIds':ids,'execMatches':{n:execIds[n] for n in physical if n in execIds},'session':session,'coverage':coverage,'wholeSourceFourCounter100':[Path(n).name+'.java' for n in mainNames],'abstractInterfacesNoExecutableMethods':abstract,'compilerGeneratedNoCodeClasses':generated,'coverageEngineDefaultSyntheticFilterOnly':bool(generated),'interfacesExcludedFromReport':False,'oldExecUnion':False,'manualCoverageExclusions':[],'noNativeAccessFlag':not any('--enable-native-access' in v for v in cmd),'onlyMemoryCallbackFixtures':True,'sdkInitializationReview':({'path':cfg['sdkReview'],'sha256':cfg['sdkReviewSha256'],'initializedSdk':sorted(initializedSdk)} if profile in {'pressure','topology','acceptor'} else None),'heldFourProbeHits':heldHits,'actualMediaAuthOrFilesOrHttpVerified':False,'newAccepted':0,'formalUpdated':False,'secondPilot':False,'driverSha256':producerHash,'verifierSha256':sha(__file__),'producerGitArtifact':producerGitArtifact,'verifierGitArtifact':verifierGitArtifact,'classInitializationLogSha256':sha(slot/'class-init.log'),'sdkMethodExtensionGitArtifact':sdkExtensionGitArtifact,'jdkExceptionInitializationReview':authJdkReviewBinding,'sdkMethodExtensionLimitations':(sdkExtension['environmentAndResourceLimitations'] if sdkExtension else None),'configHash':cfgHash,'files':{f.name:sha(f) for f in out.iterdir() if f.is_file()}};(out/'manifest.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'actualExit':0,'tests':expectedCount,'sourceQualified':len(mainNames),'physicalReported':len(physical),'abstractInterfaces':len(abstract),'compilerGeneratedNoCodeClasses':len(generated),'manifestSha256':sha(out/'manifest.json')}))
