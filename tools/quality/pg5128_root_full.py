"""Required coherent Root SSC306/307 whole source, exact six-format before any PT; no VM."""
import ast
import inspect
import json
import pg4420_shared_manager_full as driver
import pg4968_ssc304_full as previous
import pg5120_root_elf_selected as selected_role

SOURCE = 'e8ecff1bec1d7ddd51cdfbf803acda07c2f6cdb9'
LABEL = 'PG5128'
ROOT, W = driver.ROOT, driver.W


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG4968', LABEL).replace(previous.SOURCE, SOURCE)

    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in {3791, 553, 1650}:
                return ast.copy_location(ast.Constant({3791:3814, 553:556, 1650:1654}[node.value]), node)
            return node

    result = ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))
    compile(result, '<coherent Root exact3814/556/1654>', 'exec')
    return result


def main():
    path = W / 'pg5126-root-guards-green-v1'
    selected = json.loads((path / 'manifest.safe.json').read_bytes())
    if not (type(selected['actualExit']) is int and selected['actualExit'] == 0
            and selected['phaseExits'] == [0, 0] and selected['sourceSnapshot'] == SOURCE
            and selected['tests'] == 50 and selected['suites'] == 8 and not selected['reasons']):
        raise ValueError('actual fixed selected50/8 before whole')
    if selected_role.main_delta(path / 'source', 'pending') != selected['mainDelta']:
        raise ValueError('actual two Root outer/four additions byte inventory')
    raw = inspect.getsource(driver.main)
    raw = raw.replace('pg4420', 'pg5128').replace('shared-manager', 'root')
    old = "'tests': 3721, 'suites': 545, 'mainClasses': 1644"
    if raw.count(old) != 1: raise ValueError('one exact planned whole inventory')
    raw = raw.replace(old, "'tests': 3814, 'suites': 556, 'mainClasses': 1654")
    raw = raw.replace('SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved',
                      'SSC306 fixed ELF digest and SSC307 same-owner absolute Root wait; selected5126 actual50/8; new23 independent cases; required whole of changed source, not historical3791 replay; oldnative not imported')
    ns = {**vars(driver), 'SOURCE': SOURCE, 'LABEL': LABEL, 'server_source': server_source}
    exec(compile(raw, '<Root required whole once>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
