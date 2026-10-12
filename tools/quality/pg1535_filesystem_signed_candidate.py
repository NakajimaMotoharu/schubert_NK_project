"""New-only host signed candidate from independently qualified LAN six; no VM writes.

Private signing key never leaves the development host. All source/SQL/config,
prior signed release and payload hashes must be preserved before replacing JARs.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
from lan_server import HOST, authenticated, pinned_key, ssh_options
from pg1534_filesystem_candidate_contract import MODULES, verify_delta
from pg548_candidate_contract import artifacts, class_inventory

T=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='4d6bcbddb417b76d27e52d5d9640752c300edccf'
OLD_SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
OLD=W/'pg1292-release-v1'
NEXT=W/'pg1535-release-v1'
FROZEN=W/'pg1535-frozen-six-v1'
SIG=P/'pg1535-manifest-v1.sig'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def validate_gate(outer):
    if type(outer) is not dict or type(outer.get('result')) is not dict:
        raise ValueError('independently qualified whole gate required')
    gate=outer['result']
    expected={'actualExit':0,'productionSource':SOURCE,'tests':3583,'suites':524,'mainClasses':1637,'FESFlakyNotRun':0,'staticSixModules':0,'classifierFourCounters100':True,'formalAccepted':False}
    if type(outer.get('actualExit')) is not int or outer['actualExit']!=0 or any(type(gate.get(k))is not type(v) or gate[k]!=v for k,v in expected.items()):
        raise ValueError('whole source/count/quality gate refused')
    hashes=gate.get('jarHashes')
    if type(hashes)is not dict or set(hashes)!=set(MODULES) or any(type(h)is not str or len(h)!=64 or set(h)-set('0123456789abcdef')for h in hashes.values()):
        raise ValueError('exact six qualified artifact hashes required')
    debug=gate.get('debugLineQualification')
    expected_records={'dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy$Metadata.class','dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy$Snapshot.class'}
    if type(debug)is not dict or set(debug)!=expected_records or any(type(v)is not dict or set(v)!={'lineEntries','lineOffset','nonLineBytesIdentical'} or type(v['lineEntries'])is not int or v['lineEntries']<=0 or type(v['lineOffset'])is not int or v['lineOffset']!=1 or v['nonLineBytesIdentical']is not True for v in debug.values()):
        raise ValueError('independent exact debug-only record proof required')
    return gate

def receive(module):
    if module not in MODULES:raise ValueError('fixed module required')
    name=f'schubert-nk-{module}-0.1.0-SNAPSHOT.jar'
    remote=f'/home/mini/schubert-nk-pgpt/source-full-PG1532/src/schubert-nk-{module}/target/{name}'
    dest=FROZEN/module;dest.mkdir(mode=0o700)
    key=pinned_key()
    with tempfile.TemporaryDirectory(prefix='pg1535-pinned-receive-')as directory:
        known=Path(directory)/'known_hosts';known.write_text(key+'\n');os.chmod(known,0o600)
        shell=shlex.join(['ssh',*ssh_options(known)])
        code,status=authenticated(['rsync','-a','--secluded-args','-e',shell,f'mini@{HOST}:{remote}',str(dest)],known,180)
        if code:raise RuntimeError('exact qualified JAR transfer refused')
    return dest/name

def main():
    os.umask(0o077)
    if subprocess.check_output(['git','diff',SOURCE,'HEAD','--','src','pom.xml'],cwd=T) or subprocess.check_output(['git','diff','HEAD','--','src','tools','pom.xml'],cwd=T):
        raise ValueError('candidate source/tool dirty or foreign')
    operator=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
    require=lambda v:None if v else (_ for _ in ()).throw(ValueError('qualified signed candidate refused'))
    require(not any(os.path.lexists(p)for p in [NEXT,FROZEN,SIG,W/'pg1535-candidate-build-v1.safe.json']))
    raw_gate=(W/'pg1542-filesystem-full-qualified-v3/manifest.safe.json').read_bytes();outer=json.loads(raw_gate);gate=validate_gate(outer)
    from pg1541_filesystem_full_qualification_v2 import server_source
    require(outer['qualificationSourceSha256']==hashlib.sha256(server_source().encode()).hexdigest())
    old_raw=(OLD/'RELEASE-MANIFEST.json').read_bytes()
    require(hashlib.sha256(old_raw).hexdigest()=='ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99')
    data=json.loads(old_raw);baseline=artifacts(data['artifacts'])
    require(data['source']['commit']==OLD_SOURCE and data['versions']['schema']=='028')
    require(not OLD.is_symlink() and all(not p.is_symlink()and(p.is_dir()or p.is_file())for p in OLD.rglob('*')))
    require({str(p.relative_to(OLD))for p in OLD.rglob('*')if p.is_file()}==set(baseline)|{'RELEASE-MANIFEST.json','SHA256SUMS'})
    for path,row in baseline.items():require((OLD/path).stat().st_size==row['size'] and sha(OLD/path)==row['sha256'])
    require(os.statvfs(W).f_bavail*os.statvfs(W).f_frsize>=10*1024**3+sum(r['size']for r in baseline.values())*2)
    FROZEN.mkdir(mode=0o700);old_classes={};new_classes={};jars={}
    for module in MODULES:
        p=receive(module);require(sha(p)==gate['jarHashes'][module]);jars[module]=p
        old_path={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar'}.get(module)
        if old_path is None:old_path=next(path for path in baseline if Path(path).name==p.name)
        old_classes[module]=class_inventory(OLD/old_path);new_classes[module]=class_inventory(p)
    require(verify_delta(old_classes,new_classes)==1637)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    shutil.copytree(OLD,NEXT);require((NEXT/'VERSION').read_bytes()==b'0.1.0-PG1292\n');(NEXT/'VERSION').write_bytes(b'0.1.0-PG1535\n')
    main={'api/api.jar':'api','web/web.jar':'web','operations/batch.jar':'batch'};allowed={'VERSION'}
    for row in data['artifacts']:
        path=row['path'];p=NEXT/path;module=main.get(path)
        if module is None:module=next((m for m in MODULES if p.name==jars[m].name),None)
        if module is not None:shutil.copyfile(jars[module],p);allowed.add(path);require(sha(p)==gate['jarHashes'][module])
        row['size']=p.stat().st_size;row['sha256']=sha(p)
    changed={r['path']for r in data['artifacts']if r['sha256']!=baseline[r['path']]['sha256']}
    require(changed<=allowed and {'VERSION','operations/batch.jar','operations/lib/schubert-nk-storage-0.1.0-SNAPSHOT.jar'}<=changed)
    require(len(list((NEXT/'db/migration').glob('*.sql')))==28 and len(data['migrations'])==29)
    for path in set(baseline)-allowed:require((NEXT/path).read_bytes()==(OLD/path).read_bytes())
    data['release']='0.1.0-PG1535';data['source']['commit']=SOURCE
    encoded=json.dumps(data,ensure_ascii=False,indent=2).encode()+b'\n';(NEXT/'RELEASE-MANIFEST.json').write_bytes(encoded);digest=hashlib.sha256(encoded).hexdigest()
    sums={r['path']:r['sha256']for r in data['artifacts']};sums['RELEASE-MANIFEST.json']=digest
    (NEXT/'SHA256SUMS').write_bytes(''.join(sums[n]+'  '+n+'\n'for n in sorted(sums)).encode())
    require(set(artifacts(data['artifacts']))==set(baseline))
    for row in data['artifacts']:require((NEXT/row['path']).stat().st_size==row['size'] and sha(NEXT/row['path'])==row['sha256'])
    # Closed payload can be reproduced; signing material is development-host-only.
    log=W/'pg1535-sign-v1.private.log'
    with log.open('xb')as f:
        subprocess.run(['openssl','pkeyutl','-sign','-rawin','-inkey',str(P/'pg381-release-signing.pem'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-out',str(SIG)],stdout=f,stderr=f,check=True)
        subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(P/'pg381-release-pin.der'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-sigfile',str(SIG)],stdout=f,stderr=f,check=True)
    require(SIG.stat().st_size==64)
    with SIG.open('rb')as f:os.fsync(f.fileno())
    for p in NEXT.rglob('*'):
        if p.is_file():
            with p.open('rb')as f:os.fsync(f.fileno())
    for p in sorted([p for p in NEXT.rglob('*')if p.is_dir()]+[NEXT],key=lambda p:len(p.parts),reverse=True):
        fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
    result={'run':'PG1535-candidate-build-v1','actualExit':0,'candidateSource':SOURCE,'operatorSource':operator,'priorSource':OLD_SOURCE,'release':'0.1.0-PG1535','startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostGateSha256':hashlib.sha256(raw_gate).hexdigest(),'tests':3583,'suites':524,'mainClasses':1637,'changedClasses':4,'semanticChangedClasses':2,'debugOnlyChangedClasses':2,'addedClasses':2,'manifestSha256':digest,'artifacts':187,'schema':'028','sql':28,'history':29,'changedArtifactPaths':sorted(changed),'signatureVerified':True,'signatureSha256':sha(SIG),'helperSha256':sha(Path(__file__)),'guestMutations0':True,'candidateNotDeployed':True,'formalAccepted':False}
    with(W/'pg1535-candidate-build-v1.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result))
    return 0

if __name__=='__main__':raise SystemExit(main())
