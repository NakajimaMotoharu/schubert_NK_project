"""Fresh3618 complete XML/static/class/source qualification; no native replay."""
import inspect
import subprocess
import pg1533_filesystem_full_qualification as prior
from pg1636_api_boundary_full_qualification import server as old_server

def server():
    raw=old_server().replace('PG1633','PG1755')
    for old,new in [("'api':(968,159,407)","'api':(969,159,407)"),("'batch':(1200,164,568)","'batch':(1221,168,568)"),("old=json.loads((B/'runs/PG1532-six-v1/manifest.safe.json').read_bytes())","old=json.loads((B/'runs/PG1633-six-v1/manifest.safe.json').read_bytes())"),("require(set(changed)=={'api:dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.class','api:dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.class','api:dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime$1.class'})","require(changed==[])"),("require(set(added)=={'api:dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture'+s+'.class' for s in ['', '$Factory','$Open','$Capture','$Operation','$Owner']})","require(added==[])")]:
        if raw.count(old)!=1:raise ValueError('one actual complete qualifier boundary required')
        raw=raw.replace(old,new)
    raw=raw.replace('==3596','==3618').replace('==532','==536').replace("'tests':3596","'tests':3618").replace("'suites':532","'suites':536")
    compile(raw,'<whole3618 XML/static/unchanged Main oracle>','exec');return raw

def main():
    # A tool/doc-only later HEAD may differ, but all snapshot source files must not.
    import json
    begun=json.loads((prior.W/'pg1755-server-six-v1/begin.safe.json').read_bytes())
    if subprocess.check_output(['git','diff',begun['snapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('fixed Test/Main source required')
    raw=inspect.getsource(prior.main).replace('pg1533-filesystem-full-qualified-v1','pg1756-boundary-full-qualified-v1').replace('pg1532-server-six-v1','pg1755-server-six-v1').replace('PG1532','PG1755')
    marker="if subprocess.check_output(['git', 'diff', '4d6bcbddb417b76d27e52d5d9640752c300edccf', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root):"
    if raw.count(marker)!=1:raise ValueError('one host snapshot boundary required')
    raw=raw.replace(marker,"if subprocess.check_output(['git','diff',begun['snapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=root):")
    ns={**prior.__dict__,'CODE':server()}
    exec(compile(raw,'<current fresh source independent whole qualification>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
