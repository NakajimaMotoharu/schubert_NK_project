"""One current whole18, 1101 CRC/init, all three Inventory classes/39 Code without exclusions."""
from pathlib import Path
import datetime,gzip,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));up=b/'evidence/PG37438-inventory-whole18-unit-v1/manifest.json';u=ld(up);begin=ld(up.parent/'begin.json');p=ld(r/u['prepare']['path']);slot=w/'pg37438-inventory-whole18-unit-v1';component=Path(p['work'])/'component';assert u['actualExit']==0 and not u['timedOut'] and u['tests']==18 and all(u[k]==0 for k in ['failures','errors','skipped','notRun']);assert sha(slot/'jacoco.exec')==u['execSha256'] and sha(slot/'class-init.log')==u['classInitLogSha256'];assert all(sha(r/n)==h for n,h in begin['inputHashes'].items());assert all(sha(component/n)==h for n,h in p['physicalClassHashes'].items());expected={tuple(x) for x in begin['expectedCases']};cases=[]
for name,h in u['xmlHashes'].items():
 assert sha(slot/'xml'/name)==h;t=E.parse(slot/'xml'/name).getroot();assert all(int(t.get(k,0))==0 for k in ['failures','errors','skipped'])
 for c in t.findall('testcase'):assert not any(c.findall('.//'+tag) for tag in ['failure','error','skipped']) and all(x.tag in ['system-out','system-err'] for x in c);cases.append((c.get('classname'),c.get('name')))
assert len(cases)==len(set(cases))==len(expected)==18 and set(cases)==expected
out=b/'evidence/PG37440-inventory18-independent-v1';assert not out.exists();out.mkdir();cmd=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'org.jacoco.cli-0.8.15-nodeps.jar'),'execinfo',str(slot/'jacoco.exec')];x=subprocess.run(cmd,capture_output=True,timeout=60);assert x.returncode==0;(out/'execinfo.stdout').write_bytes(x.stdout);(out/'execinfo.stderr').write_bytes(x.stderr);text=x.stdout.decode();assert text.count('Session "')==1 and 'Session "PG37438-INVENTORY-WHOLE18"' in text;probes={n:dict(crc=crc,hit=int(hit),total=int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',text,re.M)}
def crc(raw):
 assert int.from_bytes(raw[6:8],'big')==69;v=0
 for byte in raw:
  v^=byte
  for _ in range(8):v=(v>>1)^0xd800000000000000 if v&1 else v>>1
 return f'{v:016x}'
ids={n[:-6]:crc((component/n).read_bytes()) for n in p['physicalClassHashes']};assert len(ids)==1101 and all(probes[n]['crc']==ids[n] for n in probes if n in ids);names=['dev/codex/schubert/nk/bootstrap/ReleaseInventory'+suffix for suffix in ['', '$Artifact','$Dependency']];shared=['dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission'+suffix for suffix in ['', '$Row']];positive={n for n,v in probes.items() if n in ids and v['hit']};assert positive==set(names+shared)
init=set(re.findall(r"Initializing '([^']+)'",(slot/'class-init.log').read_text()));held=['StartupReleaseManifest','ReleaseSignatureVerifier','RootReleaseAdmission','LinuxInodeSecurity','LinuxDirectoryCalls','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(any(n.rsplit('/',1)[-1].split('$')[0]==k for k in held) for n in init);assert not any(n.startswith(('dev/codex/schubert/nk/batch/','org/postgresql/')) for n in init)
tool=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');assert ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json')['toolTests']==12
for pin in tool['dependencies']:assert sha(Path(pin['path']))==pin['sha256']
cmd=[str(tc/'jdk-25.0.4/bin/java'),'-cp',':'.join([str(w/'pg31432-generated-code-supplemental-tool-v1/toolclasses'),*[z['path'] for z in tool['dependencies']]]),'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(slot/'jacoco.exec'),*[str(component/(n+'.class')) for n in names+shared]];x=subprocess.run(cmd,capture_output=True,timeout=60);assert x.returncode==0;(out/'unfiltered.stdout').write_bytes(x.stdout);(out/'unfiltered.stderr').write_bytes(x.stderr);measure={};methods=[]
for line in x.stdout.decode().splitlines():
 f=line.split('\t')
 if f[0]=='CLASS':row=dict(name=f[1],id=f[2],counters={});measure[f[1]]=row;offset=6
 else:assert f[0]=='METHOD';row=dict(className=f[1],name=f[2],descriptor=f[3],counters={});methods.append(row);offset=5
 for v in f[offset:]:k,miss,hit=v.split(':');row['counters'][k]=dict(missed=int(miss),covered=int(hit))
assert set(measure)==set(names+shared) and all(x['id']==ids[n] for n,x in measure.items());targets=[m for m in methods if m['className'] in names];assert len(targets)==39;raw={k:{role:sum(measure[n]['counters'][k][role] for n in names) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']};all100=all(v['missed']==0 for v in raw.values())
for name in ['manifest.json','begin.json','whole18.stdout.log','whole18.stderr.log']:
 if (up.parent/name).exists():shutil.copyfile(up.parent/name,out/('unit-'+name))
shutil.copyfile(slot/'jacoco.exec',out/'jacoco.exec');shutil.copytree(slot/'xml',out/'xml')
with (out/'class-init.log.gz').open('xb') as f:f.write(gzip.compress((slot/'class-init.log').read_bytes(),mtime=0))
value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=u['source'],sourceCore=u['sourceCore'],run=u['run'],tests=18,failed=0,errors=0,skipped=0,notRun=0,targetClasses=names,targetMethods39=targets,targetRawCounters=raw,targetRawAll100=all100,sharedClasses=shared,sharedCompleteScopeNotClaimed=True,sharedClassCounterDetails={n:measure[n] for n in shared},allMeasuredMethods=methods,all1101CrcBound=True,classIds=ids,allPhysicalHashes=p['physicalClassHashes'],positiveMain=sorted(positive),actualDbRootNativeVmKeySignerPermitPlacementActions=0,heldFourClassfileActions=0,oldExecUnion=False,manualCoverageExclusions=[],originalUnit=ref(up),prepare=u['prepare'],staticAdmission=u['staticAdmission'],formalUpdated=False,newAcceptance=0,whole451Accepted=False,effortCompletionRate=None,caseIds=[c+'.'+n for c,n in sorted(cases)],files={str(q.relative_to(out)):sha(q) for q in out.rglob('*') if q.is_file()})
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=18,target39All100=all100,raw=raw,positiveMain=5,heldRootKeySigningActions=0)))
