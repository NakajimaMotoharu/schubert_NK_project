"""One required changed-Main full regression; never import Source042 native into candidate."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import pg2770_db_contract_group_full_six as prior
from pg1446_current_cold_stage import W
from pg2510_strict_reference_full_six import SCOPE

SOURCE='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
BASE_FULL='200a92c6b7941be4627bab2b949b78b6d45c3e85'
MAIN='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.java'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java'
OWNER='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwnerAdmissionTest.java'


def validate(snapshot):
    root=Path(__file__).resolve().parents[2]
    git=lambda *args:subprocess.check_output(['git',*args],cwd=root)
    if git('diff',SOURCE,snapshot,'--',*SCOPE):raise ValueError('actual candidate source/Test/settings unchanged required')
    changed=set(git('diff','--name-only',BASE_FULL,snapshot,'--',*SCOPE).decode().splitlines())
    if changed!={MAIN,TEST,OWNER}:raise ValueError('exact Main defect fix/Session tests/owner contract group required')
    receipt=json.loads((W/'pg2796-jdbc-candidate-contract-v1/manifest.safe.json').read_bytes())
    if receipt.get('actualExit')!=0 or receipt.get('candidateSource')!=SOURCE or receipt.get('tests')!=60 or receipt.get('FESAbortedNotRun')!=0 or receipt.get('coverageClaim')is not False:
        raise ValueError('actual changed-Main whole Session qualification required')
    old=git('show',BASE_FULL+':'+TEST).decode();new=git('show',snapshot+':'+TEST).decode()
    if old.count('@Test\n')!=55 or new.count('@Test\n')!=60 or git('show',snapshot+':'+OWNER).decode().count('@Test\n')!=2:
        raise ValueError('exact seven new methods/one new suite count basis required')
    payload=(W/'pg2796-jdbc-candidate-contract-v1/selected.private.py').read_bytes()
    if hashlib.sha256(payload).hexdigest()!=receipt['payloadSha256']:raise ValueError('actual changed-Main payload authority required')


def server_source(head,digest):
    raw=prior.server_source(head,digest).replace('PG2770','PG2798').replace('3673','3680').replace('541','542').replace(prior.SOURCE,SOURCE)
    if SOURCE not in raw or '04207efc3ad78bca75942153a90c70985064c988' in raw:raise ValueError('new Main source explicitly bound required')
    compile(raw,'<changed Main full3680>','exec');return raw


def main():
    engine=prior.transport_base.previous.previous.previous.previous.transport
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=engine.prior.ROOT,text=True).strip();validate(head)
    raw=inspect.getsource(engine.main)
    for a,b in [('PG1528','PG2798'),('pg1528','pg2798'),('3582','3680'),('524','542'),('1637','1643')]:raw=raw.replace(a,b)
    raw=raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained',
        '3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643')
    raw=raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved',
        'BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable')
    ns={**engine.__dict__,'PRODUCTION':SOURCE,'server_source':server_source}
    exec(compile(raw,'<changed Main necessary full transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
