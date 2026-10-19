"""Fresh deployed296 full11 before-image; no new stop, native success, or placement authority."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
from pg4996_resume_connection import authenticate_host
from pg1446_current_cold_stage import P,SSH,W
from pg1674_critical_management_gate import management_gate
import pg5476_current_admission_image as admission

SLOT='pg5606-current-full-preservation-v2'
SOURCE=admission.SOURCE
FIELDS=('backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native')


def native_expected(original,selected):
    prefix='/run/schubert-nk/pt-coverage/'
    expected={p:v for p,v in original.items()if p.endswith('.exec')}
    if len(expected)!=92 or len(selected)!=10:raise ValueError('exact preserved92 plus genuine ten catalog points before union94')
    seen=set()
    for row in selected:
        relative=row['relative']
        if type(relative)is not str or relative.startswith('/')or'..'in relative.split('/')or not relative.endswith('.exec'):raise ValueError('fixed relative native point only')
        path=prefix+relative
        if path in seen:raise ValueError('no duplicate physical point')
        seen.add(path);value={'metadata':row['metadata'],'sha256':row['sha256']}
        if len(row['metadata'])!=9 or row['metadata'][6]!=row['bytes']or len(row['sha256'])!=64:raise ValueError('actual bounded metadata and byte hash')
        if path in expected and expected[path]!=value:raise ValueError('catalog cannot hide mutation of any original native file')
        expected[path]=value
    if len(expected)!=94:raise ValueError('all92 retained and exactly two later physical points; no old native acceptance credit')
    return expected


def payload():
    original=W/'pg5534-current-owned-post-v1';raw=(original/'payload.private.py').read_text()
    if hashlib.sha256(raw.encode()).hexdigest()!='48b0ddaaddc1b11ca517bad030b7ee7da8f4b0abfa033a4382f2f002b6bb4807':raise ValueError('immutable original closed-cohort reader; only reuse read contracts')
    catalog_raw=(W/'pg5508-current-native-catalog-v1/manifest.safe.json').read_bytes()
    if hashlib.sha256(catalog_raw).hexdigest()!='0e430c90dfa9c8c5ccaba82d7eac204dfc8462d4f31ab16ea71173c500a8ec7e':raise ValueError('immutable genuine source296 physical catalog')
    catalog=json.loads(catalog_raw)
    if catalog['actualExit']!=0 or catalog['productionSource']!=SOURCE:raise ValueError('old native catalog as preservation data only')
    tree=ast.parse(raw);end=next(n.lineno for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='result'for t in n.targets))
    raw=''.join(raw.splitlines(keepends=True)[:end-1])
    marker="return tree(pathlib.Path('/run/schubert-nk/pt-coverage'))"
    if raw.count(marker)!=1:raise ValueError('one fresh native return, retain original two independent SQL reads')
    raw=raw.replace(marker,marker+', rows',1)
    marker='    native = snapshot()\n    require(native == snapshot())'
    if raw.count(marker)!=1:raise ValueError('one double-snapshot boundary before reference release')
    replacement='''    native, fresh_rows = snapshot()
    second_native, second_rows = snapshot()
    require(native == second_native and fresh_rows == second_rows)
    expected_native = native_expected(original['native'], CATALOG_POINTS)
    require({p:v for p,v in native.items() if p.endswith('.exec')} == expected_native)
    journal = command(['journalctl','--boot='+ROOT_BINDING['boot'].replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+ROOT_BINDING['invocation'],'-o','json','--no-pager'])
    fresh_pid1 = json.loads(stable['project'](journal))
    require(fresh_pid1 == after['pid1'])
    captured = {'rows':fresh_rows,'native':native,'pid1':fresh_pid1}
    captured['units'] = {u:show(u,STATE_FIELDS) for u in after['units']}
    captured['configuration'] = {u:complete_configuration(command(['systemctl','show',u,'--property='+','.join(sorted(FIELDS))]).decode(),u) for u in after['configuration']}
    for category,path in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('runtime','/run/systemd/system')]:
        captured[category] = tree(pathlib.Path(path))
    captured['extraDurable'] = {k:tree(pathlib.Path(min(v,key=len))) for k,v in after['extraDurable'].items()}
    captured['unitFilesActual'] = {p:metadata(pathlib.Path(p))+[hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()] for p in after['unitFilesActual']}
    require(set(captured) == set(FULL11) and {k:v for k,v in captured.items() if k != 'native'} == after)
    require(native == tree(pathlib.Path('/run/schubert-nk/pt-coverage')))
    require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active') and not list(pathlib.Path('/run/schubert-nk/startup').glob('*.start.intent')))
    destination = base / NEW_SLOT
    require(not os.path.lexists(destination)); destination.mkdir(mode=0o700)
    encoded = json.dumps(captured,sort_keys=True).encode()
    with(destination/'before.private.json').open('xb') as f:
        os.fchmod(f.fileno(),0o600); f.write(encoded); f.flush(); os.fsync(f.fileno())
    for directory in (destination,destination.parent):
        fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:os.fsync(fd)
        finally:os.close(fd)
'''
    raw=raw.replace(marker,replacement,1)
    marker="\nbus = dbus.SystemBus(private=True)\nmanager ="
    if raw.count(marker)!=1:raise ValueError('one top-level metadata-reference acquisition boundary')
    preflight="""
stable_path = base / 'pg5496-current-owned-tools-v1' / 'pg5496_stable_journal.py'
stable_stat = stable_path.lstat()
require(stat.S_ISREG(stable_stat.st_mode) and stable_stat.st_uid == stable_stat.st_gid == 0 and stable_stat.st_nlink == 1 and not os.listxattr(stable_path))
stable_source = stable_path.read_bytes()
require(hashlib.sha256(stable_source).hexdigest() == HASHES['pg5496_stable_journal.py'] and metadata9(stable_path.lstat()) == metadata9(stable_stat))
stable_ast = ast.parse(stable_source)
functions = [n for n in stable_ast.body if isinstance(n,ast.FunctionDef) and n.name in {'pairs','project'}]
require(len(functions) == 2)
stable = {'json':json,'require':require}
exec(compile(ast.Module(body=functions,type_ignores=[]),'<same-source PID1 history>', 'exec'),stable)
"""
    raw=raw.replace(marker,preflight+marker,1)
    header='NEW_SLOT='+repr(SLOT)+'\nFULL11='+repr(FIELDS)+'\nCATALOG_POINTS='+repr(catalog['selected'])+'\nROOT_BINDING='+repr(admission.live())+'\n'+inspect.getsource(native_expected)+'\n'
    tail="""
require(len(refs)==10)
result={'actualExit':0,'productionSource':data['source']['commit'],'BOM':hashlib.sha256(manifest).hexdigest(),'privateBeforeSha256':hashlib.sha256(encoded).hexdigest(),'sealedFull11Fields':11,'tables':24,'all24EqualTwice':True,'unitCount':10,'nativePhysicalFiles':94,'all92OriginalAndTenCatalogUnionPreserved':True,'allTenRefsReturnedNormally':True,'freshPid1HistoryMatches':True,'allOriginalBackupCredentialTreesUnchanged':True,'allClientAdvisoryFlock0':True,'allKernelActor0':True,'startsStopsReloadsSqlWrites0':True,'dataOnlyNotRuntimeAuthority':True,'oldNativeAcceptanceImported':False,'formalAccepted':False}
with(destination/'result.safe.json').open('x') as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps(result))
"""
    result=header+raw+tail
    if check(result,'<fresh full11 preservation complete globals>'):raise ValueError('no undefined name before guest output')
    compile(result,'<fresh before-image only, not repeated ownedstop>','exec')
    return result


def main():
    fresh=json.loads((W/'pg5602-current-vm-reauthentication-v1/manifest.safe.json').read_bytes())
    if fresh['actualExit']!=0 or fresh['source']!=SOURCE or fresh['result']['artifactsVerified']!=187:raise ValueError('fresh deployed signed187 read first')
    raw=payload();authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    with(out/'payload.private.py').open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    with management_gate(P/'current-management-critical.lock'):
        result=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=240)
    for name,blob in(('stdout.private.log',result.stdout),('stderr.private.log',result.stderr)):
        with(out/name).open('xb')as f:f.write(blob);f.flush();os.fsync(f.fileno())
    value={'actualExit':result.returncode,'source':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False,'oldStopReissued':False}
    if result.returncode==0:value['result']=json.loads(result.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return result.returncode


if __name__=='__main__':raise SystemExit(main())
