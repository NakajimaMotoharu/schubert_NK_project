"""Bind original63 per-source evidence to current identical bytes; execute no Product code."""
from pathlib import Path
import datetime,hashlib,json,subprocess,zipfile
import xml.etree.ElementTree as ET
r=Path.cwd();load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
oldp=r/'evidence/01_PT/002_NK-PRO-002/evidence/PG19458-qa054-protocol-selected-v1/manifest.json';old=load(oldp);assert old['actualExit']==old['failures']==old['errors']==old['skipped']==0 and old['tests']==63
postp=oldp.parent/old['independentPost']['path'];assert sha(postp)==old['independentPost']['sha256']=='b62ef7a13c2fefb9346603c3f134819178be48357983b2e5f7cfe0e49a131ecc';ind=load(postp)
assert ind['actualExit']==ind['failures']==ind['errors']==ind['skipped']==ind['aborted']==0 and ind['tests']==63 and ind['heldFourInitializationHits']==0 and not ind['manualCoverageExclusions'] and not ind['oldExecUnion']
for name in ['begin.safe.json','unit-exit.safe.json','jacoco.xml','independent-post.safe.json','TEST-junit-jupiter.xml','TEST-junit-vintage.xml','TEST-junit-platform-suite.xml']:assert sha(oldp.parent/name)==old['files'][name]
terminal=load(oldp.parent/'unit-exit.safe.json');assert terminal['actualExit']==0 and not terminal['timedOut']
for name,h in old['inputHashes'].items():
 assert not any(t in name for t in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness'])
 assert hashlib.sha256(subprocess.check_output(['git','show',old['source']+':'+name])).hexdigest()==h
normalp=r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json';assert sha(normalp)=='1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618';normal=load(normalp);assert normal['actualExit']==0
jar=normal['jars']['protocol'];assert sha(Path(jar['path']))==jar['sha256'];sources={n:h for n,h in old['inputHashes'].items() if '/src/main/java/' in n};assert len(sources)==4
desc={a['path']:a for a in load(r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21766-current4217-static-artifact-lineage-v2/artifacts.json')}
rows=[]
for n,h in sources.items():
 assert sha(r/n)==h==normal['begin']['inputHashes'][n]==desc[n]['sha256'];assert desc[n]['owner']==desc[n]['costOwner']
 rows.append(dict(path=n,mainSha256=h,owner=desc[n]['owner'],costOwner=desc[n]['costOwner'],originalSourceFileCounters=old['coverage'][Path(n).name],originalSource=old['source'],currentSameByte=True))
with zipfile.ZipFile(jar['path']) as z:
 for cls,h in old['physicalHashes'].items():assert normal['normalPhysicalClassHashes']['protocol:'+cls+'.class']==h==hashlib.sha256(z.read(cls+'.class')).hexdigest()
 assert len(old['physicalHashes'])==7
synthetic=ind['compilerSyntheticNoCode'];assert set(synthetic)=={'dev/codex/schubert/nk/protocol/codec/PayloadCodec$1','dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog$1'}
# Original independent receipt records compiler flags; exact physical SHA retains those flags.
assert ind['physicalClassHashes']==old['physicalHashes']
tree=ET.parse(oldp.parent/'jacoco.xml');byfile={x.get('name'):{c.get('type'):dict(covered=int(c.get('covered')),missed=int(c.get('missed'))) for c in x.findall('counter')} for x in tree.findall('.//sourcefile')}
for row in rows:
 cs=row['originalSourceFileCounters'];assert byfile[Path(row['path']).name]==cs
 assert all(cs[k]['missed']==0 for k in ['LINE','METHOD','CLASS']) and ('BRANCH' not in cs or cs['BRANCH']['missed']==0)
pairs=[]
for name in ['TEST-junit-jupiter.xml','TEST-junit-vintage.xml','TEST-junit-platform-suite.xml']:
 for node in ET.parse(oldp.parent/name).getroot().iter('testcase'):
  assert not any(node.find(k) is not None for k in ['failure','error','skipped']);pairs.append((node.get('classname'),node.get('name','').removesuffix('()')))
assert len(pairs)==len(set(pairs))==63
spec=r/'evidence/01_PT/002_NK-PRO-002/030_現protocol四source原63証拠結合仕様.md';oracle=r/'evidence/01_PT/002_NK-PRO-002/028_QA054限定ACTION固定長仕様.md'
for p in [spec,Path(__file__)]:assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(p.relative_to(r))])).hexdigest()==sha(p)
out=r/'evidence/01_PT/002_NK-PRO-002/evidence/PG21852-current-protocol-four-source-existing-proof-trace-v1';assert not out.exists();out.mkdir()
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=head,productionCoreMain=normal['source'],original=dict(path=str(oldp.relative_to(r)),sha256=sha(oldp),source=old['source'],productionCoreMain=old['productionCoreMain']),originalIndependentPost=dict(path=str(postp.relative_to(r)),sha256=sha(postp)),normalManifest=dict(path=str(normalp),sha256=sha(normalp)),normalProtocolJar=jar,rows=rows,physicalHashes=old['physicalHashes'],compilerSyntheticDefaultFiltered=synthetic,originalTestMethods=pairs,historicalTestsReferenced=63,originalOracleSpecification=dict(path=str(oracle.relative_to(r)),sha256=sha(oracle)),sourcefileCounterTotal={k:sum(x['originalSourceFileCounters'].get(k,{}).get('covered',0) for x in rows) for k in ['LINE','METHOD','CLASS','BRANCH']},naturalZeroBranchSources=[x['path'] for x in rows if 'BRANCH' not in x['originalSourceFileCounters']],newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,currentCombinedRun=False,singleTestProbeAttributionMeasured=False,wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,boundSources=4,physicalClasses=7,historicalTests=63,newProductTests=0,manifestSha256=sha(out/'manifest.json'))))
