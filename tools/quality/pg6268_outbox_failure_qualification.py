"""Qualify only original51 XML/Jars/static; no repeated PT or rebuild."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6054_expiry_read_qualification import qualify
from pg6266_outbox_failure_selected import inventory,OLD,MAIN

RUN=W/'pg6266-outbox-failure-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=MAIN:raise ValueError('exact two Main, fixed independent Test/oracle')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('actual gates/Current fixed')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(51,11),MAIN,
        BASE/'PG6248-normal-phase-qualification-v1/manifest.json',
        '4495f3778a40c33c3de9f6fbd1082581fba8f7cf02caafae55687b32928b8bfe',
        W/'pg6248-normal-phase-qualification-v1/manifest.safe.json',
        W/'pg6248-normal-phase-qualification-v1/findings.safe.json',
        'pg6268-outbox-failure-qualification-v1','PG6268-outbox-failure-qualification-v1')


if __name__=='__main__':main()
