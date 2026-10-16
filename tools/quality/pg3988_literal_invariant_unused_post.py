"""Independent current full11/native46 and new candidate187 post, no publication authority."""
import ast
import inspect
import json
from pyflakes.api import check
import pg3762_hygiene_unused_post as previous
import pg3978_current_preservation_readonly as readonly
import pg3982_literal_invariant_unused_sources as role
from unit_metadata_reference_source import scope

W = role.W


def extra_source():
    raw = role.normalized_text(previous.EXTRA)
    return raw.replace('native34Preserved', 'native46Preserved')


def payload():
    raw = readonly.payload(); tree = ast.parse(raw); last = tree.body[-1]
    if not (isinstance(last, ast.Expr) and isinstance(last.value, ast.Call) and isinstance(last.value.func, ast.Name) and last.value.func.id == 'print'):
        raise ValueError('one final current readonly boundary')
    raw = ''.join(raw.splitlines(keepends=True)[:last.lineno - 1])
    capture = role.pinned(W / role.TOOLS, 'pg3982_configuration_capture.py')
    candidate = json.loads((W / 'pg3976-candidate-build-v1.safe.json').read_bytes())
    result = 'CANDIDATE=' + repr(candidate) + '\nBEFORE=' + repr(role.BEFORE) + '\n' + raw + '\n' + capture + '\n' + extra_source()
    start = result.index('units={}'); end = result.rindex('print(json.dumps(')
    result = result[:start] + scope(result[start:end]) + result[end:]
    result = result.replace("'configuration32EveryFieldUnchanged':True", "'configuration32EveryFieldUnchanged':True,'newTenReferencesReturnedNormally':len(refs)==10")
    if check(result, '<new candidate full independent preservation post>'): raise ValueError('complete new current/candidate independent namespace')
    compile(result, '<current full11/native46/new187 unused post>', 'exec')
    return result


def main():
    values = {**previous.__dict__, 'readonly': readonly, 'role': role, 'payload': payload}
    raw = role.normalized_text(inspect.getsource(previous.main))
    exec(compile(raw, '<new candidate independent post only>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
