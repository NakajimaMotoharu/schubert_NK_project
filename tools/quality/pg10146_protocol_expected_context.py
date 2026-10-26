"""Bind a human source-context review of exactly 95 sites; never execute target code."""
from collections import Counter
from pathlib import Path
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

COUNTS = dict(AuthenticationErrorProfileTest=3,FieldCodecTest=11,MessageCodecTest=1,
    PayloadCodecTest=6,PayloadGoldenVectorTest=6,LargeResultRecordCodecTest=2,HeaderModelTest=5,
    IndependentNamedFieldOracle=12,PayloadTypeCatalogTest=4,SemanticFieldValueTest=23,
    ProtocolSemanticTypeTest=10,EnumWireCompatibilityTest=1,JstWireTimestampTest=4,BrokerTopologyTest=7)
FIXTURES = {
    'layouts-ui233.tsv':'c4f290595f5cabf19c11877e2dea95627b4d42490116431bac3bfde58950d711',
    'fields-ui234-236.tsv':'b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b',
    'named-accessors-independent.tsv':'27b9a458374f5b9edda50d78fae42ee76dabf15d8d1ecd9c94e56dbab63162d5',
    'named-types-ss323.tsv':'9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76',
    'payload-golden-ui234-236.tsv':'49bb76ec610216042f8e53ed548f4d5e52707a8bbf930a9fc6c93300dfa24839'}


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10146-protocol-expected-context-v1'
    assert not out.exists()
    prior = data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/manifest.json',
        'f5dafc428c0e2367f79e0e59cd91b125639a88880f7be7bad72e879c0509527c')
    sites = data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/sites.json',prior['sitesJsonSha256'])
    selected = [r for r in sites if 'schubert-nk-protocol/' in r['path'] and r['expectedMethodSelectors'] and not r['sharedDirectMethodSelectors']]
    assert len(selected) == 95 and Counter(Path(r['path']).stem for r in selected) == COUNTS
    source_hashes = {r['path']:r['sourceSha256'] for r in selected}
    assert len(source_hashes) == 14 and all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in source_hashes.items())
    fixtures = {'src/schubert-nk-protocol/src/test/resources/protocol/'+p:h for p,h in FIXTURES.items()}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in fixtures.items())
    companion_paths = [p for p in prior['sourceHashes'] if Path(p).name in ('LayoutMetadataTest.java','LayoutFieldCatalogTest.java')]
    assert len(companion_paths) == 2
    companions = {p:prior['sourceHashes'][p] for p in companion_paths}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in companions.items())
    record = 'evidence/01_PT/018_NK-OPS-001/2030_Protocol直接期待値95site文脈レビュー結果.md'
    content = (data.ROOT/record).read_text()
    assert all('|'+name+'|' in content for name in COUNTS)
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',selected)
    data.write(out/'manifest.json',dict(actualExit=0,source='d17f122d2026b804be626bf7a3b76912923bd240',
        invocation=invocation,reviewedSites=95,sourceHashes=source_hashes,counts=COUNTS,
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),independentFixtureHashes=fixtures,
        companionSourceHashes=companions,humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        contextReviewOnly=True,automaticIndependenceVerdict=False,propertyNotSoleExternalOracle=True,
        remainingDirectExpectedSites=114,unresolvedIdentifierSites=202,countsOverlapNotCompletionRate=True,
        targetCodeExecuted=False,productTestsExecuted=0,externalActions=0,newAccepted=0,
        wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,reviewedSites=95,remainingDirect=114,
        manifestSha256=data.sha((out/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
