"""Explicit saved-static schema adapter and first shared-reader consumer, no new review/PT."""
from collections import Counter, defaultdict
import json
import subprocess
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
import jdbc_role_metadata_v1 as core

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE = '7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT = data.BASE / 'PG16074-four-repository-saved-reference-join-v1'
OLD = ('PG11570-batch-four-repository-source-review-v1', '21a66250b1d54e19576b84b3144a2ee4395925b538401a07934eaf080c2bd77b')
OLD_POST = ('PG11572-batch-four-repository-source-review-post-v1', '5fb3dcbaac87a9518a42ef7c292c6cfe1d5465d6919139922042950270d4d522')
PRIOR = ('PG16058-cleanup-terminal-current-static-review-v1', 'ca58d40993d3e8c9cf3cd008c64de040be242f306adf474e7274da5eb4946864')
CORE_PIN = 'cd1c4ef43d458dcb36f6a1f6f9e3e577c679b6b4e060f28c20e7e8217c379759'
FILES = {'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/' + name + '.java' for name in ('BackupStepRepository', 'CleanupStepRepository', 'InspectionSummaryRepository', 'RunReferenceRepository')}
CORE_PROOFS = [('PG16068-jdbc-role-metadata-qualification-v1', '002ae110aef0d25c2251f1db99dd6162d46cba4d31859afa05c59452a7309462'), ('PG16070-jdbc-role-metadata-post-v1', 'cf205ced9dbdb41894dbdd70997425c2145c58daf4193decebb24f8fd8d8d475')]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(pair):
    return data.read_checked(data.BASE / pair[0] / 'manifest.json', pair[1])


def signature(row):
    return json.dumps([row['path'], row['sourceSha256'], row['attributes']['rule'], row['attributes']], sort_keys=True)


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    old, old_post, prior = [read(pair) for pair in (OLD, OLD_POST, PRIOR)]
    require(old['actualExit'] == old_post['actualExit'] == prior['actualExit'] == 0 and old['source'] == old_post['source'] == OLD_SOURCE and prior['source'] == SOURCE and SOURCE != OLD_SOURCE and old_post['primaryManifestSha256'] == OLD[1], 'old static source remains old, not runtime reassignment')
    review = data.read_checked(data.BASE / OLD[0] / 'review.json', old['reviewSha256'])
    queue = data.read_checked(data.BASE / PRIOR[0] / 'remaining-selected-review-queue.json', prior['queueSha256'])
    require(len(queue) == 833 and prior['combinedPurposeReviewed'] == 96 and prior['combinedPurposeOrReferenceRows'] == 658, 'current separate purpose/reference domains')
    rows = review['rows']
    require(len(rows) == 48 and {r['path'] for r in rows} == FILES and Counter(r['disposition'] for r in rows) == Counter(REQUIRED_CONTRACT=40, FALSE_POSITIVE=8), 'complete fixed four-source static review')
    require(all(data.sha((data.ROOT / path).read_bytes()) == digest for path, digest in review['mainSourceHashes'].items()) and len(review['mainSourceHashes']) == 6, 'all four Main/helper/exception exact bytes')
    require(review['productTestsExecuted'] == 0 and review['historicalRuntimeImportedAsCurrent'] is False and review['coverage'] is None and review['sourceCodeChanged'] is False, 'saved static purposes only')
    proofs = [read(pair) for pair in CORE_PROOFS]
    require(all(v['actualExit'] == 0 and v['source'] == SOURCE for v in proofs) and proofs[0]['toolMetadataTests'] == 8 and proofs[1]['independentMetadataNegativeVectors'] == 14 and data.sha((data.ROOT / 'tools/quality/jdbc_role_metadata_v1.py').read_bytes()) == CORE_PIN, 'fixed qualified small reader')
    raw_manifest = data.read_checked(data.BASE / 'PG15930-f03-current-main-review-join-v2/manifest.json', '7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    observations = data.read_checked(data.BASE / 'PG15930-f03-current-main-review-join-v2/current-main-observations.json', raw_manifest['observationsSha256'])
    actual_by_id = {r['staticObservationId']: r for r in observations}
    old_by_signature = {signature(r): (index, r) for index, r in enumerate(rows)}
    require(len(old_by_signature) == 48, 'all individual old coordinates unique')
    current_keys = defaultdict(list)
    for row in queue:
        current_keys[signature(row)].append(row)
    require(all(len(current_keys[key]) == 1 for key in old_by_signature), 'all48 current exact byte/attributes and multiplicity')
    links = []
    for row in queue:
        if signature(row) not in old_by_signature:
            continue
        index, saved = old_by_signature[signature(row)]
        require(saved['rawWarningRetained'] is True and saved['oldRuntimeReassigned'] is saved['ptExecutionExempt'] is False and saved['productTestsExecuted'] == 0 and saved['reason'], 'explicit old retained-static schema')
        text = (data.ROOT / row['path']).read_text()
        _, _, token = span(text, row['attributes'])
        require(data.sha(token.encode()) == saved['currentSpanSha256'] and saved['diagnosticTextSha256'] == data.sha(actual_by_id[row['id']]['message'].encode()), 'exact current span and diagnostic text, not coordinates only')
        links.append(dict(**row, currentSource=SOURCE, staticReviewSource=OLD_SOURCE, oldFindingId=saved['id'], oldDisposition=saved['disposition'],
            reference=dict(manifest=OLD[0] + '/manifest.json', manifestSha256=OLD[1], reviewSha256=old['reviewSha256'], rowOrdinal=index, rowSha256=data.sha(json.dumps(saved, sort_keys=True).encode())),
            meaning='EXISTING_STATIC_REFERENCE_ONLY_NO_NEW_REVIEW_OR_RUNTIME_PASS'))
    require(len(links) == len({r['id'] for r in links}) == 48, 'all selected references, no duplicates')
    use = []
    alias_checked = alias_unsupported = conditional_count = 0
    for path in sorted(FILES):
        text = (data.ROOT / path).read_text()
        selected = [r for r in rows if r['path'] == path]
        facts = [r['currentSourceFacts']['ownership'] for r in selected if r['currentSourceFacts']]
        expected = {(r['primary'], r['secondary']) for r in facts}
        actual = core.close_conditions(text)
        require(len(actual) == len(expected) == 2 and {(p, c) for p, c, start, stop in actual} == expected, 'two exact current conditional roles per source')
        conditional_count += len(actual)
        aliases = []
        for row in selected:
            if row['attributes']['rule'] != 'CloseResource':
                continue
            line = text.splitlines()[int(row['attributes']['beginline']) - 1].strip()
            match = re.fullmatch(r'var ([A-Za-z_][A-Za-z_0-9]*) = present\((statement|rows|row)\);', line)
            require(match is not None, 'exact reviewed alias form')
            symbol, resource = match.groups()
            _, _, token = span(text, row['attributes'])
            require(symbol == token, 'all eight old alias span associations retained')
            if resource in ('statement', 'rows'):
                require(core.alias_variable(line, resource) == symbol, 'supported exact original resource spelling')
                alias_checked += 1
                aliases.append(dict(resource=resource, symbol=symbol, sharedReaderChecked=True))
            else:
                alias_unsupported += 1
                aliases.append(dict(resource=resource, symbol=symbol, sharedReaderChecked=False, reason='SINGULAR_ROW_UNSUPPORTED_BY_V1_NOT_INVOKED_OR_RENAMED'))
        use.append(dict(path=path, sourceSha256=review['mainSourceHashes'][path], conditionalCandidates=[dict(primary=p, cleanup=c, start=start, end=stop) for p, c, start, stop in actual], aliases=aliases))
    require((conditional_count, alias_checked, alias_unsupported) == (8, 6, 2), 'honest partial library grammar, no widening')
    design = 'documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md'
    text = (data.ROOT / design).read_text()
    require(subprocess.check_output(['git', 'show', 'origin/main:' + design], cwd=data.ROOT) == text.encode() and all(marker in text for marker in ('SSC063/PG179', 'SSC063/PG181', 'SSC063/PG182', 'SQL primary', '未知')), 'current approved precedence, not old whole-design requalification')
    ids = {r['id'] for r in links}
    remaining = [r for r in queue if r['id'] not in ids]
    for witness in (old, old_post, prior, *proofs):
        verify(witness['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'references.json', links)
    data.write(OUT / 'remaining-selected-review-queue.json', remaining)
    data.write(OUT / 'shared-reader-use.json', use)
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=SOURCE, staticReviewSource=OLD_SOURCE,
        oldReviewManifestSha256=OLD[1], oldReviewPostSha256=OLD_POST[1], oldReviewFileSha256=old['reviewSha256'], priorManifestSha256=PRIOR[1], priorQueueSha256=prior['queueSha256'],
        referencesSha256=data.sha((OUT / 'references.json').read_bytes()), queueSha256=data.sha((OUT / 'remaining-selected-review-queue.json').read_bytes()), sharedReaderUseSha256=data.sha((OUT / 'shared-reader-use.json').read_bytes()),
        newReferenceConnections=48, oldSelectedReferences=562, combinedSelectedReferences=610, previousPurposeReviewed=96, newManualReviews=0, combinedPurposeOrReferenceRows=706, remainingSelectedUnreferenced=785,
        currentSourceHashes=review['mainSourceHashes'], currentDesignSha256=data.sha(text.encode()), oldDesignReferenceRetained=review['approvedDesign'],
        sharedReaderSourceSha256=CORE_PIN, sharedReaderQualificationReferences=CORE_PROOFS, sharedConditionalSites=8, sharedAliasesChecked=6, sharedAliasesUnsupportedNotInvoked=2, unsupportedResourceNamesRenamed=False,
        rawSuppressed=0, productTestsExecuted=0, oldProductToolsReexecuted=0, oldRuntimeTransferred=False, sourceChanged=False, externalActions=0,
        wholeF03Accepted=False, whole451Accepted=False, newAccepted=0, formalUpdated=False, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, addedReferences=len(links), remaining=len(remaining), sharedConditionalSites=conditional_count)))


if __name__ == '__main__':
    main()
