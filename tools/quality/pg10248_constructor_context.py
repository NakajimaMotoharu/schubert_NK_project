"""Bind fifty constructor-expression source contexts; no code execution or automatic verdict."""
from collections import Counter
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

COUNTS=dict(AuthenticationErrorProfileTest=4,PayloadGoldenVectorTest=2,ScenarioRecordEncodingTest=8,
    PayloadTypeCatalogTest=2,SemanticFieldValueTest=15,ProtocolSemanticTypeTest=15,
    JstWireTimestampTest=2,LinuxStartupAdmissionTest=2)

def main():
    invocation=capture(Path(__file__))
    out=data.BASE/'PG10248-constructor-context-v1'
    assert not out.exists()
    index=data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/manifest.json',
        'f5dafc428c0e2367f79e0e59cd91b125639a88880f7be7bad72e879c0509527c')
    sites=data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    selected=[r for r in sites if r['expectedConstructorTypes']]
    assert len(selected)==50 and Counter(Path(r['path']).stem for r in selected)==COUNTS
    hashes={r['path']:r['sourceSha256'] for r in selected}
    assert len(hashes)==8 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    rows=[]
    for r in selected:
        lines=(data.ROOT/r['path']).read_text().splitlines()
        rows.append(dict(r,contextSha256=data.sha('\n'.join(lines[max(0,r['line']-9):r['line']+3]).encode()),
            verdict='NO_NEW_DEFECT_IDENTIFIED_CONTEXT_ONLY_NOT_WHOLE_ORACLE_CERTIFICATION'))
    record='evidence/01_PT/018_NK-OPS-001/2041_Constructor期待値50site文脈レビュー結果.md'
    text=(data.ROOT/record).read_text()
    assert all('|'+name+'|' in text for name in COUNTS)
    verify(invocation)
    out.mkdir()
    data.write(out/'reviewed-sites.json',rows)
    data.write(out/'manifest.json',dict(actualExit=0,source='ddde23ca0304654d59608b434c647c87d58ae3b6',
        invocation=invocation,sourceHashes=hashes,counts=COUNTS,reviewedSites=50,sourceFiles=8,
        reviewedSitesSha256=data.sha((out/'reviewed-sites.json').read_bytes()),humanReviewRecord=record,
        humanReviewSha256=data.sha((data.ROOT/record).read_bytes()),contextReviewOnly=True,
        automaticIndependenceVerdict=False,newDefectsIdentified=0,classificationOverlapsNotUniqueTestCount=True,
        targetCodeExecuted=False,productTestsExecuted=0,externalActions=0,newAccepted=0,
        wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((out/'manifest.json').read_bytes()))

if __name__=='__main__': main()
