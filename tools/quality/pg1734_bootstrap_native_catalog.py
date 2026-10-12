"""BUG1158 new-only native reader: metadata9 excludes observer atime."""
import inspect
import pg1732_bootstrap_native_catalog as prior

SLOT='pg1734-current-bootstrap-native-catalog-v1'

def main():
    raw=inspect.getsource(prior.main)
    old='raw=p.read_bytes();assert p.lstat()==s and'
    new='def metadata9(v):return(v.st_dev,v.st_ino,v.st_uid,v.st_gid,v.st_mode,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)\nraw=p.read_bytes();assert metadata9(p.lstat())==metadata9(s) and'
    if raw.count(old)!=1:raise ValueError('one readonly metadata guard required')
    raw=raw.replace(old,new)
    ns={**prior.__dict__,'SLOT':SLOT}
    exec(compile(raw,'<new-only native reader9 attributes>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
