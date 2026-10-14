"""Changed Main independent DB PT. No old host/native coverage or VM actions."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run
from pg1446_current_cold_stage import W
from pg1628_unsupported_ports_selected import LIBRARIES

ROOT=Path(__file__).resolve().parents[2]
BASE='/home/mini/schubert-nk-pgpt'
SLOT='PG2796-candidate-v1'
FILES=['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.java',
       'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java',
       'tools/quality/vm/050_s1/Pg2796JdbcContractLauncher.java']
SERVER=r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077)
b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2796-candidate-v1';transfer=b/'transfer/PG2796-candidate-v1';source=b/'source-full-PG2770';repo=b/'m2/repository'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(value):
 if not value:raise ValueError('changed Main JDBC contract refused')
require(not out.exists()and os.statvfs(b).f_bavail*os.statvfs(b).f_frsize>=10*1024**3)
out.mkdir(mode=0o700);classes=out/'classes';classes.mkdir(mode=0o700);(out/'tmp').mkdir(mode=0o700)
jars=[];libraries=[]
for m in ['protocol','storage','bootstrap','api','web','batch']:
 p=source/'src'/('schubert-nk-'+m)/'target'/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')
 require(sha(p)==INPUT['baseFull']['jarHashes'][m]);jars.append(str(p))
for n,h in INPUT['libraries'].items():
 p=repo/n;require(sha(p)==h);libraries.append(str(p))
oldxml=source/'src/schubert-nk-batch/target/surefire-reports/TEST-dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest.xml'
oldxmlhash=sha(oldxml);old=ET.parse(oldxml).getroot()
require(all(old.get(k)=='0'for k in ['failures','errors','skipped']))
properties=[p.get('value')for p in old.findall('properties/property')if p.get('name')=='java.class.path']
require(len(properties)==1 and properties[0]);extra={}
for name in properties[0].split(':'):
 p=Path(name)
 if p.suffix=='.jar'and p.is_relative_to(repo):
  require(p.is_file()and p.resolve().is_relative_to(repo.resolve()));extra[str(p.relative_to(repo))]=sha(p)
  if str(p)not in libraries:libraries.append(str(p))
require(any('flyway-core/'in p for p in extra)and any('postgresql/postgresql/'in p for p in extra))
fixtures=source/'src/schubert-nk-batch/target/test-classes'
fixturehashes={str(p.relative_to(fixtures)):sha(p)for p in fixtures.rglob('*.class')};require(fixturehashes)
for n,h in INPUT['files'].items():require(sha(transfer/n)==h)
cp=':'.join(jars+[str(fixtures)]+libraries);jdk=b/'tools/jdk-25.0.4/bin';commands=[];start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def execute(label,args,timeout):
 commands.append(args)
 env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']};env['SCHUBERT_PG_ROOT']=str(b/'tools/postgresql18/usr')
 r=subprocess.run(args,capture_output=True,timeout=timeout,env=env)
 (out/(label+'.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0);return r
c=execute('compile',[str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*[str(transfer/n)for n in INPUT['files']]],90);require(not c.stderr)
mainclasses={str(p.relative_to(classes)):sha(p)for p in classes.rglob('MorningDatabaseSession*.class')if 'Test'not in p.name};require(mainclasses)
expected=INPUT['tests'];xml=out/'tests.xml'
execute('tests',[str(jdk/'java'),'--enable-native-access=ALL-UNNAMED','-Dfile.encoding=UTF-8','-Dnk.pt.repository='+str(source),'-Djava.io.tmpdir='+str(out/'tmp'),'-cp',str(classes)+':'+cp,'Pg2796JdbcContractLauncher',str(xml),str(expected)],1800)
x=ET.parse(xml).getroot();cases=x.findall('testcase')
require(x.attrib=={'name':'PG2796','tests':str(expected),'failures':'0','errors':'0','skipped':'0'}and len(cases)==expected and not x.findall('.//failure'))
names={p.get('name')for p in cases}
require(len(names)==expected and {'mdb2792001SuccessfulBackupRejectsNullJdbcResourcesWithoutNpe','mdb2796001ReadOnlyAndAbandonedNullResourcesPreserveAllCommittedRows'}.issubset(names))
require(all(sha(fixtures/n)==h for n,h in fixturehashes.items())and sha(oldxml)==oldxmlhash and all(sha(repo/n)==h for n,h in extra.items())and all(sha(transfer/n)==h for n,h in INPUT['files'].items()))
result={'actualExit':0,'candidateSource':INPUT['head'],'tests':expected,'FESAbortedNotRun':0,'xmlSha256':sha(xml),'compiledMainHashes':mainclasses,'input':INPUT,'extraLibraries':extra,'commands':commands,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseFixturesUnchanged':True,'mainRecompiled':True,'coverageClaim':False,'nativeImported':False,'vmActions':0,'formalAccepted':False}
(out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True))
print(json.dumps({'actualExit':0,'candidateSource':INPUT['head'],'tests':expected,'FESAbortedNotRun':0,'xmlSha256':sha(xml),'manifestSha256':sha(out/'manifest.safe.json'),'coverageClaim':False,'nativeImported':False,'vmActions':0,'formalAccepted':False}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean candidate required')
    full=json.loads((W/'pg2772-db-contract-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit']!=0 or full['result']['tests']!=3673:raise ValueError('base dependency qualification required')
    old=json.loads((W/'pg1618-current-ordinary-native-qualified-v3/input.safe.json').read_bytes())
    libraries=dict(old['libraries'])
    for n in LIBRARIES:libraries[n]=hashlib.sha256((ROOT.parent/'toolchain/m2/repository'/n).read_bytes()).hexdigest()
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    value={'head':head,'baseFull':full['result'],'files':{Path(n).name:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()for n in FILES},'libraries':libraries,'tests':(ROOT/FILES[1]).read_text().count('@Test\n')}
    code='INPUT='+repr(value)+'\n'+SERVER
    from pyflakes.api import check
    if check(code,'<candidate real DB contract>'):raise ValueError('whole namespace required')
    os.umask(0o077);out=W/'pg2796-jdbc-candidate-contract-v1';out.mkdir(mode=0o700);script=out/'selected.private.py';script.write_text(code)
    status,_=run(f'test ! -e {BASE}/runs/{SLOT} && test ! -e {BASE}/transfer/{SLOT} && mkdir -m700 {BASE}/transfer/{SLOT}',30)
    if status:raise ValueError('new-only candidate required')
    for p in [*(ROOT/n for n in FILES),script]:
        status,_=copy(p,f'{BASE}/transfer/{SLOT}/',60)
        if status:raise ValueError('exact transfer required')
    status,output=run(f'python3 -B {BASE}/transfer/{SLOT}/selected.private.py',1900)
    (out/'server.private.log').write_text(output)
    result={'actualExit':status,'candidateSource':head,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'coverageClaim':False,'formalAccepted':False}
    if not status:result.update(json.loads(next(l for l in output.splitlines()if l.startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result));return status


if __name__=='__main__':raise SystemExit(main())
