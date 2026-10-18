"""Current all1650 CRC/session join, independent dominance of both native pairs."""
import ast
import pg5072_current_native_qualified as previous
from pg4832_new_current_bootstrap_native import PAIR
import pg5110_corrected_bootstrap_catalog as catalog

SOURCE = previous.SOURCE
SLOT = 'pg5112-corrected-bootstrap-native-v1'


def server():
    tree = ast.parse(previous.server().replace('PG5072', 'PG5112'))
    counts = [n for n in ast.walk(tree) if isinstance(n, ast.Compare)
              and ast.unparse(n.left) == "len(v['selected'])"]
    if len(counts) != 1 or ast.unparse(counts[0]) != "len(v['selected']) == 10":
        raise ValueError('one actual10point admission')
    counts[0].comparators = [ast.Constant(12)]
    markers = [i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign)
               and ast.unparse(n) == 'streams = [p for i, p in enumerate(streams) if i != early_index]']
    if len(markers) != 1 or ast.unparse(tree.body[markers[0]+1]) != 'require(len(streams) == 9)':
        raise ValueError('one existing inspector-only latestpoint boundary')
    at = markers[0]
    tree.body[at:at+2] = ast.parse(PAIR).body
    result = next(n.value for n in tree.body if isinstance(n,ast.Assign)
                  and any(isinstance(t,ast.Name)and t.id=='result'for t in n.targets))
    for key, value in zip(result.keys,result.values,strict=True):
        if isinstance(key,ast.Constant)and key.value in {'currentNativeStreams','validatedNativePoints'}:
            value.value = 10 if key.value=='currentNativeStreams'else 12
    for key in ('bootstrapLatestClosingOnly','bootstrapProbeMonotonic','bootstrapCapturedNormal20Qualified'):
        result.keys.append(ast.Constant(key));result.values.append(ast.Constant(True))
    return ast.unparse(ast.fix_missing_locations(tree))+'\n'


def source():
    raw=previous.source()
    for old,new in [(previous.catalog.SLOT,catalog.SLOT),(previous.SLOT,SLOT),('PG5072','PG5112')]:
        raw=raw.replace(old,new)
    marker="catalog=json.loads((W/"+repr(catalog.SLOT+'/manifest.safe.json')+").read_bytes())"
    if raw.count(marker)!=1:raise ValueError('one actual newcatalog boundary')
    raw=raw.replace(marker,marker+"['result']",1)
    return raw.replace("len(catalog['selected'])!=10","len(catalog['selected'])!=12").replace('require_bytes=10*16777216','require_bytes=12*16777216').replace("'streams':9,'validatedPoints':10","'streams':10,'validatedPoints':12")


def main():
    outer=previous.json.loads((previous.W/catalog.SLOT/'manifest.safe.json').read_bytes())
    if not(type(outer['actualExit'])is int and outer['actualExit']==0 and outer['source']==SOURCE):
        raise ValueError('actual current normal20 catalog first')
    template=previous.previous.previous
    ns={**template.transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':previous.qualify_snapshot}
    exec(compile(source(),'<current3791/553/1650 two-pair native>','exec'),ns)
    with template.management_gate(previous.P/'current-management-critical.lock'):
        return ns['main']()


if __name__=='__main__':raise SystemExit(main())
