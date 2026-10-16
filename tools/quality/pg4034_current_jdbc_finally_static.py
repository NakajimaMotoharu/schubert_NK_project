"""Fresh current typed JDBC precedence; unsupported two scopes remain explicit/unclassified."""
import inspect
import pg3940_jdbc_finally_contract_review as previous
from pg3966_literal_invariant_full_six import SOURCE

LABEL = 'PG4034-current-jdbc-finally-static-v1'
SLOT = 'pg4034-current-jdbc-finally-static-v1'


def server_source():
    raw = inspect.getsource(previous.server)
    replacements = {'source-full-PG3734': 'source-full-PG3966', 'PG3864-suppression-identity-review-v1': 'PG4032-current-identity-static-v1',
                    'PG3738-hygiene-whole-qualified-v1': 'PG3968-literal-invariant-whole-qualified-v1', 'PG3734-six-v1': 'PG3966-six-v1',
                    '3714': '3717', '1840': '1653', "before['technicalDispositions'] == 278": "before['technicalDispositions'] == 289",
                    "row['disposition'] == 'UNCLASSIFIED' and": "row['disposition'] in {'UNCLASSIFIED', 'REQUIRED_APPROVED_JDBC_FAILURE_PRECEDENCE'} and",
                    "resolved = facts(result.stdout); suite_hashes = {}; assessed = []": "resolved = facts(result.stdout); suite_hashes = {}; assessed = []; unsupported = []",
                    "require(row['id'] in {'PMD-7fff-1162', 'PMD-7fff-1167'}, 'only explicitly retained IOException-primary shapes may remain unassessed')":
                    "require(row['disposition'] == 'UNCLASSIFIED', 'unsupported shape remains unresolved'); unsupported.append({'id': row['id'], 'path': row['path'], 'sourceSha256': row['sourceSha256'], 'coordinates': row['coordinates'], 'reason': 'NO_MATCHING_TYPED_PRECEDENCE_SHAPE'})",
                    "len(assessed) == 26": "len(assessed) == 26 and len(unsupported) == 2",
                    "'newTechnicalAssessments': 26": "'currentTypedFinallyVerified': 26, 'newSourceRequalifiedScopes': 15",
                    "'unclassified': 1536": "'unclassified': 1349",
                    "'typedFactsSha256': sha(out / 'facts.safe.tsv')": "'typedFactsSha256': sha(out / 'facts.safe.tsv'), 'unsupportedCurrentScopes': unsupported"}
    for old, new in replacements.items():
        if old not in raw: raise ValueError('exact current JDBC shape boundary missing: ' + old)
        raw = raw.replace(old, new)
    raw = raw.replace('immutable current1653/278 source report', 'immutable current1653/289 source report')
    raw = raw.replace('other26 finally warnings unresolved including two IOException-primary scopes', 'other26 finally warnings unresolved; two selected current typed shapes explicitly held')
    marker = "    (out / 'all1653-dispositions.safe.json').write_text"
    if raw.count(marker) != 1: raise ValueError('one final current JDBC disposition boundary')
    raw = raw.replace(marker, "    require(sum(r['disposition'] != 'UNCLASSIFIED' for r in rows) == 304 and sum(r['disposition'] == 'UNCLASSIFIED' for r in rows) == 1349, 'actual exact current partition')\n" + marker)
    compile(raw, '<current seven-repository JDBC precedence>', 'exec')
    return raw


def main_source():
    raw = inspect.getsource(previous.main)
    for old, new in [('pg3738-hygiene-whole-qualified-v1', 'pg3968-literal-invariant-whole-qualified-v1'), ('pg3864-suppression-identity-review-v1', 'pg4032-current-identity-static-v1')]: raw = raw.replace(old, new)
    marker = 'inspect.getsource(f) for f in [require, facts, server]'
    if raw.count(marker) != 1: raise ValueError('one actual dynamic JDBC payload source boundary')
    return raw.replace(marker, '(server_source() if f is server else inspect.getsource(f)) for f in [require, facts, server]')


def main():
    values = {**previous.__dict__, 'SOURCE': SOURCE, 'LABEL': LABEL, 'SLOT': SLOT, 'server_source': server_source}
    exec(compile(server_source(), '<fresh actual current JDBC type analysis>', 'exec'), values)
    exec(compile(main_source(), '<current source-only JDBC qualification>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
