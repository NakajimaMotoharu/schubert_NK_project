"""Read original59 and all851/1667; original snapshot source not an inferred success."""
import json
import subprocess
from pg5940_private_lock_compile import W, BASE, ROOT
from pg6054_expiry_read_qualification import qualify
from pg6174_native_assembly_static import MAIN as ASSEMBLY
from pg6180_unstarted_management_static import MAIN as STOP
from pg6182_unstarted_management_selected import inventory, CODE

MAIN=ASSEMBLY|STOP
RUN=W/'pg6182-unstarted-management-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    if subprocess.check_output(['git','diff',CODE,source,'--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('original source snapshot has exact strict-static Main/Test inputs')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(59,20),MAIN,
        BASE/'PG6172-native-retention-qualification-v3/manifest.json',
        '191c575a681701f34b19aa2c87bcbd1dacf81369987929997c8b45bcc1795fcd',
        W/'pg6172-native-retention-qualification-v3/manifest.safe.json',
        W/'pg6172-native-retention-qualification-v3/findings.safe.json',
        'pg6184-unstarted-management-qualification-v1','PG6184-unstarted-management-qualification-v1')


if __name__=='__main__':main()
