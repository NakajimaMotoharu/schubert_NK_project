"""Read original86 XML/Jars/source/static only, never rebuild or repeat PT."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6054_expiry_read_qualification import qualify
from pg6318_outbox_graph_green import inventory,OLD,MAIN

RUN=W/'pg6318-outbox-graph-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    if set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())!=MAIN:
        raise ValueError('two API Main only, independent Test fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('gates/Current fixed')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(86,15),MAIN,
        BASE/'PG6298-web-send-qualification-v1/manifest.json',
        '00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27',
        W/'pg6298-web-send-qualification-v1/manifest.safe.json',
        W/'pg6298-web-send-qualification-v1/findings.safe.json',
        'pg6320-outbox-graph-qualification-v1','PG6320-outbox-graph-qualification-v1')


if __name__=='__main__':main()
