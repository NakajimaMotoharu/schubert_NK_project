"""Each of18 semantic enums rejects added/wire mutations in private shadow classes only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run
from pg1446_current_cold_stage import W
from pg2600_retention_group_full_six import SOURCE

ROOT=Path(__file__).resolve().parents[2]
BASE='/home/mini/schubert-nk-pgpt'
SLOT='pg2636-wire-enum-mutations-v1'
NAMES=('ContentDisposition','DeliveryMode','PairRole','VoiceCondition','UserRole','LogLevel','LogType','UserState','NotificationState','AnswerState','NotificationType','EntryType','GameCode','MediaMimeType','NotificationErrorCode','AnimationListCategory','AnimationCategory','VideoCategory')
FILES=['src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/semantic/ProtocolSemanticTypeTest.java',
       *('src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/'+n+'.java'for n in NAMES),
       'tools/quality/vm/050_s1/WireEnumOracleCanaryLauncher.java']
SERVER=r'''
import datetime,hashlib,json,os,re,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2636-v1';transfer=b/'transfer/PG2636-v1';source=b/'source-protocol-PG2634-v2';repo=b/'m2/repository'
def require(v):
 if not v:raise ValueError('complete isolated semantic mutation proof refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(mode=0o700);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
authority=b/'runs/PG2634-v2/manifest.safe.json';require(sha(authority)==INPUT['normalManifestSha256'])
normal=json.loads(authority.read_bytes());require(normal['actualExit']==0 and normal['source']==INPUT['source'] and normal['tests']==82 and normal['allProtocolMainAndResourcesSameBytes'])
jar=source/'src/schubert-nk-protocol/target/schubert-nk-protocol-0.1.0-SNAPSHOT.jar';require(sha(jar)==normal['jarSha256'])
for n,h in INPUT['files'].items():require(sha(transfer/n)==h)
xml=source/'src/schubert-nk-protocol/target/surefire-reports/TEST-dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest.xml'
x=ET.parse(xml).getroot();require(all(x.get(k)=='0'for k in('failures','errors','skipped')))
props=[n.get('value')for n in x.findall('properties/property')if n.get('name')=='java.class.path'];require(len(props)==1)
libs=[]
for entry in props[0].split(':'):
 p=Path(entry)
 if p.suffix=='.jar'and p.is_relative_to(repo):require(p.is_file()and p.resolve().is_relative_to(repo.resolve()));libs.append(p)
engines=[p for p in libs if p.name.startswith('junit-platform-engine-')];require(len(engines)==1);version=engines[0].parent.name
launcher=repo/'org/junit/platform/junit-platform-launcher'/version/('junit-platform-launcher-'+version+'.jar');require(launcher.is_file())
if launcher not in libs:libs.append(launcher)
library_hashes={str(p.relative_to(repo)):sha(p)for p in libs};cp=':'.join(map(str,[jar,*libs]));jdk=b/'tools/jdk-25.0.4/bin';env={k:v for k,v in os.environ.items()if k not in('JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS')}
vectors=[('ORIGINAL',None,None)]
for name in INPUT['names']:
 raw=(transfer/(name+'.java')).read_text();last=list(re.finditer(r'\b([A-Z][A-Z0-9_]*)\("([^"\n]+)"\);',raw));require(len(last)==1)
 m=last[0];added=raw[:m.end()-1]+',\n  UNAPPROVED_CANARY("UNAPPROVED_CANARY");'+raw[m.end():]
 first=re.search(r'\b([A-Z][A-Z0-9_]*)\("([^"\n]+)"\)',raw);require(first is not None)
 changed=raw[:first.start(2)]+'UNAPPROVED_CANARY'+raw[first.end(2):]
 vectors.extend([(name+'_ADDED',name,added),(name+'_WIRE',name,changed)])
require(len(vectors)==37);results={}
for label,name,text in vectors:
 case=out/label;case.mkdir(mode=0o700);classes=case/'classes';classes.mkdir(mode=0o700)
 files=[transfer/'ProtocolSemanticTypeTest.java',transfer/'WireEnumOracleCanaryLauncher.java']
 if name is not None:
  shadow=case/(name+'.java');shadow.write_text(text);files.insert(0,shadow)
 c=subprocess.run([str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*map(str,files)],env=env,capture_output=True,timeout=30)
 (case/'compile.private.log').write_bytes(c.stdout+c.stderr);require(c.returncode==0 and not c.stderr)
 r=subprocess.run([str(jdk/'java'),'-cp',str(classes)+':'+cp,'WireEnumOracleCanaryLauncher'],env=env,capture_output=True,timeout=30)
 (case/'test.private.log').write_bytes(r.stdout+r.stderr)
 if name is None:require(r.returncode==0 and b'CANARY_STARTED=1 SUCCEEDED=1 FAILED=0'in r.stdout)
 else:require(r.returncode==1 and b'CANARY_STARTED=1 SUCCEEDED=0 FAILED=1'in r.stdout and b'CANARY_FAILURE_CLASS=org.opentest4j.AssertionFailedError'in r.stdout)
 results[label]={'actualExit':r.returncode,'logSha256':sha(case/'test.private.log')}
require(sha(jar)==normal['jarSha256']and all(sha(repo/n)==h for n,h in library_hashes.items())and not list(out.rglob('*.exec')))
value={'actualExit':0,'source':INPUT['source'],'testSource':INPUT['head'],'startUTC':started,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baselineRealTestPassed':True,'enumTypes':18,'mutationsRejected':36,'vectors':results,'input':INPUT,'libraryHashes':library_hashes,'vmActions':0,'productionChanged':False,'coverageCredit':0,'productionPtCredit':0,'formalAccepted':False}
(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in('input','vectors','libraryHashes')}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed current Test source required')
    if subprocess.check_output(['git','diff',SOURCE,'HEAD','--',*FILES[1:-1]]):raise ValueError('Production enums unchanged required')
    proof=json.loads((W/'pg2634-protocol-oracle-regression-v2/manifest.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['source']!=SOURCE or proof['result']['tests']!=82:raise ValueError('actual current normal Protocol required')
    c,o=run("python3 -B -c \"import hashlib,pathlib;print(hashlib.sha256(pathlib.Path('/home/mini/schubert-nk-pgpt/runs/PG2634-v2/manifest.safe.json').read_bytes()).hexdigest())\"",30)
    digest=o.strip();
    if c or len(digest)!=64 or any(x not in '0123456789abcdef'for x in digest):raise ValueError('actual normal manifest hash required')
    inputs={'source':SOURCE,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'names':NAMES,'normalManifestSha256':digest,'files':{Path(n).name:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()for n in FILES}}
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);code='INPUT='+repr(inputs)+'\n'+SERVER;compile(code,'<isolated semantic mutations>','exec');script=out/'mutations.private.py';script.write_text(code)
    c,_=run('test ! -e '+BASE+'/runs/PG2636-v1 && test ! -e '+BASE+'/transfer/PG2636-v1 && mkdir -m700 '+BASE+'/transfer/PG2636-v1',30)
    if c:raise ValueError('fresh isolated semantic mutation namespace required')
    for p in[*(ROOT/n for n in FILES),script]:
        c,_=copy(p,BASE+'/transfer/PG2636-v1/',60)
        if c:raise ValueError('immutable semantic mutation inputs required')
    c,o=run('python3 -B '+BASE+'/transfer/PG2636-v1/mutations.private.py',240)
    (out/'server.private.log').write_text(o);value={'actualExit':c,'source':SOURCE,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if not c:value['result']=json.loads(next(x for x in o.splitlines()if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return c


if __name__=='__main__':raise SystemExit(main())
