"""Independent immutable resource proof qualification, without original test replay."""
from pathlib import Path
import datetime, hashlib, json, subprocess, zipfile
r=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
p=r/'evidence/01_PT/016_NK-WEB-002/evidence/PG21840-three-current-resources-existing-proof-trace-v1/manifest.json';assert sha(p)=='e3c17bfae5ee5b1157981b27849e2e13eef6481269d970a385a0e2f141b10d0a';m=load(p)
assert m['actualExit']==0 and m['newProductTests']==0 and not m['renderingRepeated'] and not m['currentCombinedRun'] and not m['oldJavaQualificationTransferred'] and m['javaCoverage'] is None
normalp=Path(m['normalManifest']['path']);assert sha(normalp)==m['normalManifest']['sha256'];normal=load(normalp);assert normal['actualExit']==0 and normal['source']==m['productionCoreMain'] and normal['jars']['web']==m['normalWebJar']
jar=m['normalWebJar'];assert sha(Path(jar['path']))==jar['sha256'];dp=r/m['descriptor']['path'];assert sha(dp)==m['descriptor']['sha256'];expected={a['path']:a for a in load(dp) if a['kind']!='JAVA'}
assert set(expected)=={a['path'] for a in m['rows']} and len(expected)==3
with zipfile.ZipFile(jar['path']) as z:
 for row in m['rows']:
  n=row['path'];assert sha(r/n)==hashlib.sha256(z.read(row['resource'])).hexdigest()==row['sha256']==expected[n]['currentSha256']
  assert row['owner']==row['costOwner']==expected[n]['owner'] and row['normalJarEntryVerified'] and not row['currentCombinedRun']
  original=r/row['originalProof']['path'];assert sha(original)==row['originalProof']['sha256'];old=load(original)
  assert old['actualExit']==old['failures']==old['errors']==old['skipped']==old['aborted']==0
  assert row['details']['javaCoverage'] is None
  if row['resource'].endswith('.css'):
   assert old['tests']==row['details']['originalTests']==7 and old['actualCssSha256']==row['sha256']
   assert old['ruleContractsMatched']==row['details']['ruleContracts']==16 and old['propertiesMatched']==row['details']['properties']==62
   assert row['originalTestIdSet']==['PT-STYLE-PORT%03d'%i for i in range(1,8)]
  else:
   assert old['tests']==row['details']['originalTests']==8 and old['resourceHashes'][row['resource']]==row['sha256'] and old['snapshotCount']==row['details']['domSnapshots']==17
   assert row['originalTestIdSet']==['PT-QST-DOM%03d'%i for i in range(1,9)]
for ref in m['independentOracleSpecifications']:assert sha(r/ref['path'])==ref['sha256']
for key in ['cssOriginalProductManifest','cssOriginalResult']:
 ref=m[key];assert sha(r/ref['path'])==ref['sha256']
assert len(m['htmlOriginalTestMethods'])==8 and len(m['cssOriginalXmlMethods'])==7 and m['historicalInvocationsReferenced']==15
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest()==sha(Path(__file__))
out=r/'evidence/01_PT/016_NK-WEB-002/evidence/PG21842-three-resources-trace-independent-post-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,checkerSha256=sha(Path(__file__)),observerSource=m['observerSource'],productionCoreMain=m['productionCoreMain'],original=dict(path=str(p.relative_to(r)),sha256=sha(p)),boundResources=3,historicalHtmlTests=8,historicalDomSnapshots=17,historicalCssTests=7,historicalCssRules=16,historicalCssProperties=62,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,currentCombinedRun=False,oldJavaQualificationTransferred=False,javaCoverage=None,renderingRepeated=False,wholeG13Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,boundResources=3,newProductTests=0,manifestSha256=sha(out/'manifest.json'))))
