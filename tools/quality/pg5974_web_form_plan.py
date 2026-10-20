"""Immutable12 form/view source22 private constant plan; no Production mutation or PT."""
import hashlib
import json
import os
from collections import defaultdict
from pg5964_api_sql_constants_plan import declared_source, formatted
from pg5940_private_lock_compile import ROOT, BASE, sha
from pg5970_api_sql1021_public import SOURCE
from static_disposition_overlay import load

PARAM = (' != 1)', ' != SINGLE_PARAMETER_VALUE_COUNT)', 'SINGLE_PARAMETER_VALUE_COUNT', '1')
PAGE = ('> 999999)', '> MAXIMUM_PAGE_NUMBER)', 'MAXIMUM_PAGE_NUMBER', '999_999')
RULES = {
    'LogSearchForm': [PARAM, PAGE], 'NotificationSearchForm': [PARAM, PAGE],
    'QuestionSearchForm': [PARAM, ('> 256)', '> MAXIMUM_KEYWORD_UTF8_BYTES)', 'MAXIMUM_KEYWORD_UTF8_BYTES', '256'), ('> 64)', '> MAXIMUM_USERNAME_UTF8_BYTES)', 'MAXIMUM_USERNAME_UTF8_BYTES', '64'), PAGE],
    'QuestionSubmitForm': [PARAM, (' == 1)', ' == SINGLE_PARAMETER_VALUE_COUNT)', 'SINGLE_PARAMETER_VALUE_COUNT', '1')],
    'ScenarioSearchForm': [PARAM, PAGE], 'UserCreateForm': [PARAM, (' == 1)', ' == SINGLE_PARAMETER_VALUE_COUNT)', 'SINGLE_PARAMETER_VALUE_COUNT', '1')],
    'UserMutationInput': [PARAM],
    'UserSearchForm': [PARAM, ('> 64)', '> MAXIMUM_USERNAME_UTF8_BYTES)', 'MAXIMUM_USERNAME_UTF8_BYTES', '64'), PAGE],
    'GameListViewModel': [('> 10)', '> MAXIMUM_GAME_RECORDS)', 'MAXIMUM_GAME_RECORDS', '10')],
    'RouteListViewModel': [('> 50)', '> MAXIMUM_ROUTE_RECORDS)', 'MAXIMUM_ROUTE_RECORDS', '50')],
    'ScenarioDetailViewModel': [('> 200)', '> MAXIMUM_INLINE_RECORDS)', 'MAXIMUM_INLINE_RECORDS', '200')],
    'ScenarioFileListViewModel': [('> 500)', '> MAXIMUM_FILE_RECORDS)', 'MAXIMUM_FILE_RECORDS', '500')]}


def main():
    bp = BASE/'PG5972-sql-static-dispositions-v1/manifest.json'; bsha = 'dac135f64f921f7b4391414eb5d76434f38fdb7c49ff3a78133ba132d70fd2c9'
    rows = load(bp, bsha, SOURCE); grouped = defaultdict(list)
    for r in rows:
        if r['status'] == 'NOT_REVIEWED_CURRENT_SOURCE' and r['rule'] == 'AvoidLiteralsInIfCondition' and r['sourcePath'].startswith('src/schubert-nk-web/') and r['sourcePath'].rsplit('/', 1)[1][:-5] in RULES:
            grouped[r['sourcePath']].append(r)
    if len(grouped) != 12 or sum(map(len, grouped.values())) != 22:
        raise ValueError('exact genuinely unreviewed12 source/22 diagnostics')
    plans = []
    for path, diagnostics in sorted(grouped.items()):
        before = (ROOT/path).read_text(); simple = path.rsplit('/', 1)[1][:-5]; changes = []; constants = set()
        for old, new, name, value in RULES[simple]:
            changes.append((old, new, 1)); constants.add('private static final int '+name+' = '+value+';')
        if len(changes) != len(diagnostics) or any(r['sourceSha256'] != sha(ROOT/path) for r in diagnostics):
            raise ValueError('one exact old condition per actual raw diagnostic')
        after = formatted(declared_source(before, changes, sorted(constants)))
        plans.append(dict(path=path, beforeSha256=sha(ROOT/path), predictedAfterSha256=hashlib.sha256(after.encode()).hexdigest(),
                          changes=changes, constants=sorted(constants), findingIds=[r['findingId'] for r in diagnostics], productionApplied=False))
    cp = BASE/'PG5944-current3973-cases/cases.json'
    if sha(cp) != '81a354697110977b2b859b14347cf62dad6b077d609d06997a3f891d7f4cc250':
        raise ValueError('existing unchanged Test semantic identities only')
    cases = [r for r in json.loads(cp.read_bytes()) if r['module'] == 'web']
    if len(cases) != 913 or len({r['class'] for r in cases}) != 143:
        raise ValueError('fullWeb913/143 established actual semantic inventory')
    out = BASE/'PG5974-web-form22-plan-v1'; os.umask(0o077); out.mkdir()
    value = dict(actualExit=0, source=SOURCE, sourcePlans=plans, selectedSourceFiles=12, selectedDiagnosticConditions=22,
                 baseManifestPath=bp.relative_to(ROOT).as_posix(), baseManifestSha256=bsha,
                 plannedWebCaseReferences=[{k:r[k] for k in ('class','caseNameSha256')} for r in cases],
                 plannedWebCases=913, plannedWebSuites=143, additionalGuardCases=8, sourceCodeApplied=False, testsExecuted=0,
                 sameHttpDomAndSingleValueRejectionRequired=True, oldCasesAreSemanticReferencesOnly=True,
                 ptAlternativeCompleted=0, formalAccepted=False, F03Accepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, sourceFiles=12, conditions=22, fullWebCases=913, fullWebSuites=143, manifestSha256=sha(out/'manifest.json'), productionApplied=False)))


if __name__ == '__main__':
    main()
