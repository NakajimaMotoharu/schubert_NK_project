"""NewSource independent whole XML/static/JAR/class/coverage/archive qualification.

Reuses the established independent verifier logic, never the old success or
old-source exec. Compares physical class scope with frozen PG1532 as a delta.
"""
import inspect
import pg1533_filesystem_full_qualification as prior
from pg1630_api_terminal_selected import PRODUCTION


def server():
    raw=prior.CODE.replace('PG1532','PG1633').replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',PRODUCTION)
    raw=raw.replace("'api':(963,157,401)","'api':(968,159,407)").replace("'batch':(1192,158,568)","'batch':(1200,164,568)")
    raw=raw.replace("B/'runs/PG1476-six-v1/manifest.safe.json'","B/'runs/PG1532-six-v1/manifest.safe.json'")
    old="require(set(changed)=={'batch:dev/codex/schubert/nk/batch/file/InspectorEnvironmentReader$NioIo.class','batch:dev/codex/schubert/nk/batch/file/EnvironmentInodePolicy.class'})"
    new="require(set(changed)=={'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.class','api:dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.class','api:dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime$1.class'})"
    if raw.count(old)!=1:raise ValueError('fixed actual class delta boundary required')
    raw=raw.replace(old,new)
    old="require(set(added)=={'storage:dev/codex/schubert/nk/storage/LinuxFilesystemClassifier.class','storage:dev/codex/schubert/nk/storage/LinuxFilesystemClassifier$StatfsCall.class'})"
    new="require(set(added)=={'api:dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture'+s+'.class' for s in ['', '$Factory','$Open','$Capture','$Operation','$Owner']})"
    if raw.count(old)!=1:raise ValueError('fixed actual added class boundary required')
    raw=raw.replace(old,new).replace('3583','3596').replace('==524','==532').replace('==1637','==1643').replace("'suites':524","'suites':532").replace("'mainClasses':1637","'mainClasses':1643")
    from pyflakes.api import check
    if check(raw,'<actual current whole independent qualifier>'):raise ValueError('generated static gate refused')
    compile(raw,'<newSource current whole independent qualifier>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1533-filesystem-full-qualified-v1','pg1636-api-boundary-full-qualified-v1').replace('pg1532-server-six-v1','pg1633-server-six-v1').replace('PG1532','PG1633')
    marker="if subprocess.check_output(['git', 'diff', '4d6bcbddb417b76d27e52d5d9640752c300edccf', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root):"
    if raw.count(marker)!=1:raise ValueError('one fixed snapshot source boundary required')
    raw=raw.replace(marker,"if subprocess.check_output(['git','diff','--name-only','1683dd9f6de00e71d2317d9af3cd50400a37bf4e',begun['snapshot'],'--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=root):")
    ns={**prior.__dict__,'CODE':server()}
    exec(compile(raw,'<fresh independent allsource qualification dispatch>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
