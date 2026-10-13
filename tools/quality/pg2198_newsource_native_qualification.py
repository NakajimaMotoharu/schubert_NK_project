"""Newsource qualified full3631 + same current ten native CRC/session inputs only."""
import json
import subprocess
import pg2104_current_newrun_native_qualified_v2 as prior
from pg1446_current_cold_stage import W
from pg2176_newsource_normal_observer import SOURCE


def qualify_snapshot():
    full=json.loads((W/'pg2125-metadata-boundary-full-qualified-v1/manifest.safe.json').read_bytes());v=full['result']
    if full['actualExit']!=0 or v['productionSource']!=SOURCE or v['tests']!=3631 or v['suites']!=540 or v['mainClasses']!=1643 or v['FESFlakyNotRun']!=0:
        raise ValueError('actual qualified current full3631/540/1643 required')
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',v['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):
        raise ValueError('clean unchanged qualified Main/test source required')


def server():
    raw=prior.server()
    for old,new in [('PG2104','PG2198'),('PG1844','PG2124'),('qualified1844Tests','qualified2124Tests'),('3618','3631'),('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE)]:raw=raw.replace(old,new)
    compile(raw,'<actual current newsource native3631 server>','exec');return raw


def source():
    raw=prior.source()
    for old,new in [('pg2100-current-newrun-native-catalog-v1','pg2196-newsource-native-catalog-v1'),('pg2104-current-newrun-native-qualified-v1','pg2198-newsource-native-qualified-v1'),('PG2104','PG2198'),('pg1845-warning-unit-full-qualified-v1','pg2125-metadata-boundary-full-qualified-v1')]:raw=raw.replace(old,new)
    compile(raw,'<actual newsource native transport>','exec');return raw


def entry():
    engine=prior.engine
    ns={**engine.previous.prior.prior.prior.prior.prior.prior.__dict__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<same source matched new native transport/server>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
