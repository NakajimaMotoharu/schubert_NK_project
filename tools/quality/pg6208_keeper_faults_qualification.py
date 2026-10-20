"""Qualify original63, no repeated PT or rebuild; seven exact current Main owners."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6206_keeper_faults_selected import inventory, OLD, MAIN, TEST

RUN=W/'pg6206-keeper-faults-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=MAIN|{TEST}:raise ValueError('exact seven coupled Main/one fault Test')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('existing build/static/Current gates unchanged')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(63,20),MAIN,
        BASE/'PG6193-management-primary-qualification-v2/manifest.json',
        'e64ddbb2f3f2d736379f374633d00efa215872b3aaee344f1b43605002ad0e1f',
        W/'pg6193-management-primary-qualification-v2/manifest.safe.json',
        W/'pg6193-management-primary-qualification-v2/findings.safe.json',
        'pg6208-keeper-faults-qualification-v1','PG6208-keeper-faults-qualification-v1')


if __name__=='__main__':main()
