"""Readonly current graph inventory; no old boot directory shape is assumed."""
import inspect
import pg1972_current_resume_input_preflight as prior

SLOT='pg1974-current-resume-input-inventory-v1'


def payload():
    raw=prior.PAYLOAD.replace('import hashlib,json,pathlib,stat','import hashlib,json,os,pathlib,stat')
    start=raw.index("assert set(before['runtime'])");end=raw.index('base_unit=',start)
    raw=raw[:start]+"""assert set(before['runtime'])in[{str(runtime)},{str(runtime),str(unitdir)}]
for name,value in before['runtime'].items():
 p=pathlib.Path(name);assert metadata(p)==value['metadata']and metadata(p)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(p)
assert not unitdir.exists()or not list(unitdir.iterdir())
assert {str(p)for p in runtime.iterdir()}==set(before['runtime'])-{str(runtime)}
"""+raw[end:]
    raw=raw.replace("'runtimeEmptyOwnedDirectoryVerified':True,'runtimeDirectoryMetadata':metadata(unitdir)","'runtimeGraphVerified':True,'runtimeUnitDirectoryPresent':unitdir.exists(),'runtimeMetadata':{name:metadata(pathlib.Path(name))for name in before['runtime']}")
    from pyflakes.api import check
    if check(raw,'<actual current resume inventory>'):raise ValueError('all actual payload globals required')
    compile(raw,'<current readonly input graph>','exec');return raw


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'PAYLOAD':payload()}
    exec(compile(inspect.getsource(prior.main),'<current readonly input inventory entry>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
