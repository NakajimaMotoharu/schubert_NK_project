"""Exact related scope plus actual public entry methods; privileged paths remain unaccepted."""
import subprocess
import pg4678_root_proof_environment_selected as previous

BASE=previous.previous.previous.template
WORK=BASE.ROOT.parent/'pgpt-runs/PG379/pg4684-external-entry-rejection-selected-v1'
MODULES={**previous.MODULES,'dev.codex.schubert.nk.batch.file.ExternalEntryRejectionTest':'batch'}
MAINS=['RootServiceLauncher','MorningProcessMain','CleanupProcessMain']


def source():
    raw=previous.source()
    raw=raw.replace('method_counters = {}','method_counters = {}; main_entries = {}',1)
    marker="    if actual != expected: reasons.append('selected identity inventory differs')"
    extra="""    tree=ET.parse(snapshot/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    for name in MAINS:
        entries=[c for c in tree.findall('package/class')if c.get('name')=='dev/codex/schubert/nk/batch/file/'+name]
        methods=[m for e in entries for m in e.findall('method')if m.get('name')=='main'and m.get('desc')=='([Ljava/lang/String;)V']
        if len(entries)!=1 or len(methods)!=1:reasons.append('one actual public entry method required')
        else:main_entries[name]={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in methods[0].findall('counter')}
    if set(main_entries)!=set(MAINS)or any(v.get('METHOD',{}).get('missed')!=0 for v in main_entries.values()):reasons.append('each real main must be observed in the same run')
"""
    if raw.count(marker)!=1:raise ValueError('one actual inventory boundary')
    raw=raw.replace(marker,extra+marker)
    return raw.replace("'targetMethodCoverage':method_counters,","'targetMethodCoverage':method_counters, 'entryMainCoverage':main_entries,")


def main():
    previous.previous.previous.validate_selection(MODULES,BASE.ROOT)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed entry-contract snapshot first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(BASE),'SOURCE':head,'WORK':WORK,'TESTS':list(MODULES),'MODULES':MODULES,'MAINS':MAINS}
    exec(compile(source(),'<actual owned host child entry contracts>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
