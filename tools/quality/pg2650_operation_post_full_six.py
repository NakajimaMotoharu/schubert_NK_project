"""Required new Web resource candidate integration; prior a79 native is not portable."""
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
import pg2640_wire_oracle_group_full_six as previous
import pg2600_retention_group_full_six as transport_base
from pg2510_strict_reference_full_six import SCOPE
from pg1446_current_cold_stage import W

SOURCE = '04207efc3ad78bca75942153a90c70985064c988'
ALLOWED = {
    'src/schubert-nk-web/src/main/resources/static/js/operation-post-submit.js',
    *('src/schubert-nk-web/src/main/resources/templates/' + x + '.html' for x in
      ('admin/user-new','admin/user-detail','notifications/detail','questions/detail')),
    'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/OperationPostScriptTest.java',
    'src/schubert-nk-web/src/test/javascript/operation-post-submit.test.cjs',
    *('src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/'+x+'.java' for x in
      ('UserBusinessControllerTest','TargetBusinessControllerTest'))}


def validate(snapshot):
    root=Path(__file__).resolve().parents[2]
    def git(*args):return subprocess.check_output(['git',*args],cwd=root)
    full=json.loads((W/'pg2641-wire-oracle-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit']!=0 or full['result']['tests']!=3664:raise ValueError('actual complete3664 baseline required')
    original=full['result']['sourceSnapshot'];previous.validate(original)
    paths=set(git('diff','--name-only',original,snapshot,'--',*SCOPE).decode().splitlines())
    if paths!=ALLOWED:raise ValueError('exact new update assets and independent Test paths required')
    selected=json.loads((W/'pg2646-operation-post-web-selected-v3/manifest.safe.json').read_bytes())
    if selected['actualExit']!=0 or selected['result']['tests']!=96 or selected['result']['suites']!=7 or selected['result']['NodeThreeCounters100']is not True:raise ValueError('actual96 seven-suite selected qualification required')
    for p in ALLOWED:
        if git('show',snapshot+':'+p)!=git('show',selected['candidateSource']+':'+p):raise ValueError('exact selected whole files required')
    if git('diff',previous.SOURCE,snapshot,'--',*[str(p.relative_to(root))for p in (root/'src').glob('*/src/main/java')]):raise ValueError('Java Main unchanged required')
    payload=(W/'pg2646-operation-post-web-selected-v3/selected.private.py').read_bytes()
    if hashlib.sha256(payload).hexdigest()!=selected['payloadSha256']:raise ValueError('exact accepted selected payload required')


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG2640','PG2650').replace('3664','3666').replace('540','541').replace(previous.SOURCE,SOURCE)
    compile(raw,'<new resource candidate all3666>', 'exec');return raw


def main():
    raw=inspect.getsource(transport_base.main).replace('PG2600','PG2650').replace('pg2600','pg2650').replace('3657','3666').replace("('524', '540')","('524', '541')")
    raw=raw.replace('3653 retained plus four independently accepted JDBC boundary methods; unchanged Main540suite1643','3664 retained plus two mandatory OperationPostScript tests; new JS/fourtemplate resources;541suite1643Main')
    raw=raw.replace('One required integration for2588/2590/2592/2594; no management-only repetition','BUG1222/YKT988 new update resources plus independent Node/HTTP DOM tests require one all-source integration; olda79 native resources not portable')
    ns={**transport_base.__dict__,'validate':validate,'server_source':server_source,'SOURCE':SOURCE}
    exec(compile(raw,'<new resource candidate immutable full transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
