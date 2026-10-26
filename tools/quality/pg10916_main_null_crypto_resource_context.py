"""Five unchanged Main static contexts, preserving original tests/coverage and current whole pending."""
from collections import Counter
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10916-main-null-crypto-resource-context-v1'
CANONICAL = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/CanonicalField.java'
CODEC = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.java'
IDS = {'PMD-00124','PMD-00125','PMD-00128','PMD-00129','PMD-00130'}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    assert normal['actualExit'] == normal['testsExecuted'] == 0 and normal['source'] == SOURCE
    current = normal['begin']['inputHashes']
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    targets = [r for r in original if r['id'] in IDS]
    assert len(targets) == 5
    assert {r['path'] for r in targets} == {CANONICAL,CODEC}
    assert all(r['inputSha256'] == current[r['path']] == data.sha((data.ROOT/r['path']).read_bytes()) for r in targets)
    legacy_path = data.BASE/'PG5426-static-findings-v1/manifest.json'
    legacy = data.read_checked(legacy_path,'41ddbd7c37b2bbcbc7ee69ef911c4743f59b29523559068581622c24efdb42bc')
    assert legacy['actualExit'] == 0
    codec_proof_path = data.BASE/'PG9876-snapshot-nonce-quality-source-post-v1/manifest.json'
    codec_proof = data.read_checked(codec_proof_path,'00eb2fb3eb8d9cb763e7a2a91eb0aa0352eff63ba17725b5f305d75a7e939f48')
    assert codec_proof['actualExit'] == 0 and codec_proof['rawPmdFindings'] == 3 and codec_proof['wholeF03Accepted'] is False
    codec_normal = data.read_checked(data.BASE/'PG9866-snapshot-nonce-six-compile-v1/manifest.json',
        '2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535')
    assert codec_normal['source'] == codec_proof['source'] and codec_normal['begin']['inputHashes'][CODEC] == current[CODEC]
    old_three = data.read_checked(codec_proof_path.parent/'pmd-three-applicability.json',codec_proof['pmdApplicabilitySha256'])
    assert len(old_three) == 3 and all(r['rawFindingRetained'] is True for r in old_three)
    canonical_source = (data.ROOT/CANONICAL).read_text()
    assert canonical_source.count('value == null ? null : value.clone()') == 2
    assert 'byte @Nullable [] value' in canonical_source and 'Arrays.fill(value, (byte) 0)' in canonical_source
    codec_source = (data.ROOT/CODEC).read_text()
    assert 'this.currentKey = validateKey(currentKey, "currentKey");' in codec_source
    assert 'return key.clone();' in codec_source and 'Objects.requireNonNull(key, name);' in codec_source
    design_path = 'documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md'
    design = subprocess.check_output(['git','show','origin/main:'+design_path],cwd=data.ROOT)
    assert b'0xFFFFFFFF' in design and 'emptyはlength 0として区別する'.encode() in design
    old_doc = data.ROOT/'evidence/01_PT/018_NK-OPS-001/1994_Snapshot乱数異常時buffer消去_実行結果.md'
    assert data.sha(old_doc.read_bytes()) == '52b399e08b41dfeaf411b87e8badb4640c5a366a549139971aa11170d1329cc4'
    result = []
    for row in targets:
        path = row['path']
        if path == CANONICAL:
            matches = [r for r in legacy['findings'] if r['sourcePath'] == path and r['rule'] == row['rule'] and
                all(r[k] == row['attributes'][k] for k in ('beginline','endline','begincolumn','endcolumn'))]
            assert len(matches) == 1
            old = matches[0]
            assert old['sourceSha256'] == current[path] and old['status'] == 'REQUIRED_CONTRACT' and old['reason'] and old['wholeCaseRefs']
            historical_source = legacy['source']
            disposition = old['status']
            basis = old['reason']
            evidence = dict(manifestSha256=data.sha(legacy_path.read_bytes()),originalFindingId=old['findingId'],
                historicalWholeCaseRefs=old['wholeCaseRefs'],approvedDesignSha256=data.sha(design))
        else:
            matches = [r for r in old_three if r['rule'] == row['rule'] and
                {k:v for k,v in r.items() if k not in ('classification','rawFindingRetained','message')} == row['attributes']]
            assert len(matches) == 1
            old = matches[0]
            historical_source = codec_proof['source']
            disposition = old['classification']
            basis = 'Existing exact Main source/JDK proof: caller key validation label, or owned Deflater/Inflater end() in finally after acquisition-gap correction; not old runtime transfer.'
            evidence = dict(manifestSha256=data.sha(codec_proof_path.read_bytes()),pmdApplicabilitySha256=codec_proof['pmdApplicabilitySha256'],
                normalManifestSha256='2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535',
                historicalSelectedTests=codec_proof['selectedTests'],historicalTargetFour100=codec_proof['targetUnitFour100'])
        result.append(dict(id=row['id'],path=path,source=SOURCE,sourceSha256=current[path],rule=row['rule'],attributes=row['attributes'],
            originalRowSha256=row['rowSha256'],priorSource=historical_source,technicalDisposition=disposition,basis=basis,
            evidence=evidence,status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',currentWholeCaseRefs=[],priorRuntimeReassigned=False,
            newProductExecutions=0,newCoverage=None,rawWarningRetained=True,scopeGeneralized=False))
    assert len(result) == 5 and Counter(r['rule'] for r in result) == Counter(NullAssignment=1,ReturnEmptyCollectionRatherThanNull=1,HardCodedCryptoKey=1,CloseResource=2)
    parent_path = data.BASE/'PG10910-current-f03-web-metric-delta-v1/manifest.json'
    parent = data.read_checked(parent_path,'7c283b56f26f3c73e1b198dee9c91000278b10961713c6de2766c728acf85d66')
    parent_delta = data.read_checked(parent_path.parent/'delta.json',parent['deltaSha256'])
    assert not IDS & {r['id'] for r in parent_delta['legacyContextOverlay']}
    assert not IDS & set(parent_delta['removedFindingIds']) and parent['source'] == SOURCE
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',result)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),parentDeltaManifestSha256=data.sha(parent_path.read_bytes()),
        exactMainSourceReused=2,findingsRebound=5,technicalRequiredContract=2,technicalFalsePositive=3,currentWholePendingAdded=5,
        priorSourceDerivedRaw=9248,sourceDerivedRaw=9248,referencedRowsBefore=2686,referencedRowsAfter=2691,
        currentWholePendingBefore=6,currentWholePendingAfter=11,noCurrentReferenceBefore=6562,noCurrentReferenceAfter=6557,
        rawWarningsRemoved=0,newProductionChanges=0,oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None,
        actualViolationCount=None,wholeF03Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
