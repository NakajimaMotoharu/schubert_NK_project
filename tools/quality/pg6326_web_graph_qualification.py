"""Read original89 only; all API86 Main retained and two Web Main changed."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6054_expiry_read_qualification import qualify
from pg6324_web_graph_green import inventory,OLD,MAIN

RUN=W/'pg6324-web-graph-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    if set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())!=MAIN:
        raise ValueError('two Web Main only, all original red Test fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('gates/Current fixed')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(89,15),MAIN,
        BASE/'PG6320-outbox-graph-qualification-v1/manifest.json',
        '55f826b2f0a116f198e3709f596f4e2a5a5be57e7364c0aabaea8ac60fcf3325',
        W/'pg6320-outbox-graph-qualification-v1/manifest.safe.json',
        W/'pg6320-outbox-graph-qualification-v1/findings.safe.json',
        'pg6326-web-graph-qualification-v1','PG6326-web-graph-qualification-v1')


if __name__=='__main__':main()
