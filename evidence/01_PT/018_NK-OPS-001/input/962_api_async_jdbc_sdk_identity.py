"""Reuse already verified SDK metadata only after exact current jar/member SHA and observed CRC matching."""
from pathlib import Path
import datetime,hashlib,json,re,zipfile
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001/evidence';S=R.parent/'pgpt-runs/PG379/pg25408-api-async-jdbc-original-whole16-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());raw=B/'PG25408-api-async-jdbc-original-whole16-v1/manifest.json';assert sha(raw)=='114a0bcba878303e21053484bf27a036e683a8a24c6ac1a2e647a7a39873403e';m=load(raw);assert m['actualExit']==0;ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);prior=B/'PG25290-api-supplied-sdk-identity-v1/manifest.json';assert sha(prior)=='d06d0675fbedffc3f6a3bc15591398681211a34c2019fdb8142def8c64854e30';old=load(prior);positive={}
for line in (S/'execinfo.stdout').read_text().splitlines():
 h=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if h and h[4].startswith('io/micrometer/') and int(h[2])>0:assert h[4] not in positive;positive[h[4]]=h[1]
assert len(positive)==43 and set(positive)<set(old['classRows']) and len(set(old['classRows'])-set(positive))==9;rows={}
for path,digest in pf['vendorJars'].items():
 assert sha(Path(path))==digest
 with zipfile.ZipFile(path) as jar:
  for name,crc in positive.items():
   if name+'.class' not in jar.namelist():continue
   row=old['classRows'][name];assert row['jarPath']==path and row['jarSha256']==digest and row['crc64']==crc and hashlib.sha256(jar.read(name+'.class')).hexdigest()==row['classSha256'];rows[name]=row
assert set(rows)==set(positive);initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));names={n.split('$$Lambda+',1)[0] for n in initializers if n.startswith('io/micrometer/')};assert names<=set(old['normalizedSdkInitializerNames']);O=B/'PG25410-api-async-jdbc-sdk-identity-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifestSha256=sha(raw),sdkPositiveClasses=43,newSdkMetadataClasses=0,reusedSdkMetadataClasses=43,classRows=rows,normalizedSdkInitializerNames=sorted(names),productTestsExecuted=0,allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,sdkRuntimeInitializedByThisMetadata=False,actualExternalCollectorOrExportActions=0,priorMetadata=dict(path=str(prior.relative_to(R)),sha256=sha(prior)),files={});(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sdkIdentityClasses=43,newMetadata=0,manifestSha256=sha(O/'manifest.json'))))
