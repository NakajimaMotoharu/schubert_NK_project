"""Unused reader rebound to original3905 before first issue; no test replay."""
import ast
import inspect
import sys
import pg5058_whole_case_projection as engine
import pg5558_snapshot_whole_public as previous
from pg5574_monitor_whole_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED,added_cases

SLOT='PG5588-current3905-cases'


def counts(raw):
    class Rebase(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value==3900:return ast.copy_location(ast.Constant(3905),node)
            return node
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            if isinstance(node.left,ast.Call)and isinstance(node.left.func,ast.Name)and node.left.func.id=='len'and len(node.left.args)==1 and isinstance(node.left.args[0],ast.Name)and node.left.args[0].id=='trace':
                for value in node.comparators:
                    if isinstance(value,ast.Constant)and value.value==4:value.value=5
            return node
        def visit_Dict(self,node):
            node=self.generic_visit(node)
            for key,value in zip(node.keys,node.values):
                if isinstance(key,ast.Constant)and key.value=='newTestIdTrace'and isinstance(value,ast.Constant)and value.value==4:value.value=5
            return node
    return ast.unparse(ast.fix_missing_locations(Rebase().visit(ast.parse(raw))))


def export_source():return counts(previous.export_source().replace('PG5550','PG5588'))


def main_source():
    raw=previous.main_source()
    for before,after in(('pg5552-snapshot-whole-qualified-v1',QUALIFIED),('pg5558-snapshot-case-projection-v1','pg5576-monitor-case-projection-v1'),
        ('PG5550','PG5588'),('PG5552','PG5574'),('PG5558_READ_ONLY','PG5576_READ_ONLY')):
        if before not in raw:raise ValueError('exact prior allowlist binding')
        raw=raw.replace(before,after)
    return counts(raw)


def namespace():
    return{**vars(engine),'SOURCE':SOURCE,'ROOT':ROOT,'W':W,'SLOT':SLOT,'QUALIFIED':QUALIFIED,'added_cases':added_cases,'export_source':export_source}


def main():
    scope=namespace();exec(compile(main_source(),'<original3905 case allowlist>','exec'),scope)
    return scope['main']()


def publish_qualification():
    scope=namespace();raw=counts(inspect.getsource(previous.publish_qualification))
    exec(compile(raw,'<current3905 full summary>','exec'),scope)
    return scope['publish_qualification']()


if __name__=='__main__':
    if sys.argv[1:]==['--qualification-summary']:publish_qualification()
    elif not sys.argv[1:]:main()
    else:raise SystemExit('known original result-only mode required')
