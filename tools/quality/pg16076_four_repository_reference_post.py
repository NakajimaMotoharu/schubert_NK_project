"""Independent saved-row/source/dual-span reconstruction; no original tools/Product executed."""
from collections import Counter
import copy
import hashlib
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE = '7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
RAW = data.BASE / 'PG16075-four-repository-saved-reference-join-v2'
PIN = '44b10dd7416d940b650c77325dd48e195fdf2dacc749fa98e75b063464bc874d'
OUT = data.BASE / 'PG16076-four-repository-reference-post-v1'
OLD = data.BASE / 'PG11570-batch-four-repository-source-review-v1'
OLD_PIN = '21a66250b1d54e19576b84b3144a2ee4395925b538401a07934eaf080c2bd77b'
PRIOR = data.BASE / 'PG16058-cleanup-terminal-current-static-review-v1'
PRIOR_PIN = 'ca58d40993d3e8c9cf3cd008c64de040be242f306adf474e7274da5eb4946864'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def wire(value):
    return json.dumps(value, sort_keys=True)


def assess(p, links, remaining, use, expected, expected_remaining, expected_use):
    require(p['actualExit'] == 0 and p['source'] == SOURCE and p['staticReviewSource'] == OLD_SOURCE and SOURCE != OLD_SOURCE, 'old static source not rewritten as new runtime source')
    require((p['newReferenceConnections'], p['oldSelectedReferences'], p['combinedSelectedReferences'], p['previousPurposeReviewed'], p['newManualReviews'], p['combinedPurposeOrReferenceRows'], p['remainingSelectedUnreferenced']) == (48, 562, 610, 96, 0, 706, 785), 'references and new manual purposes are different')
    require((p['sharedConditionalSites'], p['sharedAliasesChecked'], p['sharedAliasesUnsupportedNotInvoked']) == (8, 6, 2) and p['unsupportedResourceNamesRenamed'] is False, 'no hidden widening of shared alias grammar')
    require(p['legacyExtentIsCanonicalPmdToken'] is p['legacyExporterReexecuted'] is False and p['legacyWhitespaceExtensionCounts'] == {'SPACE': 40, 'LF': 8} and p['oldFailedConsumerFrozen'] is True, 'explicit historical plus-one representation, not canonical token')
    require(p['legacySpanExporterSha256'] == '372375bf808bf1662391d1658aab99ef6886895d75db882dca812fa228964268' and p['sharedReaderSourceSha256'] == 'cd1c4ef43d458dcb36f6a1f6f9e3e577c679b6b4e060f28c20e7e8217c379759', 'exact two separate reader versions')
    require(wire(links) == wire(expected) and wire(remaining) == wire(expected_remaining) and wire(use) == wire(expected_use), 'all48 current IDs/old rows and dual spans, all785 pending and precise partial library use')
    for field in ('rawSuppressed', 'productTestsExecuted', 'oldProductToolsReexecuted', 'externalActions', 'newAccepted'):
        require(type(p[field]) is int and p[field] == 0, 'no Product/review/authority promotion: ' + field)
    for field in ('oldRuntimeTransferred', 'sourceChanged', 'wholeF03Accepted', 'whole451Accepted', 'formalUpdated'):
        require(p[field] is False, 'unqualified runtime/gate remains unqualified: ' + field)
    require(p['effortPercent'] is None, 'unknown effort remains null')


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(RAW / 'manifest.json', PIN)
    links = data.read_checked(RAW / 'references.json', p['referencesSha256'])
    remaining = data.read_checked(RAW / 'remaining-selected-review-queue.json', p['queueSha256'])
    use = data.read_checked(RAW / 'shared-reader-use.json', p['sharedReaderUseSha256'])
    old = data.read_checked(OLD / 'manifest.json', OLD_PIN)
    review = data.read_checked(OLD / 'review.json', old['reviewSha256'])
    prior = data.read_checked(PRIOR / 'manifest.json', PRIOR_PIN)
    queue = data.read_checked(PRIOR / 'remaining-selected-review-queue.json', prior['queueSha256'])
    require(old['source'] == OLD_SOURCE and old['actualExit'] == prior['actualExit'] == 0 and prior['source'] == SOURCE and len(queue) == 833 and p['priorQueueSha256'] == prior['queueSha256'] and p['oldReviewFileSha256'] == old['reviewSha256'] and p['oldReviewManifestSha256'] == OLD_PIN and p['priorManifestSha256'] == PRIOR_PIN, 'fixed unchanged independent predecessors')
    require(all(data.sha((data.ROOT / path).read_bytes()) == h for path, h in review['mainSourceHashes'].items()) and review['mainSourceHashes'] == p['currentSourceHashes'], 'all six identical current source bytes')
    raw = data.read_checked(data.BASE / 'PG15930-f03-current-main-review-join-v2/manifest.json', '7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    observations = data.read_checked(data.BASE / 'PG15930-f03-current-main-review-join-v2/current-main-observations.json', raw['observationsSha256'])
    obs = {r['staticObservationId']: r for r in observations}
    expected = []
    whitespace = Counter()
    for current in queue:
        candidates = [(i, r) for i, r in enumerate(review['rows']) if r['path'] == current['path'] and r['sourceSha256'] == current['sourceSha256'] and r['attributes'] == current['attributes']]
        if not candidates:
            continue
        require(len(candidates) == 1, 'exact individual old occurrence')
        i, row = candidates[0]
        text = (data.ROOT / current['path']).read_text()
        lines = text.splitlines(keepends=True)
        a = current['attributes']
        start = sum(len(line) for line in lines[:int(a['beginline']) - 1]) + int(a['begincolumn']) - 1
        end = sum(len(line) for line in lines[:int(a['endline']) - 1]) + int(a['endcolumn']) - 1
        require(0 <= start < end < len(text) and text[end] in (' ', '\n'), 'canonical half-open plus exactly one known whitespace legacy extent')
        require(digest(text[start:end + 1]) == row['currentSpanSha256'] and digest(obs[current['id']]['message']) == row['diagnosticTextSha256'] and row['rawWarningRetained'] is True and row['reason'] and row['productTestsExecuted'] == 0 and row['oldRuntimeReassigned'] is row['ptExecutionExempt'] is False, 'all old hash/source/diagnostic/reason retained, no normalization')
        whitespace['SPACE' if text[end] == ' ' else 'LF'] += 1
        expected.append(dict(**current, currentSource=SOURCE, staticReviewSource=OLD_SOURCE, canonicalSpanStart=start, canonicalSpanEndExclusive=end, canonicalSpanSha256=digest(text[start:end]), legacyExtentSha256=row['currentSpanSha256'], legacyAdditionalWhitespace=repr(text[end]), legacyExtentIsCanonicalPmdToken=False, spanSchema='CANONICAL_END_EXCLUSIVE_AND_PRESERVED_LEGACY_PLUS_ONE_WHITESPACE_EXTENT', oldFindingId=row['id'], oldDisposition=row['disposition'], reference=dict(manifest=OLD.name + '/manifest.json', manifestSha256=OLD_PIN, reviewSha256=old['reviewSha256'], rowOrdinal=i, rowSha256=digest(wire(row))), meaning='EXISTING_STATIC_REFERENCE_ONLY_NO_NEW_REVIEW_OR_RUNTIME_PASS'))
    require(len(expected) == len({r['id'] for r in expected}) == 48 and whitespace == Counter(SPACE=40, LF=8), 'all legacy representations explicitly counted')
    ids = {r['id'] for r in expected}
    expected_remaining = [r for r in queue if r['id'] not in ids]
    expected_use = []
    pattern = re.compile(r'if \(JdbcResourceFailures\.replace\((statementFailure|rowFailure|rowsFailure), ([A-Za-z_][A-Za-z_0-9]*)\)\) throw \2;')
    for path in sorted({r['path'] for r in review['rows']}):
        text = (data.ROOT / path).read_text()
        selected = [r for r in review['rows'] if r['path'] == path]
        pairs = {(r['currentSourceFacts']['ownership']['primary'], r['currentSourceFacts']['ownership']['secondary']) for r in selected if r['currentSourceFacts']}
        found = list(pattern.finditer(text))
        require(len(found) == len(pairs) == 2 and {m.groups() for m in found} == pairs, 'independent current close role reconstruction')
        aliases = []
        for row in selected:
            if row['attributes']['rule'] != 'CloseResource':
                continue
            line = text.splitlines()[int(row['attributes']['beginline']) - 1].strip()
            match = re.fullmatch(r'var ([A-Za-z_][A-Za-z_0-9]*) = present\((statement|rows|row)\);', line)
            require(match is not None, 'literal supported or explicitly unsupported spelling')
            symbol, resource = match.groups()
            item = dict(resource=resource, symbol=symbol, sharedReaderChecked=resource != 'row')
            if resource == 'row':
                item['reason'] = 'SINGULAR_ROW_UNSUPPORTED_BY_V1_NOT_INVOKED_OR_RENAMED'
            aliases.append(item)
        expected_use.append(dict(path=path, sourceSha256=review['mainSourceHashes'][path], conditionalCandidates=[dict(primary=m.group(1), cleanup=m.group(2), start=m.start(), end=m.end()) for m in found], aliases=aliases))
    assess(p, links, remaining, use, expected, expected_remaining, expected_use)
    negatives = []
    for key, value in [('source', OLD_SOURCE), ('staticReviewSource', SOURCE), ('newReferenceConnections', 0), ('combinedSelectedReferences', 706), ('previousPurposeReviewed', 144), ('newManualReviews', 48), ('combinedPurposeOrReferenceRows', 1491), ('remainingSelectedUnreferenced', 0), ('sharedConditionalSites', 48), ('sharedAliasesChecked', 8), ('sharedAliasesUnsupportedNotInvoked', 0), ('unsupportedResourceNamesRenamed', True), ('legacyExtentIsCanonicalPmdToken', True), ('legacyExporterReexecuted', True), ('legacyWhitespaceExtensionCounts', {}), ('rawSuppressed', 48), ('productTestsExecuted', 48), ('oldRuntimeTransferred', True), ('wholeF03Accepted', True), ('newAccepted', True), ('effortPercent', 100)]:
        bad = copy.deepcopy(p)
        bad[key] = value
        try:
            assess(bad, links, remaining, use, expected, expected_remaining, expected_use)
        except ValueError:
            negatives.append(key)
        else:
            raise ValueError('unrejected semantic/source representation mutation: ' + key)
    for field, value in [('canonicalSpanSha256', '0' * 64), ('legacyExtentSha256', '0' * 64), ('canonicalSpanEndExclusive', 0), ('legacyAdditionalWhitespace', repr('X')), ('spanSchema', 'CANONICAL_ONLY'), ('staticReviewSource', SOURCE), ('meaning', 'PASS')]:
        bad = copy.deepcopy(links)
        bad[0][field] = value
        try:
            assess(p, bad, remaining, use, expected, expected_remaining, expected_use)
        except ValueError:
            negatives.append('row-' + field)
        else:
            raise ValueError('unrejected reference mutation: ' + field)
    for label, rr, qq, uu in [('missing-ref', links[:-1], remaining, use), ('duplicate-ref', links[1:] + [links[1]], remaining, use), ('lost-pending', links, remaining[:-1], use), ('hidden-partial-reader', links, remaining, [])]:
        try:
            assess(p, rr, qq, uu, expected, expected_remaining, expected_use)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected structural mutation: ' + label)
    historical_tools = {}
    for filename in ('pg11569_four_repository_scope_facts.py', 'pg11570_batch_four_repository_source_review.py', 'pg11572_batch_four_repository_source_review_post.py', 'pg11574_current_four_repository_reason_delta.py', 'pg11575_current_four_repository_reason_delta_post.py'):
        historical_tools[filename] = data.sha((data.ROOT / 'tools/quality' / filename).read_bytes())
    require(historical_tools['pg11569_four_repository_scope_facts.py'] == p['legacySpanExporterSha256'] and data.sha((data.ROOT / 'tools/quality/pg16074_four_repository_saved_reference_join.py').read_bytes()) == 'a4432eec0516a9a18ed478c046c53615871c0093a4cc150cdd66cb32e488fbf7', 'old exporter/failed consumer frozen')
    verify(old['invocation'])
    verify(prior['invocation'])
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation, parentManifestSha256=PIN,
        independentMetadataNegativeVectors=len(negatives), negativeLabels=negatives, newReferenceConnections=48, newManualReviews=0,
        combinedSelectedReferences=610, previousPurposeReviewed=96, combinedPurposeOrReferenceRows=706, remainingSelectedUnreferenced=785,
        legacyWhitespaceExtensionCounts=dict(whitespace), historicalToolHashes=historical_tools,
        historicalSpansNotCanonicalPmdTokens=True, oldFailedConsumerFrozen=True,
        sharedConditionalSites=8, sharedAliasesChecked=6, sharedAliasesUnsupportedNotInvoked=2,
        oldProductToolsReexecuted=0, productTestsExecuted=0, oldRuntimeTransferred=False, externalActions=0,
        newAccepted=0, formalUpdated=False, effortPercent=None, wholeF03Accepted=False, whole451Accepted=False))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentMetadataNegativeVectors=len(negatives), references=48, remaining=785)))


if __name__ == '__main__':
    main()
