"""Same04bb all1647 CRC/session with independent inspector and Bootstrap dominance."""
import pg4926_current_native_qualified as previous
import pg4832_new_current_bootstrap_native as template
import pg4940_current_bootstrap_catalog as catalog

SOURCE=previous.SOURCE
SLOT='pg4942-current-bootstrap-native-v1'


def server():
    raw=previous.server().replace('PG4926','PG4942')
    raw=raw.replace("len(v['selected'])==10","len(v['selected'])==12")
    marker="streams=[p for i,p in enumerate(streams)if i!=early_index];require(len(streams)==9)"
    if raw.count(marker)!=1:raise ValueError('one exact inspector-only dominance boundary')
    raw=raw.replace(marker,template.PAIR)
    return raw.replace("'currentNativeStreams':9,'validatedNativePoints':10", "'currentNativeStreams':10,'validatedNativePoints':12,'bootstrapLatestClosingOnly':True,'bootstrapProbeMonotonic':True")


def source():
    raw=previous.source().replace(previous.catalog.SLOT,catalog.SLOT).replace(previous.SLOT,SLOT).replace('PG4926','PG4942')
    marker="catalog=json.loads((W/"+repr(catalog.SLOT+'/manifest.safe.json')+").read_bytes())"
    if raw.count(marker)!=1:raise ValueError('one new actual catalog load')
    raw=raw.replace(marker,marker+"['result']")
    return raw.replace("len(catalog['selected'])!=10","len(catalog['selected'])!=12").replace('require_bytes=10*16777216','require_bytes=12*16777216').replace("'streams':9,'validatedPoints':10","'streams':10,'validatedPoints':12")


def main():
    value=previous.json.loads((previous.W/catalog.SLOT/'manifest.safe.json').read_bytes())
    if not(type(value['actualExit'])is int and value['actualExit']==0 and value['source']==SOURCE):raise ValueError('actual current captured20 catalog first')
    ns={**previous.previous.transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':previous.qualify_snapshot}
    exec(compile(source(),'<same current3761/551/1647 two-pair native>','exec'),ns)
    with previous.previous.management_gate(previous.P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
