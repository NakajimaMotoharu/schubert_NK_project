"""Necessary4209/653/1669 whole for one Web timing Main and six independent Test methods."""
import ast
import inspect
import json
import subprocess
import pg6828_api_management_result_whole as prior
import pg6188_native_ownership_whole as base
import pg6850_web_deadline_selected as selected
from pg6784_web_management_result_whole import require_four_counters
from pyflakes.api import check

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
LABEL='PG6862'
SLOT='pg6862-web-deadline-six-v1'
QSHA='69dba2782be8034e9efac8505b5019d466da0100bd1a3bc105f57760b61466fd'


def original_source():
    source=json.loads((W/selected.GREEN/'begin.safe.json').read_bytes())['source'];selected.green_guard(source);return source


def declared_inventory():
    raw=inspect.getsource(base.declared_inventory)
    if raw.count('(4023, 605)')!=1:raise ValueError('one independent full declaration binding')
    scope={**vars(base)};exec(compile(raw.replace('(4023, 605)','(4209, 653)',1),'<all4209 source declarations>','exec'),scope);return scope['declared_inventory']()


def server_source(head,digest):
    raw=prior.server_source(head,digest).replace('PG6828',LABEL).replace('pg6828','pg6862');tree=ast.parse(raw)
    if {n:sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==n for x in ast.walk(tree))for n in(4203,650)}!={4203:2,650:1}:raise ValueError('exact previous whole dimension constants')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            return ast.copy_location(ast.Constant({4203:4209,650:653}[node.value]),node)if type(node.value)is int and node.value in(4203,650)else node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(tree)))
    if check(raw,'<Web deadline4209 whole>'):raise ValueError('complete runner namespace')
    return raw


def driver_source(fresh):
    raw=prior.driver_source(fresh).replace(prior.SLOT,SLOT).replace('PG6828',LABEL).replace('pg6828','pg6862')
    before="'tests': 4203, 'suites': 650, 'mainClasses': 1669"
    if raw.count(before)!=1:raise ValueError('one4209/653/1669 tuple')
    raw=raw.replace(before,"'tests': 4209, 'suites': 653, 'mainClasses': 1669",1)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Necessary SS335/PG-D509 Web management finite lock/shared deadline and original Web IRQ table after genuine three old-source own-fixture timeouts. '
      'One Web Main and six new Test methods in three files since original4203, all old oracles/other Main/gates fixed. '
      'Original green42/15 and exact legacy-body expansion first. Fresh4209/653/1669 original XML, no old4203+6 PASS arithmetic. '
      'Same six format-beforePT/compile-null-Werror/static, finite owned tempDB/JMS/HTTP/child fixtures only. '
      'No actual Web/API business start, VM/Root/cohort/original DBBackup/key/permit/Unit/native operation. '
      'Original6864 and current quality/trace required; no global/F03/native/formal completion inference.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('selected Main/Test/gates remain fixed')
    qp=BASE/'PG6854-web-deadline-original-v1/manifest.json';pp=W/'pg6854-web-deadline-original-v1/manifest.safe.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze genuine green42 first')
    q,p=[json.loads(x.read_bytes())for x in(qp,pp)]
    if not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(42,15,1669)and sha(pp)==q['privateManifestSha256']):raise ValueError('original42/all8511669 exact qualification')
    if {x.relative_to(ROOT).as_posix():sha(x)for x in ROOT.glob('src/*/src/main/java/**/*.java')}!=p['allSourceHashes']:raise ValueError('all actual851 Main fixed')
    require_four_counters(p['allActualCounters']['web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class'])
    bp=BASE/'PG6860-web-deadline-structure-v1/manifest.json'
    if sha(bp)!='5a8021b2d78c2759a5a42a4783cf7d5447defcc4d1921941f6062a1ca62a80ef':raise ValueError('fixed source structure proof')
    proof=json.loads(bp.read_bytes())
    if not(proof['actualExit']==0 and proof['legacyBodyAndOutsideMethodEqual']and proof['sharedDeadlineForLockAndJoin']and proof['sourceSha256']==sha(ROOT/selected.MAIN)):raise ValueError('proof for current exact Main')
    selected.green_guard(source);declared_inventory()


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source,'prerequisites':prerequisites,'server_source':server_source,'driver_source':driver_source}
    exec(compile(inspect.getsource(base.main).replace('pg6188','pg6862'),'<necessary Web4209 whole>','exec'),scope);return scope


if __name__=='__main__':raise SystemExit(definitions()['main']())
