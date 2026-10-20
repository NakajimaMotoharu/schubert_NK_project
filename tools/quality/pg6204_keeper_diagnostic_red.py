"""Purposeful own-child diagnostic regression red against unchanged current Production."""
import subprocess
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment

ROOT=engine.ROOT
OLD='4e3a75a5e43518904d6dcb45f47b9ecf90327257'
TESTS={'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/'+n+'.java'
       for n in ('OwnedRetentionProcess','ServiceResourceRetentionTest')}


def inventory():
    cases={m:set(v) for m,v in engine.CASES.items()}
    cases['bootstrap'].add('api.file.ServiceResourceRetentionTest')
    counts={engine.PACKAGE+c:len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+c).replace('.','/')+'.java')))
        for m,names in cases.items() for c in names}
    if (sum(counts.values()),len(counts))!=(15,8):raise ValueError('15 real JUnit/8, not child input count')
    return cases,counts


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean frozen red inputs first')
    if set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!=TESTS:
        raise ValueError('all Production unchanged from genuine4024; only two red fixture paths')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('all existing build/static/Current unchanged')
    cases,counts=inventory();raw=runner_source(15,8,target_count=1)
    before="os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before)!=1:raise ValueError('one existing Node environment binding')
    raw=raw.replace(before,'os.pathsep+NODE_PATH,MAVEN_OPTS',1)
    scope={**vars(engine),'SLOT':'pg6204-keeper-diagnostic-red-v1','NODE_PATH':node_environment(),
        'CASES':cases,'COUNTS':counts,'TARGETS':{'bootstrap':['api/file/ServiceProcessResources']},'test_names':source_test_names}
    exec(compile(raw,'<own finite diagnostic red>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
