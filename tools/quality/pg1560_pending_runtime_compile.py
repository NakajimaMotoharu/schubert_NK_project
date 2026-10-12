"""Freeze SSC270 runtime operator and all generated helper dependencies, VM0."""
import inspect
import pg1555_pending_publication_compile as prior
from pg1559_pending_runtime_sources import CLASS,TOOLS,java,refs,writer,SOURCE,BOM

def main():
    raw=inspect.getsource(prior.main)
    for a,b in [('pg1550-pending-candidate-ro-independent-closing-v1/manifest.safe.json','pg1558-pending-publication-independent-closing-v1/manifest.safe.json'),('pg1555-pending-publication-build-v1','pg1560-pending-runtime-build-v1'),('pg1555-pending-publication-frozen-v1','pg1560-pending-runtime-frozen-v1'),('pg1553_pending_publication_refs.py','pg1559_pending_runtime_refs.py'),('Pg1555PublicationArgumentTest','Pg1560RuntimeArgumentTest'),('pg1553_pending_publication_sources_test.py','pg1559_pending_runtime_test.py')]:
        if a not in raw:raise ValueError('fixed runtime compiler boundary refused')
        raw=raw.replace(a,b)
    raw=raw.replace(".replace('\"prepare-ro\"','\"activate\"')", ".replace('\"prepare-ro\"','\"prepare\"')")
    marker="    release=W/'pg1292-release-v1';"
    if raw.count(marker)!=1:raise ValueError('fixed signed candidate host input required')
    raw=raw.replace(marker,"    write(out/'pg1559_pending_runtime_writer.py',writer().encode())\n    release=W/'pg1544-release-v1';")
    raw=raw.replace("'productionSource':prior['productionSource']", "'productionSource':SOURCE,'helperSource':prior['productionSource']")
    ns={**prior.__dict__,'CLASS':CLASS,'TOOLS':TOOLS,'java':java,'source':refs,'writer':writer,'SOURCE':SOURCE,'BOM':BOM}
    exec(compile(raw,'<new current pending runtime compiler>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
