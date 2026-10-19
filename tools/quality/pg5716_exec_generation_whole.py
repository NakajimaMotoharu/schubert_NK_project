"""Necessary new3908 whole after SSC309 Main correction, never a replay of original3905."""
import ast
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg5588_scope_canary_whole as previous
from pg5714_exec_generation_proof import SOURCE,SLOT as PROOF

ROOT,W=previous.ROOT,previous.W
LABEL='PG5716'
SLOT='pg5716-exec-generation-six-v1'


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG5588',LABEL).replace(previous.SOURCE,SOURCE)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3905:return ast.copy_location(ast.Constant(3908),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    if check(raw,'<SSC309 fixed3908 complete>'):raise ValueError('full emitted static0 before dispatch')
    compile(raw,'<new3908 exact source>','exec')
    return raw


def prerequisites():
    raw=(W/PROOF/'manifest.safe.json').read_bytes();proof=json.loads(raw)
    green_path=W/'pg5708-exec-generation-green-v1/manifest.safe.json'
    green_raw=green_path.read_bytes();green=json.loads(green_raw)
    if not(proof['actualExit']==0 and proof['source']==SOURCE and proof['tests']==62 and proof['suites']==8 and proof['allPhysicalMain']==1664
      and proof['greenManifestSha256']==hashlib.sha256(green_raw).hexdigest()and green['greenSelectedQualified']and green['sourceSnapshot']==SOURCE
      and len(proof['physicalDifferences'])==2 and [v['debugOnly']for v in proof['physicalDifferences']]==[True,False]):raise ValueError('actual red/green62 and independent exact code1/debug1 first')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator required')
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw','program/characterization'],cwd=ROOT):raise ValueError('canonical source all production/test/config inputs fixed')


def driver_source(fresh):
    raw=previous.driver_source(fresh).replace('pg5588','pg5716').replace('scope-canary','exec-generation')
    old="'tests': 3905, 'suites': 563, 'mainClasses': 1664"
    if raw.count(old)!=1:raise ValueError('one exact planned physical inventory')
    raw=raw.replace(old,"'tests': 3908, 'suites': 563, 'mainClasses': 1664",1)
    raw=raw.replace('BUG1463 documented runtime-scope oracle correction; new selected73/14 private monitors/all11 physical qualified; old3904 failed retained, no old native or partial test success imported',
      'SSC309 generation-only transient exec state; selected62/purposeful red2/independent code1 debug1; failed0ea Root30 preserved; no old success imported')
    return raw


def main():
    prerequisites();server_source(SOURCE,'0'*64);fresh=previous.previous.previous.preflight()
    os.umask(0o077)
    with(W/'pg5716-preflight-v1.safe.json').open('x')as f:json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(previous.previous.previous.previous.driver),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<one necessary SSC309 fresh whole>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
