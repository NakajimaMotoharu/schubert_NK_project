"""Newsource first ten points/CRC/session only, matched to actual3714/545/all1643."""
import json
import subprocess
import pg3532_outbox_current_native_qualified as previous
import pg3734_hygiene_full_six as whole
from pg3798_hygiene_current_observer import SOURCE
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate


def qualify_snapshot():
    receipt=json.loads((W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes());value=receipt['result']
    expected={'actualExit':0,'productionSource':SOURCE,'tests':3714,'suites':545,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0}
    if receipt['actualExit']!=0 or any(type(value.get(k))is not type(v)or value[k]!=v for k,v in expected.items()):raise ValueError('actual newsource3714/545/all1643 required')
    whole.validate(value['sourceSnapshot'])
    if subprocess.check_output(['git','diff',value['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('identical current qualified source/Test/settings required')


def server():
    raw=previous.server()
    for a,b in [('PG3532-native-input-v3.tar','PG3832-native-input-v1.tar'),('PG3532-native-v3','PG3832-native-v1'),('PG3412','PG3734'),('qualified3412Tests','qualified3734Tests'),('3712','3714'),(previous.SOURCE,SOURCE)]:raw=raw.replace(a,b)
    compile(raw,'<newsource physical CRC and same3714 host union>','exec');return raw


def source():
    raw=previous.previous.source()
    for a,b in [('pg2906-network-current-native-catalog-v1','pg3830-hygiene-native-catalog-v1'),('pg2908-network-current-native-qualified-v2','pg3832-hygiene-native-qualified-v1'),('pg2800-jdbc-null-fixed-full-qualified-v1','pg3738-hygiene-whole-qualified-v1'),('PG2908-native-v2','PG3832-native-v1'),('PG2908-native-input-v2.tar','PG3832-native-input-v1.tar')]:raw=raw.replace(a,b)
    compile(raw,'<newsource fresh exact native transport no old cache>','exec');return raw


def main():
    values={**previous.previous.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<actual7fff native qualification entry>','exec'),values)
    with management_gate(P/'current-management-critical.lock'):return values['main']()


if __name__=='__main__':raise SystemExit(main())
