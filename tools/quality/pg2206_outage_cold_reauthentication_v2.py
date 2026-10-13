"""BUG1217/YKT984: preserve existing cold Root0700 empty maintenance only."""
import types
import pg2204_outage_cold_reauthentication as prior

SLOT='pg2206-outage-cold-reauthentication-v2'


def maintenance_shape(m,names,attrs,filesystem):
    return (type(m)is list and len(m)==9 and m[2:7]==[0,0,0o40700,2,40]
            and type(names)is list and names==[] and type(attrs)is list and attrs==[]
            and filesystem=='tmpfs')


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT)
    old="for name in ['startup','pt-coverage','backup-request','cleanup-request','expiry-request','maintenance']:"
    if raw.count(old)!=1:raise ValueError('one exact cold namespace boundary required')
    raw=raw.replace(old,old.replace(",'maintenance'",''))
    import inspect
    raw=inspect.getsource(maintenance_shape)+'\n'+raw
    marker=" return {'boot':boot,'source':SOURCE"
    if raw.count(marker)!=1:raise ValueError('one whole cold snapshot return required')
    extra=""" maintenance=pathlib.Path('/run/schubert-nk/maintenance');m=metadata(maintenance)
 require(maintenance_shape(m,os.listdir(maintenance),os.listxattr(maintenance),command(['stat','-f','-c','%T',str(maintenance)],4096).decode().strip()))
 require(m==metadata(maintenance))
"""
    raw=raw.replace(marker,extra+marker).replace("'unitFiles':unitfiles}","'unitFiles':unitfiles,'maintenance':m}")
    from pyflakes.api import check
    if check(raw,'<whole corrected cold reauthentication>'):raise ValueError('whole namespace required')
    compile(raw,'<new cold proof with existing maintenance>','exec');return raw


def main():
    fn=types.FunctionType(prior.main.__code__,{**prior.__dict__,'SLOT':SLOT,'payload':payload})
    return fn()


if __name__=='__main__':raise SystemExit(main())
