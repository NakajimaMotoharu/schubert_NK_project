"""One necessary same-source3939 host regression after three JMS exception guards."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5754_private_contract_whole as previous

ROOT,W=previous.ROOT,previous.W
SOURCE='2bbb85a297d7f7bd1b0c243d343e0da509faf99a'
LABEL='PG5780';SLOT='pg5780-jms-primary-six-v1'
RUNTIME=previous.previous.previous.previous.previous


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5754',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3932,581):return ast.copy_location(ast.Constant({3932:3939,581:583}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<same-source3939 original runner>'):raise ValueError('complete standalone static0 first')
    if any(v in raw for v in('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume')):raise ValueError('ordinary host fixture tests only, no held operations')
    compile(raw,'<one necessary3939>','exec');return raw


def driver_source(fresh):
    raw=previous.driver_source(fresh).replace('pg5754','pg5780').replace('private-contract','jms-primary')
    before="'tests': 3932, 'suites': 581, 'mainClasses': 1664"
    if raw.count(before)!=1:raise ValueError('one complete physical inventory')
    raw=raw.replace(before,"'tests': 3939, 'suites': 583, 'mainClasses': 1664",1)
    before='Assembled64 private field fixes, equivalent nullable version guard and two JMS constructor null guards. New24 finite cases/18 suites, original3908 test bodies and resources unchanged. Old VM/failed cohort held; old3908/native success not imported.'
    after='BUG1485 three same-identity exception guards in two Main classes. Seven new finite proxy cases/two suites, all original3932 cases/resources/POM unchanged. Separate API/Web purposeful reds retained; selected14/static/current-byte proof complete. Guest/failed cohort held; no old PT/native success imported.'
    if raw.count(before)!=1:raise ValueError('one reviewed new regression trigger')
    return raw.replace(before,after,1)


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('fixed canonical Main/Test/config only')
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
    for name,digest in(('PG5778-jms-primary14/manifest.json','9be091b5b0293ce1c04998890decbe36a09912b875d980deea1ab257708ba5aa'),('PG5776-jms-primary-static-v1/manifest.json','aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f')):
        p=base/name;raw=p.read_bytes();v=json.loads(raw)
        if hashlib.sha256(raw).hexdigest()!=digest or v['source']!=SOURCE or v['actualExit']!=0:raise ValueError('actual current14/static/byte proof required')
    names=subprocess.check_output(['git','diff','--name-status',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines()
    tests=[r for r in names if '/src/test/'in r]
    if len(tests)!=2 or any(not r.startswith('A\t')or not r.endswith('Test.java')for r in tests):raise ValueError('only seven finite cases in two additional Test files')
    if subprocess.check_output(['git','diff',previous.SOURCE,SOURCE,'--','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('original build/oracle harness unchanged')


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=RUNTIME.preflight()
    os.umask(0o077)
    with(W/'pg5780-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(RUNTIME.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<one necessary JMS-primary3939>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
