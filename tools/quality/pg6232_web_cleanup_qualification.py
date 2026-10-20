"""Original64 qualifier, two declared Main changes, no PT replay or rebuild."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6054_expiry_read_qualification import qualify
from pg6230_web_cleanup_selected import inventory,OLD,MAIN,TEST,baseline

RUN=W/'pg6230-web-cleanup-selected-v1'


def original_source():
    source=json.loads((RUN/'begin.safe.json').read_bytes())['source']
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=MAIN|{TEST}:raise ValueError('exact two Main/one Test coupled cleanup source')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('existing gates/Current unchanged')
    return source


def main():
    baseline();cases,_=inventory()
    return qualify(original_source(),RUN,cases,(64,20),MAIN,
        BASE/'PG6208-keeper-faults-qualification-v1/manifest.json',
        'b000fbecefc854567332c21530dd63d1de411c06042f00d9e182e2def106ac34',
        W/'pg6208-keeper-faults-qualification-v1/manifest.safe.json',
        W/'pg6208-keeper-faults-qualification-v1/findings.safe.json',
        'pg6232-web-cleanup-qualification-v1','PG6232-web-cleanup-qualification-v1')


if __name__=='__main__':main()
