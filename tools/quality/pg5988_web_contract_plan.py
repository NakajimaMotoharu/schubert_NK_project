"""Declare remaining Web24/42 condition constants before PG; no Production/PT/runtime execution."""
import hashlib
import json
import os
import re
from collections import defaultdict
from pg5964_api_sql_constants_plan import declared_source, formatted
from pg5940_private_lock_compile import ROOT, BASE, W, sha
from pg5980_web921_public import SOURCE
from static_disposition_overlay import load

HTTP = ('if (status != 200)', 'if (status != HTTP_OK)', 'int HTTP_OK', '200')
READ_HTTP = ('if (readStatus != 200)', 'if (readStatus != HTTP_OK)', 'int HTTP_OK', '200')
VERSION = ('if (stored[6] != 1)', 'if (stored[6] != ENVELOPE_FORMAT_VERSION)', 'int ENVELOPE_FORMAT_VERSION', '1')
KEY = ('if (key.length != 32)', 'if (key.length != AES_KEY_BYTES)', 'int AES_KEY_BYTES', '32')
RULES = {
    'WebHttpAdmission': [('if (active < 1)', 'if (active < MINIMUM_ACTIVE_REQUESTS)', 'int MINIMUM_ACTIVE_REQUESTS', '1')],
    'WebManagementServer': [('if (json.length() > 1)', 'if (json.length() > JSON_OPENING_DELIMITER_LENGTH)', 'int JSON_OPENING_DELIMITER_LENGTH', '1'),
                            ('if ("/actuator/info".equals(path))', 'if (INFORMATION_PATH.equals(path))', 'String INFORMATION_PATH', '"/actuator/info"'),
                            ('if ("/actuator/prometheus".equals(path))', 'if (METRICS_PATH.equals(path))', 'String METRICS_PATH', '"/actuator/prometheus"')],
    **{name:[HTTP] for name in ('AnimationController','ContentDetailController','LogController','MediaController','MusicController','ScenarioController')},
    'NotificationController': [HTTP, READ_HTTP], 'QuestionController': [HTTP, READ_HTTP],
    'UserAdminController': [HTTP, ('if ("LOCKED".equals(page.getValues().get("state")))', 'if (LOCKED_STATE.equals(page.getValues().get("state")))', 'String LOCKED_STATE', '"LOCKED"')],
    'WebLogPayloadCodec': [VERSION, KEY], 'RevocationPayloadCodec': [VERSION, KEY], 'SessionPayloadCodec': [VERSION, KEY],
    'WebSecurityAudit': [('if (value.length() > 45)', 'if (value.length() > MAXIMUM_IP_LITERAL_CHARACTERS)', 'int MAXIMUM_IP_LITERAL_CHARACTERS', '45')],
    'JmsReplyDecoder': [('if (count < 1)', 'if (count < MINIMUM_DELIVERY_COUNT)', 'int MINIMUM_DELIVERY_COUNT', '1')],
    'WebBrokerContexts': [('if (port > 65_535)', 'if (port > MAXIMUM_TCP_PORT)', 'int MAXIMUM_TCP_PORT', '65_535')],
    'PendingRevocationRepository': [('if (statement.executeUpdate() != 1)', 'if (statement.executeUpdate() != EXPECTED_INSERT_ROWS)', 'int EXPECTED_INSERT_ROWS', '1'),
                                    ('if (size < 29)', 'if (size < MINIMUM_STORED_CIPHERTEXT_BYTES)', 'int MINIMUM_STORED_CIPHERTEXT_BYTES', '29'),
                                    ('if (size <= 116)', 'if (size <= MAXIMUM_LOADED_CIPHERTEXT_BYTES)', 'int MAXIMUM_LOADED_CIPHERTEXT_BYTES', '116')],
    'EncryptedSessionRequestCache': [('if ("XMLHttpRequest".equalsIgnoreCase(request.getHeader("X-Requested-With")))', 'if (AJAX_REQUEST_VALUE.equalsIgnoreCase(request.getHeader("X-Requested-With")))', 'String AJAX_REQUEST_VALUE', '"XMLHttpRequest"')],
    'FormCsrfTokenRequestHandler': [('if ("_csrf".equals(URLDecoder.decode(key, StandardCharsets.UTF_8)))', 'if (CSRF_QUERY_PARAMETER.equals(URLDecoder.decode(key, StandardCharsets.UTF_8)))', 'String CSRF_QUERY_PARAMETER', '"_csrf"')],
    'EncryptedWebSessionRepository': [('if (current.version() == 999999999)', 'if (current.version() == MAXIMUM_SESSION_VERSION)', 'int MAXIMUM_SESSION_VERSION', '999_999_999')],
    'JdbcWebSessionStore': [('if (statement.executeUpdate() != 1)', 'if (statement.executeUpdate() != EXPECTED_INSERT_ROWS)', 'int EXPECTED_INSERT_ROWS', '1')],
    'SessionAttributes': [('if (operationTokens.size() > 10)', 'if (operationTokens.size() > MAXIMUM_SESSION_OPERATIONS)', 'int MAXIMUM_SESSION_OPERATIONS', '10')],
    'SessionOperationTokenLifecycle': [('if (pending + required.size() > 10)', 'if (pending + required.size() > MAXIMUM_SESSION_OPERATIONS)', 'int MAXIMUM_SESSION_OPERATIONS', '10'),
                                       ('if (tokens.size() == 10)', 'if (tokens.size() == MAXIMUM_SESSION_OPERATIONS)', 'int MAXIMUM_SESSION_OPERATIONS', '10')]}


def private_source(before, changes, constants):
    header = re.search(r'^public record SessionAttributes\([^{}]*\) \{', before, re.MULTILINE)
    if header is None:
        return declared_source(before, changes, constants)
    original = header.group(); placeholder = 'public final class SessionAttributes {'
    if before.count(original) != 1 or placeholder in before:
        raise ValueError('one exact record header; no compact constructor/record component change')
    changed = declared_source(before.replace(original, placeholder, 1), changes, constants)
    return changed.replace(placeholder, original, 1)


def main():
    bp = BASE/'PG5982-web-static-dispositions-v1/manifest.json'; bsha = '7c195396d242b237c2b254ebc07b544fd142663b9c2662758131b8795f665f97'
    rows = load(bp, bsha, SOURCE); groups = defaultdict(list)
    for row in rows:
        if row['status'] == 'NOT_REVIEWED_CURRENT_SOURCE' and row['rule'] == 'AvoidLiteralsInIfCondition' and row['sourcePath'].startswith('src/schubert-nk-web/'):
            groups[row['sourcePath']].append(row)
    if len(groups) != 24 or sum(map(len, groups.values())) != 42:
        raise ValueError('all24 remaining Web owners/42 actual warnings')
    baseline = W/'pg5984-web-form-selected921-v2/manifest.safe.json'; original = json.loads(baseline.read_bytes())
    if sha(baseline) != '31345aec12416f68120efea02a8979f2dbc1df7fc3b9d90c22ddce78a3a510d9' or original['actualExit'] != 0 or original['source'] != SOURCE:
        raise ValueError('actual previous selected source; semantic baseline only')
    plans = []
    for path, diagnostics in sorted(groups.items()):
        before = (ROOT/path).read_text(); simple = path.rsplit('/',1)[1][:-5]; changes = []; constants = set()
        for old, new, declaration, value in RULES[simple]:
            count = before.count(old)
            if count < 1:
                raise ValueError('exact actual declared condition required: '+simple+' '+old)
            changes.append((old,new,count)); constants.add('private static final '+declaration+' = '+value+';')
        if sum(c[2] for c in changes) != len(diagnostics) or any(r['sourceSha256'] != sha(ROOT/path) for r in diagnostics):
            raise ValueError('one edit per exact actual current raw condition')
        counters = original['coverage']['web']['classes'][path.split('/src/main/java/')[1][:-5]]
        if not all(counters[k]['missed'] == 0 and counters[k]['covered'] > 0 for k in ('LINE','METHOD','CLASS','BRANCH')):
            raise ValueError('affected class baseline has four explicit nonzero100 measures; not new-source success')
        after = formatted(private_source(before, changes, sorted(constants)))
        plans.append(dict(path=path, beforeSha256=sha(ROOT/path), predictedAfterSha256=hashlib.sha256(after.encode()).hexdigest(), changes=changes,
                          constants=sorted(constants), findingIds=[r['findingId'] for r in diagnostics], baselineCounters=counters, productionApplied=False))
    cp = BASE/'PG5980-web921-v1/cases.json'
    if sha(cp) != 'da5085f61400650f4cc10d8e159075599120d27634f2df0b047779f29f0bea1d':
        raise ValueError('existing actual semantic Test identities, no result import')
    cases = [r for r in json.loads(cp.read_bytes()) if r['module'] == 'web']
    if len(cases) != 913 or len({r['class'] for r in cases}) != 143:
        raise ValueError('unchanged fullWeb913/143')
    out = BASE/'PG5988-web-contract42-plan-v1'; os.umask(0o077); out.mkdir()
    value = dict(actualExit=0, source=SOURCE, sourcePlans=plans, selectedSourceFiles=24, selectedDiagnosticConditions=42,
                 baseManifestPath=bp.relative_to(ROOT).as_posix(), baseManifestSha256=bsha,
                 plannedWebCaseReferences=[{k:r[k] for k in ('class','caseNameSha256')} for r in cases], plannedWebCases=913, plannedWebSuites=143,
                 additionalGuardCases=8, sourceCodeApplied=False, testsExecuted=0, oldBaselineNotNewPt=True, ptAlternativeCompleted=0, formalAccepted=False, F03Accepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, sourceFiles=24, conditions=42, manifestSha256=sha(out/'manifest.json'), productionApplied=False)))


if __name__ == '__main__':
    main()
