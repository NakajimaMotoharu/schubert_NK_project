"""Host-only new resource release; keys private, no deployment/lifecycle action."""
import inspect
import subprocess
import pg1638_api_signed_candidate as prior
import pg2512_strict_reference_signed_candidate as old_candidate
import pg2126_metadata_signed_candidate as contract
from pg2406_question_signed_candidate import verify_delta
from pg2428_question_signed_candidate import verify_container
from pg2652_operation_resource_container import verify as verify_added_web
from pg2650_operation_post_full_six import SOURCE, SCOPE, validate

W,P,T=prior.W,prior.P,prior.T
OLD=W/'pg2512-release-v1';NEXT=W/'pg2654-release-v1';FROZEN=W/'pg2654-frozen-six-v1';SIG=P/'pg2654-manifest-v1.sig'
OLD_SOURCE=old_candidate.SOURCE
OLD_BOM='2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395f'


def validate_gate(outer,source):
    raw=inspect.getsource(contract.validate_gate).replace("'tests':3631","'tests':3666").replace("'suites':540","'suites':541").replace("'semanticChangedClasses':3","'semanticChangedClasses':6")
    ns={**contract.__dict__,'CHANGED':old_candidate.PHYSICAL}
    exec(compile(raw,'<new resource qualified whole gate>','exec'),ns);return ns['validate_gate'](outer,source)


def qualify_source():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip();validate(head)
    selected='411abb597f15a221acd4c0da4a407a035fcbdd20'
    if subprocess.check_output(['git','diff','--name-only',selected,head,'--',*SCOPE],cwd=T):
        raise ValueError('whole accepted candidate input equality required')
    return b''


def receive(module):
    raw=inspect.getsource(prior.transfer.receive).replace('PG1532','PG2650').replace('pg1535','pg2654')
    ns={**prior.transfer.__dict__,'FROZEN':FROZEN}
    exec(compile(raw,'<fresh qualified six new resource Jar transfer>','exec'),ns);path=ns['receive'](module)
    old_path={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar'}.get(module)
    if old_path is None:
        import json
        rows=json.loads((OLD/'RELEASE-MANIFEST.json').read_bytes())['artifacts'];old_path=next(r['path']for r in rows if r['path'].endswith('/'+path.name))
    if module=='web':verify_added_web(OLD/old_path,path)
    else:verify_container(OLD/old_path,path,set())
    return path


def main_source():
    raw=inspect.getsource(prior.main)
    for a,b in [('pg1638','pg2654'),('PG1638','PG2654'),('PG1544','PG2512'),
      ('1683dd9f6de00e71d2317d9af3cd50400a37bf4e',SOURCE),
      ('pg1636-api-boundary-full-qualified-v1','pg2651-operation-post-full-qualified-v1'),
      ('from pg1636_api_boundary_full_qualification import server','from pg2651_operation_post_full_qualified import server'),
      ("{'VERSION', 'api/api.jar'} <= changed","{'VERSION', 'web/web.jar'} <= changed"),
      ("'tests': 3596, 'suites': 532","'tests': 3666, 'suites': 541"),
      ("'changedClasses': 3, 'addedClasses': 6","'changedClasses': 0, 'addedClasses': 0, 'changedResources':4, 'addedResources':1")]:
        if a not in raw:raise ValueError('one exact host signing boundary required')
        raw=raw.replace(a,b)
    marker="subprocess.check_output(['git', 'diff', '--name-only', '"+SOURCE+"', 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=T)"
    if raw.count(marker)!=1:raise ValueError('one source provenance boundary required')
    raw=raw.replace(marker,'qualify_source()');compile(raw,'<host-only new resource signing>','exec');return raw


def main():
    ns={**prior.__dict__,'__file__':__file__,'PRODUCTION':SOURCE,'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,
        'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,'SIG':SIG,'receive':receive,'validate_gate':validate_gate,'verify_delta':verify_delta,'qualify_source':qualify_source}
    exec(compile(main_source(),'<new unused host signed resource candidate>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
