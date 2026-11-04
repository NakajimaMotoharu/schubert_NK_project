from pathlib import Path
import ast,copy,hashlib,json,re,subprocess,shutil,xml.etree.ElementTree as E
from source_evidence_binding import bind
R=Path('/home/mini/codex/project1/work/pgpt-foundation');S=Path(__file__).parent;D=R/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104';O=R/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18622-dlq-sender-unit-v1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def record(pairs):
 assert len(pairs)==len({k for k,v in pairs});return dict(pairs)
try:record([('source','x'),('source','y')])
except AssertionError:duplicateRejected=True
else:raise AssertionError('duplicate key accepted')
for n in ast.walk(ast.parse(Path(__file__).read_text())):
 if isinstance(n,ast.Call):
  fields=[k.arg for k in n.keywords if k.arg is not None];assert len(fields)==len(set(fields))
raw=json.loads((S/'manifest.safe.json').read_text());assert H(S/'manifest.safe.json')=='9162b357376134498b7af41e9d5898741514572a7ea42889abb17bee17e3b056';assert raw['actualExit']==0;source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c';point='c8c76df775646e0c92f76595b3b01d55cc8b283c';assert raw['source']==source and raw['testSource']==point;b=raw['begin'];test=R/b['testInputPath'];assert H(test)==b['testInputHash']=='9ef8751b3436c130040668acb0ae1184ee29bac1c9d88ee6ee911794279b0824';assert subprocess.check_output(['git','show',point+':'+b['testInputPath']],cwd=R)==test.read_bytes();assert subprocess.check_output(['git','show',source+':'+b['mainInputPath']],cwd=R)==(R/b['mainInputPath']).read_bytes();assert H(R/b['mainInputPath'])==b['mainInputHash']
for key in ['dependencies','sdkDependencies','toolHashes']:assert all(H(p)==h for p,h in b[key].items())
assert all(s['actualExit']==0 and not s['timedOut'] for s in raw['stages']);assert H(S/'jacoco.exec')==raw['execSha256'];assert all(H(S/'xml'/n)==h for n,h in raw['xml'].items())
classname='dev.codex.schubert.nk.api.messaging.outbound.DlqSenderContractTest';expected={(classname,n) for n in re.findall(r'@Test\s+void\s+(\w+)',test.read_text())};assert len(expected)==8;cases=[];roots=[];env={}
for n in raw['xml']:
 root=E.parse(S/'xml'/n).getroot();roots.append((n,root));assert int(root.get('tests'))==len(root.findall('testcase')) and all(int(root.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for c in root.findall('testcase'):
  assert c.get('name').endswith('()') and not any(x.tag in ['failure','error','skipped'] for x in c);cases.append((c.get('classname'),c.get('name')[:-2]))
 for v in root.findall('properties/property'):
  if v.get('name') in ['os.name','os.arch','os.version','java.version','java.runtime.version','java.vendor']:env[v.get('name')]=v.get('value')
assert len(cases)==len(set(cases))==8 and set(cases)==expected
cov=E.parse(S/'coverage.xml').getroot();target='dev/codex/schubert/nk/api/messaging/outbound/DlqSender';assert [c.get('name') for c in cov.findall('.//class')]==[target];counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in cov.findall('counter')};assert all(counters[k]=={'missed':0,'covered':v} for k,v in [('LINE',63),('METHOD',10),('CLASS',1),('BRANCH',24)]);sessions=cov.findall('sessioninfo');assert len(sessions)==1 and sessions[0].get('id')==b['session'];executed=re.findall(r'^([0-9a-f]{16})\s+\d+ of\s+\d+\s+(dev/[^\s]+)$',(S/'execinfo.stdout').read_text(),re.M);analyzed=re.findall(r'class 0x([0-9a-f]{16})\s+(dev/[^\s]+)',(S/'classinfo.stdout').read_text());assert executed==analyzed==[('4949ef444abc9015',target)];assert all(H(S/'component'/(n+'.class'))==h for n,h in b['physical'].items())
initlines=(S/'class-init.log').read_text().splitlines()
def names(prefix):
 return sorted({m.group(1).replace('/','.') for line in initlines if (m:=re.search(r"Initializing '[^']*?("+prefix+r"[^']+)'",line)) and '$$Lambda' not in m.group(1) and 'DlqSenderContractTest' not in m.group(1)})
initialized=names('dev/codex/schubert/');api=[n for n in initialized if n.startswith('dev.codex.schubert.nk.api.')];assert api==['dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage','dev.codex.schubert.nk.api.messaging.outbound.DlqSender','dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMessageWriter','dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata','dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata$DetectedBy'];assert all(n in api or n.startswith('dev.codex.schubert.nk.protocol.') for n in initialized)
sdk=names('org/apache/activemq/artemis/');assert sdk==['org.apache.activemq.artemis.api.core.ParameterisedAddress','org.apache.activemq.artemis.api.core.SimpleString','org.apache.activemq.artemis.jms.client.ActiveMQDestination','org.apache.activemq.artemis.jms.client.ActiveMQDestination$TYPE','org.apache.activemq.artemis.jms.client.ActiveMQQueue','org.apache.activemq.artemis.jndi.JNDIStorable','org.apache.activemq.artemis.utils.uri.URISupport']
staticfile=R/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18618-dlq-sender-pg-static-v1/manifest.json';static=json.loads(staticfile.read_text());assert static['begin']['testInputHash']==b['testInputHash'] and static['checkstyleFindings']==[] and len(static['pmdFindings'])==2
baseline=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18472-current3008-resource-owner-domains-v1/manifest.json';old=json.loads(baseline.read_text());assert not set(cases)&{(c['classname'],c['name'].removesuffix('()')) for c in old['cases']}
result=record([('actualExit',0),('source',source),('testSource',point),('proofKind','WHOLE_DLQ_SENDER_CALLBACK_UNIT_NOT_REAL_BROKER_COMPATIBILITY'),('inputProvenance',b),('actualStages',raw['stages']),('originalManifestSha256',H(S/'manifest.safe.json')),('environment',env),('tests',8),('testClasses',1),('junitXmlSuites',len(roots)),('literalVectors',135),('cases',[dict(classname=c,name=m,result='PASS') for c,m in sorted(cases)]),('failures',0),('errors',0),('skipped',0),('aborted',0),('counters',counters),('session',b['session']),('execSha256',raw['execSha256']),('crc',executed),('crcMismatch',0),('physical',b['physical']),('physicalClosureComplete',True),('counterExclusions',[]),('oldExecCombined',False),('initializedProductClasses',initialized),('initializedSdkValueClasses',sdk),('unexpectedInitialized',[]),('static',dict(manifestSha256=H(staticfile),pmdRaw=2,processingErrors=0,checkstyle=0,localApplicability=static['localApplicability'],wholeF03Accepted=False)),('actualBusinessResourceOperations',dict(provider=False,broker=False,jdbc=False,root=False,vm=False,native=False,keys=False,credentials=False,sessionIssued=False)),('actualBrokerTtlAckCommitCompatibility','NOT_TESTED'),('canonicalOwner','WBS-P005-03'),('canonicalCostOwner','WBS-P005-03'),('oldRegistrySha256',H(baseline)),('oldCaseOverlap',0),('registryUpdated',False),('eligibleUnmerged',dict(uniqueMethods=4,testClasses=1,wholeSources=1,physicalClasses=1)),('newWbsAccepted',0),('formalUpdated',False),('whole451Accepted',False),('effortPercent',None),('firstVChanged',False),('postProductTestsReexecuted',0)])
def assess(x):
 assert x['source']==source and x['testSource']==point and x['tests']==8 and x['failures']==x['errors']==x['skipped']==x['aborted']==0
 assert len(x['cases'])==len({(c['classname'],c['name']) for c in x['cases']})==8 and {(c['classname'],c['name']) for c in x['cases']}==expected
 assert x['session']==b['session'] and x['crcMismatch']==0 and not x['oldExecCombined'] and not x['formalUpdated'] and not x['unexpectedInitialized'];assert all(x['counters'][k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
assess(result);negative=[]
for label,change in [('source',lambda x:x.update(source='0'*40)),('testSource',lambda x:x.update(testSource='0'*40)),('duplicate',lambda x:x['cases'].__setitem__(1,copy.deepcopy(x['cases'][0]))),('skipped',lambda x:x.update(skipped=1)),('session',lambda x:x.update(session='other')),('crc',lambda x:x.update(crcMismatch=1)),('union',lambda x:x.update(oldExecCombined=True)),('branch',lambda x:x['counters']['BRANCH'].update(missed=1)),('formal',lambda x:x.update(formalUpdated=True)),('unknownInit',lambda x:x.update(unexpectedInitialized=['UNKNOWN']))]:
 bad=copy.deepcopy(result);change(bad)
 try:assess(bad)
 except AssertionError:negative.append(label)
 else:raise AssertionError(label)
assert not O.exists();O.mkdir();(O/'xml').mkdir()
for n,r in roots:
 clean=E.Element('testsuite',{k:v for k,v in r.attrib.items() if k in ['name','tests','failures','errors','skipped','time','timestamp']})
 for c in r.findall('testcase'):E.SubElement(clean,'testcase',{k:v for k,v in c.attrib.items() if k in ['classname','name','time']})
 E.ElementTree(clean).write(O/'xml'/n,encoding='utf-8',xml_declaration=True)
for n in ['coverage.xml','coverage.csv','post.py']:shutil.copyfile(S/n,O/n)
result.update(negativeMetadata=negative,duplicateFieldNegativeRejected=duplicateRejected,postBodySha256=H(__file__),files={str(p.relative_to(O)):H(p) for p in O.rglob('*') if p.is_file()});write(O/'manifest.json',result)
p=D/'678_DLQ原八PT135vector・全Source四counterと独立post.json';assert not p.exists();write(p,record([('actualExit',0),('source',source),('testSource',point),('sourceEvidenceRefs',bind([(O/'manifest.json',H(O/'manifest.json'))],source)),('publicManifestSha256',H(O/'manifest.json')),('actualUnitTerminal','61420/8b0f98/0'),('counters',counters),('session',b['session']),('crcMismatch',0),('wholeSourcePhysical',1),('negativeMetadata',negative),('duplicateFieldNegativeRejected',duplicateRejected),('postProductTestsReexecuted',0),('newWbsAccepted',0),('formalUpdated',False)]))
print(json.dumps(dict(actualExit=0,tests=8,counters=counters,publicManifestSha256=H(O/'manifest.json'),postSha256=H(p),negativeChecks=len(negative)),ensure_ascii=False))
