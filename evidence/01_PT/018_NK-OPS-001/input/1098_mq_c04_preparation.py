"""Independent SS321 literal catalog/config checks and requirement delegation; no broker execution."""
from pathlib import Path
import datetime as dt,hashlib,json,re,subprocess,xml.etree.ElementTree as X
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';O=E/'PG26064-mq-c04-preparation-v1'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ss=R/'documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md';approved=subprocess.check_output(['git','show','origin/main:'+str(ss.relative_to(R))]);assert approved==ss.read_bytes();design=approved.decode()
vectors=[('SYNC_REQUEST','nk.sync.request',1000000,5000),('SYNC_REPLY_WEB','nk.sync.reply.web',1000000,10000),('ASYNC_WORK','nk.async.work',1000,0),('WEB_LOG','nk.web.log',10000,0),('DEAD_LETTER','nk.dead.letter',1000000,0),('EXPIRY','nk.expiry',1000000,0)]
main='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/BrokerTopology.java';test='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/transport/BrokerTopologyTest.java'
original=R/'evidence/01_PT/002_NK-PRO-002/evidence/PG24642-protocol-whole120-independent-v1/manifest.json';assert sha(original)=='8ebe6365bc701ba6432b1b55275004024dc71bc452d31b66d31c53894e3ae128';normal=load(original)
pf=load(original.parent/'preflight-manifest.json')
for p in [main,test]:assert sha(R/p)==pf['inputHashes'][p]
body=(R/test).read_text();assert body.count('@Test')==2
found=[(n,a,int(size.replace('_','')),int(ttl.replace('_',''))) for n,a,size,ttl in re.findall(r'new Vector\("([A-Z_]+)", "([a-z.]+)", ([0-9_]+), ([0-9_]+)\)',body)];assert found==vectors
for n,a,size,ttl in vectors:assert '`'+a+'`' in design and '`'+a+'.q`' in design
broker=R/'src/deployment/artemis/etc/broker.xml';core=X.parse(broker).getroot().find('{urn:activemq:core}core');assert core is not None
tag=lambda name:'{urn:activemq:core}'+name
globalsExpected={'persistence-enabled':'true','journal-type':'NIO','journal-file-size':'10MiB','journal-min-files':'4','journal-pool-files':'20','journal-compact-min-files':'10','journal-compact-percentage':'30','global-max-size':'512MiB','global-max-messages':'50000','max-disk-usage':'90','disk-scan-period':'5000','id-cache-size':'20000','persist-id-cache':'true','graceful-shutdown-enabled':'true','graceful-shutdown-timeout':'60000'}
for name,value in globalsExpected.items():assert core.findtext(tag(name))==value and '`'+name+'`' in design
addressNodes=core.find(tag('addresses')).findall(tag('address'));assert len(addressNodes)==6
for node,(_,a,_,_) in zip(addressNodes,vectors):
 assert node.get('name')==a
 anycast=node.find(tag('anycast'));assert anycast is not None and len(anycast)==1 and anycast[0].get('name')==a+'.q'
 # Omitted durable attribute is a vendor schema/default property, not a runtime assertion here.
 assert anycast[0].get('durable') in [None,'true']
settings={v.get('match'):v for v in core.find(tag('address-settings'))};assert set(settings)=={v[1] for v in vectors}
shared={'dead-letter-address':'nk.dead.letter','expiry-address':'nk.expiry','auto-create-dead-letter-resources':'false','auto-create-expiry-resources':'false','auto-create-addresses':'false','auto-create-queues':'false','auto-delete-addresses':'false','auto-delete-queues':'false','address-full-policy':'PAGE','page-full-policy':'FAIL','disk-full-policy':'BLOCK','page-size-bytes':'8MiB','redelivery-collision-avoidance-factor':'0.0','enable-metrics':'true','enable-ingress-timestamp':'true','max-read-page-bytes':'16MiB','max-read-page-messages':'100'}
capacities={'nk.sync.request':['32MiB','50','224MiB','450'],'nk.sync.reply.web':['32MiB','50','224MiB','450'],'nk.async.work':['128MiB','1000','896MiB','9000'],'nk.web.log':['64MiB','1000','192MiB','9000'],'nk.dead.letter':['128MiB','1000','1920MiB','9000'],'nk.expiry':['64MiB','1000','960MiB','9000']}
for name,node in settings.items():
 for k,v in shared.items():assert node.findtext(tag(k))==v
 assert [node.findtext(tag(k)) for k in ['max-size-bytes','max-size-messages','page-limit-bytes','page-limit-messages']]==capacities[name]
acceptors=core.find(tag('acceptors'));assert len(acceptors)==1 and acceptors[0].text=='tcp://127.0.0.1:61616?protocols=CORE'
security=core.find(tag('security-settings'));deny=[n for n in security if n.get('match')=='#'];assert len(deny)==1 and len(deny[0])==0
acl={n.get('match'):{p.get('type'):p.get('roles').split(',') for p in n} for n in security if n.get('match') in settings}
assert acl['nk.sync.request']['send']==['nk_web'] and acl['nk.sync.request']['consume']==['nk_api'] and acl['nk.sync.reply.web']['send']==['nk_api'] and acl['nk.sync.reply.web']['consume']==['nk_web']
spec=R/'evidence/01_PT/005_NK-MSG-001/001_NK-MSG-001_単体テスト仕様書.md';lines=spec.read_text().splitlines();specRefs={id:[i+1 for i,l in enumerate(lines) if l.startswith('| '+id+' |')][0] for id in ['PT-JMS-001','PT-JMS-002']}
inv=load(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json');ids=['MQ-001','MQ-002','MQ-003','MQ-004','MQ-005','MQ-011','MQ-012','MQ-013'];reqs=[]
delegation={'MQ-001':'P005 request/reply implementation + N04 actual connection','MQ-002':'P005-02 correlation registry/reply races, not a topology enum behavior','MQ-003':'P004 Inbox/Outbox + P005/P006 actual async dispatch','MQ-004':'P007 API session/role and P004 transaction owners; N03/N04 real path','MQ-005':'P004 application router and domain facade owners','MQ-011':'P001/P002 fixed byte codec and P005 BytesMessage; topology checks do not prove no ObjectMessage at runtime','MQ-012':'C03/C04 endpoint/credential-reference/timeouts; do not read actual credential values','MQ-013':'N04 effective acceptor/console/JMX + N05 firewall; XML loopback CORE only is not full management exposure proof'}
for r in inv['requirements']:
 if r['id'] in ids:
  assert r['requirement'] in (R/r['source']).read_text().splitlines()[r['line']-1]
  reqs.append(dict(id=r['id'],expected=r['requirement'],owner=r['owner'],source=r['source'],line=r['line'],coveredHere='STATIC_CATALOG_AND_CONFIGURATION_PREPARATION_ONLY',remainingOwner=delegation[r['id']],accepted=False))
assert len(reqs)==8
assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',sourcePins={p:sha(R/p) for p in [main,test]},design=dict(path=str(ss.relative_to(R)),sha256=sha(ss)),brokerTemplate=dict(path=str(broker.relative_to(R)),sha256=sha(broker)),vectors=[dict(enum=n,address=a,queue=a+'.q',maximumBytes=size,ttlMillis=ttl) for n,a,size,ttl in vectors],globalSettings=globalsExpected,addressSharedSettings=shared,capacitySettings=capacities,staticRoleAcl=acl,requirementMappings=reqs,specReferences=specRefs,existingBrokerTopologyTestsReferenced=2,existingProtocolProof=dict(path=str(original.relative_to(R)),sha256=sha(original)),configuredAddressCount=6,PTJMS001Executed=False,PTJMS002Executed=False,xmlWellformedAndLiteralChecks=True,vendorSchemaValidated=False,brokerManagementQueried=False,liveDurableRoutingOrAclVerified=False,managementConsoleJmxBindingVerified=False,actualUnitServiceDbOrBrokerOperations=0,productTestsExecuted=0,newCoverageMeasurements=0,newAcceptance=0,C04WholeAccepted=False,P00501Accepted=False,formalUpdated=False,effortRate=None,unclosedConditions=['N04 authentic broker/schema/effective address queue durable/ACL/routing/duplicate/retry management postconditions.','Management console and JMX binding plus external firewall not inferred from CORE XML.','MQ001..005 application correlation/session/route/async contracts remain with their canonical owners.'],toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,requirements=8,addresses=6,productTestsExecuted=0,vendorSchemaValidated=False,manifestSha256=sha(O/'manifest.json'))))
