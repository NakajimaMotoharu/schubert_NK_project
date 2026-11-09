"""Same-run Spring mock/Servlet SDK classfile CRC metadata only, no SDK initialization/test replay."""
from pathlib import Path
import datetime,hashlib,json,re,zipfile
import pg9666_pagination_static as stage
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25986-security-audit-sdk-identity-v1';O=B/'evidence/PG25986-security-audit-sdk-identity-v1';RUN=R.parent/'pgpt-runs/PG379/pg25982-security-audit-original-whole6-v1';assert not S.exists() and not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());rawPath=B/'evidence/PG25982-security-audit-original-whole6-v1/manifest.json';assert sha(rawPath)=='a405ec87297987d27697c73836f39d200ed54c8d8b1141c0e70ce5fc3e58ba3c';m=load(rawPath);assert type(m['actualExit']) is int and m['actualExit']==0 and m['productTestsExecuted']==6;pf=load(R/m['begin']['preflight']['path']);assert sha(R/m['begin']['preflight']['path'])==m['begin']['preflight']['sha256'];jars=pf['vendorJars'];assert len(jars)==2
info=(RUN/'execinfo.stdout').read_text();positive={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and int(hit[2])>0 and hit[4].startswith(('com/google/gson/','io/micrometer/','org/springframework/','jakarta/servlet/','org/apache/catalina/','org/apache/tomcat/','org/apache/juli/','org/apache/commons/logging/')):assert hit[4] not in positive;positive[hit[4]]=hit[1]
assert positive;S.mkdir();classes=S/'classes';classes.mkdir();bindings={}
for name in positive:
 assert re.fullmatch(r'[A-Za-z0-9_/$]+',name) and '..' not in name
 found=[]
 for jar,digest in jars.items():
  assert sha(Path(jar))==digest
  with zipfile.ZipFile(jar) as z:
   if name+'.class' in z.namelist():found.append((jar,digest,z.read(name+'.class')))
 assert len(found)==1,name;jar,digest,data=found[0];target=classes/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);bindings[name]=dict(jar=jar,jarSha256=digest,classSha256=hashlib.sha256(data).hexdigest(),observedCrc64=positive[name])
TC=R.parent/'toolchain';java=TC/'jdk-25.0.4/bin/java';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';assert sha(java)==pf['dependencies'][str(java)] and sha(cli)==pf['dependencies'][str(cli)];stage.SLOT=S;result=stage.step('classinfo-sdk',[str(java),'-jar',str(cli),'classinfo',str(classes)],S,timeout=90);assert type(result['actualExit']) is int and result['actualExit']==0 and result['timedOut'] is False;rows={}
for line in (S/'classinfo-sdk.stdout').read_text().splitlines():
 hit=re.search(r'\bclass 0x([0-9a-f]{16}) (\S+)$',line)
 if hit:assert hit[2] not in rows;rows[hit[2]]=hit[1]
assert rows==positive
for jar,digest in jars.items():assert sha(Path(jar))==digest
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],rawRef=dict(path=str(rawPath.relative_to(R)),sha256=sha(rawPath)),positiveSdkClasses=len(rows),classBindings=bindings,allObservedSdkCrcMatchPinnedJar=True,duplicateClassDefinitions=0,mode='NONINITIALIZING_CLASSINFO_METADATA_ONLY_NOT_SDK_PT',sdkClassesInitializedByWitness=0,productTestsExecuted=0,productTestsReexecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,stage=result,toolSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,positiveSdkClasses=len(rows),allSdkCrcMatched=True,manifestSha256=sha(O/'manifest.json'))))
