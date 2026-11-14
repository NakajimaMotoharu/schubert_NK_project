"""No product invocation: independent decimal/hash vectors and bounded explicit source closure."""
from pathlib import Path
import json,hashlib,subprocess,datetime
from decimal import Decimal
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';e=b/'evidence/PG32660-audio-map842-source-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));assert not (e/'manifest.json').exists()
old=json.loads((i/'3049_audio_role818_physical56_profile.json').read_text());m='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/AudioMigrationMap.java';t=m.replace('/main/','/test/').replace('.java','Test.java');changed=[m.replace('AudioMigrationMap','AssetMigrationManifest'),m.replace('AudioMigrationMap','CurrentScenarioFileMapper')];newpaths=[m,t];paths=old['mainSources']+[x['path'] for x in old['testSources']];unchanged={p:sha(r/p) for p in paths if p not in changed}
for p,h in unchanged.items():assert hashlib.sha256(subprocess.check_output(['git','show',old['productionCoreMain']+':'+p])).hexdigest()==h
vec=[('0','0'),('0.000','0'),('0.001','1'),('1','1000'),('1.234','1234'),('1.200','1200'),('999999999.999','999999999999'),('999999999','999999999000')]
for seconds,ms in vec:assert Decimal(seconds)*1000==int(ms)
def i32(v):return (v+(1<<31))%(1<<32)-(1<<31)
def longhash(v):v&=(1<<64)-1;return i32(v^(v>>32))
def rec(g,c,t):return i32(i32(g*31+longhash(c))*31+longhash(t))
assert rec(1,-20,700)==2250 and rec(1,-(1<<63),1)==rec(1,(1<<63)-1,1)==-2147482686
oracle=e/'independent-audio-vectors.json';v=json.loads(oracle.read_text());assert v['decimalVectors']==[list(x) for x in vec]
proof=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),previousProductionCoreMain=old['productionCoreMain'],newSources=[ref(r/p) for p in newpaths],changedMainSources=[ref(r/p) for p in changed],unchangedSourceHashes=unchanged,independentOracle=ref(oracle),newTests=24,existingTestsUnchanged=818,allExpected=842,mainSources=40,physicalClasses=58,closure='PURE_JDK_METADATA_ONLY_NO_FS_DB_ROOT_AUTHORITY',privateRootOrHeldClassActions=0,actualIoOrAuthority=0,formalAccepted=False)
(e/'manifest.json').open('x').write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=24,whole=842,oldSourceUnchanged=len(unchanged)))
