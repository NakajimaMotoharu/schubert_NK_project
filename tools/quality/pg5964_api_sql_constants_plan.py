"""Plan21 exact SQL-row/limit constant expressions only; main() never edits Production."""
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pg5938_private_lock93_plan import formatted
from pg5940_private_lock_compile import ROOT, BASE, sha
from pg5944_private_lock_whole import SOURCE
from static_disposition_overlay import load


def declared_source(before, changes, constants):
    if not constants or len(set(constants)) != len(constants):
        raise ValueError('one declaration per semantic private constant')
    for declaration in constants:
        name = declaration.split(' = ', 1)[0].split()[-1]
        if re.search(r'\b'+re.escape(name)+r'\b', before):
            raise ValueError('no existing declaration/reference overwritten')
    for old, new, count in changes:
        if type(count) is not int or count < 1 or before.count(old) != count:
            raise ValueError('all and only exact declared condition tokens')
        before = before.replace(old, new)
    found = re.search(r'^(?:public\s+)?final\s+class\s+\w+[^{}]*\{', before, re.MULTILINE)
    if not found:
        raise ValueError('one top-level final class declaration required')
    return before[:found.end()]+'\n'+''.join('  '+s+'\n' for s in constants)+before[found.end():]


def selected(rows):
    out = []
    for row in rows:
        if row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or row['rule'] != 'AvoidLiteralsInIfCondition' or not row['sourcePath'].startswith('src/schubert-nk-api/'):
            continue
        text = (ROOT/row['sourcePath']).read_text(); line = text.splitlines()[int(row['beginline'])-1]
        if re.search(r'if \(\w+\.executeUpdate\(\) != 1\)', line) or row['sourcePath'].endswith('/UserAuditWriter.java') and '> 1024)' in line or row['sourcePath'].endswith('/QuestionCommandService.java') and '== 999_999_999L)' in line or row['sourcePath'].endswith('/MediaRepository.java') and 'rows.size() != 1)' in line:
            out.append(row)
    if len(out) != 21 or len({r['sourcePath'] for r in out}) != 16:
        raise ValueError('exact21 genuinely unreviewed conditions/16source')
    return out


def main():
    bp = BASE/'PG5960-readiness-boundaries28-v1/manifest.json'; bsha = 'b24e154dde5b57f62f4a87081ea34ee001c89eb9e9b5226d63caa034a87912f3'
    rows = load(bp, bsha, SOURCE); groups = defaultdict(list)
    for row in selected(rows):
        groups[row['sourcePath']].append(row)
    sources = []; kinds = Counter()
    for path, diagnostics in sorted(groups.items()):
        before = (ROOT/path).read_text(); changes = Counter(); constants = set()
        if any(r['sourceSha256'] != sha(ROOT/path) for r in diagnostics):
            raise ValueError('current frozen source remains the exact raw input')
        for row in diagnostics:
            line = before.splitlines()[int(row['beginline'])-1]; match = re.search(r'if \(\w+\.executeUpdate\(\) != 1\)', line)
            if match:
                old = match.group(); new = old.replace('!= 1)', '!= EXPECTED_AFFECTED_ROWS)'); constants.add('private static final int EXPECTED_AFFECTED_ROWS = 1;'); kind = 'SINGLE_ROW_SQL_POSTCONDITION'
            elif path.endswith('/UserAuditWriter.java'):
                old, new = '> 1024)', '> MAXIMUM_DETAILS_UTF8_BYTES)'; constants.add('private static final int MAXIMUM_DETAILS_UTF8_BYTES = 1024;'); kind = 'AUDIT_UTF8_BYTE_LIMIT'
            elif path.endswith('/QuestionCommandService.java'):
                old, new = '== 999_999_999L)', '== MAXIMUM_MUTATION_VERSION)'; constants.add('private static final long MAXIMUM_MUTATION_VERSION = 999_999_999L;'); kind = 'N9_MUTATION_VERSION_LIMIT'
            elif path.endswith('/MediaRepository.java'):
                old, new = 'rows.size() != 1)', 'rows.size() != EXPECTED_RESULT_ROWS)'; constants.add('private static final int EXPECTED_RESULT_ROWS = 1;'); kind = 'SINGLE_RESULT_ROW_POSTCONDITION'
            else:
                raise ValueError('no undeclared expression edits')
            changes[old, new] += 1; kinds[kind] += 1
        edits = [(a, b, n) for (a, b), n in sorted(changes.items())]; declarations = sorted(constants)
        after = formatted(declared_source(before, edits, declarations))
        sources.append(dict(path=path, beforeSha256=sha(ROOT/path), predictedAfterSha256=hashlib.sha256(after.encode()).hexdigest(),
                            changes=edits, constants=declarations, findingIds=[r['findingId'] for r in diagnostics], sourceCodeApplied=False))
    q = BASE/'PG5926-current3973-cases/qualification.json'; cp = q.with_name('cases.json')
    if sha(q) != '89bdeed7bf69067bb0a20c766c8e59cbb780d0fd83dffa7e71c9e1255b1115cf' or sha(cp) != '706d48d8a43c7e80876ecf9fedd6cddf935bb88bba207dc04998015b6bbc0904':
        raise ValueError('existing independent semantic cases, not old-source PT import')
    cases = [r for r in json.loads(cp.read_bytes()) if r['module'] == 'api']
    if len(cases) != 1010 or len({r['class'] for r in cases}) != 169:
        raise ValueError('unchanged full API1010/169 planning inventory')
    value = dict(actualExit=0, source=SOURCE, sourcePlans=sources, selectedSourceFiles=16, selectedDiagnosticConditions=21, conditionKinds=dict(kinds),
                 baseManifestPath=bp.relative_to(ROOT).as_posix(), baseManifestSha256=bsha,
                 plannedContractCrosscheck=['single changed SQL row;0/multiple refuse', 'audit UTF8 byte upper bound1024', 'N9 maximum999999999 mutation limit', 'single media result row;0/multiple refused'],
                 independentOracleCrosscheckCompleted=False,
                 plannedApiCaseReferences=[{k:r[k] for k in ('class', 'caseNameSha256')} for r in cases],
                 plannedApiCases=1010, plannedApiSuites=169, additionalSixModuleGuardCases=11, oldCasesAreOnlySemanticReferences=True,
                 productionApplied=False, testsExecuted=0, ptAlternativeCompleted=0, F03Accepted=False, formalAccepted=False, vmActions=0)
    out = BASE/'PG5964-api-sql21-plan-v1'; os.umask(0o077); out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, sourceFiles=16, conditions=21, kinds=dict(kinds), plannedApiCases=1010, plannedApiSuites=169,
                         productionApplied=False, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
