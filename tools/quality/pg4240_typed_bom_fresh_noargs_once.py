"""BUG1346 explicit Path/bytes/digest boundary in a new-only entry; unchanged live observer."""
import inspect
import pg4234_canonical_fresh_noargs_once as canonical
import pg4222_fresh_current_noargs_once as host
from pg4060_original_profile_dual_stack import once

SLOT='pg4240-typed-bom-fresh-noargs-once-v1'


def payload(hashes):
    raw=canonical.payload(hashes).replace(canonical.SLOT,SLOT)
    raw=once(raw,"'manifestSha256':hashlib.sha256(manifest).hexdigest()","'manifestSha256':sha")
    raw=once(raw,"persist('external-start-guard.private.json',","require(manifest.read_bytes()==raw and hashlib.sha256(raw).hexdigest()==sha)\n persist('external-start-guard.private.json',")
    return raw


def main():
    ns={**vars(host),'SLOT':SLOT,'payload':payload}
    raw=inspect.getsource(host.main).replace('pg4230-final-fresh-observer-qualification-v1','pg4242-typed-bom-fresh-qualification-v1')
    exec(compile(raw,'<typed BOM full host entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
