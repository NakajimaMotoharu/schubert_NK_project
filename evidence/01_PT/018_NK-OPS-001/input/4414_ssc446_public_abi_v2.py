"""Compare real public record ABI and all unchanged class bytes without defining product classes."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=ld(b/'input/4409_ssc446_profile_v2.json');newp=r/c['slots']['prepare']/'manifest.json';new=ld(newp);oldp=b/'evidence/PG36483-protocol-aggregate-post-join-v4/manifest.json';old=ld(oldp);assert new['actualExit']==0 and new['productionCoreMain']==c['productionCoreMain']
parent='dev/codex/schubert/nk/protocol/layout/FieldDefinition.class';removed='dev/codex/schubert/nk/protocol/layout/FieldDefinition$1.class'
assert set(old['physicalClassHashes'])-set(new['physicalClassHashes'])=={removed} and not set(new['physicalClassHashes'])-set(old['physicalClassHashes'])
changed=[n for n,h in new['physicalClassHashes'].items() if old['physicalClassHashes'][n]!=h];assert changed==[parent]
for n in set(old['physicalClassHashes'])|set(new['physicalClassHashes']):policy.relative_name(n)
newdir=r.parent/'pgpt-runs/PG379'/c['privateDirs']['prepare']/'component';oldc=ld(b/'input/4387_protocol_aggregate_profile_v4.json');olddir=r.parent/'pgpt-runs/PG379'/oldc['privateDirs']['prepare']/'component'
assert all(sha(newdir/n)==h for n,h in new['physicalClassHashes'].items())
assert all(sha(olddir/n)==h for n,h in old['physicalClassHashes'].items())
e=b/'evidence/PG36566-ssc446-field-padding-public-abi-v2';e.mkdir();outputs=[]
for label,folder in [('old',olddir),('new',newdir)]:
 result=subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/javap'),'-classpath',str(folder),'-public','-s','dev.codex.schubert.nk.protocol.layout.FieldDefinition'],capture_output=True,text=True,timeout=30);assert result.returncode==0 and not result.stderr;path=e/(label+'-public.txt');path.open('x').write(result.stdout);outputs.append(result.stdout)
assert outputs[0]==outputs[1]
v=dict(actualExit=0,productionCoreMain=c['productionCoreMain'],oldPost=ref(oldp),newPrepare=ref(newp),publicRecordAbiExact=True,parentChangedOnly=True,actualRemovedCompilerMap=removed,other174PhysicalClassesByteExact=True,oldPhysical=176,newPhysical=175,oldSourceOrExecSuccessTransferred=False,productClassesDefinedOrInitialized=0,applicationTestsExecuted=0,files=[ref(e/'old-public.txt'),ref(e/'new-public.txt')]);(e/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,publicAbiExact=True,other174SameByte=True,compilerMapActuallyNotGenerated=True)))
