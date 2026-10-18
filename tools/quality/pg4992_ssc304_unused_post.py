"""Independent unused187/current04bb full11/all80 post; no publication authority."""
import ast
import io
import json
import tokenize
from pyflakes.api import check
import pg4870_ssc301_302_unused_post as previous
import pg4982_current_preservation_readonly as current
import pg4986_ssc304_unused_sources as role
from immutable_payload_binding import bind_preserving_payloads
from pg4996_resume_connection import execute

SLOT = 'pg4992-ssc304-unused-post-v1'


def rename_source_scalar(raw):
    """Rename identifiers only, never strings, snapshot capsules or hash fragments."""
    def bind(value):
        lines = value.splitlines(keepends=True)
        offsets = [0]
        for line in lines:
            offsets.append(offsets[-1] + len(line))
        edits = []
        for token in tokenize.generate_tokens(io.StringIO(value).readline):
            if token.type == tokenize.NAME and token.string == 'CANDIDATE':
                first = offsets[token.start[0] - 1] + token.start[1]
                last = offsets[token.end[0] - 1] + token.end[1]
                edits.append((first, last))
        for first, last in reversed(edits):
            value = value[:first] + 'CURRENT_VIEW_CANDIDATE_SOURCE' + value[last:]
        return value
    return bind_preserving_payloads(raw, bind)


def payload():
    role.qualify()
    raw = rename_source_scalar(current.payload())
    marker = 'save=base/' + repr(current.SLOT)
    if raw.count(marker) != 1:
        raise ValueError('one new independent evidence namespace')
    raw = raw.replace(marker, 'save=base/' + repr(SLOT), 1)
    candidate = json.loads((role.W / 'pg4980-candidate-build-v1.safe.json').read_bytes())
    capture = role.pinned(role.W / role.TOOLS, 'pg4986_configuration_capture.py')
    nodes = ast.parse(raw).body
    for node in ast.parse(capture).body:
        if isinstance(node, (ast.Assign, ast.FunctionDef)) and not any(
                ast.dump(node) == ast.dump(n) for n in nodes):
            raise ValueError('same complete current configuration definition required')
    # Already-composed3982 checks cross each remaining namespace exactly once.
    # Recursive role_text would incorrectly change the installed current release.
    extra = previous.previous.role.normalized_text(previous.previous.old.extra_source())
    extra = role.previous.normalized_text(extra)
    extra = role.normalized_text(extra).replace('native46Preserved', 'native80Preserved')
    marker = "json.loads(before)=={k:v for k,v in expected.items()if k!='native'}"
    if extra.count(marker) != 1:
        raise ValueError('one canonical full11 including native boundary')
    extra = extra.replace(marker, 'json.loads(before)==expected', 1)
    tree = ast.parse(extra)
    last = tree.body[-1]
    if not (isinstance(last, ast.Expr) and isinstance(last.value, ast.Call)
            and isinstance(last.value.args[0], ast.Call)):
        raise ValueError('one independent unused summary schema')
    summary = last.value.args[0].args[0]
    for key, value in zip(summary.keys, summary.values):
        if isinstance(key, ast.Constant) and key.value == 'guestFilesWritten':
            value.value = 3
    checks = ast.unparse(ast.Module(body=tree.body[:-1], type_ignores=[]))
    addition = ("expected={**after,'native':native}\n"
                "require(sum(p.endswith('.exec')for p in native)==80)\n"
                + checks + '\ncandidate_post=' + ast.unparse(summary))
    marker = "    proof = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in root.iterdir() if p.is_file()}"
    if raw.count(marker) != 1:
        raise ValueError('one held-tenRef pre-finally boundary')
    raw = raw.replace(marker, '\n'.join('    ' + line for line in addition.splitlines())
                      + '\n' + marker, 1)
    marker = "'sealedFull11Fields':11}))"
    if raw.count(marker) != 1:
        raise ValueError('one post-normal-close terminal summary')
    raw = raw.replace(marker, "'sealedFull11Fields':11,'genuineCompletion':FRESH_DONE,"
                      "**candidate_post,'newTenReferencesReturnedNormally':len(refs)==10}))", 1)
    _, normal, _ = role.current_tuple()
    raw = ('CANDIDATE=' + repr(candidate) + '\nBEFORE=' + repr(role.BEFORE)
           + '\nFRESH_DONE=' + repr(normal) + '\nfrom pathlib import Path\n' + raw)
    if check(raw, '<independent unused187/current04bb full11/native80>'):
        raise ValueError('complete emitted namespace static0 required')
    compile(raw, '<independent unused/current post>', 'exec')
    return raw


def qualify_placement(value):
    if not (type(value.get('actualExit')) is int and value['actualExit'] == 0
            and value.get('sourceQualified') is True
            and value.get('currentApprovalEpochChanged') is False):
        raise ValueError('actual unused-only placement first')


def main():
    value = json.loads((role.W / 'pg4990-place-v1.safe.json').read_bytes())
    qualify_placement(value)
    return execute(SLOT, payload(), 180)


if __name__ == '__main__':
    raise SystemExit(main())
