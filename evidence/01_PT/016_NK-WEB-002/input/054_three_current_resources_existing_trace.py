"""Read-only three-resource/Git/JAR/original-proof binding; no rendering or tests."""
from pathlib import Path
import datetime, hashlib, json, subprocess, zipfile
import xml.etree.ElementTree as ET
r=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
normalp=r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json';assert sha(normalp)=='1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618';normal=load(normalp);assert normal['actualExit']==0 and normal['source']=='4217e14083c6ecac116216e08d57f4361eb2f12d';jar=normal['jars']['web'];assert sha(Path(jar['path']))==jar['sha256']
dp=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21766-current4217-static-artifact-lineage-v2/changed-artifacts.json';descriptors={x['path']:x for x in load(dp) if x['kind']!='JAVA'};assert len(descriptors)==3
htmlp=r/'evidence/01_PT/016_NK-WEB-002/evidence/PG20596-question-return-fixed-resource-eight-v1/manifest.json';assert sha(htmlp)=='585a6bc67516caa539e19f5863040b34f6ab4658689b725c258e5852b866cac6';html=load(htmlp);assert html['actualExit']==html['failures']==html['errors']==html['skipped']==html['aborted']==0 and html['tests']==8 and html['snapshotCount']==17
for n,h in html['inputHashes'].items():assert sha(r/n)==h
for n,h in html['files'].items():
 if n in ['testcases.safe.xml','coverage.xml','original-manifest.json','unit-exit.safe.json','begin.json']:assert sha(htmlp.parent/n)==h
cssdir=r/'evidence/01_PT/016_NK-WEB-002/evidence/PG20706-new-media-css-green-v1';css=load(cssdir/'manifest.json');cssraw=load(cssdir/'manifest.safe.json');csspostp=r/'evidence/01_PT/016_NK-WEB-002/evidence/PG20708-media-css-independent-post-v1/manifest.json';assert sha(csspostp)=='595a6cd78a042393475d0f653736544cf870b2bfecd1dca9a5f9970cc441f9d1';csspost=load(csspostp)
assert css['actualExit']==cssraw['actualExit']==csspost['actualExit']==0 and cssraw['tests']==csspost['tests']==7
assert csspost['failures']==csspost['errors']==csspost['skipped']==csspost['aborted']==0 and csspost['ruleContractsMatched']==16 and csspost['propertiesMatched']==62
assert sha(cssdir/'manifest.safe.json')==css['files']['manifest.safe.json']==csspost['greenManifestSha256']
for n in ['results/manifest.json','results/tests.xml','actual-css.css']:assert sha(cssdir/n)==css['files'][n]
cssresult=load(cssdir/'results/manifest.json');cssxml=ET.parse(cssdir/'results/tests.xml');cases=[(t.get('classname'),t.get('name')) for t in cssxml.getroot().iter('testcase')];assert len(cases)==7
assert all(not any(t.find(n) is not None for n in ['failure','error','skipped']) for t in cssxml.getroot().iter('testcase'))
rows=[]
with zipfile.ZipFile(jar['path']) as z:
 for n,a in sorted(descriptors.items()):
  resource=n.split('/src/main/resources/',1)[1];h=hashlib.sha256(z.read(resource)).hexdigest();assert h==a['currentSha256']==sha(r/n);assert hashlib.sha256(subprocess.check_output(['git','show',normal['source']+':'+n])).hexdigest()==h
  if resource.endswith('.css'):
   assert h==csspost['actualCssSha256']==sha(cssdir/'actual-css.css');proof=dict(path=str(csspostp.relative_to(r)),sha256=sha(csspostp));ids=['PT-STYLE-PORT%03d'%i for i in range(1,8)];details=dict(originalTests=7,ruleContracts=16,properties=62,javaCoverage=None,oldPrefixPreserved=csspost['oldPrefixBytesPreserved'])
  else:
   assert html['resourceHashes'][resource]==h;proof=dict(path=str(htmlp.relative_to(r)),sha256=sha(htmlp));ids=['PT-QST-DOM%03d'%i for i in range(1,9)];details=dict(originalTests=8,domSnapshots=17,javaCoverage=None)
  rows.append(dict(path=n,resource=resource,sha256=h,owner=a['owner'],costOwner=a['costOwner'],normalJarEntryVerified=True,originalProof=proof,originalTestIdSet=ids,details=details,currentCombinedRun=False))
 for resource,h in html['resourceHashes'].items():assert hashlib.sha256(z.read(resource)).hexdigest()==h
spec=r/'evidence/01_PT/016_NK-WEB-002/147_変更三resource現source既証拠trace仕様.md';specs=[r/'evidence/01_PT/016_NK-WEB-002/134_質問入力受付menu戻り先・資源単体仕様.md',r/'evidence/01_PT/016_NK-WEB-002/145_動画Music表示CSS互換契約・単体仕様.md']
for p in [Path(__file__),spec]:assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(p.relative_to(r))])).hexdigest()==sha(p)
out=r/'evidence/01_PT/016_NK-WEB-002/evidence/PG21840-three-current-resources-existing-proof-trace-v1';assert not out.exists();out.mkdir()
m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=head,productionCoreMain=normal['source'],normalManifest=dict(path=str(normalp),sha256=sha(normalp)),normalWebJar=jar,descriptor=dict(path=str(dp.relative_to(r)),sha256=sha(dp)),rows=rows,htmlOriginalTestMethods=html['testMethods'],cssOriginalXmlMethods=cases,cssOriginalProductManifest=dict(path=str((cssdir/'manifest.json').relative_to(r)),sha256=sha(cssdir/'manifest.json')),cssOriginalResult=dict(path=str((cssdir/'results/manifest.json').relative_to(r)),sha256=sha(cssdir/'results/manifest.json')),independentOracleSpecifications=[dict(path=str(p.relative_to(r)),sha256=sha(p)) for p in specs],historicalInvocationsReferenced=15,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,javaCoverage=None,renderingRepeated=False,currentCombinedRun=False,oldJavaQualificationTransferred=False,wholeG13Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,boundResources=3,newProductTests=0,manifestSha256=sha(out/'manifest.json'))))
