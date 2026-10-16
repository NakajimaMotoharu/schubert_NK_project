"""Host-only all emitted ABI for current4856/candidate7fff; new archive, never VM operation."""
import inspect
import types
import pg3436_current_outbox_candidate_compile as previous
import pg3756_hygiene_unused_sources as role

TARGET=role.W/role.TOOLS
ARCHIVE=previous.old.previous.graph.engine.P/role.ARCHIVE


def compiler():
    raw=role.role_text(previous.compiler())
    for a,b in [('pg3152-frozen-v1','pg3602-frozen-v1'),('pg3150-browser-business-owned-stop-tools-v1','pg3600-current-browser-owned-stop-tools-v1'),('Pg3150','Pg3600')]:raw=raw.replace(a,b)
    marker="current = json.loads((W / 'pg3754-current-4856-before-view-v1/manifest.safe.json').read_bytes())"
    if raw.count(marker)!=1:raise ValueError('exact new data-only view role required')
    raw=raw.replace(marker,"current = json.loads((W / "+repr(str(role.VIEW_LOCAL.relative_to(role.W)))+").read_bytes())['result']")
    compile(raw,'<complete new unused host ABI>','exec');return raw


def validate_actual_graph(target,hashes):
    graph=previous.old.previous.graph;raw=inspect.getsource(graph.validate_actual_graph).replace('pg2132','pg3756').replace('pg2126-manifest-v1.sig','pg3748-manifest-v1.sig');ns={**graph.__dict__,'ARCHIVE':ARCHIVE};exec(compile(raw,'<exact new graph bundle and signature>','exec'),ns);return ns['validate_actual_graph'](target,hashes)


def main():
    role.qualify();graph=previous.old.previous.graph;ns={**graph.engine.__dict__,'__file__':__file__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,'TOOLS':role.TOOLS,'CURRENT':role.CURRENT,'PRODUCTION':role.SOURCE,'BEFORE':role.BEFORE,'sources':role.sources,'validate_actual_graph':validate_actual_graph,'inventory':graph.inventory};ns['write']=types.FunctionType(graph.write.__code__,{**graph.__dict__,'TARGET':TARGET});exec(compile(compiler(),'<new whole host-only compiler entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
