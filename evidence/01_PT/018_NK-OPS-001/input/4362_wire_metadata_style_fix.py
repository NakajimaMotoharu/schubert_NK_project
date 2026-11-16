"""Fix only prestyle import/literal defects; preserve the failed fixture and its exact values."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';t=r/'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/WireMetadataValueContractTest.java'
old=t.read_text();assert t.read_bytes()==(b/'evidence/PG36311-wire-metadata-original-style-failure-v1/WireMetadataValueContractTest.java.txt').read_bytes()
imports='\n'.join('import static org.junit.jupiter.api.Assertions.'+s+';' for s in ['assertEquals','assertFalse','assertNotEquals','assertNull','assertThrows','assertTrue'])
new=old.replace('import static org.junit.jupiter.api.Assertions.*;',imports)
constants=''.join('  private static final String '+k+' = "'+v+'";\n' for k,v in [('REQUEST_ADDRESS','request'),('REPLY_ADDRESS','reply'),('MESSAGE_ID','message'),('PROTOCOL_VERSION','001')])
for k,v in [('REQUEST_ADDRESS','request'),('REPLY_ADDRESS','reply'),('MESSAGE_ID','message'),('PROTOCOL_VERSION','001')]:new=new.replace('"'+v+'"',k)
new=new.replace('class WireMetadataValueContractTest {\n','class WireMetadataValueContractTest {\n'+constants)
inverse=new.replace(constants,'').replace(imports,'import static org.junit.jupiter.api.Assertions.*;')
for k,v in [('REQUEST_ADDRESS','request'),('REPLY_ADDRESS','reply'),('MESSAGE_ID','message'),('PROTOCOL_VERSION','001')]:inverse=inverse.replace(k,'"'+v+'"')
assert inverse==old
t.write_text(new)
subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(t)],check=True,timeout=30)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
e=b/'evidence/PG36330-wire-metadata-style-inverse-v2';e.mkdir();mp=e/'manifest.json';mp.open('x').write(json.dumps(dict(actualExit=0,bug='BUG3118',originalFixture=ref(b/'evidence/PG36311-wire-metadata-original-style-failure-v1/WireMetadataValueContractTest.java.txt'),currentFixture=ref(t),inverseBeforeFormatByteExact=True,assertsAndCasesUnchanged=True,newTests=3,mainChanged=0,applicationTestsExecuted=0),indent=2)+'\n')
add=b/'4432_WireMetadata仕様・依存九source補足.md';add.open('x').write('# WireMetadata仕様・依存九source補足\n\n開始時八source見積りを、LayoutIdが例外型LayoutValidationExceptionを参照するため九sourceへ数え直す。業務三class/三case/低標高.25/.75/2.25と上限2.5は不変、必要内部compile closure一sourceだけ補足。Main変更0、compile-time LargeResultDescriptorの未実行counterは未hitで保持、全九をrawへ含む。元開始・仕様の八を上書きせず本補足を追跡する。独立UUID/メッセージ名/hashは全て合成fixtureで実認証情報ではない。\n')
c=json.loads((b/'input/4361_wire_metadata_profile.json').read_text());c.update(id='PG36340-WIRE-METADATA-VALUES-THREE-V2',slots={k:str((b/('evidence/PG'+str(n)+'-wire-metadata-'+k+'-v2')).relative_to(r)) for k,n in [('prestyle',36332),('prepare',36334),('static',36336),('preflight',36338),('unit',36340),('post',36342)]},privateDirs=dict(prepare='pg36334-wire-metadata-values-v2',unit='pg36340-wire-metadata-values-v2'));c['oracleSpecs'].append(ref(add));c['closureProofs'].append(ref(mp));(b/'input/4363_wire_metadata_profile_v2.json').open('x').write(json.dumps(c,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,inverseExact=True,newTests=3,mainSources=9)))
