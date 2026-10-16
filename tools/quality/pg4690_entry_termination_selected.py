"""SSC299 same-body exit-request ports and genuine Java25 CLI, no privileged VM action."""
import subprocess
import pg4684_external_entry_rejection_selected as previous

BASE=previous.BASE
WORK=BASE.ROOT.parent/'pgpt-runs/PG379/pg4690-entry-termination-selected-v1'
MODULES={**previous.MODULES,**{'dev.codex.schubert.nk.batch.file.'+n:'batch'for n in ['MainTerminationPortTest','MorningProcessMainTest','MorningCompletedMainTest','RootServiceLauncherTest','CleanupProcessMainTest']}}


def source():
    raw=previous.source()
    old="if set(main_entries)!=set(MAINS)or any(v.get('METHOD',{}).get('missed')!=0 for v in main_entries.values()):reasons.append('each real main must be observed in the same run')"
    new="if set(main_entries)!=set(MAINS)or any(any(v.get(k,{'missed':0})['missed']!=0 for k in ['LINE','METHOD','BRANCH'])for v in main_entries.values()):reasons.append('all three same-body main conditions must be covered')"
    if raw.count(old)!=1:raise ValueError('one actual strict main gate')
    return raw.replace(old,new).replace("'sourceRole': 'test-only fixed snapshot; deployed Main964e unchanged/ordinary stopped'","'sourceRole': 'unaccepted SSC299 candidate; deployed Main964e unchanged/ordinary stopped'")


def main():
    previous.previous.previous.previous.validate_selection(MODULES,BASE.ROOT)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed SSC299 candidate snapshot first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(BASE),'SOURCE':head,'WORK':WORK,'TESTS':list(MODULES),'MODULES':MODULES,'MAINS':previous.MAINS}
    exec(compile(source(),'<SSC299 native binding/control-flow port qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
