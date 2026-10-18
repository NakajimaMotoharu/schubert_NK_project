"""BUG1405 corrected new-only graph: actual parent end is never its start."""
import ast
import types
import pg5082_current_bootstrap_sources as previous
import pg5100_retained_pair_independent_post as before

SOURCE, BOM, W, BASELINE = previous.SOURCE, previous.BOM, previous.W, previous.BASELINE
TOOLS = 'pg5102-corrected-bootstrap-tools-v1'
owned = previous.owned
OLD_END_PREDICATE = "parent_receipt['endMonotonicUs']==306951851178"
END_PREDICATE = "parent_receipt['endMonotonicUs']==308517705767"


def intermediate_text(raw):
    raw = previous.current_text(raw)
    for old, new in [(previous.TOOLS, TOOLS), (previous.before.SLOT, before.SLOT)]:
        raw = raw.replace(old, new)
    return raw.replace(OLD_END_PREDICATE, END_PREDICATE)


def final_names(raw):
    for old, new in [('Pg5082', 'Pg5102'), ('PG5082', 'PG5102'), ('pg5082', 'pg5102')]:
        raw = raw.replace(old, new)
    return raw


def current_text(raw):
    return final_names(intermediate_text(raw))


def validate_parent_end(raw):
    comparisons = [n for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Compare)
                   and ast.unparse(n.left) == "parent_receipt['endMonotonicUs']"]
    if (len(comparisons) != 1 or len(comparisons[0].ops) != 1 or not isinstance(comparisons[0].ops[0], ast.Eq)
            or len(comparisons[0].comparators) != 1 or not isinstance(comparisons[0].comparators[0], ast.Constant)
            or type(comparisons[0].comparators[0].value) is not int
            or comparisons[0].comparators[0].value != 308517705767):
        raise ValueError('independent genuine end308517705767, never start306951851178')


def eligibility(baseline_sha):
    result = types.FunctionType(previous.eligibility.__code__, {**vars(previous), 'before': before})(baseline_sha)
    if not (result.get('ownedPairRecoveryComplete') is True and result.get('allResources0') is True
            and result.get('oldCloseUnknown') is True and type(result.get('retainedVerifyActualExit')) is int
            and result['retainedVerifyActualExit'] == 143):
        raise ValueError('actual independent5100 before corrected retry')
    return result


def files(baseline_sha):
    ns = {**vars(previous), 'before': before, 'TOOLS': TOOLS, 'current_text': intermediate_text, 'eligibility': eligibility}
    values = types.FunctionType(previous.files.__code__, ns)(baseline_sha)
    values = {final_names(name): final_names(raw) for name, raw in values.items()}
    validate_parent_end(values['pg5102_bootstrap_existing.py'])
    return values
