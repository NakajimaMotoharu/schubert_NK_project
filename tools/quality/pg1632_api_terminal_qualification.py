"""Independent thirteen PT/static/source scope qualification, no repeated build."""
import hashlib
import inspect
import json
import os
from lan_server import copy, run
from pg1525_filesystem_selected import W
from pg1630_api_terminal_selected import PRODUCTION


def qualify_result(m):
    expected={'ApiProcessMainTest':4,'ApiProcessLifetimeTest':4,'ApiTerminalCaptureTest':3,'ApiCommittedFatalBindingTest':2}
    if type(m)is not dict or m.get('productionSource')!=PRODUCTION or any(type(m.get(k))is not int or m[k]!=0 for k in ['actualExit','mavenExit','dependencyCompileExit']) or m.get('sourceInputsUnchanged')is not True or m.get('globalCacheUnchanged')is not True or m.get('dependencyTestGoalAbsent')is not True:
        raise ValueError('actual unchanged successful selected source required')
    if m.get('staticIssues')!={'protocol':0,'storage':0,'bootstrap':0,'api':0}or any(type(v)is not int for v in m['staticIssues'].values())or type(m.get('suites'))is not dict or set(m['suites'])!=set(expected):
        raise ValueError('four static modules and exact four selected suites required')
    for name,count in expected.items():
        v=m['suites'][name]
        if v.get('module')!='api' or type(v.get('tests'))is not int or v['tests']!=count or any(type(v.get(k))is not int or v[k]!=0 for k in ['failures','errors','skipped'])or v.get('freshAfterBegin')is not True:
            raise ValueError('exact fresh passing API thirteen required')
    return 13


SERVER=r'''
import datetime,hashlib,json,os,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077)
b=Path('/home/mini/schubert-nk-pgpt');root=b/'runs/PG1635-selected-v1';source=b/'source-selected-PG1635';out=b/'runs/PG1632-selected-qualification-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v):
 if not v:raise ValueError('actual selected contract qualification refused')
require(not out.exists());out.mkdir(mode=0o700)
m=json.loads((root/'manifest.safe.json').read_bytes());tests=qualify_result(m)
begin=json.loads((root/'begin.safe.json').read_bytes());require(begin['sourceSnapshot']==m['sourceSnapshot'])
require(all(sha(source/n)==h for n,h in begin['inputs'].items()))
qualified=json.loads((b/'runs/PG1618-native-v1/input.safe.json').read_bytes())['qualifiedFull']
require(sha(b/'runs/PG1532-six-v1/manifest.safe.json')==qualified['serverManifestSha256'])
class_hashes={};jar_hashes={};added=[];changed=[]
for module in ['protocol','storage','bootstrap','api']:
 t=source/'src'/('schubert-nk-'+module)/'target';jar=t/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');old=b/'source-full-PG1532/src'/('schubert-nk-'+module)/'target'/jar.name
 require(sha(old)==qualified['jarHashes'][module])
 with zipfile.ZipFile(jar)as z:now={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
 with zipfile.ZipFile(old)as z:before={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
 require(set(before)<=set(now));class_hashes[module]=now;jar_hashes[module]=sha(jar)
 for n,h in now.items():
  if n not in before:added.append(module+':'+n)
  elif h!=before[n]:changed.append(module+':'+n)
 if module!='api':require(now==before)
 for p in (t/'surefire-reports').glob('TEST-*.xml'):
  x=ET.parse(p).getroot();name=x.attrib['name'].split('.')[-1];v=m['suites'].get(name)
  require(v is not None and sha(p)==v['xmlSha256'] and len(x.findall('testcase'))==v['tests'] and not any(c.find(k)is not None for c in x.findall('testcase')for k in ['failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError']))
 p=t/'spotbugsXml.xml';require(len(ET.parse(p).getroot().findall('.//BugInstance'))==0)
 require(all(sha(source/n)==h for n,h in begin['inputs'].items()))
prefix='api:dev/codex/schubert/nk/api/bootstrap/'
require(set(added)=={prefix+'ApiTerminalCapture'+s+'.class'for s in ['', '$Factory','$Open','$Capture','$Operation','$Owner']})
require(set(changed)=={prefix+'ApiProcessMain.class',prefix+'ApiProcessLifetime.class',prefix+'ApiProcessLifetime$1.class'})
result={'actualExit':0,'productionSource':PRODUCTION,'sourceSnapshot':m['sourceSnapshot'],'freshApiPt':tests,'staticModules':4,'staticIssues':0,'allSourceInputsUnchanged':True,'unchangedDependencyClassBytes':True,'changedClasses':changed,'addedClasses':added,'classHashes':class_hashes,'jarHashes':jar_hashes,'selectedManifestSha256':sha(root/'manifest.safe.json'),'selectedLogSha256':sha(root/'maven.private.log'),'suites':m['suites'],'affectedCoverage':m['affectedCoverage'],'compileOnlyUnselectedNotPtPass':True,'oldSourceExecImported':False,'wholeFreshRegressionPending':True,'formalAccepted':False,'vmOperations':0,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'freshApiPt':tests,'staticModules':4,'staticIssues':0,'unchangedDependencyClassBytes':True,'changedClasses':len(changed),'addedClasses':len(added),'manifestSha256':sha(out/'manifest.safe.json'),'formalAccepted':False,'vmOperations':0}))
'''


def main():
    os.umask(0o077);out=W/'pg1632-api-terminal-qualified-v1';out.mkdir(mode=0o700)
    code='PRODUCTION='+repr(PRODUCTION)+'\n'+inspect.getsource(qualify_result)+'\n'+SERVER
    from pyflakes.api import check
    if check(code,'<actual complete selected contract qualifier>'):raise ValueError('generated static gate refused')
    p=out/'pg1632-qualified.private.py';p.write_text(code)
    e,o=run('test ! -e /home/mini/schubert-nk-pgpt/transfer/pg1632-qualified.private.py && test ! -e /home/mini/schubert-nk-pgpt/runs/PG1632-selected-qualification-v1',timeout=30)
    if e:raise ValueError('new-only qualification namespace required')
    e,o=copy(p,'/home/mini/schubert-nk-pgpt/transfer/',timeout=60)
    if e:raise ValueError('fixed qualifier transfer refused')
    e,o=run('python3 -B /home/mini/schubert-nk-pgpt/transfer/pg1632-qualified.private.py',timeout=90)
    (out/'server.private.log').write_text(o);safe={'actualExit':e,'scriptSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if e==0:safe.update(json.loads(next(v for v in o.splitlines()if v.startswith('{'))))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return e


if __name__=='__main__':raise SystemExit(main())
