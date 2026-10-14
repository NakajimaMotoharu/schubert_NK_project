"""Host-only new JDBC Main candidate signing after fresh whole; no VM/deployment action."""
import inspect
import pg1638_api_signed_candidate as prior
import pg2512_strict_reference_signed_candidate as historical
import pg2126_metadata_signed_candidate as contract
from pg2428_question_signed_candidate import verify_container
from pg2798_jdbc_null_fixed_full_six import SOURCE, validate

W,P,T=prior.W,prior.P,prior.T
OLD=W/'pg2654-release-v1';NEXT=W/'pg2802-release-v1';FROZEN=W/'pg2802-frozen-six-v1';SIG=P/'pg2802-manifest-v1.sig'
OLD_SOURCE='04207efc3ad78bca75942153a90c70985064c988'
OLD_BOM='552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37'
DELTA={'batch:dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.class',
       'batch:dev/codex/schubert/nk/batch/repository/MorningDatabaseSession$Session.class',
       'batch:dev/codex/schubert/nk/batch/repository/MorningDatabaseSession$Rows.class'}
PHYSICAL=historical.PHYSICAL|DELTA


def validate_gate(outer,source):
    raw=inspect.getsource(contract.validate_gate).replace("'tests':3631","'tests':3680").replace(
        "'suites':540","'suites':542").replace("'semanticChangedClasses':3","'semanticChangedClasses':None")
    ns={**contract.__dict__,'CHANGED':PHYSICAL}
    exec(compile(raw,'<new JDBC Main full gate>','exec'),ns);return ns['validate_gate'](outer,source)


def verify_delta(before,after):
    raw=inspect.getsource(contract.verify_delta)
    ns={**contract.__dict__,'CHANGED':DELTA}
    exec(compile(raw,'<exact current three JDBC Main deltas>','exec'),ns);return ns['verify_delta'](before,after)


def receive(module):
    raw=inspect.getsource(prior.transfer.receive).replace('PG1532','PG2798').replace('pg1535','pg2802')
    ns={**prior.transfer.__dict__,'FROZEN':FROZEN}
    exec(compile(raw,'<actual new JDBC whole six Jar transfer>','exec'),ns);path=ns['receive'](module)
    old_path={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar'}.get(module)
    if old_path is None:
        import json
        rows=json.loads((OLD/'RELEASE-MANIFEST.json').read_bytes())['artifacts'];old_path=next(r['path']for r in rows if r['path'].endswith('/'+path.name))
    changed={p.split(':',1)[1]for p in DELTA if p.startswith(module+':')}
    verify_container(OLD/old_path,path,changed);return path


def main_source():
    raw=inspect.getsource(prior.main)
    for a,b in [('pg1638','pg2802'),('PG1638','PG2802'),('PG1544','PG2654'),
      ('1683dd9f6de00e71d2317d9af3cd50400a37bf4e',SOURCE),
      ('pg1636-api-boundary-full-qualified-v1','pg2800-jdbc-null-fixed-full-qualified-v1'),
      ('from pg1636_api_boundary_full_qualification import server','from pg2800_jdbc_null_fixed_full_qualified import server'),
      ("{'VERSION', 'api/api.jar'} <= changed","{'VERSION', 'operations/batch.jar'} <= changed"),
      ("'tests': 3596, 'suites': 532","'tests': 3680, 'suites': 542"),
      ("'changedClasses': 3, 'addedClasses': 6","'changedClasses': 3, 'addedClasses': 0, 'changedResources':0")]:
        if a not in raw:raise ValueError('exact immutable signing boundary required')
        raw=raw.replace(a,b)
    marker="subprocess.check_output(['git', 'diff', '--name-only', '"+SOURCE+"', 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=T)"
    if raw.count(marker)!=1:raise ValueError('one source boundary required')
    raw=raw.replace(marker,'qualify_source()');compile(raw,'<host-only JDBC candidate>','exec');return raw


def qualify_source():
    import subprocess
    validate(subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip());return b''


def main():
    ns={**prior.__dict__,'__file__':__file__,'PRODUCTION':SOURCE,'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,
        'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,'SIG':SIG,'receive':receive,'validate_gate':validate_gate,
        'verify_delta':verify_delta,'qualify_source':qualify_source}
    exec(compile(main_source(),'<new unused JDBC Main candidate>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
