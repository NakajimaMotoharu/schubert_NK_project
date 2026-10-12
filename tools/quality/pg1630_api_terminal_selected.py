"""PG-D412 new source/API thirteen affected PT and compile/static dependencies.

Four isolated module targets; no older-source exec union or native operation.
"""
import ast
import inspect
import pg1525_filesystem_selected as prior

PRODUCTION='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'


def server():
    tree=ast.parse(prior.SERVER.replace('PG1525','PG1630'))
    for n in tree.body:
        if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name):
            if n.targets[0].id=='EXPECTED':n.value=ast.parse("{'ApiProcessMainTest':4,'ApiProcessLifetimeTest':4,'ApiTerminalCaptureTest':3,'ApiCommittedFatalBindingTest':2}",mode='eval').body
            if n.targets[0].id=='MODULES':n.value=ast.parse("['protocol','storage','bootstrap','api']",mode='eval').body
    raw=ast.unparse(tree)
    marker="'-pl', 'src/schubert-nk-storage,src/schubert-nk-batch', '-am'"
    if raw.count(marker)!=1:raise ValueError('fixed selected reactor marker required')
    raw=raw.replace(marker,"'-pl', ','.join('src/schubert-nk-'+m for m in MODULES)")
    raw=raw.replace("c.attrib['name'].endswith('/LinuxFilesystemClassifier')", "c.attrib['name'] in ['dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture','dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture$Owner','dev/codex/schubert/nk/api/bootstrap/ApiProcessMain','dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime']")
    raw=raw.replace("'classifierCoverage': coverage", "'affectedCoverage': coverage")
    raw=raw.replace("'sourceSnapshot': SOURCE_HEAD", "'productionSource':PRODUCTION,'sourceSnapshot':SOURCE_HEAD")
    raw=raw.replace("'compileOnlyUnselectedModules': ['protocol', 'bootstrap']", "'compileOnlyUnselectedModules': ['protocol', 'storage', 'bootstrap']")
    raw='PRODUCTION='+repr(PRODUCTION)+'\n'+raw
    from pyflakes.api import check
    if check('SOURCE_HEAD=""\n'+raw,'<actual complete selected API thirteen>'):raise ValueError('generated static gate refused')
    compile(raw,'<new-source API thirteen>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('PG1525','PG1630').replace('pg1525','pg1630').replace("'expectedTests':101","'expectedTests':13").replace("'expectedSuites':7","'expectedSuites':4").replace('SSC269 production filesystem implementation and all delegated original/runtime IO selected suites','PG-D412 API terminal hold and committed-fatal binding, affected API thirteen plus compile/static only dependencies')
    ns={**prior.__dict__,'SERVER':server()}
    exec(compile(raw,'<new-only API thirteen dispatch>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
