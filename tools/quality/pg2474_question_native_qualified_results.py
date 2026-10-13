"""BUG1241: whole unchanged inputs plus one independently proven new A01 result."""
import hashlib
import json
import subprocess
from pathlib import Path
import pg2468_question_current_native_qualification as prior
from pg2446_question_current_observer import SOURCE
from pg1446_current_cold_stage import W
from pg2404_question_jdbc_full_six import validate
from pg876_public_artifact_check import check

ARTIFACT='program/characterization/reports/nk/PG2470-native-a01-v1/artifacts/CHR-A01.json'
ARTIFACT_SHA='3f4ed53954d6c3652d8265adde23004d79dd51fec9e16eb1db79255abd059558'
BASELINE='program/characterization/baseline/current/artifacts/CHR-A01.json'
BASELINE_SHA='df68edfbd59d60fc0d87fcce818401788740153c8b630f790d785f6414001993'


def result_changes(changes,artifact,baseline,receipt):
    if type(changes)is not list or len(changes)!=len(set(changes))or any(x!=ARTIFACT for x in changes):
        raise ValueError('only one explicitly qualified result, no input exclusion allowed')
    if type(artifact)is not bytes or type(baseline)is not bytes or hashlib.sha256(artifact).hexdigest()!=ARTIFACT_SHA or hashlib.sha256(baseline).hexdigest()!=BASELINE_SHA:
        raise ValueError('actual sanitized A01 and immutable Current baseline required')
    if type(receipt)is not dict or type(receipt.get('actualExit'))is not int or receipt['actualExit']!=0 or receipt.get('productionSource')!=SOURCE:
        raise ValueError('actual same source case receipt required')
    for key,value in {'sameCapturedParentApiWebCaddyBeforeAfter':True,'sharedCurrentDriver':True,
        'approvedDIF001TitleOnly':True,'otherCasesNotRun':True,'fullGate':False,'formalAccepted':False,
        'rawCookieTokenExported':False,'baselineSha256':BASELINE_SHA,
        'harnessClassesSha256':'122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d'}.items():
        if type(receipt.get(key))is not type(value)or receipt[key]!=value:raise ValueError('complete independent case proof required')
    check(json.loads(artifact),json.loads(baseline))


def qualify_snapshot():
    v=json.loads((W/'pg2405-question-jdbc-full-qualified-v1/manifest.safe.json').read_bytes())
    if v['actualExit']!=0:raise ValueError('actual current whole full required')
    f=v['result']
    if not(f['productionSource']==SOURCE and f['tests']==3637 and f['suites']==540 and f['mainClasses']==1643 and f['FESFlakyNotRun']==0 and f['staticSixModules']==0):
        raise ValueError('current3637/540/1643/static6 required')
    validate(f['sourceSnapshot'])
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean current input/result operator required')
    changes=subprocess.check_output(['git','diff','--name-only',f['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization'],text=True).splitlines()
    result_changes(changes,Path(ARTIFACT).read_bytes(),Path(BASELINE).read_bytes(),
                   json.loads((W/'pg2470-chr-a01-native-v1.safe.json').read_bytes()))


def server():
    return prior.server().replace('PG2468','PG2474')


def source():
    return prior.source().replace('pg2468-question-current-native-qualified-v1','pg2474-question-current-native-qualified-v1').replace('PG2468','PG2474')


def entry():
    ns={**prior.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<same-source current native and explicit result join>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
