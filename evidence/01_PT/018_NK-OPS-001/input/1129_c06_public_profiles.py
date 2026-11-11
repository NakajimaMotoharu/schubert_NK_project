"""Public nonsecret config/credential-name contracts only; never open a credential path."""
from pathlib import Path
import datetime as dt,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26138-c06-public-profiles-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
descriptor=load(B/'evidence/PG22122-current7aed-lineage-style-v1/artifacts.json');art={x['path']:x for x in descriptor};root=R/'src/deployment/config';names=['api.env.template','api.yml.template','batch.yml.template','common.yml.template','inbox-inspector.env.template','web.env.template','web.yml.template'];pins={}
for n in names:
 p=root/n;k=str(p.relative_to(R));assert sha(p)==art[k]['sha256'] and art[k]['owner']=='WBS-C06';pins[k]=sha(p)
expected={
'common.yml.template':{'nk.protocol.version':'001','nk.time.display-zone':'Asia/Tokyo','nk.monitoring.mode':'STANDARD'},
'api.yml.template':{'nk.api.storage.asset-manifest-entries':59627,'nk.mq.url':'tcp://127.0.0.1:61616','nk.mq.sync-request':'nk.sync.request','nk.mq.sync-reply':'nk.sync.reply.web','nk.mq.async-work':'nk.async.work','nk.mq.web-log':'nk.web.log','nk.mq.dlq':'nk.dead.letter','nk.mq.expiry':'nk.expiry','nk.db.url':'jdbc:postgresql://127.0.0.1:5432/schubert_nk','nk.db.connect-timeout':'3s','nk.db.pool.api.max':'8','nk.db.pool.api.min':'2','nk.api.sync-consumers.initial':'4','nk.api.sync-consumers.max':'8','nk.api.async-consumers':'1','nk.api.storage.asset-root':'/srv/schubert-nk/data/assets','nk.api.storage.transfer-root':'/srv/schubert-nk/data/transfer','nk.inbox.reference-retention':'24h','nk.inbox.update-retention':'7d','nk.outbox.sent-retention':'7d'},
'web.yml.template':{'nk.db.url':'jdbc:postgresql://127.0.0.1:5432/schubert_nk','nk.mq.url':'tcp://127.0.0.1:61616','nk.db.pool.web.max':'2','nk.db.pool.web.min':'1','nk.db.connect-timeout':'3s','nk.web.http.address':'127.0.0.1','nk.web.http.port':'8080','nk.web.management.port':'8081','nk.web.mq.reply-timeout':'2s','nk.web.mq.wait.initial':'12','nk.web.mq.wait.max':'20','nk.web.session.idle-timeout':'8h','nk.web.session.max-per-user':'2','nk.web.storage.asset-root':'/srv/schubert-nk/data/assets','nk.web.storage.transfer-root':'/srv/schubert-nk/data/transfer','nk.web.media.max-streams':'20','nk.web.media.max-range-bytes':'1048576'},
'batch.yml.template':{'nk.batch.zone':'Asia/Tokyo','nk.batch.schedule':'05:00','nk.batch.backup-root':'/srv/schubert-nk/backup','nk.batch.backup-generations':'7','nk.batch.transfer-cleanup':'enabled','nk.batch.expiry-retention':'7d','nk.batch.log-retention':'90d','nk.batch.run-retention':'400d','nk.batch.chunk-size.notification':'1000','nk.batch.chunk-size.question':'1000','nk.batch.chunk-size.log':'10000'}}
for name,golden in expected.items():
 actual={}
 for line in (root/name).read_text().splitlines():
  if not line.strip() or line.startswith('#'):continue
  key,value=line.split(':',1);key=json.loads(key);assert key not in actual;actual[key]=json.loads(value)
 assert actual==golden
for n in ['api.env.template','web.env.template']:assert (root/n).read_bytes()==b'SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk\n'
assert (root/'inbox-inspector.env.template').read_bytes()==b'NK_INSPECTOR_DB_URL=jdbc:postgresql://127.0.0.1:@PG_PORT@/@PG_DATABASE@\nNK_INSPECTOR_FINGERPRINT_VERSIONS=@FINGERPRINT_VERSION_NAMES@\n'
ids={'api':['db-api','mq-api','api-context-aes-current','api-inbox-response-aes-current','operation-hmac-current'],'web':['db-web','mq-web','web-session-aes-current','web-revoke-aes-current','web-log-aes-current']};units={}
for service,golden in ids.items():
 p=R/('src/deployment/systemd/schubert-nk-'+service+'.service.template');got=[l.partition('=')[2] for l in p.read_text().splitlines() if l.startswith('LoadCredential=')];assert got==[id+':/etc/schubert-nk/credentials/'+id for id in golden];assert sha(p)==art[str(p.relative_to(R))]['sha256'];units[service]=dict(path=str(p.relative_to(R)),sha256=sha(p),publicCredentialIds=golden)
assert not set(ids['api'])&set(ids['web'])
inspector=R/'src/deployment/systemd/schubert-nk-inbox-inspector.service';optional=['src/deployment/systemd/optional/inbox-inspector-context-previous.conf','src/deployment/systemd/optional/inbox-inspector-response-previous.conf'];base=[l.partition('=')[2].split(':',1)[0] for l in inspector.read_text().splitlines() if l.startswith('LoadCredential=')];assert base==['db-inbox-inspector','maintenance-owner','api-context-aes-current','api-inbox-response-aes-current']
profiles=[]
for selection in [[],optional[:1],optional[1:],optional]:
 selected=base[:]
 for n in selection:
  p=R/n;assert sha(p)==art[n]['sha256'];selected += [l.partition('=')[2].split(':',1)[0] for l in p.read_text().splitlines() if l.startswith('LoadCredential=')]
 assert len(selected)==len(set(selected));profiles.append(selected)
ss343=R/'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md';ss352=R/'documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md';design={}
for p in [ss343,ss352]:data=subprocess.check_output(['git','show','origin/main:'+str(p.relative_to(R))]);design[str(p.relative_to(R))]=hashlib.sha256(data).hexdigest()
prior=B/'evidence/PG26100-inspector-eight-six-independent-v1/manifest.json';assert sha(prior)=='c567a0f673e45fbdc50baff9ecde2490cb8655fc9111674dcf54bfbd7824fbf1';assert load(prior)['allFourProfiles']==[4,5,5,6]
assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',sourcePins=pins,approvedDesignPins=design,goldenNonsecretSettings=expected,publicApiWebCredentialProfiles=units,publicInspectorProfiles=profiles,existingInspectorProfileProof=dict(path=str(prior.relative_to(R)),sha256=sha(prior)),templatesAreNotRenderedOrDistributed=True,credentialPathsActuallyOpened=0,credentialValuesOrKeyMaterialRead=0,cryptoOperations=0,sessionOrTokenIssued=0,actualJmsDbVmServiceOperations=0,productTestsExecuted=0,newCoverageMeasurements=0,newAcceptance=0,formalUpdated=False,effortRate=None,decision='NOT_ACCEPTED_PUBLIC_PROFILE_ONLY_ACTUAL_DISTRIBUTION_AND_ROTATION_UNPROVEN',remainingConditions=['Private source/file/UID/GID/mode/ACL/nlink/size/LoadCredential effective delivery and readiness remain unverified; public path string is not permission.','Actual key length/current/previous version binding, retained-session validity/expiry/rotation/retirement and redaction not inferred from names or prior unrelated tests.','Configured max2 sessions remains DIF016 requirement, not tested by this static template check.','Shared nonsecret source counts59627 and profile labels are approved config; no master/rawDB/Backup/credential/key was opened.'],toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,configTemplates=7,nonsecretKeys=sum(map(len,expected.values())),apiWebIds=10,inspectorProfileSizes=list(map(len,profiles)),productTestsExecuted=0,sha256=sha(O/'manifest.json'))))
