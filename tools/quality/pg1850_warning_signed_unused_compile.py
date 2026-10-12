"""Freeze closed placement ABI only after actual signed candidate and fresh current proof."""
import inspect
import json
import ast
from pathlib import PurePosixPath
import pg1642_completed_candidate_compile as engine
from pg1848_warning_signed_unused_sources import sources,TOOLS
from pg1844_warning_unit_full_six import CANDIDATE,OLD

TARGET=engine.W/TOOLS
ARCHIVE=engine.P/'pg1851-warning-release-v1.tar'


def validate_actual_graph(target,hashes):
    raw=(target/'pg1848_input_preflight.py').read_text()
    tree=ast.parse(raw)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'canonical','validate_graph'}or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='STANDARD'for t in n.targets)]
    if len(nodes)!=3:raise ValueError('three actual input graph declarations required')
    ns={'PurePosixPath':PurePosixPath,'re':__import__('re')}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual input graph declarations>','exec'),ns)
    ns['validate_graph'](hashes,{n:(target/n).read_text()for n in hashes if n.endswith('.py')},ARCHIVE.name,{ARCHIVE.name,'pg1846-manifest-v1.sig','bundle.safe.json'})


def compiler():
    raw=inspect.getsource(engine.main)
    for old,new in [('pg1638','__NEW_PREFIX__'),('pg1544','pg1638'),('__NEW_PREFIX__','pg1846'),('pg1641-completed-current-before-v2','pg1849-warning-completed-current-before-v1'),('pg1610-frozen-v1','pg1834-frozen-v1'),('pg1609-current-ordinary-owned-stop-tools-v1','pg1833-warning-owned-stop-tools-v1'),('Pg1609','Pg1833'),('pg1643-release-v1','pg1851-warning-release-v1'),('pg1642','pg1850'),('Pg1640','Pg1848'),('pg1640','pg1848')]:raw=raw.replace(old,new)
    marker="    generated['bundle.safe.json'] = bundle.decode()"
    if raw.count(marker)!=1:raise ValueError('one actual closure input injection required')
    raw=raw.replace(marker,"    generated['pg1848_input_preflight.py'] = 'BUNDLE_HASH=' + repr(hashlib.sha256(bundle).hexdigest()) + '\\n' + generated['pg1848_input_preflight.py']\n"+marker)
    raw=raw.replace("    data = json.loads((release / 'RELEASE-MANIFEST.json').read_bytes())","    ARCHIVE.chmod(0o400)\n    data = json.loads((release / 'RELEASE-MANIFEST.json').read_bytes())")
    marker="    names = ['Pg1848UnusedStage.java', 'Pg1848NativeArgumentTest.java', 'Pg1848StopLabelTest.java', 'Pg1848OriginalTupleTest.java']"
    if raw.count(marker)!=1:raise ValueError('one complete helper Java source boundary required')
    raw=raw.replace(marker,"    names = sorted(n for n in generated if n.endswith('.java'))")
    raw=raw.replace("('original', 'Pg1848OriginalTupleTest')]]","('original', 'Pg1848OriginalTupleTest'),('identity','Pg1848CurrentIdentityTest'),('input','Pg1848InputBoundaryTest')]]")
    # The frozen import graph/undefined names are checked after all literal input
    # hashes are injected, not by a fixture supplying missing globals at runtime.
    marker="    for name, raw in generated.items():"
    raw=raw.replace(marker,"    from pyflakes.api import check\n    for n, body in generated.items():\n        if n.endswith('.py') and check(body,'<actual closed helper '+n+'>'):raise ValueError('actual emitted dependency static gate refused')\n"+marker)
    raw=raw.replace("    for p in TARGET.iterdir():","    validate_actual_graph(TARGET,hashes)\n    for p in TARGET.iterdir():")
    compile(raw,'<current WARNING signed placement compiler>','exec');return raw


def main():
    before=json.loads((engine.W/'pg1849-warning-completed-current-before-v1/manifest.safe.json').read_bytes())
    if before['actualExit']!=0 or before['productionSource']!=OLD or before['allTenUnitsKernelEmpty']is not True or before['genuineCompletion']['managerFailureRetained']is not True:raise ValueError('fresh genuine failed-manager current proof required')
    digest=before['privateBeforeSha256']
    ns={**engine.__dict__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'TOOLS':TOOLS,'CURRENT':OLD,'PRODUCTION':CANDIDATE,'BEFORE':digest,'sources':lambda bom:sources(bom,digest),'validate_actual_graph':validate_actual_graph}
    exec(compile(compiler(),'<all actual freeze/compile input closure>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
