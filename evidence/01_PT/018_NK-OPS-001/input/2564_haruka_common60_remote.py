"""One isolated public-tool run on haruka. Never operates a service, DB, VM or existing job."""
from pathlib import Path
import datetime, fcntl, hashlib, json, os, shutil, signal, stat, subprocess, sys, tarfile, time
import xml.etree.ElementTree as ET

RUN = Path('/home/mini/schubert-nk-pgpt/runs/pg30726-common91-v3')
BASE_TMP = Path('/dev/shm/pgpt-pg30726-common91-v3')
TMP = BASE_TMP
JAVA = Path('/opt/schubert-nk-test-tools/jdk-25.0.4')
MVN = Path('/opt/schubert-nk-test-tools/maven/bin/mvn')
OLD_CACHE = Path('/home/mini/schubert-nk-pgpt/m2/repository')
SELECTED = dict(ArtifactComparatorTest=9, GateCliTest=12, GateContractTest=8,
                GateContractValidatorNegativeTest=17, TargetAdapterTest=3,
                CorrelatedLogEvidenceValidatorTest=11, BaselineNumericMetadataTest=5,
                GateMetricsCountTest=6, GateDefinitionDocumentsTest=11,
                GateEvidenceDocumentsTest=9)
MAIN = ('ArtifactComparator', 'GateCli', 'GateContractValidator', 'TargetAdapter',
        'CorrelatedLogEvidenceValidator')
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())

def proc(pid):
    text = Path('/proc', str(pid), 'stat').read_text()
    return dict(pid=pid, startTicks=int(text.rsplit(')', 1)[1].split()[19]),
                bootId=Path('/proc/sys/kernel/random/boot_id').read_text().strip())

def verify_inputs(config):
    require(Path('/etc/hostname').read_text().strip() == 'haruka' and os.getuid() == 1000,
            'fixed authorized host/mini only')
    require(not RUN.is_symlink() and RUN.stat().st_uid == os.getuid()
            and stat.S_IMODE(RUN.stat().st_mode) == 0o700, 'new own private run')
    stage = json.loads((RUN/'stage.json').read_text())
    require(stage['configSha256'] == sha(RUN/'payload/config.json')
            and stage['archiveSha256'] == sha(RUN/'source-payload.tar'), 'original stage bytes')
    require(config['sourceCommit'] == stage['sourceCommit'],
            'original staged source identity')
    for name, digest in config['payloadHashes'].items():
        path = RUN/'payload'/name
        require(not path.is_symlink() and path.is_file() and sha(path) == digest,
                'immutable exact payload input')
    require((RUN/'owner.json').is_file(), 'original namespace receipt required')
    owner = json.loads((RUN/'owner.json').read_text())
    require((RUN.stat().st_dev,RUN.stat().st_ino)==(owner['runDevice'],owner['runInode']),
            'same exclusive namespace inode')
    require(owner['bootId'] == proc(os.getpid())['bootId'],
            'no old boot/run authority reuse')

def capacity():
    owner = json.loads((RUN/'owner.json').read_text())
    require(time.monotonic() < owner['deadlineMonotonic'], 'original thirty-minute budget expired')
    disk = os.statvfs(RUN); low = os.statvfs(TMP)
    mem = int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines()
                   if l.startswith('MemAvailable:')))
    require(disk.f_bavail*disk.f_frsize >= 20*1024**3, 'real high disk20GiB')
    require(32*1024**2 < low.f_bavail*low.f_frsize < 20*1024**3, 'real low tmpfs capacity')
    require(mem >= 3*1024**2, 'current available RAM3GiB')
    return dict(highAvailableBytes=disk.f_bavail*disk.f_frsize,
                lowAvailableBytes=low.f_bavail*low.f_frsize, memoryAvailableKiB=mem)

def establish_phase_tmp(phase):
    require(phase in ('prepare','run'), 'fixed phase tmp only')
    directory = Path(str(BASE_TMP)+'-'+phase)
    require(directory.parent.resolve()==directory.parent, 'fixed real tmpfs parent')
    directory.mkdir(mode=0o700)
    info = directory.lstat()
    require(stat.S_ISDIR(info.st_mode) and info.st_uid==os.getuid()
            and stat.S_IMODE(info.st_mode)==0o700, 'new exclusively owned phase tmp')
    write(RUN/(phase+'-tmp.json'), dict(atUTC=now(), path=str(directory),
          device=info.st_dev, inode=info.st_ino, uid=info.st_uid, mode=oct(stat.S_IMODE(info.st_mode)),
          mountNamespace=os.readlink('/proc/self/ns/mnt'), owner=proc(os.getpid()),
          noCrossSshPersistenceRequired=True))
    return directory

def step(label, command, env, timeout):
    require(not (RUN/(label+'-begin.json')).exists(), 'existing phase must be observed, no replay')
    write(RUN/(label+'-begin.json'), dict(atUTC=now(), owner=proc(os.getpid()),
          command=command, environment=env, cwd=str(RUN/'payload/source'), timeoutSeconds=timeout))
    remaining = json.loads((RUN/'owner.json').read_text())['deadlineMonotonic']-time.monotonic()
    require(remaining > 30, 'original budget cannot start another process')
    timeout = min(timeout, remaining-30)
    with (RUN/(label+'.private.log')).open('xb') as log:
        child = subprocess.Popen(command, cwd=RUN/'payload/source', env=env,
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        owned = proc(child.pid)
        write(RUN/(label+'-process.json'), dict(owner=owned, pgid=child.pid, command=command))
        timed_out = False
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            require(proc(child.pid) == owned and os.getpgid(child.pid) == child.pid,
                    'only same owned process group may receive deadline signal')
            os.killpg(child.pid, signal.SIGTERM)
            try:
                code = child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                require(proc(child.pid) == owned, 'same owned generation before final deadline signal')
                os.killpg(child.pid, signal.SIGKILL)
                code = child.wait(timeout=15)
        log.flush(); os.fsync(log.fileno())
    result = dict(actualExit=code, timedOut=timed_out, atUTC=now(), process=owned,
                  logSha256=sha(RUN/(label+'.private.log')))
    # A missing process group is an actual owned-child postcondition, never global host idle.
    try:
        os.killpg(child.pid, 0)
        result['ownedProcessGroupAbsent'] = False
    except ProcessLookupError:
        result['ownedProcessGroupAbsent'] = True
    except PermissionError:
        result['ownedProcessGroupAbsent'] = None
    write(RUN/(label+'-exit.json'), result)
    require(result['ownedProcessGroupAbsent'] is True, 'owned child group postcondition unknown/nonempty')
    return result

def copy_public_cache():
    target = RUN/'repository'
    require(not target.exists() and OLD_CACHE.is_dir() and not OLD_CACHE.is_symlink(),
            'new private repository from existing public dependency cache only')
    target.mkdir(mode=0o700)
    count = 0
    total_bytes = 0
    deadline = json.loads((RUN/'owner.json').read_text())['deadlineMonotonic']
    for root, dirs, files in os.walk(OLD_CACHE, followlinks=False):
        rel = Path(root).relative_to(OLD_CACHE)
        # Exclude NK project artifacts before any stat/read/copy; only public vendor cache.
        if rel.as_posix() == 'dev/codex':
            dirs[:] = [x for x in dirs if x != 'schubert']
        for name in dirs:
            require(not (Path(root)/name).is_symlink(), 'cache symlink refused before traversal')
        dest = target/rel
        dest.mkdir(mode=0o700, parents=True, exist_ok=True)
        for name in files:
            source = Path(root)/name
            require(not source.is_symlink() and source.is_file(), 'public regular cache entry only')
            total_bytes += source.stat().st_size
            require(count<200000 and total_bytes<16*1024**3 and time.monotonic()<deadline-30,
                    'bounded public cache copy within original budget')
            shutil.copyfile(source, dest/name)
            require(sha(source) == sha(dest/name), 'copied public dependency bytes')
            count += 1
    return count

def commands(config):
    tools = RUN/'payload/static'
    source = RUN/'payload/source'
    module = source/'program/characterization'
    main_paths = [module/'src/main/java/dev/codex/schubert/characterization'/(n+'.java') for n in MAIN]
    test_paths = [module/'tests/java/dev/codex/schubert/characterization'/(n+'.java') for n in SELECTED]
    formats = [str(p.relative_to(module)) for p in main_paths+test_paths]
    base = [str(MVN), '-o', '--no-transfer-progress', '-s', str(RUN/'settings.xml'),
            '-gs', str(RUN/'settings.xml'), '-Dmaven.repo.local='+str(RUN/'repository'),
            '-pl', 'program/characterization', '-Dtest='+','.join(SELECTED),
            '-DspotlessFiles='+','.join(formats), '-Djacoco.sessionId=PG30726-COMMON91',
            '-Dspotbugs.xmlOutput=true']
    env = dict(PATH=str(JAVA/'bin')+':/usr/bin:/bin', JAVA_HOME=str(JAVA),
               MAVEN_USER_HOME=str(RUN/'maven-home'), MAVEN_SKIP_RC='true', LANG='C.UTF-8',
               MAVEN_OPTS='-Xmx2g -Djava.awt.headless=true',
               JAVA_TOOL_OPTIONS='-Djava.io.tmpdir='+str(TMP)
               +' -Xlog:class+init=info:file='+str(RUN/'class-init-%p.log'))
    listing = RUN/'static-sources.txt'
    if not listing.exists():
        listing.write_text(''.join(str(p)+'\n' for p in main_paths+test_paths))
    repo = RUN/'repository'
    deps = [tools/'junit-platform-console-standalone-1.13.4.jar',
            repo/'org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar']
    deps += [repo/'com/fasterxml/jackson/core'/n/'2.19.2'/(n+'-2.19.2.jar')
             for n in ('jackson-databind','jackson-core','jackson-annotations')]
    libs = [tools/'record-fix-v1/pmd-record-1298.jar', *sorted((tools/'pmd-lib').glob('*.jar'))]
    pmd = [str(JAVA/'bin/java'), '-cp', ':'.join(map(str, libs)),
           'net.sourceforge.pmd.cli.PmdCli', 'check', '--file-list', str(listing),
           '--rulesets', str(source/'tools/quality/static/pmd.xml'), '--use-version', 'java-25',
           '--aux-classpath', ':'.join(map(str, [module/'target/classes', module/'target/test-classes', *deps])),
           '--no-cache', '--format', 'xml', '--report-file', str(RUN/'pmd.xml')]
    cs = [str(JAVA/'bin/java'), '-jar', str(tools/'checkstyle-14.3.0-all.jar'),
          '-c', str(source/'tools/quality/static/checkstyle.xml'), '-f', 'xml',
          '-o', str(RUN/'checkstyle.xml'), '@'+str(listing)]
    return base, env, pmd, cs

def prepare(config):
    write(RUN/'prepare-claim.json', dict(atUTC=now(), source=config['sourceCommit'], owner=proc(os.getpid())))
    capacity()
    copied = copy_public_cache()
    (RUN/'maven-home').mkdir(mode=0o700)
    (RUN/'settings.xml').write_text('<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"/>\n')
    resources = capacity()
    base, env, pmd, cs = commands(config)
    versions = {}
    for label, command, expected in [
        ('java-version',[str(JAVA/'bin/java'),'-version'],'25.0.4'),
        ('maven-version',[str(MVN),'-version'],'3.9.12')]:
        receipt = step(label, command, env, 30)
        text = (RUN/(label+'.private.log')).read_text()
        require(receipt['actualExit']==0 and expected in text, 'exact declared tool version')
        versions[label] = text[:8192]
    compile_result = step('compile-static', base+['test-compile',
        'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:spotbugs'], env, 480)
    require(compile_result['actualExit'] == 0, 'normal compiler/format/enforcer/SpotBugs process failed; preserve terminal')
    pmd_result = step('pmd', pmd, env, 180)
    cs_result = step('checkstyle', cs, env, 180)
    root = ET.parse(RUN/'pmd.xml').getroot()
    raw = [dict(path=n.get('name'), **v.attrib, message=' '.join(''.join(v.itertext()).split()))
           for n in root if n.tag.rpartition('}')[2]=='file'
           for v in n if v.tag.rpartition('}')[2]=='violation']
    errors = [dict(x.attrib) for x in root.iter() if x.tag.rpartition('}')[2] in ('error','configerror')]
    sb = ET.parse(RUN/'payload/source/program/characterization/target/spotbugsXml.xml').getroot()
    result = dict(actualExit=0, atUTC=now(), sourceCommit=config['sourceCommit'], owner=proc(os.getpid()),
                  resources=resources, copiedPublicCacheFiles=copied, originalRepositoryModified=False,
                  os=dict(sysname=os.uname().sysname,release=os.uname().release,machine=os.uname().machine),
                  pythonVersion=sys.version, versions=versions,
                  originalProjectArtifactsCopied=False, sourceHashesVerified=True,
                  compileStatic=compile_result, pmd=pmd_result, checkstyle=cs_result,
                  rawFindings=raw, processingErrors=errors,
                  checkstyleErrors=len(ET.parse(RUN/'checkstyle.xml').findall('.//error')),
                  spotbugs={n:len(sb.findall('.//'+n)) for n in ('BugInstance','MissingClass','Error')},
                  testsExecuted=0, globalUnknownProcessesInspected=False, globalIdleAccepted=False,
                  actualDbVmRootNativeServiceActions=0)
    write(RUN/'prepare-result.json', result)
    return result

def run_tests(config):
    admission = json.loads((RUN/'admission.json').read_text())
    previous = json.loads((RUN/'prepare-result.json').read_text())
    require(admission['sourceCommit']==config['sourceCommit'] and admission['prepareSha256']==sha(RUN/'prepare-result.json')
            and admission['applicable']==admission['unclassified']==0, 'specific exact-source static admission')
    require(not previous['processingErrors'] and previous['checkstyleErrors']==0
            and all(v==0 for v in previous['spotbugs'].values()), 'static errors remain')
    capacity()
    base, env, _, _ = commands(config)
    terminal = step('unit-verify', base+['verify'], env, 480)
    verify_inputs(config)
    write(RUN/'unit-result.json', dict(**terminal, sourceCommit=config['sourceCommit'],
          selectedWholeClasses=SELECTED, expectedTests=91, coverageExclusions=[], qualitySkips=[],
          rawTerminalOnly=True, oldExecCombined=False, formalAcceptanceAdded=0))
    return json.loads((RUN/'unit-result.json').read_text())

def collect():
    require((RUN/'unit-result.json').is_file(), 'only true saved terminal artifacts may be collected')
    module = RUN/'payload/source/program/characterization/target'
    names = ['owner.json', 'stage.json', 'payload/config.json', 'prepare-result.json',
             'prepare-tmp.json', 'run-tmp.json', 'unit-verify-begin.json',
             'unit-verify-process.json', 'unit-verify-exit.json', 'unit-result.json',
             'admission.json', 'pmd.xml', 'checkstyle.xml']
    required_classes = {
        'ArtifactComparator.class', 'ArtifactComparator$ComparisonResult.class',
        'GateCli.class', 'GateCli$BaselineNumbers.class', 'GateCli$TreeStats.class',
        'GateContractValidator.class', 'GateContractValidator$ValidationResult.class',
        'TargetAdapter.class', 'TargetAdapter$Target.class', 'CorrelatedLogEvidenceValidator.class'}
    actual_classes = list((module/'classes').rglob('*.class'))
    require({p.name for p in actual_classes}==required_classes and len(actual_classes)==10,
            'exact five public Main/ten physical classes, no held class materialization')
    paths = [RUN/n for n in names]+actual_classes
    paths += [module/'jacoco.exec', module/'site/jacoco/jacoco.xml', module/'spotbugsXml.xml']
    paths += [module/'surefire-reports'/('TEST-dev.codex.schubert.characterization.'+n+'.xml') for n in SELECTED]
    paths += sorted(RUN.glob('class-init-*.log'))
    with tarfile.open(fileobj=sys.stdout.buffer, mode='w|') as archive:
        for path in paths:
            require(path.is_file() and not path.is_symlink() and path.stat().st_size<64*1024**2,
                    'bounded exact own-run artifact only')
            archive.add(path, arcname=str(path.relative_to(RUN)), recursive=False)

def main():
    global TMP
    os.umask(0o077)
    config = json.loads((RUN/'payload/config.json').read_text())
    verify_inputs(config)
    phase = sys.argv[1]
    if phase=='status':
        result = {n:json.loads((RUN/n).read_text()) for n in
                  ['owner.json','stage.json','prepare-tmp.json','run-tmp.json','prepare-claim.json','prepare-result.json',
                   'compile-static-process.json','compile-static-exit.json',
                   'unit-verify-process.json','unit-verify-exit.json','unit-result.json'] if (RUN/n).exists()}
        print('PGPT_JSON_BEGIN'); print(json.dumps(result)); print('PGPT_JSON_END')
        return
    with (RUN/'phase.lock').open('a+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        if phase in ('prepare','run'):
            require(not (RUN/('prepare-claim.json' if phase=='prepare' else 'unit-verify-begin.json')).exists(),
                    'no phase restart after any prior claim')
            TMP = establish_phase_tmp(phase)
        if phase=='prepare': result = prepare(config)
        elif phase=='run': result = run_tests(config)
        elif phase=='collect':
            collect()
            return
        else: raise ValueError('fixed phase required')
    print('PGPT_JSON_BEGIN'); print(json.dumps(result)); print('PGPT_JSON_END')

if __name__=='__main__':
    main()
