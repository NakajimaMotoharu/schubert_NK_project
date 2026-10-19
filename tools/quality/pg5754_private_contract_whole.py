"""One necessary coherent3932 host regression after assembled private/value/null PG; no VM actions."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5716_exec_generation_whole as previous

ROOT,W=previous.ROOT,previous.W
SOURCE='9463db1ac23437043facf95b87f64b9fc7e758bd'
LABEL='PG5754'
SLOT='pg5754-private-contract-six-v1'


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5716',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3908,563):return ast.copy_location(ast.Constant({3908:3932,563:581}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<one required coherent3932 standalone>'):raise ValueError('standalone static names before dispatch')
    if any(s in raw for s in('qemu-system','systemctl','virsh','sudo ','/opt/schubert-nk/current','--resume','--recover')):raise ValueError('ordinary host Maven only, never held runtime operations')
    compile(raw,'<coherent3932 no VM>','exec')
    return raw


def driver_source(fresh):
    raw=previous.driver_source(fresh).replace('pg5716','pg5754').replace('exec-generation','private-contract')
    before="'tests': 3908, 'suites': 563, 'mainClasses': 1664"
    if raw.count(before)!=1:raise ValueError('one exact planned full inventory')
    raw=raw.replace(before,"'tests': 3932, 'suites': 581, 'mainClasses': 1664",1)
    raw=raw.replace('SSC309 generation-only transient exec state; selected62/purposeful red2/independent code1 debug1; failed0ea Root30 preserved; no old success imported',
      'Assembled64 private field fixes, equivalent nullable version guard and two JMS constructor null guards. New24 finite cases/18 suites, original3908 test bodies and resources unchanged. Old VM/failed cohort held; old3908/native success not imported.')
    compile(raw,'<new-only coherent3932 driver>','exec')
    return raw


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean operator first')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('fixed canonical Main/Test/resources')
    proofs=[('PG5752-exception17/manifest.json','051b1cf06652ffc2eab86114068e9e19a86b59c94aece838ff4cbb1412d4cce9'),('PG5750-exception-static-v1/manifest.json','70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9')]
    for rel,digest in proofs:
        p=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/rel
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('original selected and independent static proof')
        v=json.loads(p.read_bytes())
        if v['source']!=SOURCE or v['actualExit']!=0:raise ValueError('actual same-source prerequisite0')
    names=subprocess.check_output(['git','diff','--name-status','6db56fe',SOURCE,'--','src'],cwd=ROOT,text=True).splitlines()
    tests=[row for row in names if '/src/test/'in row]
    if len(tests)!=18 or any(not row.startswith('A\t')or not row.endswith('Test.java')for row in tests):raise ValueError('only reviewed18 finite test files added; original tests/resources unchanged')
    if subprocess.check_output(['git','diff','6db56fe',SOURCE,'--','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('original host harness/archive/characterization contracts unchanged')


def main():
    prerequisites();server_source(SOURCE,'0'*64)
    # The inherited pinned-host preflight reads only dedicated host job identity/headroom,
    # never the guest/Units/DB contents, and refuses any matching active full test job.
    fresh=previous.previous.previous.previous.preflight()
    os.umask(0o077)
    with(W/'pg5754-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(previous.previous.previous.previous.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<one necessary private contract whole3932>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
