"""Independent raw measurement of the original single exec: seven physical classes, no exclusions."""
from pathlib import Path
import datetime,hashlib,json,subprocess,xml.etree.ElementTree as ET
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));cfg=ld(b/'input/4459_ssc448_pure8_profile_v3.json');postp=r/cfg['slots']['post']/'manifest.json';post=ld(postp);prep=ld(r/cfg['slots']['prepare']/'manifest.json');assert post['actualExit']==0 and post['tests']==8
names=sorted(prep['physicalClassHashes']);assert len(names)==7 and set(names)==set(cfg['physicalClasses'])
for name in names:policy.relative_name(name)
folder=r.parent/'pgpt-runs/PG379'/cfg['privateDirs']['prepare']/'component';files=[folder/n for n in names];before={n:sha(p) for n,p in zip(names,files)};assert before==prep['physicalClassHashes']
for name,value in post['inputHashes'].items():assert sha(r/name)==value==hashlib.sha256(subprocess.check_output(['git','show',post['source']+':'+name])).hexdigest()
def crc(data):
 assert int.from_bytes(data[6:8],'big')==69
 value=0
 for byte in data:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
ids={n[:-6]:crc(p.read_bytes()) for n,p in zip(names,files)};assert ids==post['classIds']
compiled=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');selftest=ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json');assert selftest['actualExit']==0 and selftest['toolTests']==12
for pin in compiled['dependencies']+[dict(path=str(r/compiled['source']['path']),sha256=compiled['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
execp=postp.parent/'jacoco.exec';assert sha(execp)==post['files']['jacoco.exec'];defaultp=postp.parent/'original-coverage.xml';assert sha(defaultp)==post['files']['original-coverage.xml'];default={x.get('name'):x for x in ET.parse(defaultp).getroot().findall('.//package/class')}
out=b/'evidence/PG36778-ssc448-pure8-raw-post-v1';out.mkdir();tool=r.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1/toolclasses';cp=':'.join([str(tool),*[p['path'] for p in compiled['dependencies']]]);command=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',cp,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(execp),*map(str,files)];start=datetime.datetime.now(datetime.timezone.utc).isoformat();result=subprocess.run(command,capture_output=True,timeout=60);(out/'analysis.stdout').write_bytes(result.stdout);(out/'analysis.stderr').write_bytes(result.stderr);assert result.returncode==0;classes={};methods=[]
for line in result.stdout.decode().splitlines():
 f=line.split('\t')
 if f[0]=='CLASS':
  assert len(f)==12;row=dict(name=f[1],id=f[2],dataPresent=f[3]=='true',probes=int(f[4]),access=int(f[5]),counters={});classes[f[1]]=row;offset=6
 else:
  assert f[0]=='METHOD' and len(f)==11;row=dict(className=f[1],name=f[2],descriptor=f[3],access=int(f[4]),counters={});methods.append(row);offset=5
 for token in f[offset:]:
  kind,missed,covered=token.split(':');row['counters'][kind]=dict(missed=int(missed),covered=int(covered))
assert set(classes)==set(ids) and all(x['id']==ids[n] for n,x in classes.items());assert len(methods)==sum(post['actualJvmCodeMethodCounts'].values());target='dev/codex/schubert/nk/batch/repository/RunReferenceRepository';tc=classes[target]['counters'];assert len([m for m in methods if m['className']==target])==6 and all(tc[k]['missed']==0 and tc[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH']);assert before=={n:sha(p) for n,p in zip(names,files)} and sha(execp)==post['files']['jacoco.exec']
for name,digest in post['files'].items():assert sha(postp.parent/name)==digest
for name in post['originalUnitXmlHashes']:
 xml=ET.parse(postp.parent/name).getroot();assert not xml.findall('.//system-out') and not xml.findall('.//system-err') and not any(xml.findall('.//'+k) for k in ['failure','error','skipped']);assert {x.get('name') for x in xml.findall('.//properties/property')}<=set(post['publicUnitXmlPropertyNames'])
oldp=b/'evidence/PG29956-maintenance-records16-post-v2/manifest.json';old=ld(oldp);assert old['actualExit']==0 and old['tests']==16 and all(sha(r/n)==value for n,value in old['inputHashes'].items())
measure=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=cfg['productionCoreMain'],unitSource=post['source'],run=cfg['id'],tests=8,failed=0,errors=0,skipped=0,notRun=0,originalPost=ref(postp),originalExec=ref(execp),rawMeasurementCommand=command,rawMeasurementExit=result.returncode,rawMeasurementStartUTC=start,files={p.name:sha(p) for p in out.iterdir() if p.is_file()},classes=classes,methods=methods,independentCrc=ids,allPhysicalHashes=before,target=target,targetRawCounters=tc,targetRawFour100=True,allSevenComponentRawFour100=all(all(x['counters'][k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']) for x in classes.values()),sharedClassesMissedCodeMethods=[m for m in methods if m['className']!=target and m['counters']['METHOD']['missed']],allClassesRetained=True,manualExclusions=[],oldExecCombined=False,measurementProductDefinitionsOrInitialization=0,measurementApplicationTests=0,existingMaintenance16CurrentSourceReuse=dict(evidence=ref(oldp),all12InputHashesExact=True,testsReplayed=0,newPtCount=0,originalSource=old['source'],currentCore=cfg['productionCoreMain'],rawFourNotRequalifiedByThisRead=True),bug3125StaticFindingAbsent=True,bug3126TypedCleanupRawAll100=True,bug3127DuplicateLiteralAbsent=True,whole451Accepted=False,formalUpdated=False,newAcceptance=0,effortRate=None)
(out/'manifest.json').write_text(json.dumps(measure,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=8,rawTargetCounters=tc,sharedRawWhole100=measure['allSevenComponentRawFour100'],old16Replayed=0,formalUpdated=False)))
