"""Required fresh six after PG-D412, old source/native/results cannot qualify it."""
import inspect
import json
import subprocess
import pg1532_filesystem_closing_full_six as previous
import pg1528_filesystem_full_six as transport
from pg1630_api_terminal_selected import PRODUCTION


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG1532','PG1633').replace('3583','3596').replace('524','532').replace('1637','1643').replace(previous.PRODUCTION,PRODUCTION)
    from pyflakes.api import check
    if check(raw,'<actual complete newSource fullsix>'):raise ValueError('actual generated static gate refused')
    compile(raw,'<PG-D412 sourcefixed fullsix>','exec');return raw


def main():
    qualified=json.loads((transport.prior.W/'pg1632-api-terminal-qualified-v1/manifest.safe.json').read_bytes())
    if qualified.get('actualExit')!=0 or qualified.get('freshApiPt')!=13 or qualified.get('staticModules')!=4 or qualified.get('staticIssues')!=0 or qualified.get('unchangedDependencyClassBytes')is not True:
        raise ValueError('newSource API13 independent qualification required')
    changed=subprocess.check_output(['git','diff','--name-only',PRODUCTION,'--','src','pom.xml'],cwd=transport.prior.ROOT,text=True).splitlines()
    if changed!=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiTerminalCaptureTest.java']:
        raise ValueError('same Main and only independently corrected terminal test oracle required')
    raw=inspect.getsource(transport.main).replace('PG1528','PG1633').replace('pg1528','pg1633').replace('3582','3596').replace('524','532').replace('1637','1643').replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained','3583/524/1637 + batch8/sixsuites + API5/twosuites + terminalcapture6 Main; all prior tests retained').replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved','PG-D412 API Main/lifetime/package terminal boundary; qualified affected13, required newSource fullsix before native/release/formal')
    ns={**transport.__dict__,'server_source':server_source,'PRODUCTION':PRODUCTION}
    exec(compile(raw,'<fresh PG-D412 fullsix dispatch>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
