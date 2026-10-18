"""Independent corrected20 captured terminal before currentGC/all-resources, unchanged oracle."""
import inspect
import ast
from types import SimpleNamespace
import pg4828_new_current_bootstrap_post as template
import pg5102_corrected_bootstrap_sources as role
import pg5106_corrected_bootstrap_dispatch as dispatch

SLOT = 'pg5108-corrected-bootstrap-post-v1'


def bind_recovery_preimage(raw):
    tree = ast.parse(raw)
    changes = [0, 0, 0]
    class Bound(ast.NodeTransformer):
        def visit_Compare(self, node):
            if ast.unparse(node) == "fresh['native'] == native":
                node.comparators[0] = ast.Name(id='retained_native', ctx=ast.Load())
                changes[0] += 1
            elif (isinstance(node.left, ast.Name) and node.left.id == 'post'
                  and len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Dict)):
                for i, key in enumerate(node.comparators[0].keys):
                    if isinstance(key, ast.Constant) and key.value == 'native':
                        if ast.unparse(node.comparators[0].values[i]) != 'native':
                            raise ValueError('exact old recovery native boundary')
                        node.comparators[0].values[i] = ast.Name(id='retained_native', ctx=ast.Load())
                        changes[1] += 1
            elif ast.unparse(node) == 'hashlib.sha256(snapshot_raw).hexdigest() == BASELINE':
                node.left.func.value.args[0] = ast.Name(id='baseline_raw', ctx=ast.Load())
                changes[2] += 1
            return self.generic_visit(node)
    tree = Bound().visit(tree)
    if changes != [1, 1, 1]:
        raise ValueError('only three exact prior recovery-capsule references')
    at = next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name)and t.id=='bus'for t in n.targets))
    tree.body[at:at] = ast.parse("retained_native=json.loads(baseline_raw)['native']").body
    return ast.unparse(ast.fix_missing_locations(tree)) + '\n'


def payload():
    current_dispatch = SimpleNamespace(fixed=dispatch.namespace()['fixed'], SLOT=dispatch.SLOT)
    current_role = SimpleNamespace(**{**vars(role), 'template': role.previous.previous.previous.template})
    ns = {**vars(template), 'role': current_role, 'dispatch': current_dispatch, 'SLOT': SLOT}
    raw = inspect.getsource(template.payload).replace('pg4820', 'pg5102')
    marker = 'marker="save=base/"+repr(role.before.SLOT)'
    if raw.count(marker) != 1:
        raise ValueError('one exact AST-spaced new before output')
    raw = raw.replace(marker, 'marker="save = base / "+repr(role.before.SLOT)', 1)
    # The old result qualifies recovery; the new result qualifies normal20.
    marker = '    def tool(name):\n'
    if raw.count(marker) != 1:
        raise ValueError('one post-hash output qualification boundary')
    extra = """    if raw.count("'allResources0': True, ")!=1:raise ValueError('one previous recovery result flag')
    raw=raw.replace("'allResources0': True, ","",1)
"""
    raw = raw.replace(marker, extra + marker, 1)
    marker = '"\'startsStopsWrites0\':True"'
    if raw.count(marker) != 1:
        raise ValueError('one current normal20 result insertion boundary')
    raw = raw.replace(marker, '"\'startsStopsWrites0\': True"', 1)
    exec(compile(raw, '<same source corrected20 independent post>', 'exec'), ns)
    return bind_recovery_preimage(ns['payload']())


if __name__ == '__main__':
    raise SystemExit(role.before.admission.execute(SLOT, payload(), 180))
