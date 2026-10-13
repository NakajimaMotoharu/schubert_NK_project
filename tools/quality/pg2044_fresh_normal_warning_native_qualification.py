"""Same current candidate full3618/MainCRC and current ten point normal-Root native qualification."""
import json
import subprocess
import pg1843_warning_current_native_qualification as previous
from pg1446_current_cold_stage import W
from pg2030_fresh_normal_warning_owned_stop_sources import SOURCE


def qualify_snapshot():
    full=json.loads((W/'pg1845-warning-unit-full-qualified-v1/manifest.safe.json').read_bytes());value=full['result']
    if full['actualExit']!=0 or value['productionSource']!=SOURCE or value['tests']!=3618 or value['changedClasses']!=[]or value['addedClasses']!=[]:raise ValueError('actual current full Main bytes required')
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',value['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('clean unchanged qualified Main/test source required')


def source():
    raw=previous.source()
    for old,new in [('pg1842-warning-inspector-two-point-catalog-v1','pg2042-fresh-normal-warning-native-catalog-v1'),('pg1843-warning-current-native-qualified-v1','pg2044-fresh-normal-warning-native-qualified-v1'),('PG1843','PG2044'),('pg1756-boundary-full-qualified-v1','pg1845-warning-unit-full-qualified-v1')]:
        if old not in raw:raise ValueError('one current candidate full/native boundary required')
        raw=raw.replace(old,new)
    compile(raw,'<same current full3618 native transport>','exec');return raw


def server():
    raw=previous.server()
    for old,new in [('PG1843','PG2044'),('PG1755','PG1844'),('qualified1755Tests','qualified1844Tests'),('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',SOURCE)]:
        if old not in raw:raise ValueError('one actual current main/native byte binding required')
        raw=raw.replace(old,new)
    raw=raw.replace("'notDeployedUnitCandidateAccepted':False","'actualCurrentNormalWarningSource':True")
    compile(raw,'<current ten points/session/CRC/full3618>','exec');return raw


def main():
    ns={**previous.prior.prior.prior.prior.prior.prior.__dict__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<current only ten point native qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
