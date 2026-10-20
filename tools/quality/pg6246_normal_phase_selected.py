"""Test-only independent normal Closeable/phase wrapper contracts, unchanged all Main/gates."""
import inspect
import subprocess
import pg6238_confirmed_rollback_selected as prior

ROOT=prior.ROOT
OLD='f985e88a2a75333e6e6f1f3459524fa802a32c2a'
TESTS={
    'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceResourceRetentionTest.java',
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/InternalEventListenerTest.java'}


def inventory():return prior.inventory()


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed source/operator')
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=TESTS:raise ValueError('exact two independent Test bodies; no Main change')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('unchanged gates/Current')
    raw=inspect.getsource(prior.main)
    start=raw.index('    raw=inspect.getsource(prior.main)')
    raw='def run_normal():\n'+raw[start:]
    raw=raw.replace('    scope={**vars(prior),\'inventory\':inventory}',
        "    raw=raw.replace('pg6238-confirmed-rollback-selected-v1','pg6246-normal-phase-selected-v1',1)\n    scope={**vars(prior),'inventory':inventory}",1)
    scope={**vars(prior),'prior':prior.prior,'inventory':inventory}
    exec(compile(raw,'<two normal Test contracts/113>','exec'),scope)
    return scope['run_normal']()


if __name__=='__main__':raise SystemExit(main())
