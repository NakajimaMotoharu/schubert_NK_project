"""Current ten points/latest nine against all1644 exact Main and actual3721 host bytes."""
import inspect
import json
import subprocess
from pyflakes.api import check
import pg3532_outbox_current_native_qualified as template
import pg2908_network_current_native_qualification as transport
import pg4660_current_native_catalog as catalog
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

SOURCE=catalog.role.SOURCE
FULL='pg4428-shared-manager-whole-qualified-v1'
SLOT='pg4662-current-native-qualified-v1'


def qualify(value):
    q=value.get('result',{})
    expected={'actualExit':0,'productionSource':SOURCE,'tests':3721,'suites':545,'mainClasses':1644,'FESFlakyNotRun':0,'staticSixModules':0}
    if type(value.get('actualExit'))is not int or value['actualExit']!=0 or any(type(q.get(k))is not type(v)or q[k]!=v for k,v in expected.items()):raise ValueError('exact actual3721/545/all1644 independent input first')
    if not(q.get('allOriginalCaseIdentitiesRetained')is True and len(q.get('allPhysicalMainSha256',{}))==1644 and len(q.get('changedClasses',[]))==14 and q.get('oldNativeImported')is False):raise ValueError('all physical Main/current fourteen differences/oldnative0 first')
    return q


def qualify_snapshot():
    q=qualify(json.loads((W/FULL/'manifest.safe.json').read_bytes()))
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff',q['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('clean identical Main/Test/settings first')
    catalog.role.admission.authenticate_host()


def server():
    raw=template.server()
    for old,new in [('PG3532-native-input-v3.tar','PG4662-native-input-v1.tar'),('PG3532-native-v3','PG4662-native-v1'),('PG3412','PG4420'),('qualified3412Tests','qualified4420Tests'),('3712','3721'),(template.SOURCE,SOURCE)]:raw=raw.replace(old,new)
    # The full jar/exec/XML hashes and every class CRC are checked by the existing
    # independent Java readers. No native from older releases is an input.
    coordinates=transport.prior.previous.entry().__globals__['coordinates']
    complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(coordinates)+'\n'+raw
    if check(complete,'<actual all1644 current native server>'):raise ValueError('whole emitted server static0')
    return raw


def source():
    raw=transport.source()
    for old,new in [('pg2906-network-current-native-catalog-v1',catalog.SLOT),('pg2908-network-current-native-qualified-v2',SLOT),('pg2800-jdbc-null-fixed-full-qualified-v1',FULL),('PG2908-native-v2','PG4662-native-v1'),('PG2908-native-input-v2.tar','PG4662-native-input-v1.tar'),('PG2908','PG4662')]:raw=raw.replace(old,new)
    before="    code,status=copy(str(archive),'/home/mini/schubert-nk-pgpt/transfer/PG4662-native-input-v1.tar',timeout=120)"
    guard="    code,status=run('test ! -e /home/mini/schubert-nk-pgpt/transfer/PG4662-native-input-v1.tar && test ! -e /home/mini/schubert-nk-pgpt/runs/PG4662-native-v1',timeout=30)\n    if code:raise ValueError('new-only native server artifacts; recover original instead of replay')\n"
    if raw.count(before)!=1:raise ValueError('one new-only archive transfer boundary')
    return raw.replace(before,guard+before)


def main():
    values={**transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<actual current3721 native transport>','exec'),values)
    with management_gate(P/'current-management-critical.lock'):return values['main']()


if __name__=='__main__':raise SystemExit(main())
