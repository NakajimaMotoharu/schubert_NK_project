"""Fresh actual nine latest streams qualified against all Main bytes of fresh full3635."""
import json
import subprocess
import pg2256_newboot_native_qualification as previous
from pg1446_current_cold_stage import W
from pg2374_current_resume_owned_sources import SOURCE
from pg2300_jdbc_host_integration_full_six import validate


def qualify_snapshot():
    v=json.loads((W/'pg2301-jdbc-host-integration-qualified-v1/manifest.safe.json').read_bytes())
    if v['actualExit']!=0:raise ValueError('actual qualified fresh full required')
    f=v['result']
    if not(f['productionSource']==SOURCE and f['tests']==3635 and f['suites']==540 and f['mainClasses']==1643 and f['FESFlakyNotRun']==0 and f['staticSixModules']==0):raise ValueError('current3635/540/1643/all six qualified required')
    validate(f['sourceSnapshot'])
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',f['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('fixed whole source/Main/test inputs required')


def server():
    raw=previous.server().replace('PG2256','PG2384').replace('PG2228','PG2300').replace('qualified2228Tests','qualified2300Tests').replace('3633','3635')
    compile(raw,'<actual current nine latest full3635 server>','exec');return raw


def source():
    raw=previous.source()
    for a,b in [('pg2254-newboot-native-catalog-v1','pg2382-current-resume-native-catalog-v1'),('pg2256-newboot-native-qualified-v1','pg2384-current-resume-native-qualified-v1'),('PG2256','PG2384'),('pg2236-root-host-integration-full-qualified-v1','pg2301-jdbc-host-integration-qualified-v1')]:raw=raw.replace(a,b)
    compile(raw,'<actual current nine latest full3635 transport>','exec');return raw


def entry():
    ns={**previous.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<current whole Main CRC/session qualification>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
