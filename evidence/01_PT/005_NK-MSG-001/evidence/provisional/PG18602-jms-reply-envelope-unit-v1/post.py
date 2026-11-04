from pathlib import Path
import ast,copy,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E
from source_evidence_binding import bind
R=Path('/home/mini/codex/project1/work/pgpt-foundation');S=Path(__file__).parent;D=R/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104';O=R/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18602-jms-reply-envelope-unit-v1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
compile(Path(__file__).read_text(),__file__,'exec')
for n in ast.walk(ast.parse(Path(__file__).read_text())):
 if isinstance(n,ast.Call):
  keys=[k.arg for k in n.keywords if k.arg is not None];assert len(keys)==len(set(keys))
raw=json.loads((S/'manifest.safe.json').read_text());assert H(S/'manifest.safe.json')=='5fe3daffff4dead6fdbfc2e100b0ced9ed08584e8c9a746c1856db86d431da4c';assert raw['actualExit']==0;source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c';testsource='a8afbe30aa044add0504be44233e2fabb114af26';assert raw['source']==source and raw['testSource']==testsource
b=raw['begin'];assert all(H(p)==h for p,h in b['dependencies'].items()) and all(H(p)==h for p,h in b['tools'].items());test=R/b['testInputPath'];assert H(test)==b['testInputHash']=='9187f5a6b40e071a5eec53eb5df476c4147023556f35ac517b338a88e04739c9';assert subprocess.check_output(['git','show',testsource+':'+b['testInputPath']],cwd=R)==test.read_bytes();assert H(S/'jacoco.exec')==raw['execSha256'];assert all(not s['timedOut'] and s['actualExit']==0 for s in raw['stages']);assert all(H(S/'xml'/n)==h for n,h in raw['xml'].items())
classname='dev.codex.schubert.nk.api.messaging.outbound.JmsReplyEnvelopeContractTest';expected={(classname,n) for n in re.findall(r'@Test\s+void\s+(\w+)',test.read_text())};assert len(expected)==4;cases=[];roots=[];env={}
for n in raw['xml']:
 root=E.parse(S/'xml'/n).getroot();roots.append((n,root));assert int(root.get('tests'))==len(root.findall('testcase')) and all(int(root.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for c in root.findall('testcase'):
  assert c.get('name').endswith('()') and not any(x.tag in ['failure','error','skipped'] for x in c);cases.append((c.get('classname'),c.get('name')[:-2]))
 for p in root.findall('properties/property'):
  if p.get('name') in ['os.name','os.arch','os.version','java.version','java.runtime.version','java.vendor']:env[p.get('name')]=p.get('value')
assert len(cases)==len(set(cases))==4 and set(cases)==expected
cov=E.parse(S/'coverage.xml').getroot();name='dev/codex/schubert/nk/api/messaging/outbound/JmsMessageFactory';assert [c.get('name') for c in cov.findall('.//class')]==[name];counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in cov.findall('counter')};assert all(counters[k]=={'missed':0,'covered':v} for k,v in [('LINE',16),('METHOD',2),('CLASS',1),('BRANCH',6)])
methods={(m.get('name'),m.get('desc')) for m in cov.findall('.//class/method')};assert methods=={('createReply','(Ljakarta/jms/JMSContext;[B)Ljakarta/jms/BytesMessage;'),('<clinit>','()V')};sessions=cov.findall('sessioninfo');assert len(sessions)==1 and sessions[0].get('id')==b['session'];executed=re.findall(r'^([0-9a-f]{16})\s+\d+ of\s+\d+\s+(dev/[^\s]+)$',(S/'execinfo.stdout').read_text(),re.M);analyzed=re.findall(r'class 0x([0-9a-f]{16})\s+(dev/[^\s]+)',(S/'classinfo.stdout').read_text());assert executed==analyzed==[('7b2689768bfed517',name)]
for n,h in b['physical'].items():assert H(S/'component'/(n+'.class'))==h
initialized=sorted({m.group(1).replace('/','.') for line in (S/'class-init.log').read_text().splitlines() if (m:=re.search(r"Initializing '[^']*?(dev/codex/schubert/[^']+)'",line)) and '$$Lambda' not in m.group(1) and 'JmsReplyEnvelopeContractTest' not in m.group(1)})
assert [n for n in initialized if n.startswith('dev.codex.schubert.nk.api.')]==[name.replace('/','.')];assert all(n==name.replace('/','.') or n.startswith('dev.codex.schubert.nk.protocol.') for n in initialized)
staticfile=R/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18598-jms-envelope-pg-static-v1/manifest.json';static=json.loads(staticfile.read_text());assert static['source']==source and static['begin']['testInputHash']==b['testInputHash'] and static['pmdRawCount']==3 and static['checkstyleFindings']==0
baseline=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18472-current3008-resource-owner-domains-v1/manifest.json';old=json.loads(baseline.read_text());oldcases={(c['classname'],c['name'].removesuffix('()')) for c in old['cases']};assert not set(cases)&oldcases
result=dict(actualExit=0,source=source,testSource=testsource,proofKind='WHOLE_REPLY_ENVELOPE_FACTORY_UNIT_NOT_REAL_BROKER_COMPATIBILITY',testInputPath=b['testInputPath'],testInputHash=b['testInputHash'],compiledTestClasses=b['compiledTestClasses'],dependencies=b['dependencies'],toolHashes=b['tools'],actualStages=raw['stages'],originalManifestSha256=H(S/'manifest.safe.json'),environment=env,tests=4,testClasses=1,junitXmlSuites=len(roots),literalVectors=26,cases=[dict(classname=c,name=m,result='PASS') for c,m in sorted(cases)],failures=0,errors=0,skipped=0,aborted=0,counters=counters,session=b['session'],execSha256=raw['execSha256'],executedAndAnalyzedCRC=executed,crcMismatch=0,physical=b['physical'],physicalClosureComplete=True,officialGeneratedFilters='JaCoCo0.8.15 default enum/synthetic helpers and implicit enumconstructor filters; handwritten createReply and initialization allcovered. No added method/class/line exclusions.',generatedMethods=['values()','valueOf(String)','$values()','implicit enum constructor'],rawHitProbes='19/21 retained; not reported as21/21; filtered generated code not extra tests',oldExecCombined=False,initializedProductClasses=initialized,unexpectedProductInitialized=[],static=dict(manifestSha256=H(staticfile),pmdRawFindings=3,processingErrors=0,checkstyle=0,localApplicability=static['localApplicability'],wholeF03Accepted=False),scope=dict(actualBroker=False,actualJdbc=False,actualRoot=False,actualVm=False,actualNative=False,actualKeys=False,actualSessionIssued=False,syntheticFormatOnlyContext=True,realJmsTransactionTtlDlqNotTested=True),canonicalOwner='WBS-P005-03',canonicalCostOwner='WBS-P005-03',oldRegistrySha256=H(baseline),oldCaseOverlap=0,registryUpdated=False,eligibleUnmerged=dict(uniqueMethods=4,testClasses=1,wholeSources=1,physicalClasses=1),newWbsAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None,firstVChanged=False,originalRoot18474Terminal='UNRECOVERED',postProductTestsReexecuted=0)
def assess(x):
 assert x['source']==source and x['testSource']==testsource and x['tests']==4
 assert x['failures']==x['errors']==x['skipped']==x['aborted']==0
 assert len(x['cases'])==len({(c['classname'],c['name']) for c in x['cases']})==4 and {(c['classname'],c['name']) for c in x['cases']}==expected
 assert x['session']==b['session'] and x['crcMismatch']==0 and not x['oldExecCombined'] and not x['formalUpdated'];assert not x['unexpectedProductInitialized']
 assert all(x['counters'][k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
assess(result);negative=[]
for label,change in [('source',lambda x:x.update(source='0'*40)),('testsource',lambda x:x.update(testSource='0'*40)),('duplicate',lambda x:x['cases'].__setitem__(1,copy.deepcopy(x['cases'][0]))),('skip',lambda x:x.update(skipped=1)),('session',lambda x:x.update(session='other')),('crc',lambda x:x.update(crcMismatch=1)),('union',lambda x:x.update(oldExecCombined=True)),('branch',lambda x:x['counters']['BRANCH'].update(missed=1)),('formal',lambda x:x.update(formalUpdated=True)),('unknownInitialization',lambda x:x.update(unexpectedProductInitialized=['UNKNOWN']))]:
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
result.update(negativeMetadataLabels=negative,postBodySha256=H(__file__),files={str(p.relative_to(O)):H(p) for p in O.rglob('*') if p.is_file()});put(O/'manifest.json',result)
p=D/'666_JMS返信factory原四PT・一Source全counterと独立post.json';assert not p.exists();put(p,dict(actualExit=0,source=source,testSource=testsource,sourceEvidenceRefs=bind([(O/'manifest.json',H(O/'manifest.json'))],source),publicManifestSha256=H(O/'manifest.json'),actualUnitTerminal='3571/76a55a/0',independentInputGitByteMatch=True,counters=counters,session=b['session'],crcMismatch=0,wholePhysicalSources=1,oldCaseOverlap=0,negativeMetadata=negative,productTestsReexecuted=0,enumDeclarationRead='9361c4 actual0',generatedFilterScope=result['officialGeneratedFilters'],rawProbes='19/21',whole451Accepted=False,newWbsAccepted=0))
print(json.dumps(dict(actualExit=0,tests=4,counters=counters,publicManifestSha256=H(O/'manifest.json'),independentPostSha256=H(p),negativeChecks=len(negative)),ensure_ascii=False))
