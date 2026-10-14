"""Requalify retained own-source streams against new full; no VM recapture or byte exclusions."""
import hashlib
import ast
import json
import os
import shlex
import subprocess
from pyflakes.api import check
from lan_server import run
import pg2642_wire_oracle_native_qualified as bridge
from pg2744_backup_admission_group_full_six import SOURCE,validate
from pg1446_current_cold_stage import W


def server():
    raw=bridge.server().replace('PG2642','PG2746').replace('PG2640','PG2744').replace('3664','3669').replace(
        'source-full-PG2510','source-full-PG2694').replace(bridge.SOURCE,SOURCE)
    raw=raw.replace("transfer/PG2746-native-input.tar","transfer/PG2722-native-input.tar")
    assignments=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='OLD_JARS'for t in n.targets)]
    if len(assignments)!=1:raise ValueError('one historical embedded Jar binding required')
    assigned=assignments[0]
    hashes=ast.literal_eval(assigned.value)
    if set(hashes)!={'protocol','storage','bootstrap','api','web','batch'}or any(type(h)is not str or len(h)!=64 for h in hashes.values()):raise ValueError('typed historical binding boundary required')
    lines=raw.splitlines(keepends=True)
    raw=''.join(lines[:assigned.lineno-1]+lines[assigned.end_lineno:])
    raw=raw.replace('PG2746-native-v1','PG2746-native-v2').replace('qualified2640Tests','qualified2744Tests')
    marker="full=json.loads((B/'runs/PG2744-six-v1/manifest.safe.json').read_bytes());qualified=v['qualifiedFull']"
    if raw.count(marker)!=1:raise ValueError('one exact retained native/full boundary required')
    proof="""require(sha(B/'runs/PG2722-native-v1/manifest.safe.json')==OLD_NATIVE_SHA)
require(v['qualifiedFull']==OLD_FULL and v['productionSource']==SOURCE)
v['qualifiedFull']=QUALIFIED
"""
    raw=raw.replace(marker,proof+marker)
    if check('ARCHIVE_SHA=""\nOLD_JARS={}\nOLD_FULL={}\nOLD_NATIVE_SHA=""\nQUALIFIED={}\nSOURCE=""\ncoordinates=lambda a,b:{}\n'+raw,'<retained ownsource native>'):
        raise ValueError('complete strict native namespace required')
    compile(raw,'<retained current native full3669>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean input required')
    old=json.loads((W/'pg2722-operation-native-qualified-v1/manifest.safe.json').read_bytes())
    full=json.loads((W/'pg2745-backup-admission-full-qualified-v1/manifest.safe.json').read_bytes())
    for receipt in [old,full]:
        if type(receipt.get('actualExit'))is not int or receipt['actualExit']!=0:raise ValueError('actual full and own-native authority required')
    f=full['result'];expected={'productionSource':SOURCE,'tests':3669,'suites':541,'mainClasses':1643,'staticSixModules':0,'FESFlakyNotRun':0}
    if any(type(f.get(k))is not type(v)or f[k]!=v for k,v in expected.items()):raise ValueError('exact independent new full required')
    if old.get('productionSource')!=SOURCE or old['result']['classByteMismatch']!=0 or old['result']['oldNativeImported']is not False:raise ValueError('only actual ownsource streams required')
    validate(f['sourceSnapshot'])
    if subprocess.check_output(['git','diff','--name-only',f['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('all current inputs fixed required')
    inputs=json.loads((W/'pg2722-operation-native-qualified-v1/input.safe.json').read_bytes())
    archive=W/'pg2722-operation-native-qualified-v1/input.private.tar'
    definitions={'ARCHIVE_SHA':hashlib.sha256(archive.read_bytes()).hexdigest(),'OLD_JARS':inputs['qualifiedFull']['jarHashes'],
        'OLD_FULL':inputs['qualifiedFull'],'OLD_NATIVE_SHA':old['manifestSha256'],'QUALIFIED':f,'SOURCE':SOURCE}
    coordinates=bridge.entry().__globals__['coordinates']
    import inspect
    raw='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\n'+'\n'.join(k+'='+repr(v)for k,v in definitions.items())+'\n'+inspect.getsource(coordinates)+'\n'+server()
    if check(raw,'<complete actual retained qualification>'):raise ValueError('whole namespace required')
    authorities=set(definitions)
    counts={name:0 for name in authorities}
    for node in ast.parse(raw).body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name)and target.id in counts:counts[target.id]+=1
    if any(count!=1 for count in counts.values()):raise ValueError('single authority binding in complete namespace required')
    os.umask(0o077);out=W/'pg2746-backup-admission-native-qualified-v2';out.mkdir(mode=0o700)
    (out/'payload.private.py').write_text(raw)
    code,log=run('python3 -B -c '+shlex.quote(raw),180)
    (out/'server.private.log').write_text(log)
    result={'actualExit':code,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'newVmOperations0':True,'formalAccepted':False}
    if not code:result.update(json.loads(next(l for l in log.splitlines()if l.startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True))
    print(json.dumps({'actualExit':code,'newVmOperations0':True,'formalAccepted':False,
        'remaining':{k:sum(v[k]['missed']for v in result['result']['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']}if not code else None}));return code


if __name__=='__main__':raise SystemExit(main())
