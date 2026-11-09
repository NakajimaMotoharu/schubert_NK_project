"""Current original API Exact10/DB9 SDK identity: exact reused member hashes or noninitializing classinfo/javap, no SDK PT."""
from pathlib import Path
import datetime,hashlib,json,re,zipfile,os
import pg9666_pagination_static as stage
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001/evidence';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';S=RUNS/'pg25594-api-exact-db-duration-original-whole19-v1';Q=RUNS/'pg25596-api-exact-db-duration-sdk-identity-v1';O=B/'PG25596-api-exact-db-duration-sdk-identity-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());assert not Q.exists() and not O.exists();raw=B/'PG25594-api-exact-db-duration-original-whole19-v1/manifest.json';assert sha(raw)=='7d4f3ad0c343403bf7b937eb59bb4fa278ce09e380e5899b6f2ffb4555e3b373';m=load(raw);assert m['actualExit']==0 and m['source']=='cecf4f7e1542379cead612961890868874c9c609';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);old={};priorRefs=[]
for name,digest in [('PG25234-batch-text-sdk-identity-v1','a1b915ebbef7289a45ae928441e9f6170a744b1d84828e6b0f22ec1f0c6a7bee'),('PG25290-api-supplied-sdk-identity-v1','d06d0675fbedffc3f6a3bc15591398681211a34c2019fdb8142def8c64854e30'),('PG25572-http-duration-sdk-identity-v1','8e069f5eb8432c2ca3a2252a6ee68339889c370290393ca1981503901e771c80')]:
 p=B/name/'manifest.json';assert sha(p)==digest;v=load(p);assert v['actualExit']==0;old.update(v['classRows']);priorRefs.append(dict(path=str(p.relative_to(R)),sha256=digest))
positive={}
for line in (S/'execinfo.stdout').read_text().splitlines():
 h=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if h and h[4].startswith('io/micrometer/') and int(h[2])>0:assert h[4] not in positive;positive[h[4]]=h[1]
assert len(positive)==60;new=set(positive)-set(old);assert len(new)==4;Q.mkdir();(Q/'members').mkdir();stage.SLOT=Q;rows={};members={}
for path,digest in pf['vendorJars'].items():
 assert sha(Path(path))==digest
 with zipfile.ZipFile(path) as jar:
  names=set(jar.namelist());members.update({n.removesuffix('.class'):(path,digest) for n in names if n.endswith('.class')})
  for name,crc in positive.items():
   if name+'.class' not in names:continue
   content=jar.read(name+'.class');memberSha=hashlib.sha256(content).hexdigest()
   if name in old:
    row=old[name];assert row['jarPath']==path and row['jarSha256']==digest and row['crc64']==crc and row['classSha256']==memberSha;rows[name]=row
   else:
    p=Q/'members'/(name+'.class');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content);rows[name]=dict(jarPath=path,jarSha256=digest,classSha256=memberSha,crc64=crc,metadataOnlyNotInitialized=True)
assert set(rows)==set(positive);jdk=TC/'jdk-25.0.4/bin';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';assert sha(cli)==pf['dependencies'][str(cli)]
steps={};steps['classinfo']=stage.step('classinfo',[str(jdk/'java'),'-jar',str(cli),'classinfo',str(Q/'members')],Q,timeout=90);assert steps['classinfo']['actualExit']==0 and steps['classinfo']['timedOut'] is False;actual={}
for line in (Q/'classinfo.stdout').read_text().splitlines():
 h=re.fullmatch(r'\s*\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+class 0x([0-9a-f]{16}) (\S+)',line)
 if h:assert h[2] not in actual;actual[h[2]]=h[1]
assert actual=={n:positive[n] for n in new};steps['javap']=stage.step('javap',[str(jdk/'javap'),'-classpath',os.pathsep.join(pf['vendorJars']),'-p','-c','-s',*[n.replace('/','.') for n in sorted(new)]],Q,timeout=90);assert steps['javap']['actualExit']==0 and steps['javap']['timedOut'] is False
initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));normalized={n.split('$$Lambda+',1)[0] for n in initializers if n.startswith('io/micrometer/')};assert normalized<=set(members)
O.mkdir()
for name in ['classinfo.stdout','classinfo.stderr','javap.stdout','javap.stderr']:(O/name).write_bytes((Q/name).read_bytes())
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifestSha256=sha(raw),sdkPositiveClasses=60,newSdkMetadataClasses=4,reusedSdkMetadataClasses=56,classRows=rows,normalizedSdkInitializerNames=sorted(normalized),newMetadataNames=sorted(new),metadataStages=steps,priorMetadata=priorRefs,productTestsExecuted=0,allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,sdkRuntimeInitializedByThisMetadata=False,actualExternalCollectorOrExportActions=0,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sdkIdentityClasses=60,reusedMetadata=56,newMetadataOnly=4,manifestSha256=sha(O/'manifest.json'))))
