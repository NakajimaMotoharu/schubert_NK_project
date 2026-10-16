"""Required fresh whole for SSC299 entry shape, preserving all original strict gates."""
import ast
import inspect
import pg4420_shared_manager_full as previous

SOURCE='825e463334c43a5bc96f50db964df22e11758d1b'
LABEL='PG4694'
ROOT,W=previous.ROOT,previous.W


def server_source(head,digest):
    ns={**vars(previous),'SOURCE':SOURCE,'LABEL':LABEL}
    exec(compile(inspect.getsource(previous.server_source),'<new fixed whole factory>','exec'),ns)
    raw=ns['server_source'](head,digest)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in {3721,545,1644}:return ast.copy_location(ast.Constant({3721:3739,545:549,1644:1646}[node.value]),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    raw=inspect.getsource(previous.main).replace('pg4420','pg4694').replace('shared-manager','ssc299')
    raw=raw.replace("'tests': 3721, 'suites': 545, 'mainClasses': 1644","'tests': 3739, 'suites': 549, 'mainClasses': 1646")
    raw=raw.replace('SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved','SSC299 three entry termination ports change Main bytes; selected4690 actual78PT/16suite/main conditions0; old964e native not portable; old4684 qualification1 preserved')
    ns={**vars(previous),'SOURCE':SOURCE,'LABEL':LABEL,'server_source':server_source}
    exec(compile(raw,'<one required SSC299 fresh whole>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
