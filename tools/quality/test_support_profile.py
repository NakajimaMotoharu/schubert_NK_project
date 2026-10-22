"""Finite test-support profile: no Production target/class percentage is claimed."""
import ast
import inspect
import finite_selected_profile as profile
import pg6780_web_management_result_selected as physical


def runner(total, suites, targets):
    if targets:
        raise ValueError('test-support profile must not invent a Production coverage target')
    # The prior renderer uses this dictionary only to count target slots. Actual TARGETS is empty.
    raw = physical.runner(total, suites, {'batch': ['N/A_TEST_SUPPORT']})
    tree = ast.parse(raw)
    assignments = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'target100' for t in n.targets)]
    if len(assignments) != 1:
        raise ValueError('one target reporting assignment, never alter verdict')
    assignments[0].value = ast.Constant(None)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'done' for t in n.targets):
            if any(isinstance(x, ast.Name) and x.id == 'target100' for x in ast.walk(n.value)):
                raise ValueError('target coverage must not participate in the fixed full selected verdict')
    return ast.unparse(ast.fix_missing_locations(tree))


def execute(slot, guard, cases, counts, expected):
    scope = {**vars(profile), 'runner': runner}
    exec(compile(inspect.getsource(profile.execute), '<finite test support>', 'exec'), scope)
    return scope['execute'](slot, guard, cases, counts, expected, {})
