"""Bind corrected pure DTO proof and preserve two failed metadata consumers without PT replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17965-closed-projection-source-binding-v1'
RECORDS=[["PG17949-closed-projection-value-review-v1","3445ac22444a6ca1d2e20a8f523e45529933ee1dec08268cd5826790218413a0"],["PG17950-closed-projection-six-pt-v1","c32700867c3272c5453906200ebde55b097f6f93e7ac638b1c3ad8b954bddf7a"],["PG17955-closed-projection-six-post-v3","1926662d6d41c53dba39955e9c29a52f1d1e540e8882b4c70257c677a0ad0d9e"],["PG17954-closed-projection-six-independent-v1","17019f5d360ca190b629980bf04815695e8b9b4317ec93c800daf384b868ad1d"],["PG17958-current2846-closed-projection-registry-v1","b65ad3a517cd4ef79b9587ec948e17bf397d873274d2f800861e1bcab59f2c94"],["PG17961-current2846-closed-projection-registry-post-v2","49b2143675ba8d3562892988ac50296e67f06e9219029a84c6499f09e28c1705"],["PG17962-current2846-closed-projection-wbs-v1","46b0da1a957c41ff6f5c69b590d2260298b8dc01ca07b7f4f60c64aba7c9ac01"],["PG17964-current2846-closed-projection-wbs-post-v1","183c4b6a0ac72b401ef9d1b90426c3b8a0d63ff98d3e73b4d98e0b8b5d1c19db"],["PG17952-closed-projection-six-post-v1","d82c2f5047798011110314ec634bcbd8abff267c00dd6d906d4f61455bd928c7"]]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    bindings=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    m=data.read_checked(data.BASE/RECORDS[4][0]/'manifest.json',RECORDS[4][1])
    p=data.read_checked(data.BASE/RECORDS[2][0]/'manifest.json',RECORDS[2][1])
    q=data.read_checked(data.BASE/RECORDS[5][0]/'manifest.json',RECORDS[5][1])
    name='dev/codex/schubert/nk/web/security/ClosedWebAuthentication'
    assert m['fullSourceUnits'][name]['four100'] is True and m['qualificationReplacedUnitHistory'][name]['four100'] is False
    assert m['tests']==2846 and m['totalMethodExecutions']==2985 and m['totalRepeatedOriginalMethods']==139 and m['necessaryJointRepeatedMethods']==55 and len(m['jointQualificationReferences'])==5
    assert p['normalOrdinaryTestSourceDomain'] is False and p['normalOrdinaryMethodCount']==0 and p['independentQualityMethodCount']==6
    assert len(p['domainCorrectionNegativeVectors'])==len(p['rawSchemaNegativeVectors'])==len(q['xmlLineageNegativeVectors'])==3
    assert q['xmlSourceReference']==p['originalCompletedPostReference']==RECORDS[8]
    for name in ['PG17953-closed-projection-six-post-v2','PG17960-current2846-closed-projection-registry-post-v1']:assert not (data.BASE/name).exists()
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=bindings,oldPartialProofPreserved=True,incorrectDisclosureOriginalPreserved=True,failedMetadataConsumerOutputsNotCreated=True,newFour100Sources=1,newQualityCases=6,newOrdinaryCases=0,productAndAnalyzerReexecutedForCorrections=0,coverageExecUnion=False,actualNetworkActions=0,actualVmActions=0,actualDatabaseActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
