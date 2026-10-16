"""SSC287 data/protocol guards. No process, filesystem, DB or service operations on import."""
from pg4086_failed_done_recovery_contract import ORDER, Plan, require


class Recovery:
    """Fresh external proofs are mandatory before reservation, before send and after termination.

    A durable reservation is intentionally never removed after failure. A second instance must
    authenticate existing terminal data instead of issuing a second stop. Callbacks are supplied
    only by a separately pinned, root-owned dispatcher; this class itself grants no authority.
    """
    def __init__(self, verify, reserve, stop, terminal, record):
        require(all(callable(f) for f in (verify, reserve, stop, terminal, record)))
        self.verify = verify
        self.reserve = reserve
        self.stop = stop
        self.terminal = terminal
        self.record = record
        self.plan = Plan()

    def one(self, unit):
        self.plan.reserve(unit)
        self.verify(unit)
        self.reserve(unit)
        self.verify(unit)
        # Neither a callback exception nor an uncertain stop permits a retry.
        self.stop(unit)
        require(self.terminal(unit) is True)
        self.verify(unit)
        self.record(unit)
        self.plan.terminal(unit)

    def complete(self):
        require(self.plan.next == len(ORDER) and self.plan.reserved is None)


def preserved_tree(before, after, mutable_files=(), mutable_directories=()):
    """Finite namespace delta. Mutable files may grow or be atomically replaced as explicit oracle allows.

    This checks metadata envelope only. Callers must separately authenticate bytes/native stream
    provenance or exact canonical epoch text and preserve private before/after artifacts.
    """
    require(type(before) is dict and type(after) is dict and set(before) == set(after))
    require(type(mutable_files) in (tuple, frozenset) and type(mutable_directories) in (tuple, frozenset))
    mutable = set(mutable_files) | set(mutable_directories)
    require(not set(mutable_files) & set(mutable_directories) and mutable <= set(before))
    for path in before:
        b, a = before[path], after[path]
        require(type(b) is dict and type(a) is dict and set(b) == set(a) == {'metadata', 'sha256'})
        bm, am = b['metadata'], a['metadata']
        require(type(bm) is list and type(am) is list and len(bm) == len(am) == 9
                and all(type(n) is int for n in bm + am))
        if path not in mutable:
            require(b == a)
        elif path in mutable_directories:
            require(b['sha256'] is None and a['sha256'] is None and bm[:7] == am[:7])
        else:
            require(type(b['sha256']) is str and type(a['sha256']) is str
                    and bm[0] == am[0] and bm[2:6] == am[2:6])
    return True
