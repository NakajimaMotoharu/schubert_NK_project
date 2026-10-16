"""Exact planned eight suites: real project set equals the declared six-module set."""
import subprocess
import pg4670_root_identity_reactor_selection as previous

WORK=previous.template.ROOT.parent/'pgpt-runs/PG379/pg4674-root-self-identity-selected-v1'
PROJECTS='src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch'


def source():
    raw=previous.source()
    marker="'-pl', 'src/schubert-nk-batch', '-am'"
    if raw.count(marker)!=1:raise ValueError('one actual reactor project boundary')
    if {p.removeprefix('src/schubert-nk-')for p in PROJECTS.split(',')}!=set(previous.MODULES.values()):raise ValueError('actual projects must equal expected modules')
    return raw.replace(marker,"'-pl', "+repr(PROJECTS)+", '-am'",1)


def main():
    previous.validate_selection(previous.MODULES,previous.template.ROOT)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed complete selection')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    ns={**vars(previous.template),'SOURCE':head,'WORK':WORK,'TESTS':list(previous.MODULES),'MODULES':previous.MODULES}
    exec(compile(source(),'<same eight suites actual all-six projects>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
