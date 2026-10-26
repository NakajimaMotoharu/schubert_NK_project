"""Independent15 catch-body/exception/header/raw identity and local-policy references; no Product execution."""
from collections import Counter
import copy
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10930-main-empty-catch-post-v1'
EXPECTED = {
    'PMD-00204':'FATAL_ROLLBACK_HALT_NO_ACK','PMD-00231':'FATAL_ROLLBACK_HALT_NO_ACK',
    'PMD-00261':'FATAL_ROLLBACK_HALT_NO_ACK','PMD-07342':'FATAL_ROLLBACK_HALT_NO_ACK',
    'PMD-02820':'ATTEMPTED_PURGE_FAILURE_STATE','PMD-02821':'HEALTH_FAILURE_STATE',
    'PMD-02890':'COMPLETION_DIAGNOSIS_PRESERVES_UNKNOWN','PMD-02893':'CADDY_BOUNDED_NOT_READY',
    'PMD-02906':'SERVICE_BOUNDED_NOT_LISTENING','PMD-03133':'VANISHED_FD_NOT_OWNED_EVIDENCE',
    'PMD-03141':'VANISHED_FD_NOT_OWNED_EVIDENCE','PMD-06133':'UNKNOWN_DIAGNOSIS_NOT_RELEASE',
    'PMD-06138':'UNKNOWN_FALLBACK_NOT_RELEASE','PMD-06144':'INTERRUPTED_TICK_NOT_RELEASE',
    'PMD-07274':'WEB_UNKNOWN_DIAGNOSIS_NOT_RELEASE'}


def contract(rows,original,hashes):
    if len(rows) != 15 or {r['id'] for r in rows} != set(EXPECTED):
        raise ValueError('all original15 once')
    for row in rows:
        old = original[row['id']]
        if row['source'] != SOURCE or row['path'] != old['path'] or row['sourceSha256'] != old['inputSha256'] or row['sourceSha256'] != hashes.get(row['path']):
            raise ValueError('exact current Main input')
        if row['attributes'] != old['attributes'] or row['rule'] != 'EmptyCatchBlock' or row['originalRowSha256'] != old['rowSha256']:
            raise ValueError('raw diagnostic identity')
        if row['policy'] != EXPECTED[row['id']] or not row['reason'] or row['catchBodyTokens'] != [] or not row['catchHeaderTokens']:
            raise ValueError('reviewed local policy and comment-only catch')
        if row['status'] != 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING' or row['currentWholeCaseRefs'] != [] or row['productTestsExecuted'] != 0 or row['coverage'] is not None:
            raise ValueError('no dynamic/whole-source qualification')
        if row['ptExecutionExempt'] is not False or row['scopeGeneralized'] is not False or row['rawWarningRetained'] is not True or row['oldRuntimeReassigned'] is not False:
            raise ValueError('no test exemption/suppression/source transfer')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10928-main-empty-catch-policy-v1/manifest.json'
    primary = data.read_checked(path,'6e1ed0ff67610462fd6d3e0830dc5bd8ccaad18248a7625f351707de9fad340f')
    rows = data.read_checked(path.parent/'contexts.json',primary['contextsSha256'])
    raw = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original = {r['id']:r for r in raw}
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    hashes = normal['begin']['inputHashes']
    assert primary['actualExit'] == 0 and primary['source'] == normal['source'] == SOURCE
    contract(rows,original,hashes)
    assert {r['id'] for r in raw if r['sourceKind'] == 'MAIN' and r['rule'] == 'EmptyCatchBlock'} == set(EXPECTED)
    for row in rows:
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == row['sourceSha256']
        lines = text.splitlines(keepends=True)
        line = int(row['attributes']['beginline'])
        offset = sum(len(v) for v in lines[:line-1])
        match = re.search(r'\bcatch\s*\(([^)]*)\)\s*\{',text[offset:])
        assert match and match.start() < len(lines[line-1])
        end = text.index('}',offset+match.end())
        assert canonical(text[offset+match.end():end]) == []
        assert canonical(match.group(1)) == row['catchHeaderTokens']
        if row['policy'] == 'VANISHED_FD_NOT_OWNED_EVIDENCE':
            assert row['catchHeaderTokens'][0] == 'NoSuchFileException'
        elif row['policy'] == 'ATTEMPTED_PURGE_FAILURE_STATE':
            assert row['catchHeaderTokens'][0] == 'ArtemisExpiryPurgeException'
        elif row['policy'] == 'HEALTH_FAILURE_STATE':
            assert row['catchHeaderTokens'][0] == 'ArtemisManagementReadinessException'
        elif row['policy'] == 'INTERRUPTED_TICK_NOT_RELEASE':
            assert row['catchHeaderTokens'][0] == 'InterruptedException'
        if row['policy'] == 'FATAL_ROLLBACK_HALT_NO_ACK':
            assert row['catchHeaderTokens'][:3] == ['RuntimeException','|','Error']
            assert 'halted.set(true);' in text and 'rollbackAttempted.compareAndSet(false, true)' in text
        if row['id'] == 'PMD-07342':
            assert 'if (selectedFatal != null) throw selectedFatal;' in text
    for p,digest in primary['approvedDesignHashes'].items():
        assert data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT)) == digest
    prior_paths = [
        ('PG10910-current-f03-web-metric-delta-v1','7c283b56f26f3c73e1b198dee9c91000278b10961713c6de2766c728acf85d66'),
        ('PG10916-main-null-crypto-resource-context-v1','d41f3747340987cf0a408a71e2224b07b9ec5f08664b79f687b75b240f19492d'),
        ('PG10922-main-null-owner-route-context-v1','9360be53ed58a1cf468f0968ca1b91b51fe288a4e217b6576fd342e6c1a88480')]
    prior_ids = set()
    for name,digest in prior_paths:
        previous = data.read_checked(data.BASE/name/'manifest.json',digest)
        if 'deltaSha256' in previous:
            delta = data.read_checked(data.BASE/name/'delta.json',previous['deltaSha256'])
            prior_ids.update(r['id'] for r in delta['legacyContextOverlay'])
            prior_ids.update(r['id'] for r in delta['freshRows'])
        else:
            values = data.read_checked(data.BASE/name/'contexts.json',previous['contextsSha256'])
            prior_ids.update(r['id'] for r in values)
    assert not set(EXPECTED)&prior_ids
    assert len({r['path'] for r in rows}) == 10 and Counter(r['policy'] for r in rows) == Counter(EXPECTED.values())
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('source','old'),('sourceSha256','0'*64),('policy','UNKNOWN'),('catchBodyTokens',['return',';']),
                        ('status','PASS'),('ptExecutionExempt',True),('currentWholeCaseRefs',['old-case']),
                        ('scopeGeneralized',True),('productTestsExecuted',15)]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try: contract(bad,original,hashes)
        except ValueError: pass
        else: raise AssertionError('incomplete/forged/test-exemption metadata accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),contextsSha256=primary['contextsSha256'],
        mainFindings=15,mainSources=10,metadataNegativeVectors=len(bads),sourceDerivedRaw=9248,
        referencedRows=2711,currentWholePending=31,noCurrentReference=6537,
        rawWarningRemoved=False,wholeF03Accepted=False,productTestsExecuted=0,coverage=None,
        ptExecutionExempt=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
