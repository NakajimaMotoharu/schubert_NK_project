"""New-only v2 all ABI and mandatory exactly-once actual bundle definition audit."""
import hashlib
import inspect
import types
import pg3758_hygiene_unused_compile as previous
import pg3766_hygiene_unused_sources_v2 as role
from bundle_hash_contract import require_bound

TARGET=role.W/role.TOOLS;ARCHIVE=previous.previous.old.previous.graph.engine.P/role.ARCHIVE


def compiler():return role.bind(previous.compiler())


def validate_actual_graph(target,hashes):
    bundle_raw=(target/'bundle.safe.json').read_bytes();expected=hashlib.sha256(bundle_raw).hexdigest()
    for name in ['pg3766_native_refs.py','pg3766_input_preflight.py']:require_bound((target/name).read_text(),expected)
    graph=previous.previous.old.previous.graph;raw=inspect.getsource(graph.validate_actual_graph).replace('pg2132','pg3766').replace('pg2126-manifest-v1.sig','pg3748-manifest-v1.sig');ns={**graph.__dict__,'ARCHIVE':ARCHIVE};exec(compile(raw,'<v2 actual graph and singleton input bundle>','exec'),ns);return ns['validate_actual_graph'](target,hashes)


def main():
    role.qualify();graph=previous.previous.old.previous.graph;ns={**graph.engine.__dict__,'__file__':__file__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'TOOLS':role.TOOLS,'CURRENT':role.CURRENT,'PRODUCTION':role.SOURCE,'BEFORE':role.BEFORE,'sources':role.sources,'validate_actual_graph':validate_actual_graph,'inventory':graph.inventory};ns['write']=types.FunctionType(graph.write.__code__,{**graph.__dict__,'TARGET':TARGET});exec(compile(compiler(),'<v2 new-only whole host ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
