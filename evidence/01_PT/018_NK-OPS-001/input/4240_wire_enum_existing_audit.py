"""Audit exactly eleven admitted N12 class entries from the original verified protocol JAR and single execution."""
from pathlib import Path
import datetime,hashlib,json,subprocess,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));cfg=ld(b/'input/802_common_values_method_trace_scope.json')
def pinned(pin):
 p=r/pin['path'];assert sha(p)==pin['sha256'];return ld(p)
normal=pinned(cfg['normalProof']);inventory=pinned(cfg['metadataInventory']);index=pinned(cfg['physicalIndex']);assert normal['actualExit']==0 and normal['tests']==120 and normal['productionCoreMain']==cfg['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5' and not normal['oldExecUnion'];pp=r/cfg['normalProof']['path'];pre=pp.parent/'preflight-manifest.json';assert sha(pre)==normal['files'][pre.name];pf=ld(pre);cp=pp.parent/'compile-manifest.json';assert sha(cp)==pf['compileManifestSha256'];cm=ld(cp);jars=[Path(n) for n in cm['dependencies'] if Path(n).name=='schubert-nk-protocol-0.1.0-SNAPSHOT.jar'];assert len(jars)==1;jar=jars[0];assert sha(jar)==cm['dependencies'][str(jar)];short=['WireEnum',*cfg['standardEnumSources']];names=['dev/codex/schubert/nk/protocol/layout/semantic/'+n for n in short]
for name in names:policy.relative_name(name)
w=r.parent/'pgpt-runs/PG379/pg35960-wire-enum-existing-raw-v1';o=b/'evidence/PG35960-wire-enum-existing-nineteen-raw-v1';assert not w.exists() and not o.exists();w.mkdir();o.mkdir();records={};files=[]
def crc64(binary):
 assert int.from_bytes(binary[6:8],'big')==69
 value=0
 for byte in binary:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
with zipfile.ZipFile(jar) as z:
 for name in names:
  ent=index[name];source=ent['path'];assert source=='src/schubert-nk-protocol/src/main/java/'+name+'.java';meta=next(x for x in inventory if x['sourcePath']==source and x['physicalKey'].endswith(':'+name+'.class'));assert sha(r/source)==meta['sourceSha256'];binary=z.read(name+'.class');h=hashlib.sha256(binary).hexdigest();assert h==ent['sha256']==meta['classSha256'];identity=crc64(binary);assert identity==ent['crc64'];path=w/'classes'/(name+'.class');path.parent.mkdir(parents=True,exist_ok=True);path.open('xb').write(binary);files.append(path);records[name]=dict(sourcePath=source,currentSourceSha256=sha(r/source),classSha256=h,crc64=identity,actualCodeMethods=sum(x['hasCode'] for x in meta['structure']['methods']))
ex=pp.parent/'jacoco.exec';assert sha(ex)==normal['files']['jacoco.exec'];compiled=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');st=ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json');assert st['actualExit']==0 and st['toolTests']==12
for pin in compiled['dependencies']+[dict(path=str(r/compiled['source']['path']),sha256=compiled['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
toolwork=r.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1';classpath=':'.join([str(toolwork/'toolclasses'),*[p['path'] for p in compiled['dependencies']]]);command=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',classpath,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(ex),*map(str,files)];v=subprocess.run(command,capture_output=True,timeout=60);(o/'analysis.stdout').open('xb').write(v.stdout);(o/'analysis.stderr').open('xb').write(v.stderr);assert v.returncode==0;classes={};methods=[]
for line in v.stdout.decode().splitlines():
 fields=line.split('\t')
 if fields[0]=='CLASS':
  assert len(fields)==12;name=fields[1];assert name in records and name not in classes;row=dict(name=name,id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),counters={});assert row['id']==records[name]['crc64'];classes[name]=row;start=6
 else:
  assert fields[0]=='METHOD' and len(fields)==11 and fields[1] in records;row=dict(className=fields[1],name=fields[2],descriptor=fields[3],counters={});methods.append(row);start=5
 for item in fields[start:]:
  k,missed,covered=item.split(':');row['counters'][k]=dict(missed=int(missed),covered=int(covered))
assert set(classes)==set(names)
for name,item in classes.items():assert sum(item['counters']['METHOD'].values())==records[name]['actualCodeMethods']
codezero=[n for n,x in records.items() if x['actualCodeMethods']==0];assert codezero==['dev/codex/schubert/nk/protocol/layout/semantic/WireEnum'];counter={k:dict(missed=sum(x['counters'][k]['missed'] for x in classes.values()),covered=sum(x['counters'][k]['covered'] for x in classes.values())) for k in next(iter(classes.values()))['counters']};assert len(methods)==sum(counter['METHOD'].values());assert all(sha(path)==records[name]['classSha256'] for name,path in zip(names,files));assert sha(ex)==normal['files']['jacoco.exec'];missed=[x for x in methods if any(y['missed'] for y in x['counters'].values())];m=dict(actualExit=0,source='185c27a827cff4e9d953f0d1652f4e34b4a5788c',productionCoreMain='185c27a827cff4e9d953f0d1652f4e34b4a5788c',historicalCore=cfg['source'],historicalUnitSource=normal['source'],terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalNormalProof=cfg['normalProof'],originalCompile=ref(cp),jar=dict(path=str(jar),sha256=sha(jar)),originalSingleExec=ref(ex),classAndSourceIndex=records,classes=classes,methods=methods,rawCounters=counter,missedCodeMethods=missed,physicalClasses=19,codeClasses=18,naturalCodeZero=codezero,allCurrentRelevantJavaSourcesByteExact=True,historicalWhole120Referenced=True,productExecutions=0,toolSelftest12Replayed=False,productionClassDefinitionOrInitialization=0,oldExecCombined=False,oldSuccessPromotedToCurrentWholeCore=False,formalUpdated=False,newAcceptance=0,effortRate=None,command=command);(o/'manifest.json').open('x').write(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=counter,missed=[dict(className=x['className'],name=x['name'],descriptor=x['descriptor']) for x in missed],productExecutions=0)))
