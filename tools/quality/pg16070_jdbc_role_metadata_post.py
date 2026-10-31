"""Independent saved metadata/log/source qualification, plus static library lint only."""
import ast
import copy
import io
import json
import re
from contextlib import redirect_stdout, redirect_stderr
from pyflakes.api import check
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

PIN = '002ae110aef0d25c2251f1db99dd6162d46cba4d31859afa05c59452a7309462'
CORE_PIN = 'cd1c4ef43d458dcb36f6a1f6f9e3e577c679b6b4e060f28c20e7e8217c379759'
OUT = data.BASE / 'PG16070-jdbc-role-metadata-post-v1'
CORE = data.ROOT / 'tools/quality/jdbc_role_metadata_v1.py'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def assess(value):
    require(value['actualExit'] == 0 and value['source'] == '6b53efeec87f3ec36a840dd8e7759656cb4aee5c', 'same genuine source/tool result')
    require(value['toolSource'] == 'tools/quality/jdbc_role_metadata_v1.py' and value['toolSourceSha256'] == CORE_PIN, 'exact reviewed library source')
    require(type(value['toolMetadataTests']) is int and value['toolMetadataTests'] == 8 and value['toolMetadataTestIds'] == ['Q-JDBCROLE' + str(i).zfill(3) for i in range(1, 9)], 'eight exact metadata tests')
    ids = re.findall(r'(?m)^test_Q_JDBCROLE([0-9]{3})_.* \.\.\. ok$', value['log'])
    require(ids == [str(i).zfill(3) for i in range(1, 9)] and 'Ran 8 tests' in value['log'], 'original complete unittest output not a begin declaration')
    for field in ('failures', 'errors', 'skipped', 'existingProductTestsReexecuted', 'productTestsExecuted', 'actualVmActions', 'actualDatabaseActions', 'actualRootOrAuthorityActions', 'externalActions', 'newAccepted', 'originalPlanProgressDelta'):
        require(type(value[field]) is int and value[field] == 0, 'no hidden execution/acceptance: ' + field)
    require(type(value['staticExistingSites']) is int and value['staticExistingSites'] == 16, 'two explicit existing static source sets')
    require(value['lexicalCandidatesAreNotAstOrPermission'] is value['allOldExecutedToolsAndProofsUnchanged'] is True, 'bounded lexical scope not new authority')
    require(value['formalUpdated'] is value['wholeF03Accepted'] is value['whole451Accepted'] is False and value['effortPercent'] is None, 'no formal/effort promotion')


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    value = data.read_checked(data.BASE / 'PG16068-jdbc-role-metadata-qualification-v1/manifest.json', PIN)
    content = CORE.read_bytes()
    require(data.sha(content) == CORE_PIN, 'immutable actual library bytes')
    text = content.decode('utf-8')
    tree = ast.parse(text)
    require([alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names] == ['re'] and not any(isinstance(node, ast.ImportFrom) for node in tree.body), 'no IO/execution/target dependency imports')
    require({node.name for node in tree.body if isinstance(node, ast.FunctionDef)} == {'_require', 'close_conditions', 'alias_variable'}, 'only the three reviewed pure metadata functions')
    require(not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'open', 'exec', 'eval', 'compile', '__import__', 'input', 'print'} for node in ast.walk(tree)), 'no hidden dynamic execution or IO call')
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        static_exit = check(text, str(CORE))
    require(static_exit == 0, 'actual static library lint only, never direct module execution')
    assess(value)
    negatives = []
    for field, mutation in [('actualExit', 1), ('source', '0' * 40), ('toolSourceSha256', '0' * 64), ('toolMetadataTests', 7), ('failures', 1), ('skipped', 1), ('staticExistingSites', 48), ('productTestsExecuted', 8), ('actualRootOrAuthorityActions', 1), ('lexicalCandidatesAreNotAstOrPermission', False), ('newAccepted', True), ('formalUpdated', True), ('effortPercent', 100), ('originalPlanProgressDelta', 1)]:
        bad = copy.deepcopy(value)
        bad[field] = mutation
        try:
            assess(bad)
        except ValueError:
            negatives.append(field)
        else:
            raise ValueError('unrejected metadata promotion: ' + field)
    verify(value['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=value['source'], invocation=invocation,
        parentManifestSha256=PIN, coreSourceSha256=CORE_PIN, toolMetadataTests=8, staticExistingSites=16,
        coreStaticLintExit=static_exit, coreStaticLintOutput=output.getvalue(), independentMetadataNegativeVectors=len(negatives), negativeLabels=negatives,
        directModuleEntryGuardRejectionBeforeBody=True, directModuleExecutionReissued=False,
        permittedTopLevelEntryGuardUnchanged=True, lexicalCandidatesAreNotAstOrPermission=True,
        productTestsExecuted=0, oldProductTestsReexecuted=0, actualVmActions=0, actualDatabaseActions=0,
        actualRootOrAuthorityActions=0, externalActions=0, originalPlanProgressDelta=0,
        newAccepted=0, formalUpdated=False, effortPercent=None, wholeF03Accepted=False, whole451Accepted=False))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentMetadataNegativeVectors=len(negatives), coreStaticLintExit=static_exit)))


if __name__ == '__main__':
    main()
