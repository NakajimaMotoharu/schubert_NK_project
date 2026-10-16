"""Affected93 tool qualification, typed BOM entry only. Existing observer is not restarted."""
import inspect
import pg4236_canonical_fresh_qualification as previous
import pg4240_typed_bom_fresh_noargs_once as entry


def main():
    ns={**vars(previous),'entry':entry}
    raw=inspect.getsource(previous.main).replace('pg4236-canonical-fresh-qualification-v1','pg4242-typed-bom-fresh-qualification-v1')
    old="'pg4234_canonical_fresh_noargs_once_test']"
    if raw.count(old)!=1:raise ValueError('one complete affected test inventory')
    raw=raw.replace(old,"'pg4234_canonical_fresh_noargs_once_test','pg4240_typed_bom_fresh_noargs_once_test']")
    raw=raw.replace("'pg423*.py'","'pg423*.py','pg424*.py'")
    exec(compile(raw,'<all affected93 and typed entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
