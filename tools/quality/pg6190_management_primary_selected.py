"""New60 ordinary cases after startup primary preservation; original59 remains historical."""
import subprocess
import pg6164_native_retention_selected as seed
import pg6182_unstarted_management_selected as profile
from pg5940_private_lock_compile import ROOT

OLD='769cf537696e135a63ef678ccf4bf19f5677be95'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementBindTest.java'


def inventory():
    cases,_=seed.inventory()
    cases['api'].update(('api.bootstrap.ApiManagementServerTest','api.bootstrap.ApiManagementStopTest',
        'api.bootstrap.ApiManagementBindTest','api.storage.ApiApplicationPreparationTest','api.storage.ApiPreparationOwnerTest'))
    cases['web'].update(('web.bootstrap.WebManagementServerTest','web.bootstrap.WebUnstartedManagementTest'))
    counts={seed.engine.PACKAGE+c:len(seed.source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((seed.engine.PACKAGE+c).replace('.','/')+'.java')))
        for m,names in cases.items() for c in names}
    if (sum(counts.values()),len(counts))!=(60,20):raise ValueError('exact60/20 source cases; eight compound inputs are not eight PT')
    return cases,counts


def runner_source():
    raw=seed.base_runner(60,20,target_count=14)
    before="os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before)!=1:raise ValueError('one pinned Node binding')
    return raw.replace(before,'os.pathsep+NODE_PATH,MAVEN_OPTS',1)


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed inputs first')
    if set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!={MAIN,TEST}:
        raise ValueError('only primary redaction Main and one new Test method')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('unchanged build/static/Current gates')
    # Reuse the exact previously reviewed target set/ordinary engine, not its old source or PASS.
    import inspect
    raw=inspect.getsource(profile.main)
    start=raw.index('    targets=');end=raw.index('\n    engine=',start)
    cases,counts=inventory()
    scope={**vars(seed.engine),'SLOT':'pg6190-management-primary-selected-v1','NODE_PATH':seed.node_environment(),
        'CASES':cases,'COUNTS':counts,'test_names':seed.source_test_names}
    exec(compile(raw[start:end].removeprefix('    ').replace('\n    ','\n'),'<unchanged14 targets>','exec'),scope)
    scope['TARGETS']=scope.pop('targets')
    exec(compile(runner_source(),'<own60 including compound startup failures>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
