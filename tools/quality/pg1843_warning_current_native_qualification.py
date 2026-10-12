"""Current Root13 ten native points, qualified against real full PG1755 Main bytes.

Current Unit candidate/test are explicitly not this deployed-source acceptance.
"""
import json
import subprocess
import pg1709_new_source_native_qualification as prior
from pg1446_current_cold_stage import W


def qualify_snapshot():
    full=json.loads((W/'pg1756-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    v=full['result']
    if full['actualExit']!=0 or v['productionSource']!=prior.SOURCE or v['tests']!=3618 or v['changedClasses']!=[]or v['addedClasses']!=[]:raise ValueError('actual current full Main class identity required')
    changed=set(subprocess.check_output(['git','diff','--name-only',v['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization'],text=True).splitlines())
    allowed={'src/deployment/systemd/schubert-nk-morning-controller.service.template','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningServiceUnitTest.java'}
    if changed!=allowed:raise ValueError('only explicit not-deployed Unit candidate and its independent test may differ')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean native operator required')


def source():
    raw=prior.source()
    line="if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only','1683dd9f6de00e71d2317d9af3cd50400a37bf4e','--','src','pom.xml']):raise ValueError('clean same current source operator required')"
    if raw.count(line)!=1:raise ValueError('one actual snapshot gate required')
    raw=raw.replace(line,'qualify_snapshot()')
    for old,new in [('pg1708-new-source-native-catalog-v1','pg1842-warning-inspector-two-point-catalog-v1'),('pg1709-new-source-native-qualified-v1','pg1843-warning-current-native-qualified-v1'),('PG1709','PG1843'),('pg1636-api-boundary-full-qualified-v1','pg1756-boundary-full-qualified-v1')]:
        if old not in raw:raise ValueError('one sameSource readonly transport binding required')
        raw=raw.replace(old,new)
    raw=raw.replace("len(catalog['selected'])!=8","len(catalog['selected'])!=10").replace('8*16777216','10*16777216').replace("'streams':8","'streams':10")
    compile(raw,'<actual full3618 current native transport>','exec');return raw


def server():
    raw=prior.server()
    for old,new in [('PG1709','PG1843'),('PG1633','PG1755'),('qualified1633Tests','qualified1755Tests'),('3596','3618')]:
        if old not in raw:raise ValueError('actual full source native input required')
        raw=raw.replace(old,new)
    raw=raw.replace("len(v['selected'])==8","len(v['selected'])==10").replace("'currentNativeStreams':8","'currentNativeStreams':10")
    marker="modules=['protocol','storage','bootstrap','api','web','batch'];executions=[];jars={}"
    if raw.count(marker)!=1:raise ValueError('one actual vendor session boundary required')
    extra="""inspector=[(point,session)for point,session in zip(v['selected'],sessions,strict=True)if point['unit']=='schubert-nk-inbox-inspector.service']
require(len(inspector)==2 and inspector[0][0]['relative'].endswith('.closing.exec')and inspector[1][0]['relative'].endswith('.terminal.exec'))
closed=inspector[0][1];early=inspector[1][1]
require(closed['sessionIdSha256']==early['sessionIdSha256']and closed['startMs']==early['startMs']and early['dumpMs']<=closed['dumpMs'])
"""
    raw=raw.replace(marker,extra+marker)
    raw=raw.replace("'classByteMismatch':0,","'classByteMismatch':0,'inspectorTwoPointsSameSessionAndOrdered':True,'distinctSessionIdsMeasured':len({s['sessionIdSha256']for s in sessions}),'notDeployedUnitCandidateAccepted':False,")
    compile(raw,'<current ten point CRC/independent sessions/full3618 union>','exec');return raw


def main():
    ns={**prior.prior.prior.prior.prior.prior.__dict__,'CODE':server(),'SOURCE':prior.SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<actual current ten point native qualification>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
