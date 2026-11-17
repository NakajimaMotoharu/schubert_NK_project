"""Independently bind whole5/457 CRC/initialization and all API Code counters, no exec union."""
from pathlib import Path
import datetime,gzip,hashlib,json,re,shutil,subprocess,sys,xml.etree.ElementTree as E
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'));import pgpt_closed_host_profile as policy
b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));slot=w/'pg37346-request-details-whole5-unit-v1';u=ld(slot/'terminal.json');begin=ld(slot/'begin.json');prepare=ld(b/'evidence/PG37342-request-details-prepare-v1/manifest.json');assert u['actualExit']==0 and not u['timedOut'] and u['originalMainClassesUnchanged'] and u['testSourcesUnchanged'];assert all(sha(slot/name)==h for name,h in u['files'].items());assert all(sha(r/name)==h for name,h in begin['testSourceHashes'].items());assert all(sha(r/name)==h for name,h in prepare['inputHashes'].items())
expected={('dev.codex.schubert.nk.api.logging.RequestLogDetailsTest',n+'()') for n in ['allowedScalarsAndRolesMatchLiteralJson','unsafeMalformedDuplicateAndWrongTypesAreRejected']};expected.update(('dev.codex.schubert.nk.api.logging.RequestLogDetailsRawContractTest',n+'()') for n in ['raw001PureUtilityRejectsConstructionAndAccessIsRestored','raw002FourFixedHashCollisionsRemainUnknownKeys','raw003ForbiddenPublicCanariesNeverEscapeThroughAnyRoleOrParserDiagnostic']);cases=[]
def valid(c):return all(x.tag in ['system-out','system-err'] for x in c) and not any(c.findall('.//'+tag) for tag in ['failure','error','skipped'])
assert valid(E.fromstring('<testcase><system-out>metadata</system-out></testcase>'))
for tag in ['failure','error','skipped','unknown']:assert not valid(E.fromstring('<testcase><'+tag+'/></testcase>'))
for f in (slot/'xml').glob('*.xml'):
 t=E.parse(f).getroot();assert all(int(t.get(k,0))==0 for k in ['failures','errors','skipped'])
 for c in t.findall('testcase'):assert valid(c);cases.append((c.get('classname'),c.get('name')))
assert len(cases)==len(set(cases))==5 and set(cases)==expected
classes={};snapshot=w/'pg37342-request-details-prepare-v1/snapshot'
for module,pins in prepare['physicalClassHashes'].items():
 for name,h in pins.items():
  policy.relative_name(name);p=snapshot/('src/schubert-nk-'+module)/'target/classes'/name;assert sha(p)==h and name not in classes;classes[name]=p
assert len(classes)==457
out=b/'evidence/PG37348-request-details5-independent-v1';assert not out.exists();out.mkdir()
cmd=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'org.jacoco.cli-0.8.15-nodeps.jar'),'execinfo',str(slot/'jacoco.exec')];x=subprocess.run(cmd,capture_output=True,timeout=60);assert x.returncode==0;(out/'execinfo.stdout').write_bytes(x.stdout);(out/'execinfo.stderr').write_bytes(x.stderr);text=x.stdout.decode();assert text.count('Session "')==1 and 'Session "PG37346-DETAILS5"' in text;probes={n:dict(crc=crc,hit=int(hit),total=int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',text,re.M)}
def crc64(raw):
 assert int.from_bytes(raw[6:8],'big')==69;value=0
 for byte in raw:
  value^=byte
  for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
 return f'{value:016x}'
ids={name[:-6]:crc64(p.read_bytes()) for name,p in classes.items()};positive={name for name,x in probes.items() if name.startswith('dev/codex/schubert/nk/') and name in ids and x['hit']};target='dev/codex/schubert/nk/api/logging/RequestLogDetails';assert positive=={target,'dev/codex/schubert/nk/protocol/codec/PermanentProtocolException','dev/codex/schubert/nk/protocol/layout/semantic/UserRole'};assert all(probes[n]['crc']==ids[n] for n in probes if n in ids)
initializing=set(re.findall(r"Initializing '([^']+)'",(slot/'class-init.log').read_text()));assert not any(n.startswith(('dev/codex/schubert/nk/bootstrap/','dev/codex/schubert/nk/batch/','dev/codex/schubert/nk/web/','org/postgresql/')) for n in initializing);assert not any(any(d in n for d in policy.DENIED) for n in initializing)
tool=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');assert ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json')['toolTests']==12
for p in tool['dependencies']:assert sha(Path(p['path']))==p['sha256']
cmd=[str(tc/'jdk-25.0.4/bin/java'),'-cp',':'.join([str(w/'pg31432-generated-code-supplemental-tool-v1/toolclasses'),*[p['path'] for p in tool['dependencies']]]),'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(slot/'jacoco.exec'),*[str(p) for n,p in sorted(classes.items())]]
x=subprocess.run(cmd,capture_output=True,timeout=120);assert x.returncode==0;(out/'unfiltered.stdout').write_bytes(x.stdout);(out/'unfiltered.stderr').write_bytes(x.stderr);measure={};methods=[]
for line in x.stdout.decode().splitlines():
 f=line.split('\t')
 if f[0]=='CLASS':row=dict(name=f[1],id=f[2],counters={});measure[f[1]]=row;offset=6
 else:assert f[0]=='METHOD';row=dict(className=f[1],name=f[2],descriptor=f[3],counters={});methods.append(row);offset=5
 for v in f[offset:]:k,miss,hit=v.split(':');row['counters'][k]=dict(missed=int(miss),covered=int(hit))
assert set(measure)==set(ids) and all(row['id']==ids[n] for n,row in measure.items());targetMethods=[m for m in methods if m['className']==target];assert len(targetMethods)==5;raw=measure[target]['counters'];all100=all(v['missed']==0 for v in raw.values());noCode=measure['dev/codex/schubert/nk/api/logging/package-info'];assert all(sum(v.values())==0 for v in noCode['counters'].values())
abi=[]
for name,path in [('before',w/'pg37336-request-details-static-gap-v1/RequestLogDetails.class'),('after',classes[target+'.class'])]:
 cmd2=[str(tc/'jdk-25.0.4/bin/javap'),'-p','-s',str(path)];y=subprocess.run(cmd2,capture_output=True,timeout=30);assert y.returncode==0;(out/('abi-'+name+'.txt')).write_bytes(y.stdout);abi.append(y.stdout)
assert abi[0]==abi[1]
old=ld(b/'evidence/PG37274-record-codec-four-main-compile-v1/manifest.json');dependencySame=all(prepare['physicalClassHashes'][m]==old['physicalClassHashes'][m] for m in ['protocol','storage','bootstrap']);assert dependencySame
for name in ['terminal.json','begin.json','process.json','jacoco.exec','unit.stdout','unit.stderr']:shutil.copyfile(slot/name,out/name)
shutil.copytree(slot/'xml',out/'xml')
with (out/'class-init.log.gz').open('xb') as f:f.write(gzip.compress((slot/'class-init.log').read_bytes(),mtime=0))
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=u['source'],productionCoreMain=u['productionCoreMain'],run='PG37346-DETAILS5',expected=5,success=5,failed=0,errors=0,skipped=0,notRun=0,wholeSuites=2,rawCounters=raw,rawCodeMethods=targetMethods,rawAll100=all100,physicalApiClasses2=True,naturalNoCodePackageRetained=True,all457CrcBound=True,positiveMainClasses=sorted(positive),allPositiveMainCounterDetails={n:measure[n] for n in positive},otherPositiveProtocolPartialCountersNotAccepted=True,allMethodMeasurements=methods,classMeasurements=measure,classSha256={n:sha(p) for n,p in classes.items()},classIds=ids,apiPrivatePublicAbiExact=True,dependency455PhysicalUnchangedFrom91c=True,oldExecUnion=False,manualCoverageExclusions=[],realDbRootNativeVmKeyOperations=0,heldFourClassfileActions=0,formalUpdated=False,newAcceptance=0,whole451Accepted=False,cases=[dict(className=c,name=n,result='PASS') for c,n in sorted(cases)],sourceTestPins=begin['testSourceHashes'],prepare=ref(b/'evidence/PG37342-request-details-prepare-v1/manifest.json'),staticAdmission=ref(b/'evidence/PG37344-request-details-static-admission-v1/manifest.json'),files={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()})
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,success=5,rawAll100=all100,counters=raw,all457Crc=True,positiveMain=3,abiExact=True)))
