"""Independent primitive hash/wire oracle and distinct preserved Main/Test source identities."""
from pathlib import Path
import json,hashlib,datetime,subprocess,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG32748-audio-link-map886-source-v1';e.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();newmain=r/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/CurrentAudioLinkMapper.java';newtest=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/CurrentAudioLinkMapperTest.java';old={}
for folder,source in [('main','bda326b59f6220cc6e7419eff2c88c36a2088867'),('test','14343ab02d1fc6495a9b4109636390668df7b28d')]:
 for p in (r/('src/schubert-nk-bootstrap/src/'+folder+'/java/dev/codex/schubert/nk/migration')).glob('*.java'):
  if p in [newmain,newtest]:continue
  path=str(p.relative_to(r));assert sha(p)==hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest(),path;old[path]=sha(p)
assert len(old)==84 and sum(len(re.findall(r'@Test\b',(r/p).read_text())) for p in old if '/test/' in p)==862 and len(re.findall(r'@Test\b',newtest.read_text()))==24
def i32(v):return (v+(1<<31))%(1<<32)-(1<<31)
def lh(v):v&=(1<<64)-1;return i32(v^(v>>32))
def sh(s):
 h=0
 for c in s:h=i32(h*31+ord(c))
 return h
def record(e,a,t,n):return i32(i32(i32(lh(e)*31+lh(a))*31+sh(t))*31+n)
assert record(-20,-30,'voice',9)==-810396415 and record(-(1<<63),0,'se',1)==record((1<<63)-1,0,'se',1)==-2147370001
wire='100\t800\t1\tvoice\t2\t2026-01-02T03:04:05Z\n100\t700\t1\tvoice\t9\t2026-01-02T03:04:05Z\n200\t900\t2\tse\t999\t2026-01-02T03:04:05Z\n'
v=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),previousProductionCoreMain='bda326b59f6220cc6e7419eff2c88c36a2088867',previousUnitSource='14343ab02d1fc6495a9b4109636390668df7b28d',oldSourceHashes=old,newMain=dict(path=str(newmain.relative_to(r)),sha256=sha(newmain)),newTest=dict(path=str(newtest.relative_to(r)),sha256=sha(newtest)),recordHashVectors=[dict(entry=-20,audio=-30,type='voice',order=9,expected=-810396415),dict(entry=-(1<<63),audio=0,type='se',order=1,expected=-2147370001),dict(entry=(1<<63)-1,audio=0,type='se',order=1,expected=-2147370001)],wireHex=wire.encode().hex(),wireSha256=hashlib.sha256(wire.encode()).hexdigest(),newDefinitions=24,oldDefinitions=862,wholeExpected=886,allMain=42,physicalClasses=61,expectedFromProduction=False,currentBusinessOrderWitness=False,privateRootOrHeldClassActions=0,actualDbOrMasterBackupKeyFileVmAuthorityActions=0,newAcceptance=0)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=24,old=862,whole=886,noActions=True))
