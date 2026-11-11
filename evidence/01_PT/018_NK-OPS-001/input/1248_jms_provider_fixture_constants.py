"""BUG2662 only literal names; exact inverse confirms every old/new test token and value."""
from pathlib import Path
import hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';before=json.loads((B/'evidence/PG26483-provider-fixture-literals-before-v1/manifest.json').read_text());out=B/'evidence/PG26488-provider-fixture-literals-manufacture-v1';assert not out.exists();out.mkdir();results=[]
for entry in before['before']:
 p=R/entry['path'];old=p.read_text();assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'];mapping={'"propertyExists"':'PROPERTY_EXISTS_METHOD','"getStringProperty"':'STRING_PROPERTY_METHOD','"synthetic provider failure"':'PROVIDER_FAILURE','"JMSXDeliveryCount"':'DELIVERY_COUNT_PROPERTY'}
 if '/api/' in entry['path']:mapping.update({'"NKLayoutID"':'LAYOUT_ID_PROPERTY','"NKProtocolVersion"':'VERSION_PROPERTY'})
 new=old
 for literal,name in mapping.items():assert name not in old;new=new.replace(literal,name)
 block=''.join('  private static final String '+name+' = '+literal+';\n' for literal,name in mapping.items());anchor='  private static final String BODY_FIELD';assert new.count(anchor)==1;new=new.replace(anchor,block+anchor)
 inverse=new.replace(block,'')
 for literal,name in mapping.items():inverse=inverse.replace(name,literal)
 assert inverse==old
 fmt=TC/'google-java-format-1.36.1-all-deps.jar'
 if not fmt.exists():fmt=next(TC.rglob(fmt.name))
 f=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(fmt),'-'],input=new,text=True,capture_output=True);assert f.returncode==0,f.stderr;p.write_text(f.stdout);results.append(dict(path=entry['path'],beforeSha256=entry['sha256'],afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),inverseAllTokensExactlyOriginal=True,constants=mapping,valuesChanged=False))
(out/'manifest.json').write_text(json.dumps(dict(actualExit=0,results=results,productTestsExecuted=0,mainUnchanged=True),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,files=2,allInverseExact=True)))
