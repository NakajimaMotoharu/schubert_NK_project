"""Latest two Root host boundaries; immutable current Main, fresh outputs, no prior PT addition."""
import inspect
import pg2220_root_uid_host_selected as prior

FILES=[p.replace('Pg2220RootUidLauncher.java','Pg2222RootHostLauncher.java')for p in prior.FILES]


def server():
    raw=prior.SERVER.replace('PG2220','PG2222').replace('Pg2220RootUidLauncher','Pg2222RootHostLauncher')
    raw=raw.replace('tests1 failures0','tests2 failures0').replace("'tests':'1'","'tests':'2'").replace("len(x.findall('testcase'))==1","len(x.findall('testcase'))==2").replace("'tests':1","'tests':2")
    from pyflakes.api import check
    if check('INPUT={}\n'+raw,'<actual current two Root host tests>'):raise ValueError('whole source required')
    compile(raw,'<latest two Root host tests>','exec');return raw


def main():
    # The actual transport's literal paths are bound as well as its globals.
    raw=inspect.getsource(prior.main).replace('PG2220','PG2222').replace('pg2220','pg2222')
    ns={**prior.__dict__,'FILES':FILES,'SLOT':'pg2222-root-host-selected-v1','SERVER':server()}
    exec(compile(raw,'<latest current Root selection transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
