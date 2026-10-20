"""One necessary current4023/605 ordinary regression after the grouped SS313..317 changes."""
import ast
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg6118_http_owner_whole as prior
import pg6060_expiry_current_whole as declarations
from pg6040_remaining33_whole import RUNTIME
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6184_unstarted_management_qualification import original_source

LABEL='PG6188'
SLOT='pg6188-native-ownership-six-v1'


def declared_inventory():
    raw=inspect.getsource(declarations.declared_inventory)
    if raw.count('(3979, 594)')!=1:raise ValueError('one independently inventoried source declaration count')
    scope=dict(vars(declarations))
    exec(compile(raw.replace('(3979, 594)','(4023, 605)',1),'<4023 declarations>','exec'),scope)
    return scope['declared_inventory']()


def server_source(head,digest):
    raw=prior.server_source(head,digest).replace('PG6118',LABEL).replace('pg6118','pg6188').replace(prior.SOURCE,head)
    tree=ast.parse(raw)
    if {n:sum(isinstance(x,ast.Constant) and type(x.value)is int and x.value==n for x in ast.walk(tree))
            for n in (3988,595,1667)}!={3988:2,595:1,1667:1}:
        raise ValueError('exact prior complete verdict/result dimensions')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in (3988,595):
                return ast.copy_location(ast.Constant({3988:4023,595:605}[node.value]),node)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Counts().visit(tree)))
    if check(raw,'<current ordinary4023>') or any(x in raw for x in
            ('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume')):
        raise ValueError('same finite self-owned fixtures; held actual operations excluded')
    compile(raw,'<fixed4023>','exec')
    return raw


def driver_source(fresh):
    raw=prior.driver_source(fresh).replace(prior.SLOT,SLOT).replace('PG6118',LABEL).replace('pg6118','pg6188')
    before="'tests': 3988, 'suites': 595, 'mainClasses': 1667"
    if raw.count(before)!=1:raise ValueError('one integrated complete source inventory')
    raw=raw.replace(before,"'tests': 4023, 'suites': 605, 'mainClasses': 1667",1)
    start=raw.index("'trigger': ");end=raw.index('}, sort_keys=True)',start)
    trigger=('Necessary grouped SS313..317 ownership regression, not a confirmation replay. '
        'S1 management stop;S2 JMS completion;S3 factory/native retention and parent/inner assembly;'
        'SSC317 unstarted management stop remains UNKNOWN. Original59 all-six qualification and '
        'current JVM/source ownership review first. Full source declarations4023/605/1667, including '
        'the unchanged historical repeated10 case. Allsix format before any PT; own tempDB/JMS/HTTP '
        'and finite child fixtures only. No VM/current/actualRoot/failedcohort/intent/permit action;'
        'no old-source/native/coverage success import. Native/CHR/global100/451/trace/formal separate.')
    raw=raw[:start]+"'trigger': "+repr(trigger)+raw[end:]
    compile(raw,'<new-only4023 driver>','exec')
    return raw


def prerequisites(source):
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed operator first')
    if subprocess.check_output(['git','diff',source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('canonical selected Main/Test/gates fixed')
    qp=BASE/'PG6184-unstarted-management-qualification-v1/manifest.json'
    op=BASE/'PG6186-native-ownership-order-v1/manifest.json'
    q,order=[json.loads(p.read_bytes()) for p in (qp,op)]
    if not (q['actualExit']==order['actualExit']==0 and q['source']==order['source']==source
            and (q['tests'],q['suites'],q['physicalMain'])==(59,20,1667)
            and order['qualificationSha256']==sha(qp) and order['ownershipReviewed']):
        raise ValueError('genuine original59/all Main/Jars and current ownership review before whole')
    private=W/'pg6184-unstarted-management-qualification-v1/manifest.safe.json'
    if sha(private)!=q['privateManifestSha256']:raise ValueError('original fixed all-Main map')
    proof=json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=proof['allSourceHashes']:
        raise ValueError('all851 Main fixed; no results from other source')
    declared_inventory()


def main():
    source=original_source()
    prerequisites(source);server_source(source,'0'*64)
    fresh=RUNTIME.preflight();os.umask(0o077)
    with (W/'pg6188-preflight-v1.safe.json').open('x') as f:
        json.dump(fresh,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    scope={**vars(RUNTIME.previous.driver),'SOURCE':source,'LABEL':LABEL,'server_source':server_source}
    exec(compile(driver_source(fresh),'<necessary4023 whole>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
