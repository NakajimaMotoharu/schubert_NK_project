"""Fixed pinned SSH phases for one new public-tool namespace; never targets old runtime or aru."""
from pathlib import Path
import base64, datetime, hashlib, io, json, os, re, shlex, subprocess, sys, tarfile

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R/'tools/quality'))
from pmo_quota_binding import window
I = R/'evidence/01_PT/018_NK-OPS-001/input'
W = R.parent/'pgpt-runs/PG379/pg30726-haruka-common91-v3'
PUBLIC = R/'evidence/01_PT/018_NK-OPS-001/evidence'
PMO = R.parent/'PMO/hourly-monitor'
REMOTE = '/home/mini/schubert-nk-pgpt/runs/pg30726-common91-v3'
TMP = '/dev/shm/pgpt-pg30726-common91-v3'
TC = R.parent/'toolchain'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()

def require(value, message):
    if not value:
        raise ValueError(message)

def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())

def fresh(path):
    value = json.loads(Path(path).read_text())
    at = datetime.datetime.fromisoformat(value['observedAtUTC'])
    age = (datetime.datetime.now(datetime.timezone.utc)-at).total_seconds()
    require(value['schema']=='PGPT_FRESH_QUOTA_V1' and 0<=age<=120
            and value['ordinaryUsageAllowed'] is True and value['primary'] is not None,
            'fresh available shared limits before a new phase')
    for key in ('primary','secondary'):
        item = value[key]
        if item:
            require(window(item)==item and item['remainingPercent']>10
                    and item['resetsAt']>datetime.datetime.now(datetime.timezone.utc).timestamp(),
                    'ordinary ten-percent reserve, no override')
    return value

def connection():
    sys.path.insert(0, str(PMO/'haruka-transition-20261114'))
    from remote_access import config
    data = config('haruka')
    environment = json.loads((PMO/'haruka-transition-20261114/HARUKA_EXECUTION_ENVIRONMENT.json').read_text())
    require(environment['hostName']=='haruka' and environment['status']=='DIRECT_OS_BASELINE_READY',
            'dedicated current host reference')
    pin = Path(environment['knownHosts'])
    require(pin.is_file() and pin.stat().st_size>0, 'dedicated existing host key pin')
    askpass = PMO/'haruka-transition-20261114/ssh_askpass.py'
    require(askpass.is_file() and os.access(askpass, os.X_OK), 'existing private auth provider')
    args = ['/usr/bin/ssh','-F','/dev/null','-o','StrictHostKeyChecking=yes',
            '-o','UserKnownHostsFile='+str(pin),'-o','GlobalKnownHostsFile=/dev/null',
            '-o','UpdateHostKeys=no','-o','ForwardAgent=no','-o','ClearAllForwardings=yes',
            '-o','ControlMaster=no','-o','IdentityAgent=none','-o','PubkeyAuthentication=no',
            '-o','PreferredAuthentications=password','-o','KbdInteractiveAuthentication=no',
            '-o','NumberOfPasswordPrompts=1','-o','ConnectTimeout=12','mini@'+data['addr']]
    env = dict(PATH='/usr/bin:/bin', DISPLAY='pgpt-no-ui', SSH_ASKPASS=str(askpass),
               SSH_ASKPASS_REQUIRE='force', PMO_SSH_TARGET='haruka', LANG='C.UTF-8')
    return args, env, dict(knownHostsSha256=sha(pin), authProviderCodeSha256=sha(askpass),
                          hostSelector='server.info haruka/mini', credentialExported=False)

def ssh(label, code, input_file=None, input_bytes=None, binary=False):
    args, env, pins = connection()
    require(not (W/(label+'-local-begin.json')).exists(), 'observe original phase, do not duplicate')
    command = 'python3 -c '+shlex.quote('import base64;exec(base64.b64decode('
              +repr(base64.b64encode(code.encode()).decode())+'))')
    write(W/(label+'-local-begin.json'), dict(atUTC=now(), sourcePlanSha256=sha(W/'plan.json'),
          localOwnerPid=os.getpid(), hostPins=pins, phase=label, remoteCodeSha256=hashlib.sha256(code.encode()).hexdigest()))
    stdin = open(input_file,'rb') if input_file else subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL
    output = W/(label+('.private.tar' if binary else '.private.stdout'))
    try:
        with output.open('xb') as out, (W/(label+'.private.stderr')).open('xb') as err:
            child = subprocess.Popen([*args, command], env=env, stdin=stdin, stdout=out,
                                     stderr=err, start_new_session=True)
            write(W/(label+'-local-process.json'), dict(pid=child.pid, ownerPid=os.getpid(), atUTC=now()))
            try:
                child.communicate(input=input_bytes, timeout=1100)
            except subprocess.TimeoutExpired:
                # Closing our SSH transport does not certify any remote child termination.
                child.kill(); child.wait(timeout=15)
                write(W/(label+'-local-terminal.json'), dict(actualExit=child.returncode,
                      remoteTerminal='UNKNOWN_TRANSPORT_TIMEOUT_NO_RESTART', atUTC=now()))
                raise
            code_value = child.returncode
    finally:
        if input_file:
            stdin.close()
    write(W/(label+'-local-terminal.json'), dict(actualExit=code_value, atUTC=now(),
          outputSha256=sha(output), privateStderrSha256=sha(W/(label+'.private.stderr'))))
    require(code_value==0, 'SSH phase nonzero; preserve private transport/remote evidence, no retry')
    if binary:
        return output
    text = output.read_text()
    require(len(text)<8*1024**2 and 'PGPT_JSON_BEGIN' in text and 'PGPT_JSON_END' in text,
            'bounded structured response required')
    return json.loads(text.split('PGPT_JSON_BEGIN',1)[1].split('PGPT_JSON_END',1)[0])

def source_payload(source):
    require(re.fullmatch('[0-9a-f]{40}',source), 'explicit fixed Git source')
    review = json.loads((PUBLIC/'PG30718-common91-whole-source-closure-and-independent-inverses-v1/manifest.json').read_text())
    paths = review['allSelectedMainPaths']+review['allSelectedTestPaths']+[review['fullTestHelperPath']]
    paths += ['pom.xml','mvnw','program/characterization/pom.xml',
              'tools/quality/static/pmd.xml','tools/quality/static/checkstyle.xml']
    paths += ['src/schubert-nk-'+name+'/pom.xml' for name in ('protocol','storage','bootstrap','api','web','batch')]
    prefixes = ['.mvn', 'program/characterization/tests/resources', 'program/characterization/baseline/current',
                'program/characterization/reports/current/pgpt-gate-20260901-05',
                'program/characterization/reports/current/pgpt-gate-20260901-06']
    for prefix in prefixes:
        listing = subprocess.check_output(['git','ls-tree','-r','-z','--name-only',source,'--',prefix],cwd=R)
        paths += [p for p in listing.decode().split('\0') if p]
    paths += ['program/characterization/reports/'+n for n in
              ['source-verification.json','preflight.json','review-record.json','current-repeat-comparison.json']]
    values = {}
    for name in sorted(set(paths)):
        require(not any(v in name for v in ['RootFailedStart','SnapshotKeyCloseWitness','NativeNk']),
                'no held or unknown native/Root source in snapshot')
        mode = subprocess.check_output(['git','ls-tree',source,'--',name],cwd=R,text=True).split()[0]
        require(mode in ['100644','100755'], 'regular public Git input only')
        data = subprocess.check_output(['git','show',source+':'+name],cwd=R)
        require(len(data)<32*1024**2 and (R/name).read_bytes()==data, 'current fixed public input bytes')
        values['source/'+name] = data
    helper = I/'2564_haruka_common60_remote.py'
    require(subprocess.check_output(['git','show',source+':'+str(helper.relative_to(R))],cwd=R)==helper.read_bytes(),
            'remote tool must itself be reviewed and fixed in Git')
    values['helper.py'] = helper.read_bytes()
    static = TC/'static-gates-20261015'
    tools = { 'checkstyle-14.3.0-all.jar': static/'checkstyle-14.3.0-all.jar',
              'record-fix-v1/pmd-record-1298.jar':static/'record-fix-v1/pmd-record-1298.jar',
              'junit-platform-console-standalone-1.13.4.jar':TC/'junit-platform-console-standalone-1.13.4.jar',
              'org.jacoco.cli-0.8.15-nodeps.jar':TC/'org.jacoco.cli-0.8.15-nodeps.jar' }
    tools.update({'pmd-lib/'+p.name:p for p in (static/'pmd-bin-7.28.0/lib').glob('*.jar')})
    for name, path in tools.items():
        require(path.is_file() and not path.is_symlink(), 'regular public static tool only')
        values['static/'+name] = path.read_bytes()
    config = dict(sourceCommit=source, productionCoreMain='2ebbdf391873a5be6247ea59cb9addffb886c591',
                  run='PG30726-HARUKA-COMMON91-V3', expectedTests=91,
                  payloadHashes={n:hashlib.sha256(v).hexdigest() for n,v in values.items()},
                  originalBaselineHashes={str(p.relative_to(R)):sha(p) for p in
                    sorted((R/'program/characterization/baseline/current').rglob('*')) if p.is_file()},
                  qualitySkips=[], manualCoverageExclusions=[], oldExecCombined=False)
    require(len(config['originalBaselineHashes'])==27, 'fixed original baseline inventory')
    write(W/'payload-config.json', config)
    values['config.json'] = (json.dumps(config,ensure_ascii=False,indent=2)+'\n').encode()
    require(sum(map(len,values.values()))<256*1024**2, 'bounded public payload')
    archive = W/'source-payload.tar'
    with tarfile.open(archive,'x') as stream:
        for name, data in sorted(values.items()):
            item = tarfile.TarInfo(name); item.size=len(data); item.mode=0o600
            stream.addfile(item, io.BytesIO(data))
    return archive, config

def stage(source, quota):
    observed = fresh(quota)
    require(not W.exists(), 'new-only controller plan; existing run must be observed')
    W.mkdir(mode=0o700)
    write(W/'plan.json', dict(sourceCommit=source, run='PG30726-HARUKA-COMMON91-V3',
          atUTC=now(), quotaBefore=observed, remote=REMOTE, temp=TMP,
          globalUnknownProcessCwds=3, globalIdleClaim=False, actualRootDbVmNativeServiceActions=0))
    archive, config = source_payload(source)
    digest = sha(archive)
    bootstrap = '''from pathlib import Path
import datetime,fcntl,hashlib,json,os,stat,sys,tarfile,time
run=Path(REMOTE);tmp=Path(TMP);os.umask(0o077)
assert Path('/etc/hostname').read_text().strip()=='haruka' and os.getuid()==1000
parent=run.parent;assert parent.is_dir() and parent.resolve()==parent and parent.stat().st_uid==1000 and stat.S_IMODE(parent.stat().st_mode)==0o700
assert tmp.parent.resolve()==tmp.parent
run.mkdir(mode=0o700)
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
owner=dict(uid=os.getuid(),gid=os.getgid(),pid=os.getpid(),startTicks=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),bootId=boot,createdUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadlineMonotonic=time.monotonic()+1800,sourceCommit=SOURCE,newNamespaceOnly=True,runDevice=run.stat().st_dev,runInode=run.stat().st_ino)
with (run/'owner.json').open('x') as f:json.dump(owner,f)
with (run/'phase.lock').open('x+b') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 with (run/'source-payload.tar.uploading').open('xb') as f:
  total=0
  while data:=sys.stdin.buffer.read(1024*1024):
   total+=len(data);assert total<256*1024**2;f.write(data)
  f.flush();os.fsync(f.fileno())
 archive=run/'source-payload.tar.uploading';assert hashlib.sha256(archive.read_bytes()).hexdigest()==ARCHIVE
 archive.rename(run/'source-payload.tar');payload=run/'payload';payload.mkdir(mode=0o700)
 with tarfile.open(run/'source-payload.tar') as t:
  entries=t.getmembers();assert len({e.name for e in entries})==len(entries)
  for e in entries:
   p=Path(e.name);assert e.isfile() and not p.is_absolute() and '..' not in p.parts
  t.extractall(payload,filter='data')
 c=json.loads((payload/'config.json').read_text());assert c['sourceCommit']==SOURCE and c['expectedTests']==91
 assert {e.name for e in entries}==set(c['payloadHashes'])|{'config.json'}
 for n,h in c['payloadHashes'].items():assert hashlib.sha256((payload/n).read_bytes()).hexdigest()==h
 stage=dict(actualExit=0,sourceCommit=SOURCE,archiveSha256=ARCHIVE,configSha256=hashlib.sha256((payload/'config.json').read_bytes()).hexdigest(),owner=owner,expectedTests=91,oldJobActions=0,aruConnections=0,testsExecuted=0)
 with (run/'stage.json').open('x') as f:json.dump(stage,f)
 stage['stageReceiptSha256']=hashlib.sha256((run/'stage.json').read_bytes()).hexdigest()
print('PGPT_JSON_BEGIN');print(json.dumps(stage));print('PGPT_JSON_END')
'''
    prefix = 'REMOTE='+repr(REMOTE)+'\nTMP='+repr(TMP)+'\nSOURCE='+repr(source)+'\nARCHIVE='+repr(digest)+'\n'
    result = ssh('stage', prefix+bootstrap, input_file=archive)
    write(W/'stage-receipt.json', result)
    publish('PG30726-haruka-common91-stage-v3', result)
    print(json.dumps(dict(actualExit=0,phase='stage',source=source,archiveSha256=digest,newNamespace=True,testsExecuted=0)))

def publish(name, result):
    out = PUBLIC/name
    require(not out.exists(), 'new-only public phase receipt')
    out.mkdir()
    write(out/'manifest.json', result)

def main():
    os.umask(0o077)
    phase = sys.argv[1]
    if phase=='stage':
        stage(sys.argv[2],sys.argv[3]); return
    require(W.is_dir() and (W/'stage-local-terminal.json').is_file(), 'saved same stage required')
    if phase in ('prepare','run'):
        fresh(sys.argv[-1])
    stage_receipt = json.loads((W/'stage-receipt.json').read_text())
    config = json.loads((W/'payload-config.json').read_text())
    pre = 'from pathlib import Path\nimport hashlib,json,os\n'
    pre += 'r=Path('+repr(REMOTE)+')\n'
    pre += 'assert hashlib.sha256((r/"stage.json").read_bytes()).hexdigest()=='+repr(stage_receipt['stageReceiptSha256'])+'\n'
    pre += 'assert (r.stat().st_dev,r.stat().st_ino)=='+repr((stage_receipt['owner']['runDevice'],stage_receipt['owner']['runInode']))+'\n'
    pre += 'assert hashlib.sha256((r/"payload/helper.py").read_bytes()).hexdigest()=='+repr(config['payloadHashes']['helper.py'])+'\n'
    admission_data = None
    if phase=='run':
        admission = Path(sys.argv[2]).read_bytes()
        require(len(admission)<1024*1024, 'bounded source-specific admission')
        pre += 'import sys\na=sys.stdin.buffer.read(1048576)\n'
        pre += 'assert hashlib.sha256(a).hexdigest()=='+repr(hashlib.sha256(admission).hexdigest())+'\n'
        pre += 'with (r/"admission.json").open("xb") as f:f.write(a)\n'
        admission_data = admission
    require(phase in ['prepare','run','status','collect'], 'fixed phase only')
    code = pre+'import runpy,sys\nsys.argv=['+repr(REMOTE+'/payload/helper.py')+','+repr(phase)+']\nrunpy.run_path(sys.argv[0],run_name="__main__")\n'
    label = phase
    if phase=='status':
        label = 'status-'+str(1+len(list(W.glob('status-*-local-begin.json')))).zfill(3)
    result = ssh(label,code,input_bytes=admission_data,binary=phase=='collect')
    if phase=='collect':
        print(json.dumps(dict(actualExit=0,phase=phase,privateArchive=str(result),sha256=sha(result)))); return
    if phase=='status':
        out = PUBLIC/'PG30732-haruka-common91-same-run-status-v3'
        out.mkdir(exist_ok=True)
        write(out/(label+'.json'),result)
    else:
        publish({'prepare':'PG30728-haruka-common91-full-static-raw-v3',
                 'run':'PG30730-haruka-common91-unit-raw-terminal-v3'}[phase],result)
    print(json.dumps(dict(actualExit=0,phase=phase,source=json.loads((W/'plan.json').read_text())['sourceCommit'],
                         rawReceiptOnly=True,productPtAccepted=False)))

if __name__=='__main__':
    main()
