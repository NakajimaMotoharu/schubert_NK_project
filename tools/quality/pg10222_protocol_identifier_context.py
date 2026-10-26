"""Bind human review of 67 identifier sites; no target execution or automatic oracle verdict."""
from collections import Counter
from pathlib import Path
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10146_protocol_expected_context import FIXTURES

COUNTS=dict(AuthenticationErrorProfileTest=4,MessageCodecTest=8,PayloadGoldenVectorTest=3,
    ScenarioRecordEncodingTest=2,LargeResultRecordCodecTest=11,MediaDescriptorValidatorTest=6,
    HeaderModelTest=4,IndependentNamedFieldOracle=5,LayoutFieldCatalogTest=2,LayoutMetadataTest=1,
    PayloadTypeCatalogTest=3,SemanticFieldValueTest=6,JstWireTimestampTest=2,BrokerTopologyTest=1,
    FailedJmsIsolationExceptionTest=4,UnconfirmedJmsRollbackExceptionTest=5)

def main():
    invocation=capture(Path(__file__))
    out=data.BASE/'PG10222-protocol-identifier-context-v1'
    assert not out.exists()
    prior=data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/manifest.json',
        'f5dafc428c0e2367f79e0e59cd91b125639a88880f7be7bad72e879c0509527c')
    sites=data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/sites.json',prior['sitesJsonSha256'])
    selected=[r for r in sites if r['expectedAstKind']=='IDENTIFIER' and 'schubert-nk-protocol/' in r['path']
        and not r['path'].endswith('/PayloadCodecTest.java')]
    assert len(selected)==67 and Counter(Path(r['path']).stem for r in selected)==COUNTS
    hashes={r['path']:r['sourceSha256'] for r in selected}
    assert len(hashes)==16 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    rows=[]
    for r in selected:
        row=dict(r)
        text=(data.ROOT/r['path']).read_text().splitlines()
        row.update(contextSha256=data.sha('\n'.join(text[max(0,r['line']-18):r['line']+3]).encode()),
            verdict=('INDEPENDENT_WIRE_VECTOR_GAP_BUG1806' if Path(r['path']).stem=='MessageCodecTest'
                and r['method']=='responseAndEventHeadersRoundTripWithoutLeakingContext'
                else 'NO_DEFECT_IDENTIFIED_IN_REVIEWED_CONTEXT_NOT_SOLE_ORACLE_CERTIFICATION'))
        rows.append(row)
    assert sum(r['verdict']=='INDEPENDENT_WIRE_VECTOR_GAP_BUG1806' for r in rows)==2
    fixtures={'src/schubert-nk-protocol/src/test/resources/protocol/'+p:h for p,h in FIXTURES.items()}
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in fixtures.items())
    record='evidence/01_PT/018_NK-OPS-001/2038_Protocol間接期待値67siteレビュー結果.md'
    content=(data.ROOT/record).read_text()
    assert all('|'+name+'|' in content for name in COUNTS)
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source='d4ba0fcbe8855b9674413d395b46d2de7bb2ded9',
        invocation=invocation,reviewedSites=67,sourceHashes=hashes,counts=COUNTS,
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),independentFixtureHashes=fixtures,
        humanReviewRecord=record,humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),
        noDefectIdentifiedContexts=65,oracleGapSites=2,oracleGapMethods=1,remainingIdentifierSites=123,
        contextReviewOnly=True,automaticIndependenceVerdict=False,propertyNotSoleExternalOracle=True,
        bug='BUG-1806',ykt='YKT-1557',targetCodeExecuted=False,productTestsExecuted=0,externalActions=0,
        newAccepted=0,wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))

if __name__=='__main__': main()
