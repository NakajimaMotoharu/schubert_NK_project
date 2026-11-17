"""Source namespace/API and exact old/new class universes. javap only, no class definition."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess

r=Path.cwd(); b=r/'evidence/01_PT/018_NK-OPS-001'; w=r.parent/'pgpt-runs/PG379'
load=lambda p:json.loads(p.read_text()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=load(b/'evidence/PG37428-inventory-four-main-compile-v1/manifest.json')['physicalClassHashes']['protocol']
prep=load(b/'evidence/PG37646-ssc452-grammar-prepare-v2/manifest.json'); new=prep['physicalClassHashes']
before=w/'pg37428-inventory-four-main-compile-v1/snapshot/src/schubert-nk-protocol/target/classes'
after=w/'pg37646-ssc452-grammar-v2/component'
removed=sorted(set(old)-set(new)); added=sorted(set(new)-set(old))
assert len(old)==175 and len(new)==176
assert removed==sorted('dev/codex/schubert/nk/protocol/'+n+'$1.class' for n in ['codec/PayloadCodec','file/MediaDescriptorValidator','layout/LayoutFieldCatalog'])
assert added==sorted(['dev/codex/schubert/nk/protocol/'+n+'Rules.class' for n in ['codec/FieldCodec','file/MediaDescriptorValidator','layout/PayloadSemanticValidator']]+['dev/codex/schubert/nk/protocol/file/LargeResultDigest.class'])
common=sorted(set(old)&set(new))
assert all(sha(before/n)==old[n] and sha(after/n)==new[n] for n in common)
names=[n[:-6].replace('/','.') for n in common]
out=b/'evidence/PG37658-ssc452-grammar-abi-v3'; assert not out.exists(); out.mkdir()
def run(label,root):
    p=subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/javap'),'-public','-s','-classpath',str(root),*names],capture_output=True,timeout=90)
    (out/(label+'.stdout')).write_bytes(p.stdout); (out/(label+'.stderr')).write_bytes(p.stderr)
    assert p.returncode==0
    return re.sub(r'public final class (dev\.codex\.schubert\.nk\.protocol\.(?:codec\.FieldCodec|file\.(?:LargeResultRecordCodec|MediaDescriptorValidator)|layout\.PayloadSemanticValidator)) \{',r'public interface \1 {',p.stdout.decode())
a=run('before',before); z=run('after',after)
assert a==z, 'Only four explicit public type-kind changes are permitted; all static descriptors exact'
own=[n for n in common if old[n]!=new[n]]
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalPhysical=175,currentPhysical=176,common172PublicAbiExactExceptFourDeclaredTypeKinds=True,removedSyntheticMaps=removed,addedNonPublicGrammarInterfaces=added,physicalChanged=len(own),physicalChangedNames=own,commonByteUnchanged=len(common)-len(own),publicMethodDescriptorsChanged=0,privateReflection=False,productionClassesDefined=0,testsExecuted=0,newAcceptance=0,files={p.name:sha(p) for p in out.iterdir()})
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print({k:v[k] for k in ['actualExit','publicMethodDescriptorsChanged','physicalChanged','commonByteUnchanged']})
