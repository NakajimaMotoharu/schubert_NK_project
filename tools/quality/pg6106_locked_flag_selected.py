"""Normal Web925 after one lock-protected private modifier change; no runtime operations."""
import subprocess
import pg5732_enum48_selected as engine
from pg6080_web_factory_selected import inventory, runner_source
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment

ROOT = engine.ROOT
OLD = '870010d6681d74519237be7a7ca6381a190f471a'
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers.java'


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):
        raise ValueError('clean committed current source/Test/operator first')
    changed = set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())
    if changed != {MAIN}:
        raise ValueError('exact one Main change;all Tests/oracles unchanged')
    before = subprocess.check_output(['git','show',OLD+':'+MAIN],cwd=ROOT,text=True)
    if before.count('private volatile boolean closed;') != 1 or (ROOT/MAIN).read_text() != before.replace('private volatile boolean closed;','private boolean closed;',1):
        raise ValueError('one private modifier only,no method or other volatile edit')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('unchanged build/static/Current gates')
    cases, counts = inventory()
    scope = {**vars(engine),'SLOT':'pg6106-locked-flag-web925-v1','NODE_PATH':node_environment(),
        'CASES':cases,'COUNTS':counts,'TARGETS':{'web':['web/messaging/ArtemisReplyConsumers']},'test_names':source_test_names}
    exec(compile(runner_source(),'<normal925 lock flag>', 'exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
