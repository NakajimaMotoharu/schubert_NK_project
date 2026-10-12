"""New-only static-clean verifier, same immutable1532 campaign; no Maven repeat."""
import inspect
import pg1533_filesystem_full_qualification as prior
from pg1541_filesystem_full_qualification_v2 import server_source

def main():
    raw=inspect.getsource(prior.main).replace('pg1533-filesystem-full-qualified-v1','pg1542-filesystem-full-qualified-v3')
    ns={**prior.__dict__,'CODE':server_source()}
    exec(compile(raw,'<static-clean new-only whole source qualification>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
