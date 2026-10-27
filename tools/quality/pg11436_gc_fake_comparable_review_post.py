"""Independent24-candidate/poison-oracle facts and namespace-preservation negative, no product replay."""
import pg11434_gc_fake_comparable_review as stage
stage.PRIMARY_SHA='609dc58ea0942b7b5de4412328233f5609c28dcba91406ed8489cfea6b93419f'
if __name__=='__main__':
    path=stage.data.ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiGcMetricRegistrationTest.java'
    text=path.read_text()
    bad=text.replace('org.junit.jupiter.api.','org.junit.jupiter.invalid.')
    assert bad!=text
    try:
        stage.normalized(bad,'api')
    except AssertionError:
        pass
    else:
        raise AssertionError('foreign JUnit namespace accepted')
    stage.post()
