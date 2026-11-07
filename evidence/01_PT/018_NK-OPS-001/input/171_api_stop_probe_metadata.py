"""Inspect only saved own exec bytes and offline instrumented pure budget bytes; never run Product."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import pg9666_pagination_static as c
r=Path.cwd();w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';jdk=tc/'jdk-25.0.4/bin';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pub=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22090-api-stop-state-twenty-unit-v1';m=json.loads((pub/'manifest.json').read_text());assert sha(pub/'manifest.json')=='95faef01085b82bf04edbb5ed8e34df304c98684e61c672b00b9245d6cc215ee' and m['actualExit']==0
execp=pub/'jacoco.exec';assert sha(execp)==m['files']['jacoco.exec'];data=execp.read_bytes();assert len(data)<8*1024*1024;pos=0;target='dev/codex/schubert/nk/api/bootstrap/ApiStopBudget';records=[];sessions=[]
def take(n):
 global pos
 assert 0<=n<=len(data)-pos
 value=data[pos:pos+n];pos+=n;return value
def number(n):return int.from_bytes(take(n),'big')
def utf():return take(number(2)).decode('utf-8')
def varint():
 value=0
 for i in range(5):
  b=number(1);value|=(b&127)<<(7*i)
  if b<128:return value
 raise ValueError('invalid varint')
while pos<len(data):
 tag=number(1)
 if tag==1:assert number(2)==0xc0c0 and number(2)==0x1007
 elif tag==16:sessions.append(dict(id=utf(),start=number(8),end=number(8)))
 elif tag==17:
  crc=take(8).hex();name=utf();length=varint();assert length<=1000000;packed=take((length+7)//8)
  if name==target:records.append(dict(crc=crc,name=name,probeCount=length,unhit=[i for i in range(length) if not (packed[i//8]>>(i%8))&1]))
 else:raise ValueError('unexpected exec block')
assert len(sessions)==len(records)==1 and sessions[0]['id']=='PG22090-API-STOP-ATOMIC20' and records[0]['crc']==m['classIds'][0][0] and records[0]['probeCount']==29 and len(records[0]['unhit'])==2
raw=Path(m['originalManifest']['path']).parent;component=raw/'component';entry=component/(target+'.class');assert sha(entry)==m['physical'][target]
cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar';assert sha(cli)==m['begin']['toolHashes'][str(cli)];slot=w/'pg22102-api-stop-probe-metadata-v1';assert not slot.exists();slot.mkdir();c.SLOT=slot;stages={}
stages['instrument']=c.step('instrument',[str(jdk/'java'),'-Xlog:class+init=info:file='+str(slot/'instrument-init.stdout'),'-jar',str(cli),'instrument',str(component),'--dest',str(slot/'instrumented')],r);assert stages['instrument']['actualExit']==0
instrumented=slot/'instrumented'/(target+'.class');assert instrumented.is_file()
stages['javap']=c.step('javap',[str(jdk/'javap'),'-J-Xlog:class+init=info:file='+str(slot/'javap-init.stdout'),'-cp',str(slot/'instrumented'),'-p','-c','-l','dev.codex.schubert.nk.api.bootstrap.ApiStopBudget'],r);assert stages['javap']['actualExit']==0
for n in ['instrument-init.stdout','javap-init.stdout']:assert not any(x.startswith('dev/codex/schubert/nk/') for x in re.findall(r"Initializing '([^']+)",(slot/n).read_text()))
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),unitSource=m['source'],productionCoreMain=m['productionCoreMain'],originalUnitManifest=dict(path=str((pub/'manifest.json').relative_to(r)),sha256=sha(pub/'manifest.json')),execSha256=sha(execp),session=sessions[0]['id'],probeRecords=records,originalClassSha256=sha(entry),instrumentedClassSha256=sha(instrumented),stages=stages,productInitialisations=0,productTestsExecuted=0,oldExecUnion=False,manualCoverageExclusions=[],interpretation='OFFLINE_PROBE_LOCATIONS_REQUIRE_SOURCE_REVIEW_NOT_NEW_COVERAGE')
write(slot/'manifest.json',value);out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22102-api-stop-probe-metadata-v1';assert not out.exists();out.mkdir();files={}
for p in slot.iterdir():
 if p.is_file():name='original-manifest.json' if p.name=='manifest.json' else p.name;shutil.copyfile(p,out/name);files[name]=sha(out/name)
value.update(files=files,driverSha256=sha(__file__));write(out/'manifest.json',value);print(json.dumps(dict(actualExit=0,probes=records,productTests=0,manifestSha256=sha(out/'manifest.json'))))
