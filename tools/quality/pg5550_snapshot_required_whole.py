"""One required coherent snapshot-fix whole, exact3900/563/1664, no historical replay."""
import ast
import inspect
import json
import os
import shlex
import subprocess
from pyflakes.api import check
import pg5414_ownership_whole as previous
import pg5544_snapshot_scratch_public as selection
from lan_server import run

ROOT,W=previous.ROOT,previous.W
SOURCE=selection.SOURCE
LABEL='PG5550'
SLOT='pg5550-snapshot-six-v1'


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5414',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in{3896,562}:
                return ast.copy_location(ast.Constant({3896:3900,562:563}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<snapshot exact3900 full standalone>'):raise ValueError('all standalone full dependencies before output or transfer')
    compile(raw,'<new source3900 genuine whole only>','exec')
    return raw


def prerequisites():
    green,_=selection.load(selection.audit.RUN,'fb49c8579faff830f2df86f80286f9073392d436b0b986a537b3a0bbbf8e6a78')
    proof,_=selection.load(selection.audit.SLOT,'cc4b8e5ccd0b1f359b9acd1bb44e1d0cefad390cc5a48bc99b7c5219965fcbb1')
    if not(green['sourceSnapshot']==proof['sourceSnapshot']==SOURCE and green['greenSelectedQualified']and green['actualCases']==29 and green['targetFour100']and proof['actualExit']==0 and len(proof['fixtureFactories'])==8):raise ValueError('actual29 and independent all8/physical scratch first')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed operator before new whole')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('exact canonical a19 Main/Test inputs, never a mixed source')


def preflight():
    code=r'''
import hashlib,json,os,pathlib,shutil
base=pathlib.Path('/home/mini/schubert-nk-pgpt');jobs=[]
for path in pathlib.Path('/proc').iterdir():
    if not path.name.isdecimal():continue
    try:
        args=(path/'cmdline').read_bytes();comm=(path/'comm').read_text().strip();cwd=(path/'cwd').resolve()
        inside=str(cwd).startswith(str(base)+'/source-full-')
        whole=comm.startswith('python')and any(piece.startswith(b'/home/mini/schubert-nk-pgpt/tools/pg')and piece.endswith(b'-full.py')for piece in args.split(bytes([0])))
        if whole or(inside and(comm=='java'or comm.startswith('mvn')or comm.startswith('postgres'))):
            fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            jobs.append({'pid':int(path.name),'ticks':int(fields[19]),'argvSha256':hashlib.sha256(args).hexdigest(),'cwd':str(cwd),'comm':comm})
    except(FileNotFoundError,ProcessLookupError,PermissionError):pass
mem={row.split(':',1)[0]:row.split(':',1)[1].strip()for row in pathlib.Path('/proc/meminfo').read_text().splitlines()}
result={'host':os.uname().nodename,'boot':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'matchingActiveJobs':jobs,'freeBytes':shutil.disk_usage(base).free,'availableKiB':int(mem['MemAvailable'].split()[0]),'vmActions':0,'startsStops0':True}
print(json.dumps(result,sort_keys=True))
'''
    status,output=run('python3 -B -c '+shlex.quote(code),timeout=30)
    if status:raise ValueError('pinned-server read-only identity/job preflight failed')
    value=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    if value['matchingActiveJobs']:raise ValueError('existing whole/JVM/database job: preserve and inspect, no duplicate or kill')
    if value['freeBytes']<12*1024**3 or value['availableKiB']<4*1024**2:raise ValueError('required fresh whole headroom unavailable')
    return value


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=preflight()
    # Save the fresh host/job fact before invoking the ordinary new-only driver.
    path=W/'pg5550-preflight-v1.safe.json'
    os.umask(0o077)
    with path.open('x')as target:json.dump(fresh,target,sort_keys=True);target.flush();os.fsync(target.fileno())
    raw=inspect.getsource(previous.driver.main).replace('pg4420','pg5550').replace('shared-manager','snapshot')
    old="'tests': 3721, 'suites': 545, 'mainClasses': 1644"
    if raw.count(old)!=1:raise ValueError('one original whole planned inventory')
    raw=raw.replace(old,"'tests': 3900, 'suites': 563, 'mainClasses': 1664",1)
    raw=raw.replace('SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved',
        'BUG1453 shared snapshot scratch correction; genuine selected29/all8 physical audit; all old3896 plus exact4 newly specified methods; no old native imported')
    marker="'archiveSha256': digest, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),"
    if raw.count(marker)!=1:raise ValueError('one real pre-dispatch source metadata boundary')
    raw=raw.replace(marker,marker+"'operatorBranch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'serverPreflight':"+repr(fresh)+',',1)
    ns={**vars(previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(raw,'<one exact a19 whole3900 with fresh server owner>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
