"""Original113 source/Jar/XML/static qualification; no repeated Test or rebuild."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6054_expiry_read_qualification import qualify
from pg6238_confirmed_rollback_selected import inventory,OLD,MAIN,TEST

RUN=W/'pg6238-confirmed-rollback-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=MAIN|{TEST}:raise ValueError('original eightMain/oneTest input source')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('actual gates/Current unchanged')
    return source


def main():
    cases,_=inventory()
    return qualify(original_source(),RUN,cases,(113,28),MAIN,
        BASE/'PG6232-web-cleanup-qualification-v1/manifest.json',
        '0061d492f2c42b834f5e88250c0c4536c35eb1276173e92d2bc5510fd9c99137',
        W/'pg6232-web-cleanup-qualification-v1/manifest.safe.json',
        W/'pg6232-web-cleanup-qualification-v1/findings.safe.json',
        'pg6240-confirmed-rollback-qualification-v1','PG6240-confirmed-rollback-qualification-v1')


if __name__=='__main__':main()
