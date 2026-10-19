"""Necessary new3905 after documented runtime-oracle repair; original3904 failure retained."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg5572_monitor_required_whole as previous

ROOT,W=previous.ROOT,previous.W
SOURCE='0ea400109d79e47327d9fff105ff763f9310a31f'
LABEL='PG5588'
SLOT='pg5588-scope-canary-six-v1'


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5572',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3904:return ast.copy_location(ast.Constant(3905),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<corrected runtime scope3905 complete>'):raise ValueError('all standalone names before output')
    compile(raw,'<one new3905 whole>','exec')
    return raw


def prerequisites():
    paths=[(W/'pg5566-private-monitor-green-v3/manifest.safe.json','9eef40acd5388ebf53737907bb5d664cf60a38430894de07a4a56df31896ca73'),
        (W/'pg5568-monitor-bytecode-v3/manifest.safe.json','8e852219d9ada714da01b66604238ecf21025bfae14ce76b0d33a21bf87f0d32'),
        (W/previous.SLOT/'manifest.safe.json','666fbade1b0c8ccf48a7a5a356add7a06b3f81c067a699d4a04995351d9f44e6')]
    values=[]
    for path,digest in paths:
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('immutable original pass/proof/failure record')
        values.append(json.loads(raw))
    green,proof,failed=values
    if not(green['sourceSnapshot']==proof['sourceSnapshot']==SOURCE and green['actualExit']==proof['actualExit']==0
        and green['greenSelectedQualified']and green['scopeIncludesRuntimeCanary']and green['actualCases']==73 and green['suites']==9
        and proof['actualSelectedCases']==73 and proof['allPhysicalMain']==1664 and sum(map(len,proof['privateMonitorMethods'].values()))==14
        and len(proof['allPhysicalDifferenceClassifications'])==11 and failed['actualExit']==1 and failed['source']==previous.SOURCE):raise ValueError('new source73/14/11 qualified and old3904 actual1 retained')
    change=subprocess.check_output(['git','diff','--name-only',previous.SOURCE,SOURCE,'--','src'],cwd=ROOT,text=True).splitlines()
    if change!=['src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/bootstrap/BatchRuntimeDependencyTest.java']:raise ValueError('only documented scope oracle changed since2fc, not production Main')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator required')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('canonical0ea all inputs fixed')


def driver_source(fresh):
    raw=inspect.getsource(previous.previous.previous.driver.main).replace('pg4420','pg5588').replace('shared-manager','scope-canary')
    marker="'tests': 3721, 'suites': 545, 'mainClasses': 1644"
    if raw.count(marker)!=1:raise ValueError('one actual planned whole inventory')
    raw=raw.replace(marker,"'tests': 3905, 'suites': 563, 'mainClasses': 1664",1)
    raw=raw.replace('SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved',
        'BUG1463 documented runtime-scope oracle correction; new selected73/14 private monitors/all11 physical qualified; old3904 failed retained, no old native or partial test success imported')
    marker="'archiveSha256': digest, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),"
    if raw.count(marker)!=1:raise ValueError('one pre-dispatch original identity boundary')
    return raw.replace(marker,marker+"'operatorBranch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'serverPreflight':"+repr(fresh)+',',1)


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=previous.previous.preflight()
    os.umask(0o077)
    with(W/'pg5588-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(previous.previous.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<new3905 after source repair only>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
