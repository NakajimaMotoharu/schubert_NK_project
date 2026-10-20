"""Normal API1010+11 guards after15/18 bounds;no deployed/VM operations."""
import json
import subprocess
import pg5966_api_sql_selected as previous
from pg5984_web_form_selected_v2 import node_environment,NODE_SHA
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg5994_web24_public import SOURCE as OLD
from static_disposition_overlay import load

PLAN=BASE/'PG6004-api-bounds18-plan-v1/manifest.json'
PLAN_SHA='c10cb0ae8fab810e4a43140218a26c3a332c3a18401cee5d4060367feef972fa'


def inventory():
    if sha(PLAN)!=PLAN_SHA:raise ValueError('immutable15/18 declaration')
    plan=json.loads(PLAN.read_bytes());cases,counts,_targets=previous.inventory()
    targets={'api':[r['path'].split('/src/main/java/dev/codex/schubert/nk/')[1][:-5]for r in plan['sourcePlans']]}
    if len(targets['api'])!=15 or sum(counts.values())!=1021 or len(counts)!=175:raise ValueError('all15 actual targets/API1010+11 semantic Test inventory')
    return cases,counts,targets


def prerequisites():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed source first')
    plan=json.loads(PLAN.read_bytes());source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())!={r['path']for r in plan['sourcePlans']}or any(sha(ROOT/r['path'])!=r['predictedAfterSha256']for r in plan['sourcePlans']):raise ValueError('all15 exact Main only;Test/oracle/SQL/resources unchanged')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('same quality/build/compatibility gates')
    rows=load(BASE/'PG6002-direct-jdbc-finally63-v1/manifest.json','ad81ef51ee6c97ec86f72266a3e8bfd8183cb4789b91cd00949395ba8fbfd181',OLD);ids={i for r in plan['sourcePlans']for i in r['findingIds']};chosen=[r for r in rows if r['findingId']in ids]
    if len(chosen)!=18 or any(r['status']!='NOT_REVIEWED_CURRENT_SOURCE'for r in chosen):raise ValueError('all18 genuinely unreviewed current conditions')


def runner_source():
    raw=previous.runner_source()
    for old,new in (('len(target_counters)==16','len(target_counters)==15'),("executionKind='NORMAL_API_SQL_SELECTED1021'","executionKind='NORMAL_API_BOUNDS15_SELECTED1021'"),("os.pathsep+os.environ['PATH'],MAVEN_OPTS","os.pathsep+NODE_PATH,MAVEN_OPTS")):
        if raw.count(old)!=1:raise ValueError('one explicit currentAPI15 runner binding: '+old)
        raw=raw.replace(old,new,1)
    compile(raw,'<current API15 normal1021>','exec')
    return raw


def main():
    prerequisites();path=node_environment();cases,counts,targets=inventory()
    scope={**vars(previous.engine),'NODE_PATH':path,'NODE_SHA':NODE_SHA,'SLOT':'pg6006-api-bounds-selected1021-v1','CASES':cases,'COUNTS':counts,'TARGETS':targets,'test_names':previous.source_test_names}
    exec(compile(runner_source(),'<API15 approved independent fixtures>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
