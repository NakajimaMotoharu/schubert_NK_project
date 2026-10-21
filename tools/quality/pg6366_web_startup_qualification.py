"""Read actual original54 XML/Jars and allowed static, no additional Production execution."""
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE
from pg6054_expiry_read_qualification import qualify
from pg6364_web_startup_green import inventory, OLD, MAIN

RUN = W/'pg6364-web-startup-selected-v1'


def original_source():
    source = json.loads((RUN/'begin.safe.json').read_bytes())['source']
    if set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()) != MAIN:
        raise ValueError('two localized Main only; all independent red oracles fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('gates/Current unchanged')
    return source


def main():
    cases, _ = inventory()
    return qualify(original_source(), RUN, cases, (54, 15), MAIN,
        BASE/'PG6350-web-lifetime-qualification-v1/manifest.json',
        'fb7279b4a9133049b535475703d2eb52f76c7f9c2c5fc040a2c25369fb7d3b71',
        W/'pg6350-web-lifetime-qualification-v1/manifest.safe.json',
        W/'pg6350-web-lifetime-qualification-v1/findings.safe.json',
        'pg6366-web-startup-qualification-v1', 'PG6366-web-startup-qualification-v1')


if __name__ == '__main__':
    main()
