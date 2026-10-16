"""Only new825e streams/all1646 CRC joined to genuine3739/549 host input."""
import inspect
import json
import subprocess
from pyflakes.api import check
import pg3532_outbox_current_native_qualified as template
import pg2908_network_current_native_qualification as transport
import pg4780_new_current_native_catalog as catalog
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

SOURCE=catalog.role.SOURCE
FULL='pg4696-ssc299-whole-qualified-v1'
SLOT='pg4782-new-current-native-qualified-v1'


def qualify(value):
    q=value.get('result',{})
    expected={'actualExit':0,'productionSource':SOURCE,'tests':3739,'suites':549,'mainClasses':1646,'FESFlakyNotRun':0,'staticSixModules':0}
    if not(type(value.get('actualExit'))is int and value['actualExit']==0)or any(type(q.get(k))is not type(v)or q[k]!=v for k,v in expected.items()):raise ValueError('exact actual3739/549/all1646 whole first')
    if not(q.get('allOriginalCaseIdentitiesRetained')is True and len(q.get('allPhysicalMainSha256',{}))==1646 and len(q.get('changedClasses',[]))==8 and q.get('oldNativeImported')is False):raise ValueError('whole physical1646/eight registered deltas/oldnative0')
    if not(sum(c['action']=='MODIFIED'for c in q['changedClasses'])==6 and sum(c['action']=='ADDED_INTERNAL_INTERFACE'for c in q['changedClasses'])==2):raise ValueError('exact six byte changes/two declaration additions')
    return q


def qualify_snapshot():
    q=qualify(json.loads((W/FULL/'manifest.safe.json').read_bytes()))
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff',q['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('clean identical qualified Main/Test/settings')
    catalog.role.admission.authenticate_host()


def server():
    raw=template.server()
    for old,new in [('PG3532-native-input-v3.tar','PG4782-native-input-v1.tar'),('PG3532-native-v3','PG4782-native-v1'),('PG3412','PG4694'),('qualified3412Tests','qualified4694Tests'),('3712','3739'),(template.SOURCE,SOURCE)]:raw=raw.replace(old,new)
    coordinates=transport.prior.previous.entry().__globals__['coordinates']
    complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(coordinates)+'\n'+raw
    if check(complete,'<all1646 new current native server>'):raise ValueError('whole emitted server static0')
    compile(raw,'<current native CRC/session and union>','exec');return raw


def source():
    raw=transport.source()
    for old,new in [('pg2906-network-current-native-catalog-v1',catalog.SLOT),('pg2908-network-current-native-qualified-v2',SLOT),('pg2800-jdbc-null-fixed-full-qualified-v1',FULL),('PG2908-native-v2','PG4782-native-v1'),('PG2908-native-input-v2.tar','PG4782-native-input-v1.tar'),('PG2908','PG4782')]:raw=raw.replace(old,new)
    marker="    code,status=copy(str(archive),'/home/mini/schubert-nk-pgpt/transfer/PG4782-native-input-v1.tar',timeout=120)"
    guard="    code,status=run('test ! -e /home/mini/schubert-nk-pgpt/transfer/PG4782-native-input-v1.tar && test ! -e /home/mini/schubert-nk-pgpt/runs/PG4782-native-v1',timeout=30)\n    if code:raise ValueError('new-only native; recover existing result, no replay')\n"
    if raw.count(marker)!=1:raise ValueError('one archive transfer boundary')
    return raw.replace(marker,guard+marker,1)


def main():
    ns={**transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<same3739 actual native transport>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
