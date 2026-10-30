"""Independent whole four-Source measurement of original batch run/diagnostic3."""
import reviewed_whole_pure_source_post_v1 as core
import pg14690_batch_run_diagnostic_three_pt as original

PROFILE={
    'rawFolder':'PG14690-batch-run-diagnostic-three-pt-v1',
    'rawSha256':'850ab1d51a32b82ac3410c66a31d6f76ec6f75429b08d343dd3e2e63ba298e89',
    'postFolder':'PG14692-batch-run-diagnostic-three-post-v1',
    'kind':'REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',
    'originalTestsAlreadyCounted':False,
    'sources':{}
}
for name,pin,owner in [
    ('platform/StopGateFailure','e62e08a9ba6be579d39a92d420e2c9f0b1067644d735bd4533252890c9227d8e','WBS-P018-04'),
    ('platform/StopGateException','a3edce9d305b127863271fb0757a403ebfcb1e6e973261db3dede83fda1a7758','WBS-P018-04'),
    ('repository/BatchRun','c440d3e16da86b7814cf8fbd6247e48c1ab4cd6de2da3a114a38c308ae3c7ce4','WBS-P017-02'),
    ('repository/MaintenanceActivation','0467e9722cc3c46e238fcdb9e2d1deffde11b3a498e54e61c0f477d18440889e','WBS-P017-02')]:
    internal='dev/codex/schubert/nk/batch/'+name
    PROFILE['sources'][internal]=dict(path='src/schubert-nk-batch/src/main/java/'+internal+'.java',sha256=pin,module='batch',closure=[internal],owner=owner)

if __name__=='__main__':core.verify_profile(original,PROFILE)
