"""New immutable v4 input closure and Werror compiler, old failed slots untouched."""
import pg1642_completed_candidate_compile as engine
import pg1645_completed_candidate_compile_v2 as nested
import pg1660_completed_candidate_compile_v3 as previous
from pg1681_closed_candidate_sources import sources, TOOLS
from pg1681_input_closure_contract import validate_graph

TARGET=engine.W/TOOLS
ARCHIVE=engine.P/'pg1683-release-v4.tar'


def write(path,raw):
    if path.is_relative_to(TARGET):
        nested.canonical_relative(str(path.relative_to(TARGET)))
        path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    engine.write(path,raw)


def compiler():
    raw=previous.compiler().replace('pg1660-','pg1682-').replace('pg1658-owned-recovery-independent-post-v1/manifest.safe.json','pg1675-remaining-owner-full-post-v1/manifest.safe.json')
    marker="    data = json.loads((release / 'RELEASE-MANIFEST.json').read_bytes())"
    if raw.count(marker)!=1:raise ValueError('one new input freeze required')
    raw=raw.replace(marker,'    ARCHIVE.chmod(0o400)\n'+marker)
    marker="    generated['pg1640_native_refs.py'] = 'BUNDLE_HASH=' + repr(hashlib.sha256(bundle).hexdigest()) + '\\n' + generated['pg1640_native_refs.py']"
    if raw.count(marker)!=1:raise ValueError('one bundle source boundary required')
    raw=raw.replace(marker,"    for name in ['pg1640_native_refs.py','pg1681_input_preflight.py']:\n        generated[name]='BUNDLE_HASH='+repr(hashlib.sha256(bundle).hexdigest())+'\\n'+generated[name]")
    raw=raw.replace("'Pg1660CurrentIdentityTest.java']","'Pg1660CurrentIdentityTest.java','Pg1681InputBoundaryTest.java']")
    raw=raw.replace("('identity','Pg1660CurrentIdentityTest')","('identity','Pg1660CurrentIdentityTest'),('input','Pg1681InputBoundaryTest')")
    marker='    hashes = inventory(TARGET)'
    if raw.count(marker)!=1:raise ValueError('one completed frozen closure inventory required')
    raw=raw.replace(marker,marker+"\n    validate_graph(hashes,{n:(TARGET/n).read_text()for n in hashes if n.endswith('.py')},ARCHIVE.name,{'pg1683-release-v4.tar','pg1638-manifest-v1.sig','bundle.safe.json'})")
    compile(raw,'<new v4 complete input compiler>','exec')
    return raw


def main():
    ns={**engine.__dict__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'write':write,'sources':sources,'inventory':nested.inventory,'canonical_relative':nested.canonical_relative,'validate_graph':validate_graph}
    exec(compiler(),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
