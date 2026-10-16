"""BUG1353 new-only read. Preserve the canonical Unit property string namespace."""
import ast
import inspect
import pg4374_current_half_handoff_read as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4376-scoped-half-handoff-read-v1'


def payload():
    raw = once(previous.payload(), "save=base/'" + previous.SLOT + "'", "save=base/'" + SLOT + "'")
    raw = once(raw, "fields=(Path('/proc/815726/stat').read_text().rsplit(')',1)[1].split())",
               "zombie_fields=(Path('/proc/815726/stat').read_text().rsplit(')',1)[1].split())")
    raw = once(raw, "require(fields[0]=='Z'and int(fields[1])==815643 and int(fields[19])==15409721",
               "require(zombie_fields[0]=='Z'and int(zombie_fields[1])==815643 and int(zombie_fields[19])==15409721")
    nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'fields' for t in n.targets)]
    if len(nodes) != 1 or not isinstance(nodes[0].value, ast.Constant) or type(nodes[0].value.value) is not str:
        raise ValueError('unchanged canonical Unit fields string required')
    return raw


def main():
    ns = {**vars(previous), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.main), '<new scoped readonly transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
