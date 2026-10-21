"""Qualify only original84 XML/Jars/static; no repeated PT or rebuild."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6054_expiry_read_qualification import qualify
from pg6296_web_send_green import inventory,OLD,MAIN

RUN=W/'pg6296-web-send-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    if set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())!=MAIN:
        raise ValueError('two Web Main only, original Test fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('gates/Current fixed')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(84,15),MAIN,
        BASE/'PG6268-outbox-failure-qualification-v1/manifest.json',
        'd4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225',
        W/'pg6268-outbox-failure-qualification-v1/manifest.safe.json',
        W/'pg6268-outbox-failure-qualification-v1/findings.safe.json',
        'pg6298-web-send-qualification-v1','PG6298-web-send-qualification-v1')


if __name__=='__main__':main()
