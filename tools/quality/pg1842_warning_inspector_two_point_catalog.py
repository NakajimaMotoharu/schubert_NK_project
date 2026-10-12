"""BUG1180 new-only catalog: ten points, not ten process executions."""
import inspect
import pg1840_warning_inspector_native_catalog as prior

SLOT='pg1842-warning-inspector-two-point-catalog-v1'


def catalog_source(receipt):
    raw=prior.catalog_source(receipt)
    first=raw.index('closing_item=next(');last=raw.index('excluded=[]',first)
    raw=raw[:first]+raw[last:]
    raw=raw.replace("names.append((closing,'schubert-nk-inbox-inspector.service'))","names.extend([(closing,'schubert-nk-inbox-inspector.service'),(earlier,'schubert-nk-inbox-inspector.service')])")
    raw=raw.replace('len(selected)==9','len(selected)==10').replace("for v in selected})==9","for v in selected})==10")
    raw=raw.replace("or relative==earlier:continue",":continue")
    raw=raw.replace("'sameSessionEarlierPointNotImported':[earlier],'sameSessionEarlierPointSameBytes':True,","'inspectorTwoPointsOneProcessPendingQualification':True,")
    compile(raw,'<current ten points with independent bytes>','exec');return raw


def main():
    ns={**prior.engine.__dict__,'SLOT':SLOT,'catalog_source':catalog_source}
    exec(compile(inspect.getsource(prior.previous_main),'<new-only ten point transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
