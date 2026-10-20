"""Original113 Test-only qualification; all851 Main/1667 physical classes must remain identical."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6054_expiry_read_qualification import qualify
from pg6246_normal_phase_selected import inventory,OLD,TESTS

RUN=W/'pg6246-normal-phase-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=TESTS:raise ValueError('exact two Test-only inputs, unchanged all Main')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('gates/Current fixed')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(113,28),set(),
        BASE/'PG6240-confirmed-rollback-qualification-v1/manifest.json',
        'ec42a732eccf0c26d664b0511399f87ad68f5036259fd20453cdc21995a004b1',
        W/'pg6240-confirmed-rollback-qualification-v1/manifest.safe.json',
        W/'pg6240-confirmed-rollback-qualification-v1/findings.safe.json',
        'pg6248-normal-phase-qualification-v1','PG6248-normal-phase-qualification-v1')


if __name__=='__main__':main()
