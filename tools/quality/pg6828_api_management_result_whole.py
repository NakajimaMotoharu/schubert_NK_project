"""Necessary4203/650/1669 whole after API result protocol and default-bind normal Test."""
import ast
import inspect
import json
import subprocess
import pg6802_web_correlation_whole as prior
import pg6188_native_ownership_whole as base
import pg6824_api_management_result_selected as selected
from pg6784_web_management_result_whole import require_four_counters
from pyflakes.api import check

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
LABEL='PG6828'
SLOT='pg6828-api-management-result-six-v1'
QSHA='8098c42d9af5490123b9a60fcfcb7a79c8f9f432862a34864078a4cb11e16f59'


def original_source():
    s=json.loads((W/selected.SLOT/'begin.safe.json').read_bytes())['source'];selected.guard(s);return s


def declared_inventory():
    raw=inspect.getsource(base.declared_inventory)
    if raw.count('(4023, 605)')!=1:raise ValueError('one current declaration binding')
    scope={**vars(base)};exec(compile(raw.replace('(4023, 605)','(4203, 650)',1),'<all4203 source declarations>','exec'),scope);return scope['declared_inventory']()


def server_source(head,digest):
    raw=prior.server_source(head,digest).replace('PG6802',LABEL).replace('pg6802','pg6828');tree=ast.parse(raw)
    if {n:sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==n for x in ast.walk(tree))for n in(4202,649)}!={4202:2,649:1}:raise ValueError('exact preceding whole dimensions')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            return ast.copy_location(ast.Constant({4202:4203,649:650}[node.value]),node)if type(node.value)is int and node.value in(4202,649)else node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(tree)))
    if check(raw,'<ordinary API4203 whole>'):raise ValueError('complete runner namespace')
    return raw


def driver_source(fresh):
    raw=prior.driver_source(fresh).replace(prior.SLOT,SLOT).replace('PG6802',LABEL).replace('pg6802','pg6828')
    before="'tests': 4202, 'suites': 649, 'mainClasses': 1669"
    if raw.count(before)!=1:raise ValueError('one exact4203/650/1669 tuple')
    raw=raw.replace(before,"'tests': 4203, 'suites': 650, 'mainClasses': 1669",1)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Necessary PG-D506 API management typed Runtime result and default bind normal '
      'literal Test. One API Main/one Test addition; all old4202 oracles and other Main/gates '
      'fixed. Fresh4203/650/1669 original XML, not old4202 plus1 arithmetic. Original30/11 '
      'and exact five-outcome/state/deadline/interrupt/exception-region source proof first. '
      'Allsix format-beforePT/compile/null/Werror/static, finite owned tempDB/JMS/HTTP/child '
      'fixtures only. No actual API business startup/admission, VM/Root/current/cohort/'
      'original/Backup/permit/key/native operation. Original6830 and same-source quality/'
      'trace required; global/F03/native/formal remain separate.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('selected Main/Test/gates fixed')
    qp=BASE/'PG6826-api-management-result-original-v1/manifest.json';pp=W/'pg6826-api-management-result-original-v1/manifest.safe.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze qualified original30 first')
    q,p=[json.loads(x.read_bytes())for x in(qp,pp)]
    if not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(30,11,1669)and sha(pp)==q['privateManifestSha256']):raise ValueError('genuine current30/all8511669 original qualification')
    if {x.relative_to(ROOT).as_posix():sha(x)for x in ROOT.glob('src/*/src/main/java/**/*.java')}!=p['allSourceHashes']:raise ValueError('all851 actual Main fixed')
    require_four_counters(p['allActualCounters']['api:dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.class'])
    bp=BASE/'PG6822-api-stop-result-equivalence-v1/manifest.json'
    if sha(bp)!='3fac857e43f801b0a1b2fe99f1c0e2da806ad35573c2827bd0f5d128a31dc42f':raise ValueError('frozen ordinary API source proof')
    proof=json.loads(bp.read_bytes())
    if not(proof['actualExit']==0 and proof['emptyPreparedBeforeBind']and proof['fixedUnknownOutcomes']==5 and proof['sourceSha256']==sha(ROOT/selected.MAIN)):raise ValueError('proof byte exact for current Main')
    selected.guard(source);declared_inventory()


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source,'prerequisites':prerequisites,'server_source':server_source,'driver_source':driver_source}
    exec(compile(inspect.getsource(base.main).replace('pg6188','pg6828'),'<necessary API4203 whole>','exec'),scope);return scope


def main():return definitions()['main']()


if __name__=='__main__':raise SystemExit(main())
