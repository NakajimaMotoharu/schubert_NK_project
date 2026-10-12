"""SSC275 typed complete99FD fresh guard; old101 proof remains immutable."""
import inspect
from pg1665_unused_pair_contract import fresh_parent


def source():
    raw = inspect.getsource(fresh_parent).replace('fresh_parent(', 'fresh_sole_parent(').replace('101', '99').replace('other99', 'other97')
    compile(raw, '<sole owner99 complete guard>', 'exec')
    return raw


_namespace = {}
exec(source(), _namespace)
fresh_sole_parent = _namespace['fresh_sole_parent']
