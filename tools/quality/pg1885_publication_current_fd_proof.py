"""New-only current FD oracle; old1884 rejection and actual retained owner unchanged."""
import ast
import inspect
import pg1884_publication_current_pair_proof as prior

SLOT='pg1885-publication-current-fd-proof-v1'


def payload():
    tree=ast.parse(prior.payload())
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='fd_relation')
    class CurrentFd(ast.NodeTransformer):
        def visit_Constant(self,node):
            value={'30':'88','33':'91','34':'92','43':'101'}.get(node.value,node.value)if type(node.value)is str else node.value
            return ast.copy_location(ast.Constant(value),node)
    CurrentFd().visit(function);ast.fix_missing_locations(tree)
    raw=ast.unparse(tree)+'\n'
    return raw.replace(prior.SLOT,SLOT)


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(prior.main),'<actual new current fd proof transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
