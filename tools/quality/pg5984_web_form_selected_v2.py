"""BUG1518: same a623/archive Web921 after fixed Node environment, no runtime operations."""
import os
import shutil
import subprocess
import pg5976_web_form_selected as previous
from pg5940_private_lock_compile import ROOT, TC, W, sha

SOURCE = 'a623f0506bb11006dbb83ee8546609e1960ff9a2'
SLOT = 'pg5984-web-form-selected921-v2'
NODE = TC/'node-v24.19.0/bin/node'
NODE_SHA = 'bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12'


def node_environment():
    path = str(NODE.parent)+os.pathsep+os.environ['PATH']
    if sha(NODE) != NODE_SHA or shutil.which('node', path=path) != str(NODE):
        raise ValueError('fixed actual Node bytes and PATH resolution first')
    if subprocess.check_output([str(NODE), '--version'], text=True).strip() != 'v24.19.0':
        raise ValueError('fixed Node24.19.0 fixture runtime')
    return path


def runner_source():
    raw = previous.runner_source()
    changes = {
        "head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()": 'head=SOURCE',
        "os.pathsep+os.environ['PATH'],MAVEN_OPTS": "os.pathsep+NODE_PATH,MAVEN_OPTS",
        "snapshot=out/'source';snapshot.mkdir()": "if sha(archive) != '043d226d79e10e0d2696adca50d949892ded3dc1ab5e73d485aa4326eca31836':raise ValueError('exact original a623 archive')\n    snapshot=out/'source';snapshot.mkdir()",
        "value.update(executionKind='NORMAL_WEB_FORM_SELECTED921',webCases=913,guardCases=8,noDeployedRuntimeOperation=True,oldSuccessImported=False)": "value.update(executionKind='NORMAL_WEB_FORM_SELECTED921_NODE_FIXED',webCases=913,guardCases=8,noDeployedRuntimeOperation=True,oldSuccessImported=False,priorFailedRun='pg5976-web-form-selected921-v1',nodeVersion='24.19.0',nodeSha256=NODE_SHA)"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one explicit same-source/Node binding: '+old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<same a623 normal921 Nodefixed>', 'exec')
    return raw


def main():
    previous.prerequisites()
    if subprocess.check_output(['git', 'diff', SOURCE, 'HEAD', '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('canonical a623 Main/Test/oracle/gates unchanged')
    original = W/'pg5976-web-form-selected921-v1/manifest.safe.json'
    if sha(original) != 'aa5fe4a0f0671e315e6ddc80e21c4ac23d41bf4aee7efabcfc72d0aeecc768d8':
        raise ValueError('actual original failed receipt retained')
    path = node_environment(); cases, counts, targets = previous.inventory()
    scope = {**vars(previous.previous.engine), 'SOURCE': SOURCE, 'NODE_PATH': path, 'NODE_SHA': NODE_SHA,
             'SLOT': SLOT, 'CASES': cases, 'COUNTS': counts, 'TARGETS': targets, 'test_names': previous.previous.source_test_names}
    exec(compile(runner_source(), '<same-source Web921 Nodefixed>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
