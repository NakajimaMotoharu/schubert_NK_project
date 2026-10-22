"""One combined necessary4202/649/1669 whole after Web correction and five pure boundary tests."""
import ast
import inspect
import json
import subprocess
import pg6784_web_management_result_whole as prior
import pg6806_correlation_positive_selected as selected
from pyflakes.api import check

ROOT,W,BASE,sha=prior.ROOT,prior.W,prior.BASE,prior.sha
LABEL='PG6802'
SLOT='pg6802-web-correlation-six-v1'
QSHA=None


def original_source():
    s=json.loads((W/selected.SLOT/'begin.safe.json').read_bytes())['source'];selected.guard(s);return s


def declared_inventory():
    raw=inspect.getsource(prior.prior.base.declared_inventory)
    raw=raw.replace('(4023, 605)','(4202, 649)')
    if raw.count('(4202, 649)')!=1:raise ValueError('one exact current declaration tuple')
    scope={**vars(prior.prior.base)};exec(compile(raw,'<all4202 source declarations>','exec'),scope);return scope['declared_inventory']()


def server_source(head,digest):
    raw=prior.server_source(head,digest).replace('PG6784',LABEL).replace('pg6784','pg6802');tree=ast.parse(raw)
    if {n:sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==n for x in ast.walk(tree))for n in(4197,646)}!={4197:2,646:1}:raise ValueError('exact preceding verdict dimensions')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            return ast.copy_location(ast.Constant({4197:4202,646:649}[node.value]),node)if type(node.value)is int and node.value in(4197,646)else node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(tree)))
    if check(raw,'<combined4202 ordinary whole>'):raise ValueError('complete runner namespace')
    return raw


def driver_source(fresh):
    raw=prior.driver_source(fresh).replace(prior.SLOT,SLOT).replace('PG6784',LABEL).replace('pg6784','pg6802')
    before="'tests': 4197, 'suites': 646, 'mainClasses': 1669"
    if raw.count(before)!=1:raise ValueError('one exact declared4202/649/1669 tuple')
    raw=raw.replace(before,"'tests': 4202, 'suites': 649, 'mainClasses': 1669",1)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Necessary combined PG-D504 early cleanup correction and PG-D505 independent five '
      'public in-memory correlation boundary tests. One Web Main/three added Test files; all '
      'old4197 oracles and every other Main/quality gate fixed. Fresh4202/649/1669 XML, not '
      'old4197 plus5 arithmetic. Qualified original48/16 and exact pre-bind/state/exception '
      'source proof first. Allsix format-beforePT/compile/null/Werror/static, existing finite '
      'owned tempDB/JMS/HTTP/child fixtures only. No Root/VM/current/failedcohort/recovery/'
      'original/Backup/intent/permit/key/native action or old-native import. Original6804 '
      'and same-source SQL/static/JVM/trace required, global/F03/formal remain separate.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('selected Main/Test/gates fixed')
    qp=BASE/'PG6808-web-correlation-original-v2/manifest.json';pp=W/'pg6808-web-correlation-original-v2/manifest.safe.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze qualified original48 first')
    q,p=[json.loads(x.read_bytes())for x in(qp,pp)]
    if not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(48,16,1669)and sha(pp)==q['privateManifestSha256']):raise ValueError('genuine current48/8511669 original qualification')
    if {x.relative_to(ROOT).as_posix():sha(x)for x in ROOT.glob('src/*/src/main/java/**/*.java')}!=p['allSourceHashes']:raise ValueError('all851 actual Main exact')
    if set(q['targetCounters'])!=selected.MEASURED_TARGETS:raise ValueError('all four actual targets present')
    for c in q['targetCounters'].values():prior.require_four_counters(c)
    bp=BASE/'PG6796-web-early-cleanup-proof-v1/manifest.json'
    if sha(bp)!='ed57a92075e2a92387a0f550017494b3faa8f8cc5363874e23524b81e8478229':raise ValueError('frozen pre-acquisition source proof')
    proof=json.loads(bp.read_bytes())
    if not(proof['actualExit']==0 and proof['emptyPreparedBeforeBind']and proof['sourceSha256']==sha(ROOT/selected.MAIN)):raise ValueError('proof byte exact for current Main, not old-source result transfer')
    selected.guard(source);declared_inventory()


def definitions():
    base=prior.prior.base
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source,'prerequisites':prerequisites,'server_source':server_source,'driver_source':driver_source}
    exec(compile(inspect.getsource(base.main).replace('pg6188','pg6802'),'<necessary combined4202 whole>','exec'),scope);return scope


def main():return definitions()['main']()


if __name__=='__main__':raise SystemExit(main())
