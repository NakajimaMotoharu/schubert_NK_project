"""Verify two real public API surfaces and every other physical byte without defining classes."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
config=b/'input/4425_ssc447_profile.json';c=ld(config);np=r/c['slots']['prepare']/'manifest.json';new=ld(np);op=b/'evidence/PG36563-ssc446-field-padding-post-join-v2/manifest.json';old=ld(op);assert new['actualExit']==0 and new['config']==ref(config)
assert all(sha(r/n)==h==hashlib.sha256(subprocess.check_output(['git','show',c['productionCoreMain']+':'+n])).hexdigest() for n,h in new['inputHashes'].items())
parents={'dev/codex/schubert/nk/protocol/layout/TypedFieldValues.class','dev/codex/schubert/nk/protocol/time/JstWireTimestamp.class'};assert set(new['physicalClassHashes'])==set(old['physicalClassHashes']) and len(new['physicalClassHashes'])==175
changed={n for n,h in new['physicalClassHashes'].items() if old['physicalClassHashes'][n]!=h};assert changed==parents
for n in new['physicalClassHashes']:policy.relative_name(n)
newdir=r.parent/'pgpt-runs/PG379'/c['privateDirs']['prepare']/'component';oc=ld(b/'input/4409_ssc446_profile_v2.json');olddir=r.parent/'pgpt-runs/PG379'/oc['privateDirs']['prepare']/'component';assert all(sha(newdir/n)==h for n,h in new['physicalClassHashes'].items()) and all(sha(olddir/n)==h for n,h in old['physicalClassHashes'].items())
e=b/'evidence/PG36626-ssc447-cache-owners-public-abi-v1';e.mkdir();files=[]
for name in sorted(parents):
 values=[]
 for label,folder in [('old',olddir),('new',newdir)]:
  result=subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/javap'),'-classpath',str(folder),'-public','-s',name.removesuffix('.class').replace('/','.')],capture_output=True,text=True,timeout=30);assert result.returncode==0 and not result.stderr;path=e/(Path(name).stem+'-'+label+'-public.txt');path.open('x').write(result.stdout);values.append(result.stdout);files.append(ref(path))
 assert values[0]==values[1]
v=dict(actualExit=0,productionCoreMain=c['productionCoreMain'],oldPost=ref(op),newPrepare=ref(np),twoPublicApisExact=True,onlyTwoParentClassesChanged=sorted(parents),other173PhysicalClassesByteExact=True,physicalClasses=175,publicStaticFieldExposureAdded=False,productClassesDefinedOrInitialized=0,applicationTestsExecuted=0,files=files);(e/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,publicApis=2,other173SameByte=True,physical175=True)))
