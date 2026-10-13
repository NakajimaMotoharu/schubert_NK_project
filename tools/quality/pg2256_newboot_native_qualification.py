"""Fresh3633 same Main + currentboot actual ten native CRC/session inputs; no oldsource union."""
import json
import subprocess
import pg2198_newsource_native_qualification as prior
from pg1446_current_cold_stage import W
from pg2176_newsource_normal_observer import SOURCE


def qualify_snapshot():
    full=json.loads((W/'pg2236-root-host-integration-full-qualified-v1/manifest.safe.json').read_bytes());v=full['result']
    if full['actualExit']!=0 or v['productionSource']!=SOURCE or v['tests']!=3633 or v['suites']!=540 or v['mainClasses']!=1643 or v['FESFlakyNotRun']!=0 or v['staticSixModules']!=0:
        raise ValueError('actual qualified same-source full3633/540/1643 required')
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',v['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):
        raise ValueError('clean fixed current full Main/test input required')


def server():
    raw=prior.server().replace('PG2198','PG2256').replace('PG2124','PG2228').replace('qualified2124Tests','qualified2228Tests').replace('3631','3633')
    compile(raw,'<currentboot native3633 CRC/session server>','exec');return raw


def source():
    raw=prior.source()
    for old,new in [('pg2196-newsource-native-catalog-v1','pg2254-newboot-native-catalog-v1'),('pg2198-newsource-native-qualified-v1','pg2256-newboot-native-qualified-v1'),('PG2198','PG2256'),('pg2125-metadata-boundary-full-qualified-v1','pg2236-root-host-integration-full-qualified-v1')]:raw=raw.replace(old,new)
    compile(raw,'<currentboot matched transport>','exec');return raw


def entry():
    engine=prior.prior.engine
    ns={**engine.previous.prior.prior.prior.prior.prior.prior.__dict__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<currentboot matched new native transport/server>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
