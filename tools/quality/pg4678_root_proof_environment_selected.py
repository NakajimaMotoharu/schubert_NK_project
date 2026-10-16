"""Related root correlation/exec environment tests, exact projects and method conditions."""
import subprocess
import pg4674_root_identity_complete_selection as previous

WORK=previous.previous.template.ROOT.parent/'pgpt-runs/PG379/pg4678-root-proof-environment-selected-v1'
MODULES={**previous.previous.MODULES,**{'dev.codex.schubert.nk.batch.file.'+n:'batch'for n in ['RootServiceProofTest','RootServiceEnvironmentTest']}}


def source():
    raw=previous.source().replace('dev/codex/schubert/nk/batch/file/RootStartupPending','dev/codex/schubert/nk/batch/file/RootServiceLauncher')
    marker="methods=[m for m in entry.findall('method')if m.get('name')=='verifySelf']"
    replacement="methods=[m for m in entry.findall('method')if m.get('name')in {'proof','environment'}]"
    if raw.count(marker)!=1:raise ValueError('one qualified method selection')
    raw=raw.replace(marker,replacement)
    raw=raw.replace("if len(methods)!=1:reasons.append('one target method required')","if len(methods)!=2:reasons.append('two exact target methods required')")
    raw=raw.replace("else:method_counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in methods[0].findall('counter')}","else:method_counters={m.get('name'):{c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in m.findall('counter')}for m in methods}")
    marker="if not method_counters or any(method_counters.get(k,{}).get('missed')!=0 for k in ['LINE','METHOD','BRANCH']):reasons.append('target identity conditions incomplete')"
    replacement="if set(method_counters)!={'proof','environment'}or any(any(v.get(k,{}).get('missed')!=0 for k in ['LINE','METHOD'])or v.get('BRANCH',{'missed':0})['missed']!=0 for v in method_counters.values()):reasons.append('target proof/environment conditions incomplete')"
    if raw.count(marker)!=1:raise ValueError('one exact method qualification')
    return raw.replace(marker,replacement)


def main():
    base=previous.previous.template
    previous.previous.validate_selection(MODULES,base.ROOT)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed proof/environment snapshot first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(base),'SOURCE':head,'WORK':WORK,'TESTS':list(MODULES),'MODULES':MODULES}
    exec(compile(source(),'<independent proof and environment selected run>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
