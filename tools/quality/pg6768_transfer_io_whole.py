"""Required4197/646/1669 whole after one Transfer Main and two explicit nested IO types."""
import ast
import inspect
import json
import subprocess
from pyflakes.api import check
import pg6188_native_ownership_whole as base
import pg6760_transfer_io_selected as selected

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
OLD=selected.OLD
LABEL='PG6768'
SLOT='pg6768-transfer-io-six-v1'
QSHA='ca1b4171ac208630189b42c6aa54f4d89b7306e29d73433c8ed55b202ba0535d'


def original_source():
    source=json.loads((W/selected.SLOT/'begin.safe.json').read_bytes())['source'];selected.guard(source);return source


def definitions():
    scope={**vars(base),'LABEL':LABEL,'SLOT':SLOT,'original_source':original_source,'prerequisites':prerequisites}
    for name in ('declared_inventory','server_source','driver_source','main'):
        raw=inspect.getsource(getattr(base,name))
        for before,after in (('4023','4197'),('605','646'),('pg6188','pg6768')):raw=raw.replace(before,after)
        exec(compile(raw,'<Transfer4197 '+name+'>','exec'),scope)
    return scope


def declared_inventory():return definitions()['declared_inventory']()


def server_source(head,digest):
    raw=definitions()['server_source'](head,digest);tree=ast.parse(raw)
    if sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==1667 for x in ast.walk(tree))!=1:
        raise ValueError('one exact prior complete physical class verdict')
    class MainCount(ast.NodeTransformer):
        def visit_Constant(self,node):
            return ast.copy_location(ast.Constant(1669),node)if type(node.value)is int and node.value==1667 else node
    raw=ast.unparse(ast.fix_missing_locations(MainCount().visit(tree)))
    if check(raw,'<Transfer4197 bounded whole>'):raise ValueError('complete runner namespace')
    return raw


def driver_source(fresh):
    raw=definitions()['driver_source'](fresh)
    before="'tests': 4197, 'suites': 646, 'mainClasses': 1667"
    if raw.count(before)!=1:raise ValueError('one exact4197/646/1669 declared dimension')
    raw=raw.replace(before,"'tests': 4197, 'suites': 646, 'mainClasses': 1669",1)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Necessary PG-D503 Transfer reader seam and proven admission-invariant factoring. '
      'One Main/one new independent eight-Test file, all prior oracles fixed. Exact two nested '
      'read-only IO types1667-to1669; all851source and every unchanged old class accounted for. '
      'Original27/10 current qualification and bytecode applicability first. Full4197/646 '
      'fresh XML,not old4189 plus8 PASS arithmetic. Allsix format-beforePT/compile/null/static '
      'and existing finite own tempDB/JMS/HTTP/child fixtures only. No VM/current/Root/cohort/'
      'original/Backup/intent/permit/key/native qualification operation or old-success import. '
      'Independent original6770, actual counters/static/trace required; global/F03/formal separate.')
    return raw[:start]+"'trigger': "+repr(trigger)+raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('selected Main/Test/gates fixed')
    qp=BASE/'PG6766-transfer-io-original-v2/manifest.json';pp=W/'pg6766-transfer-io-original-v2/manifest.safe.json'
    if QSHA is None or sha(qp)!=QSHA:raise ValueError('freeze genuine current27/10 original first')
    q=json.loads(qp.read_bytes());p=json.loads(pp.read_bytes())
    if not(q['source']==source and q['actualExit']==0 and(q['tests'],q['suites'],q['physicalMain'])==(27,10,1669)
      and sha(pp)==q['privateManifestSha256'] and set(q['addedPhysical'])==selected.ADDED):raise ValueError('genuine all8511669 with exact two declared additions')
    if {x.relative_to(ROOT).as_posix():sha(x)for x in ROOT.glob('src/*/src/main/java/**/*.java')}!=p['allSourceHashes']:raise ValueError('all851 Main byte fixed')
    counter=p['allActualCounters']['batch:dev/codex/schubert/nk/batch/file/TransferCleanup.class']
    if any(counter[k]['missed']!=0 for k in ('LINE','METHOD','CLASS','BRANCH')):raise ValueError('all actual outer Transfer counters before integrated run')
    bp=BASE/'PG6767-transfer-io-bytecode-v1/manifest.json'
    if sha(bp)!='9c5098465d94835588016947ef95d2acf05cb71258d520f6fa0e558f526e99e7':raise ValueError('frozen original IO bytecode applicability')
    b=json.loads(bp.read_bytes())
    if not(b['actualExit']==0 and b['source']==source and b['originalQualificationSha256']==QSHA and set(b['rows'])==selected.ADDED
      and all(not x['conditionalInstructions']and not x['branchCounterSynthesized']for x in b['rows'].values())):raise ValueError('same original concrete/declaration type proof, never missing counter as100')
    selected.guard(source);declared_inventory()


def main():
    scope=definitions();scope['main'].__globals__.update(driver_source=driver_source,server_source=server_source)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
