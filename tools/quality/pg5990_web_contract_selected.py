"""Normal Web913+8 guards after24/42 constants; fixed Node, no deployment/runtime operations."""
import json
import subprocess
import pg5984_web_form_selected_v2 as previous
from pg5940_private_lock_compile import ROOT, BASE, sha
from pg5980_web921_public import SOURCE as OLD
from static_disposition_overlay import load

PLAN = BASE/'PG5988-web-contract42-plan-v1/manifest.json'
PLAN_SHA = '82031f26c9cd398fe674ba00aae48609b4c12ea0d80be481f0455ae76db8df37'


def inventory():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('immutable24/42 conditions declaration')
    plan = json.loads(PLAN.read_bytes()); cases, counts, _targets = previous.previous.inventory()
    targets = {'web':[r['path'].split('/src/main/java/dev/codex/schubert/nk/')[1][:-5] for r in plan['sourcePlans']]}
    if len(targets['web']) != 24 or sum(counts.values()) != 921 or len(counts) != 149:
        raise ValueError('actual24 targets and unchanged913+8 semantic inventory')
    return cases, counts, targets


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source/operator first')
    plan = json.loads(PLAN.read_bytes()); paths = {r['path'] for r in plan['sourcePlans']}
    source = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    if set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'], cwd=ROOT, text=True).splitlines()) != paths or any(sha(ROOT/r['path']) != r['predictedAfterSha256'] for r in plan['sourcePlans']):
        raise ValueError('only24 exact Main changes, no Test/oracle/JS/template/SQL changes')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'], cwd=ROOT):
        raise ValueError('quality/build/compatibility gates unchanged')
    rows = load(BASE/'PG5982-web-static-dispositions-v1/manifest.json','7c195396d242b237c2b254ebc07b544fd142663b9c2662758131b8795f665f97',OLD)
    ids = {i for r in plan['sourcePlans'] for i in r['findingIds']}; chosen = [r for r in rows if r['findingId'] in ids]
    if len(chosen) != 42 or any(r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' for r in chosen):
        raise ValueError('all42 genuinely current unreviewed warnings, not duplicate PG credit')


def runner_source():
    raw = previous.runner_source()
    changes = {'head=SOURCE': "head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()",
               "if sha(archive) != '043d226d79e10e0d2696adca50d949892ded3dc1ab5e73d485aa4326eca31836':raise ValueError('exact original a623 archive')\n    ": '',
               'len(target_counters)==12': 'len(target_counters)==24',
               "executionKind='NORMAL_WEB_FORM_SELECTED921_NODE_FIXED'": "executionKind='NORMAL_WEB_CONTRACT24_SELECTED921'",
               "priorFailedRun='pg5976-web-form-selected921-v1',": ''}
    for old,new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one explicit current Web24 runner binding: '+old)
        raw = raw.replace(old,new,1)
    compile(raw,'<Web24 normal921>', 'exec')
    return raw


def main():
    prerequisites(); path = previous.node_environment(); cases, counts, targets = inventory()
    scope = {**vars(previous.previous.previous.engine), 'NODE_PATH':path,'NODE_SHA':previous.NODE_SHA,
             'SLOT':'pg5990-web-contract-selected921-v1','CASES':cases,'COUNTS':counts,'TARGETS':targets,'test_names':previous.previous.previous.source_test_names}
    exec(compile(runner_source(),'<Web24 same approved local fixtures>','exec'),scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
