"""Close Web screen22 source trace, preserving quota-marker transition as unknown consumption."""
import json
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    transition=json.loads((close.BASE/'PG9462-web-screen22-source-join-v1/quota-window-transition.safe.json').read_bytes())
    before,intermediate,after=transition['observations']
    assert before['usedPercent']==67 and intermediate['usedPercent']==68 and before['resetsAt']==intermediate['resetsAt']==1793382075
    assert after['usedPercent']==0 and after['resetsAt']==1793513428 and transition['wholeGroupObservedSharedPp'] is None
    close.run(Path(__file__),'G13_WEB_SCREEN22_SOURCE_V1',close.BASE/'PG9466-web-screen22-metrics-v1',
      close.BASE/'PG9468-web-screen22-public-delta-v1','e7ba0e8f9add1c30d91deb37f105664dd9c0d090',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=6),groupCapPp=10,
        quotaBefore=dict(usedPercent=67,remainingPercent=33,resetsAt=1793382075),quotaAfter=dict(usedPercent=0,remainingPercent=100,resetsAt=1793513428),
        quotaBeforeObservedAtUTC=before['observedAtUTC'],quotaAfterObservedAtUTC=after['observedAtUTC'],sameQuotaWindow=None,observedSharedPp=None,
        quotaWindowComparisonStatus='WINDOW_MARKER_CHANGED_EXACT_CHANGE_TIME_CAUSE_AND_WHOLE_GROUP_CONSUMPTION_UNDETERMINED',
        splitQuotaObservations=transition['observations'],knownOldWindowSharedObservationPp=1,knownOldWindowPpNotWholeGroupOrExclusive=True,
        resetTicketOperationsByAgent=0,extraChargeOperationsByAgent=0,continuedActiveExecutionNotResumeAfterStop=True,
        attemptResult='22_EXACT_WEB_SCREEN_FORM_VIEW_PRIMARY_RELATED_SCOPES_REGISTERED; WINDOW_CHANGE_PRESERVED_NO_CONSUMPTION_INFERENCE; REMAIN157',
        originalPlanEngineeringDelta=dict(item='EXACT_WEB_SCREEN22_PRIMARY_SOURCE_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[],sharedControllerOriginalMainOwnerPreserved=True,observedQuotaWindowMarkerChanged=True),
        sourceReauthentication=dict(old785CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,targetCompile=0,targetRuntimeInvocation=0,sourceSelectionVectors=5,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=22,sourceRows=807,javaPaths=1789,registered=1632,registeredMain=965,totalMain=965,
          registeredTest=667,totalTest=824,unregisteredTest=157,remainingMultiOwner=139,remainingNoMainCp=18,
          verifiedSourceClosure=31,independentTestClassDeclarations=105,independentMainClassDeclarations=238,independentUniqueMainSourceFiles=221,
          catalogNegatives=9,mapperNegatives=8,neighbourInvariance=22,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1921_G13WebScreen22_主関連責任結果.md'],
        tokenMeasurementIds=['790153a8065dccdd35d9b45c4682af1d9c69ac30956fddb538b417b6fd7ce0fd'],
        nextCommand='9468 public scan/save-push; fresh current-window remaining>10 then remaining157 source responsibilities and independent PG/PT'),[
        ('PG9458-web-screen22-source-metadata-v1/manifest.json','d39b094d21537a2353795cfc217b811ba42e9f4d6b2ac6d92e5139153cb19e9a'),
        ('PG9460-web-screen22-source-post-v1/manifest.json','704d0f881f083a44cb746e2dcc4a1fb77ac61c47259137747bc51830703d5008'),
        ('PG9462-web-screen22-source-join-v1/manifest.json','7ea77aaaa24b59d395ea34e6e1e0af822ec5d43354c6ec1e4748f0c0b9084bdc'),
        ('PG9464-web-screen22-snapshot-post-v1/manifest.json','df95e10a3e2c355cf2ed909dc48b12d84ae8a2f0b2bf74b8ae66afacfbb0dedc')])
