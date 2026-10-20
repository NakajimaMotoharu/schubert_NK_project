"""Bounded javap CFG ownership check for one compiler-generated private monitor scope."""
import re
from collections import deque
from pg6084_web_factory_order import instructions


def local_slot(op, arg, action):
    if op.startswith(action+'_'):
        return int(op.split('_', 1)[1])
    if op == action and arg.strip().isdigit():
        return int(arg.strip())
    raise ValueError('explicit local reference load/store required')


def check_monitor(code, expected_exits):
    ops = instructions(code); indices = {at: i for i, (at, _, _) in enumerate(ops)}
    entries = [i for i, (_, op, _) in enumerate(ops) if op == 'monitorenter']
    exits = [i for i, (_, op, _) in enumerate(ops) if op == 'monitorexit']
    if len(entries) != 1 or len(exits) != expected_exits or any('switch' in op for _, op, _ in ops):
        raise ValueError('one explicitly reviewed scope and expected normal/exception release sites')
    entered = entries[0]
    if entered < 3 or ops[entered-2][1] != 'dup' or ops[entered-3][1] != 'getfield' or '// Field lock:Ljava/lang/Object;' not in ops[entered-3][2]:
        raise ValueError('private lock reference copied before monitorenter')
    slot = local_slot(ops[entered-1][1], ops[entered-1][2], 'astore')
    for i in exits:
        if not i or local_slot(ops[i-1][1], ops[i-1][2], 'aload') != slot:
            raise ValueError('all exits release the identical captured monitor local')
    if any(local_slot(op, arg, 'astore') == slot for i, (_, op, arg) in enumerate(ops)
           if i != entered-1 and (op == 'astore' or op.startswith('astore_'))):
        raise ValueError('captured monitor local must not be overwritten')
    handlers = [(int(a), int(b), int(c)) for a, b, c in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+any\s*$', code)]
    if not handlers:
        raise ValueError('compiler catch-all release handler required')
    queue = deque([(0, 0)]); seen = set(); terminal = set()
    while queue:
        index, depth = queue.popleft()
        if (index, depth) in seen:
            continue
        seen.add((index, depth)); at, op, arg = ops[index]
        normal_depth = depth
        if op == 'monitorenter':
            if depth != 0:
                raise ValueError('no nested/reentered unknown monitor')
            normal_depth = 1
        elif op == 'monitorexit':
            if depth != 1:
                raise ValueError('release without ownership')
            normal_depth = 0
        catches = [indices[target] for start, end, target in handlers if start <= at < end]
        # Every potentially abrupt body operation is conservatively covered. The proved
        # nonnull captured lock and owned depth exclude monitorexit monitor-mismatch faults.
        if depth == 1 and op != 'monitorexit':
            if not catches:
                raise ValueError('owned abrupt path has no catch-all release')
            queue.extend((target, depth) for target in catches)
        if op.endswith('return'):
            if normal_depth:
                raise ValueError('normal return leaks monitor')
            terminal.add(at)
            continue
        if op == 'athrow':
            if depth and not catches:
                raise ValueError('uncaught throw leaks monitor')
            continue
        if op == 'goto' or op.startswith('if'):
            queue.append((indices[int(arg.strip())], normal_depth))
            if op == 'goto':
                continue
        if index+1 >= len(ops):
            raise ValueError('no fallthrough outside method')
        queue.append((index+1, normal_depth))
    if not terminal or any(i not in {s[0] for s in seen} for i in exits):
        raise ValueError('normal return and every expected release site must be reachable')
    return dict(monitorLocal=slot, releaseOffsets=[ops[i][0] for i in exits],
                normalReturnOffsets=sorted(terminal), catchAllHandlers=handlers, reachableAbstractStates=len(seen))
