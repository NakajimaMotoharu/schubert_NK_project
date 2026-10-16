"""Same1646 CRC and two same-session point dominances, no source/host regression replay."""
import inspect
import json
from pyflakes.api import check
import pg4782_new_current_native_qualified as previous
import pg4830_new_current_bootstrap_catalog as catalog
from pg1674_critical_management_gate import management_gate

SOURCE=previous.SOURCE
SLOT='pg4832-new-current-bootstrap-native-v1'

PAIR=r'''
bootstrap=[(i,point,session)for i,(point,session)in enumerate(zip(v['selected'],sessions,strict=True))if point['unit']=='schubert-nk-bootstrap-admin.service']
require(len(bootstrap)==2 and bootstrap[0][1]['relative'].endswith('.closing.exec')and bootstrap[1][1]['relative'].endswith('.terminal.exec'))
bootstrap_close_index,bootstrap_closed_point,bootstrap_closed=bootstrap[0]
bootstrap_early_index,bootstrap_early_point,bootstrap_early=bootstrap[1]
require(bootstrap_closed['sessionIdSha256']==bootstrap_early['sessionIdSha256']and bootstrap_closed['startMs']==bootstrap_early['startMs']and bootstrap_closed['dumpMs']>=bootstrap_early['dumpMs'])
check_bootstrap=subprocess.run([str(J/'java'),'-cp',cp,'NativePointDominance',str(streams[bootstrap_early_index]),str(streams[bootstrap_close_index])],capture_output=True,timeout=30)
require(check_bootstrap.returncode==0 and not check_bootstrap.stderr and check_bootstrap.stdout==b'sameSessionProbeMonotonic=true;latestClosingOnly=true\n')
(O/'bootstrap-point-dominance.private.log').write_bytes(check_bootstrap.stdout)
streams=[p for i,p in enumerate(streams)if i not in {early_index,bootstrap_early_index}];require(len(streams)==10)
'''


def server():
    raw=previous.server().replace('PG4782','PG4832')
    raw=raw.replace("len(v['selected'])==10","len(v['selected'])==12")
    marker="streams=[p for i,p in enumerate(streams)if i!=early_index];require(len(streams)==9)"
    if raw.count(marker)!=1:raise ValueError('one original inspector-only dominance boundary')
    raw=raw.replace(marker,PAIR)
    raw=raw.replace("'currentNativeStreams':9,'validatedNativePoints':10", "'currentNativeStreams':10,'validatedNativePoints':12,'bootstrapLatestClosingOnly':True,'bootstrapProbeMonotonic':True")
    coordinates=previous.transport.prior.previous.entry().__globals__['coordinates']
    complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(coordinates)+'\n'+raw
    if check(complete,'<same1646 two dominance native server>'):raise ValueError('complete assembled static0')
    compile(raw,'<current inspector and Bootstrap pair CRC/session qualification>','exec');return raw


def source():
    raw=previous.source().replace('pg4780-new-current-native-catalog-v1',catalog.SLOT).replace(previous.SLOT,SLOT).replace('PG4782','PG4832')
    marker="catalog=json.loads((W/"+repr(catalog.SLOT+'/manifest.safe.json')+").read_bytes())"
    if raw.count(marker)!=1:raise ValueError('one catalog loading boundary')
    raw=raw.replace(marker,marker+"['result']")
    raw=raw.replace("len(catalog['selected'])!=10","len(catalog['selected'])!=12")
    raw=raw.replace('require_bytes=10*16777216','require_bytes=12*16777216')
    raw=raw.replace("'streams':9,'validatedPoints':10","'streams':10,'validatedPoints':12")
    return raw


def main():
    # Read only new catalog; existing completed4782 files and actual3739/549 stay fixed.
    value=json.loads((previous.W/catalog.SLOT/'manifest.safe.json').read_bytes())
    if value['actualExit']!=0 or value['source']!=SOURCE:raise ValueError('actual new catalog first')
    ns={**previous.transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':previous.qualify_snapshot}
    exec(compile(source(),'<new-only actual Bootstrap native transport>','exec'),ns)
    with management_gate(previous.P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
