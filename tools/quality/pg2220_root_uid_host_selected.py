"""Current frozen Main real kernel boundary PT; no Main recompilation or VM operation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run
from pg1446_current_cold_stage import W
from pg2176_newsource_normal_observer import SOURCE
from pg1628_unsupported_ports_selected import LIBRARIES

ROOT=Path(__file__).resolve().parents[2]
SLOT='pg2220-root-uid-host-selected-v1'
BASE='/home/mini/schubert-nk-pgpt'
FILES=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/RootStartupContextTest.java',
       'tools/quality/vm/050_s1/Pg2220RootUidLauncher.java','tools/quality/vm/050_s1/NativeCoverage.java',
       'tools/quality/vm/050_s1/NativeCoverageXml471.java']

SERVER=r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077)
b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG2220-selected-v1';transfer=b/'transfer/PG2220-selected-v1';source=b/'source-full-PG2124';repo=b/'m2/repository'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v):
 if not v:raise ValueError('current frozen Main kernel boundary refused')
require(not out.exists() and os.statvfs(b).f_bavail*os.statvfs(b).f_frsize>=10*1024**3)
out.mkdir(mode=0o700);classes=out/'classes';classes.mkdir(mode=0o700);(out/'tmp').mkdir(mode=0o700)
jars=[];hosts=[];libraries=[]
for m in ['protocol','storage','bootstrap','api','web','batch']:
 t=source/'src'/('schubert-nk-'+m)/'target';jar=t/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');e=t/'jacoco.exec'
 require(sha(jar)==INPUT['full']['jarHashes'][m] and sha(e)==INPUT['full']['qualificationInputs'][m]['exec'])
 jars.append(str(jar));hosts.append(str(e))
for name,h in INPUT['libraries'].items():
 p=repo/name;require(sha(p)==h);libraries.append(str(p))
for n,h in INPUT['files'].items():require(sha(transfer/n)==h)
fixtures=source/'src/schubert-nk-batch/target/test-classes'
fixture_hashes={str(p.relative_to(fixtures)):sha(p) for p in fixtures.rglob('*.class')}
require(fixture_hashes)
cp=':'.join(jars+[str(fixtures)]+libraries);jdk=b/'tools/jdk-25.0.4/bin'
commands=[];start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def execute(label,args):
 commands.append(args)
 env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']}
 r=subprocess.run(args,capture_output=True,timeout=60,env=env)
 (out/(label+'.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0);return r
c=execute('compile',[str(jdk/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*[str(transfer/n)for n in INPUT['files']]])
require(not c.stderr)
execfile=out/'selected.exec';xml=out/'tests.xml';agent=repo/'org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
r=execute('tests',[str(jdk/'java'),'--enable-native-access=ALL-UNNAMED','-Dfile.encoding=UTF-8','-Djava.io.tmpdir='+str(out/'tmp'),'-javaagent:'+str(agent)+'=destfile='+str(execfile)+',append=false','-cp',str(classes)+':'+cp,'Pg2220RootUidLauncher',str(xml)])
require(b'PG2220 tests1 failures0 errors0 skipped0 aborted0 notRun0' in r.stdout)
x=ET.parse(xml).getroot();require(x.attrib=={'name':'PG2220','tests':'1','failures':'0','errors':'0','skipped':'0'} and len(x.findall('testcase'))==1 and not x.findall('.//failure'))
coverage={};xml_hashes={}
for m,jar in zip(['protocol','storage','bootstrap','api','web','batch'],jars):
 r=execute(m+'-coverage',[str(jdk/'java'),'-cp',str(classes)+':'+cp,'NativeCoverage',jar,*hosts,str(execfile)])
 coverage[m]=json.loads(r.stdout);require(coverage[m]['classByteMismatch']==0)
 p=out/(m+'.xml');execute(m+'-xml',[str(jdk/'java'),'-cp',str(classes)+':'+cp,'NativeCoverageXml471',jar,str(p),*hosts,str(execfile)]);xml_hashes[m]=sha(p)
require(all(sha(fixtures/n)==h for n,h in fixture_hashes.items()))
require(all(sha(transfer/n)==h for n,h in INPUT['files'].items()))
remaining={k:sum(v[k]['missed']for v in coverage.values())for k in ['LINE','METHOD','CLASS','BRANCH']}
result={'actualExit':0,'tests':1,'FESAbortedNotRun':0,'source':INPUT['source'],'testSource':INPUT['head'],'xmlSha256':sha(xml),'execSha256':sha(execfile),'coverage':coverage,'remainingHostOnly':remaining,'xmlHashes':xml_hashes,'input':INPUT,'commands':commands,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixturesUnchanged':True,'MainRecompiled':False,'oldNativeImported':False,'vmActions0':True,'formalAccepted':False}
(out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True))
print(json.dumps({'actualExit':0,'tests':1,'FESAbortedNotRun':0,'remainingHostOnly':remaining,'source':INPUT['source'],'testSource':INPUT['head'],'manifestSha256':sha(out/'manifest.safe.json'),'classByteMismatch':0,'javacWarnings':0,'oldNativeImported':False,'vmActions0':True,'formalAccepted':False}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed test source required')
    changed=subprocess.check_output(['git','diff','--name-only',SOURCE,'HEAD','--','src','pom.xml'],text=True).splitlines()
    if any('/src/main/'in n or n.endswith('pom.xml')for n in changed):raise ValueError('unchanged qualified Main required')
    full=json.loads((W/'pg2125-metadata-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit']!=0 or full['result']['productionSource']!=SOURCE:raise ValueError('actual whole current source required')
    old=json.loads((W/'pg1618-current-ordinary-native-qualified-v3/input.safe.json').read_bytes())
    libs=dict(old['libraries']);repo=ROOT.parent/'toolchain/m2/repository'
    for n in LIBRARIES:libs[n]=hashlib.sha256((repo/n).read_bytes()).hexdigest()
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    value={'source':SOURCE,'head':head,'full':full['result'],'files':{Path(n).name:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()for n in FILES},'libraries':libs}
    code='INPUT='+repr(value)+'\n'+SERVER
    from pyflakes.api import check
    if check(code,'<actual fixed current selected server>'):raise ValueError('whole namespace required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);script=out/'selected.private.py';script.write_text(code)
    c,_=run('test ! -e '+BASE+'/runs/PG2220-selected-v1 && test ! -e '+BASE+'/transfer/PG2220-selected-v1 && mkdir -m700 '+BASE+'/transfer/PG2220-selected-v1',30)
    if c:raise ValueError('one fresh selected namespace required')
    for p in [*(ROOT/n for n in FILES),script]:
        c,_=copy(p,BASE+'/transfer/PG2220-selected-v1/',60)
        if c:raise ValueError('immutable selected transfer required')
    c,o=run('python3 -B '+BASE+'/transfer/PG2220-selected-v1/selected.private.py',180)
    (out/'server.private.log').write_text(o)
    result={'actualExit':c,'source':SOURCE,'testSource':head,'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if not c:result.update(json.loads(next(l for l in o.splitlines()if l.startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result));return c


if __name__=='__main__':raise SystemExit(main())
