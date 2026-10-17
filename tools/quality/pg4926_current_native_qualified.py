"""Current04bb streams/all1647 CRC join to actual3761/551; no old-source import."""
import json
import subprocess
import pg4782_new_current_native_qualified as previous
import pg4924_current_native_catalog as catalog
from pg4860_ssc301_302_signed_candidate import validate_gate

SOURCE=catalog.role.SOURCE
W,P=previous.W,previous.P
FULL='pg4846-ssc301-302-whole-qualified-v1'
SLOT='pg4926-current-native-qualified-v1'


def qualify(value):return validate_gate(value,SOURCE)


def qualify_snapshot():
    q=qualify(json.loads((W/FULL/'manifest.safe.json').read_bytes()))
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff',q['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):
        raise ValueError('same clean qualified3761 source/Test/settings first')
    catalog.role.admission.authenticate_host()


def server():
    raw=previous.server()
    for a,b in [('PG4782','PG4926'),('PG4694','PG4844'),('qualified4694Tests','qualified4844Tests'),('3739','3761'),(previous.SOURCE,SOURCE)]:raw=raw.replace(a,b)
    return raw


def source():
    raw=previous.source()
    for a,b in [(previous.catalog.SLOT,catalog.SLOT),(previous.SLOT,SLOT),(previous.FULL,FULL),('PG4782','PG4926')]:raw=raw.replace(a,b)
    return raw


def main():
    ns={**previous.transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<current3761 exact native transport>','exec'),ns)
    with previous.management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
