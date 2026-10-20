"""Genuine original60/all source/classes/Jars; no PT or runtime invocation by the reader."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6190_management_primary_selected import inventory, OLD, MAIN, TEST

RUN=W/'pg6190-management-primary-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!={MAIN,TEST}:raise ValueError('exact primary Main/Test input correction in original source')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('unchanged original source gates')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(60,20),{MAIN},
        BASE/'PG6184-unstarted-management-qualification-v1/manifest.json',
        'c944bf948732c010e7b820f3882eebb293009f8eb3d545d523f6f4b03ae70ac6',
        W/'pg6184-unstarted-management-qualification-v1/manifest.safe.json',
        W/'pg6184-unstarted-management-qualification-v1/findings.safe.json',
        'pg6192-management-primary-qualification-v1','PG6192-management-primary-qualification-v1')


if __name__=='__main__':main()
