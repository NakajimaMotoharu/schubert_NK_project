"""Metadata-only actual review-validator negatives; zero Production/JUnit/SDK execution."""
import copy
import datetime
import json
from pathlib import Path
import pg8798_management_static_review_join as review
from host_tool_invocation import capture,verify

OUT=review.host.BASE/'PG8800-management-static-review-negatives-v1'
QUALIFIED=review.host.BASE/'PG8798-management-static-review-join-v1/manifest.json'
QUALIFIED_SHA='084bfae2f09e2b30ec5c6cb99afbc7cd4909d7579ae293530658c15753fe5339'
VALIDATOR_SHA='86c014c4499d3ef01a6f98747d8c9f121dc7932032ad01136334766f06f9826a'

def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    assert review.host.sha(QUALIFIED)==QUALIFIED_SHA
    proof=json.loads(QUALIFIED.read_text())
    assert proof['actualExit']==0 and proof['source']==review.SOURCE and proof['invocation']['entrypointSha256']==VALIDATOR_SHA
    assert review.host.sha(Path(review.__file__))==VALIDATOR_SHA and review.host.sha(review.MANUAL)==review.MANUAL_SHA and review.host.sha(review.ORIGIN)==review.ORIGIN_SHA
    manual=json.loads(review.MANUAL.read_text());origin=json.loads(review.ORIGIN.read_text())
    positive=review.validate(manual,origin)
    mutations=(
      ('foreign-source',lambda x:x.update(source='0'*40)),
      ('foreign-design',lambda x:x.update(formalDesignCommit='0'*40)),
      ('wrong-source-path',lambda x:x['rows'][0].update(path=x['rows'][18]['path'])),
      ('wrong-source-hash',lambda x:x['rows'][0].update(sourceSha256='0'*64)),
      ('shifted-raw-line',lambda x:x['rows'][0]['raw'].update(beginline='38')),
      ('shifted-raw-column',lambda x:x['rows'][0]['raw'].update(begincolumn='18')),
      ('drop-overlapping-occurrence',lambda x:x['rows'].pop(6)),
      ('duplicate-index',lambda x:x['rows'][6].update(index=6)),
      ('blanket-nonapplicability',lambda x:x['rows'][1].update(status='CONTEXT_NOT_APPLICABLE_J2EE_RULE')),
      ('invent-current-xml',lambda x:x['rows'][1]['testReference'].update(currentXmlQualified=True)),
      ('invent-product-pass',lambda x:x.update(productTestsExecuted=40)),
      ('invent-coverage',lambda x:x.update(coverage=100)),
      ('invent-qualification',lambda x:x['rows'][1].update(qualityGatePass=True)),
      ('invent-runtime',lambda x:x['rows'][1].update(actualRuntimeProven=True)),
      ('invent-pt-alternative',lambda x:x['rows'][1].update(ptAlternativeCompleted=1)),
      ('erase-warning',lambda x:x['rows'][0].update(rawWarningRetained=False)),
      ('vacuous-reason',lambda x:x['rows'][1].update(reason='required')),
      ('invent-independent-reviewer',lambda x:x['rows'][1].update(reviewOwner='INDEPENDENT_AGENT')),
      ('wrong-test-file',lambda x:x['rows'][1]['testReference'].update(path='src/schubert-nk-api/Unknown.java')))
    rejected=[]
    for name,mutate in mutations:
        changed=copy.deepcopy(manual);mutate(changed)
        assert changed!=manual
        try: review.validate(changed,origin)
        except (AssertionError,ValueError): rejected.append(name)
        else: raise AssertionError('actual immutable validator must reject '+name)
    assert len(rejected)==19
    assert review.host.sha(Path(review.__file__))==VALIDATOR_SHA and review.host.sha(review.MANUAL)==review.MANUAL_SHA
    verify(invocation);OUT.mkdir()
    review.host.write(OUT/'manifest.json',dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=review.SOURCE,invocation=invocation,qualifiedReviewManifestSha256=QUALIFIED_SHA,validatorSha256=VALIDATOR_SHA,manualSha256=review.MANUAL_SHA,positiveStatusCounts=positive,rejected=rejected,negativeMetadataCases=19,testsExecutedByThisTool='METADATA_GUARDS_ONLY_NOT_PRODUCTION_PT',productTestsExecuted=0,coverage=None,ptAlternativeCompleted=0,formalUpdated=False,F03Accepted=False,newAccepted=0,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0))
    print(json.dumps(dict(actualExit=0,metadataNegatives=19,productPt=0,manifestSha256=review.host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
