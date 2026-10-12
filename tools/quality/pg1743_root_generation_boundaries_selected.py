"""Fresh current generation8 after target-phase kernel/budget boundaries."""
import inspect
import pg1741_root_generation_selected as prior

SLOT='pg1743-root-generation-boundaries-selected-v1'

def server():
    raw=prior.server().replace('PG1741','PG1743').replace('Pg1741RootGenerationLauncher','Pg1743RootGenerationBoundaryLauncher')
    for a,b in [('tests4','tests8'),("=='4'","=='8'"),('==4)','==8)'),("'tests':4","'tests':8")]:raw=raw.replace(a,b)
    compile(raw,'<current generation8 boundary server>','exec');return raw

def main():
    raw=inspect.getsource(prior.main).replace('PG1741','PG1743').replace('pg1741','pg1743')
    files=[s.replace('Pg1741RootGenerationLauncher','Pg1743RootGenerationBoundaryLauncher')for s in prior.FILES]
    ns={**prior.__dict__,'FILES':files,'SLOT':SLOT,'server':server}
    exec(compile(raw,'<new-only generation8 transport>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
