"""New-only current796->832 same-original pending code-only, with phase-specific guards."""
import ast
from pathlib import Path
import pg799_pending_sources as old
R=Path(__file__).resolve().parent
SOURCE='2a0d5aa392c85a1dc12a1cdb423978e8500895b8'
DIGEST='8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'
OLD_SOURCE=old.SOURCE
OLD_DIGEST=old.DIGEST
BASELINE='d725011754d5a06d8591b16820b9e272aa41116723df8d6946384d6d1bc13652'
def bind(raw):
    return (raw.replace('Pg799','Pg835').replace('PG799','PG835').replace('pg799','pg835')
      .replace('PG796','NEXT_PG832').replace('pg796','NEXT_pg832')
      .replace('PG750','PG796').replace('pg750','pg796')
      .replace('NEXT_PG832','PG832').replace('NEXT_pg832','pg832')
      .replace(old.DIGEST,'NEXT_DIGEST').replace(old.OLD_DIGEST,OLD_DIGEST).replace('NEXT_DIGEST',DIGEST)
      .replace('2797579','3123795'))
def java():
    raw=bind(old.java())
    raw=raw.replace('args[0].equals("'+OLD_SOURCE+'")','args[0].equals("'+SOURCE+'")')
    return raw
def snapshot_library():
    raw=bind(old.snapshot_library())
    raw=raw.replace('pg800-probe-post-v1/after.private.json','pg833-current-before832-v1/after.private.json')
    raw=raw.replace('07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2',BASELINE)
    raw=raw.replace("==544","==554").replace("== 544","== 554")
    raw=raw.replace("return {**value,'capturedSnapshot':value}","return {**value,'capturedSnapshot':{k:value[k]for k in ('rows','trees','configuration')}}")
    raw=raw.replace("PARENT='e4093109ab234700b61dd45711126e4e'", "PARENT='7ea672e8a76c4a4a8a7994652366a4cc'")
    raw=raw.replace("v['ExecMainStartTimestampMonotonic']=='137240785885'", "v['ExecMainStartTimestampMonotonic']=='155954641282'")
    raw=raw.replace('accepted(old,new,show(unit),{})', "accepted(old,new,show(unit),baseline()['units'][unit])")
    raw=raw.replace(repr(OLD_SOURCE),repr(SOURCE))
    ast.parse(raw);return raw
def refs():
    raw=bind(old.refs()).replace("SOURCE='"+OLD_SOURCE+"'","SOURCE='"+SOURCE+"'")
    # Source prefix uses repr without spaces, but any old literal still rejects final join.
    raw=raw.replace(repr(OLD_SOURCE),repr(SOURCE))
    ast.parse(raw);return raw
def before_freeze():
    raw=bind(old.before_freeze());ast.parse(raw);return raw
