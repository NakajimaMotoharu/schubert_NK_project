"""BUG911 new-only corrected existing ADMIN tool; historical helper imports only."""
from pathlib import Path
import pg662_sources as old

R=Path(__file__).resolve().parent


def current(raw):
    pairs=tuple((a,b)for a,b in(('pg662','pg664'),('Pg662','Pg664'),('PG662','PG664'))if a in raw)
    assert pairs
    return old.replace(raw,pairs)


def java():return current(old.java())
def refs():return current(old.refs())
def receipt():return old.receipt()
def join():return current(old.join())
def argument_test():return current(old.argument_test())
def compile_script():return current(old.compile_script())


def native():
    raw=current(old.native())
    raw=old.replace(raw,(("'pg664_parent_receipt.py', 'pg559_terminal_refs.py'", "'pg556_parent_receipt.py', 'pg664_parent_receipt.py', 'pg559_terminal_refs.py'"),))
    return raw


def python_files():
    values={'pg664_bootstrap_existing.py':refs(),'pg664_parent_receipt.py':receipt(),'pg664_parent_join.py':join()}
    for name in ('pg535_bootstrap_contract.py','pg536_bootstrap_execution_contract.py','pg529_dependency_graph.py',
                 'pg556_parent_receipt.py','pg559_terminal_refs.py','pg457_stable_actor.py','pg570_directory_identity.py'):
        values[name]=(R/name).read_text()
    return values
