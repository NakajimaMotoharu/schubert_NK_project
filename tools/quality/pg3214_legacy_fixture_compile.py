"""Compile isolated negative harness against exact3694/a9 jars, no Main recompile.

SS343/451/PT-OPS-LFACT001..007. Runtime archive contains public binaries only;
host-only secrets and private VM keys never leave this host.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
from pg1446_current_cold_stage import W
from lan_server import run, copy, HOST, pinned_key, ssh_options, authenticated
from pg3204_expiry_group_full_six import SOURCE, validate

ROOT = Path(__file__).resolve().parents[2]
OUT = W / 'pg3214-legacy-fixture-compile-v1'
REMOTE = '/home/mini/schubert-nk-pgpt/transfer/PG3214-legacy-fixture-v1'
SERVER = '/home/mini/schubert-nk-pgpt/runs/PG3214-legacy-fixture-v1'
JAVA = ROOT / 'tools/quality/vm/050_s1/NativeLegacyAdmissionNegative.java'

CODE = r'''
import datetime,hashlib,json,os,subprocess,tarfile,zipfile,xml.etree.ElementTree as E
from pathlib import Path
os.umask(0o077)
B=Path('/home/mini/schubert-nk-pgpt');out=Path(SERVER);transfer=Path(REMOTE);full=INPUT['full'];jdk=B/'tools/jdk-25.0.4/bin';repo=B/'m2/repository'
def require(v):
 if not v:raise ValueError('exact isolated helper compilation refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
require(not out.exists()and sha(transfer/'NativeLegacyAdmissionNegative.java')==INPUT['helperSha256'])
require(full['tests']==3694 and full['suites']==542 and full['mainClasses']==1643 and full['productionSource']==SOURCE and full['staticSixModules']==0)
out.mkdir(mode=0o700);classes=out/'classes';classes.mkdir(mode=0o700)
source=B/'source-full-PG3204';jars=[];entries={};main=resource=0
for m in ['protocol','storage','bootstrap','api','web','batch']:
 p=source/'src'/('schubert-nk-'+m)/'target'/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')
 require(sha(p)==full['jarHashes'][m]);jars.append(p);entries['jars/'+p.name]=p
 with zipfile.ZipFile(p)as z:
  main+=sum(n.endswith('.class')for n in z.namelist());resource+=sum(not n.endswith(('.class','/'))for n in z.namelist())
require(main==1643 and resource==79)
xml=source/'src/schubert-nk-batch/target/surefire-reports/TEST-dev.codex.schubert.nk.batch.file.MorningControlScopeTest.xml'
root=E.parse(xml).getroot();require(all(root.get(k)=='0'for k in ['failures','errors','skipped']))
paths=[p.get('value')for p in root.findall('properties/property')if p.get('name')=='java.class.path'];require(len(paths)==1)
libraries=[];seen=set()
for name in paths[0].split(':'):
 p=Path(name)
 if p.suffix=='.jar'and p.is_relative_to(repo)and not str(p.relative_to(repo)).startswith('dev/codex/schubert/')and p not in seen:
  require(p.is_file()and p.resolve().is_relative_to(repo.resolve()));seen.add(p);libraries.append(p)
for i,p in enumerate(libraries):entries['lib/'+str(i).zfill(3)+'-'+p.name]=p
agent=repo/'org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';require(agent.is_file());entries['agent.jar']=agent
before={name:sha(p)for name,p in entries.items()};cp=':'.join(str(p)for p in jars+libraries)
args=[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,'-d',str(classes),str(transfer/'NativeLegacyAdmissionNegative.java')]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(args,capture_output=True,timeout=90)
(out/'compile.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stdout and not r.stderr)
for p in classes.rglob('*.class'):
 require(p.name.startswith('NativeLegacyAdmissionNegative'));entries['classes/'+str(p.relative_to(classes))]=p
require(len(list(classes.rglob('*.class')))==3)
require(all(sha(entries[name])==value for name,value in before.items()))
files={name:{'sha256':sha(p),'bytes':p.stat().st_size}for name,p in entries.items()}
meta={'loadedMainSource':SOURCE,'sourceSnapshot':full['sourceSnapshot'],'hostTests':3694,'allMainSameBytes':1643,'allResourceMetaSameBytes':79,'helperSha256':INPUT['helperSha256'],'files':files,'runtimeClasspath':['classes']+[n for n in entries if n.startswith(('jars/','lib/'))],'normalDeploymentAuthority':False}
(out/'input.safe.json').write_text(json.dumps(meta,sort_keys=True))
archive=out/'runtime.private.tar'
with tarfile.open(archive,'x:')as tar:
 for name,p in entries.items():tar.add(p,arcname=name,recursive=False)
 tar.add(out/'input.safe.json',arcname='input.safe.json',recursive=False)
require(all(sha(entries[name])==value for name,value in before.items())and sha(transfer/'NativeLegacyAdmissionNegative.java')==INPUT['helperSha256'])
value={'actualExit':0,'loadedMainSource':SOURCE,'operatorSource':INPUT['operatorSource'],'sourceSnapshot':full['sourceSnapshot'],'helperSha256':INPUT['helperSha256'],'archiveSha256':sha(archive),'archiveBytes':archive.stat().st_size,'inputSha256':sha(out/'input.safe.json'),'mainClasses':1643,'resources':79,'helperClasses':3,'casesPlanned':7,'casesRun':0,'mainRecompiled':False,'guestOperations':0,'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'normalDeploymentAuthority':False,'formalAccepted':False}
(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
'''


def fetch_archive(destination, expected):
    source = SERVER + '/runtime.private.tar'
    if destination.exists() or destination.parent != OUT:
        raise ValueError('new-only exact private artifact destination required')
    key = pinned_key()
    with tempfile.TemporaryDirectory(prefix='pgpt-fixed-fixture-fetch-') as directory:
        known = Path(directory) / 'known_hosts'; known.write_text(key + '\n'); known.chmod(0o600)
        remote_shell = shlex.join(['ssh', *ssh_options(known)])
        code, output = authenticated(['rsync', '-a', '--partial', '--secluded-args', '-e', remote_shell, f'mini@{HOST}:{source}', str(destination)], known, 120)
    if code or hashlib.sha256(destination.read_bytes()).hexdigest() != expected:
        raise ValueError('exact fixture runtime transfer hash refused; preserve partial')
    return output


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed helper source required')
    proof = json.loads((W / 'pg3206-expiry-group-full-qualified-v1/manifest.safe.json').read_bytes())
    full = proof['result']
    if proof['actualExit'] != 0:
        raise ValueError('actual3694 required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'diff', full['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization']):
        raise ValueError('exact unchanged qualified Main/Test bytes required')
    data = {'full': full, 'helperSha256': hashlib.sha256(JAVA.read_bytes()).hexdigest(), 'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
    OUT.mkdir(mode=0o700)
    code, status = run('python3 - <<\'PREP\'\nfrom pathlib import Path\np=Path(' + repr(REMOTE) + ');s=Path(' + repr(SERVER) + ');assert not p.exists()and not s.exists();p.mkdir(mode=0o700)\nPREP', timeout=20)
    if code:
        raise ValueError('new-only helper transfer refused')
    code, status = copy(str(JAVA), REMOTE + '/', timeout=30)
    if code:
        raise ValueError('helper source transfer refused')
    raw = 'INPUT=' + repr(data) + '\nSOURCE=' + repr(SOURCE) + '\nSERVER=' + repr(SERVER) + '\nREMOTE=' + repr(REMOTE) + '\n' + CODE
    from pyflakes.api import check
    if check(raw, '<whole negative helper and exact3694 runtime compiler>'):
        raise ValueError('complete runtime compiler namespace required')
    (OUT / 'server.private.py').write_text(raw)
    code, status = run("python3 -B - <<'COMPILE'\n" + raw + '\nCOMPILE', timeout=120)
    (OUT / 'server.private.log').write_text(status)
    if code:
        (OUT / 'failed.safe.json').write_text(json.dumps({'actualExit': code, 'helperSha256': data['helperSha256'], 'casesRun': 0, 'guestOperations': 0}))
        raise ValueError('helper compile failed; no guest action')
    value = json.loads(next(line for line in status.splitlines() if line.startswith('{')))
    value['archiveFetchLogSha256'] = hashlib.sha256(fetch_archive(OUT / 'runtime.private.tar', value['archiveSha256']).encode()).hexdigest()
    with (OUT / 'manifest.safe.json').open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())
    print(json.dumps(value, sort_keys=True))
    return value['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
