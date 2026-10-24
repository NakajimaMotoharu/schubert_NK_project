"""Exact45/6 and all12 Batch selected Main, preserving the one existing classified raw row."""
import json
import scoped_prometheus_post as post

if __name__=='__main__':
    post.common.SOURCE='6246c954d6d0ac7171bf009663bb2e6539d8be32'
    post.common.COMPILE=post.host.W/'pg8212-counter-name-six-compile-v1'
    post.common.COMPILE_SHA='db14f540178f960e7aa2c08303867340a2643e6c9f9f0c73c23fd245f675f7d6'
    post.RUN=post.host.W/'pg8226-batch-prometheus-host-v1'
    post.RAW_SHA='6d636763c4370630961c18eb93876073f77bfa8a5ef610c637bc7fcaaa713ca0'
    post.SLOT=post.host.W/'pg8228-batch-prometheus-post-v1'
    post.OUT=post.host.BASE/'PG8228-batch-prometheus-post-v1'
    post.MODULE='batch'
    post.PREFIX='dev/codex/schubert/nk/batch/monitoring/'
    p=post.PREFIX
    post.NAMES={p+'TransferMetricRecorder'+s for s in ('','$Counts','$Usage','$Suffix')}
    post.NAMES|={p+'IntegrityFailureMetricRecorder'+s for s in ('','$Area')}
    post.NAMES|={p+'ProcessRestartMetricRecorder'+s for s in ('','$Reason')}
    post.NAMES|={p+'BatchMetricRecorder'}
    post.NAMES|={p+'BatchMetricContract'+s for s in ('','$Step','$Status')}
    post.SOURCE_PATHS={'src/schubert-nk-batch/src/main/java/'+n.split('$',1)[0]+'.java' for n in post.NAMES}
    post.COUNTS={'TransferMetricRecorderTest':8,'IntegrityFailureMetricRecorderTest':8,
                 'BatchMetricRecorderTest':8,'ProcessRestartMetricRecorderTest':8,
                 'BatchMetricContractTest':5,'BatchPrometheusContractTest':8}
    post.GENERATED={p+'TransferMetricRecorder$Counts':['files','bytes','equals','hashCode','toString'],
        p+'TransferMetricRecorder$Suffix':['values','valueOf'],p+'IntegrityFailureMetricRecorder$Area':['values','valueOf'],
        p+'ProcessRestartMetricRecorder$Reason':['values','valueOf'],p+'BatchMetricContract$Step':['values','valueOf'],
        p+'BatchMetricContract$Status':['values','valueOf']}
    post.ENUM_TYPES=set(post.GENERATED)-{p+'TransferMetricRecorder$Counts'}
    post.WITNESS_CASE_PREFIXES=('batchprom008','integrityMetric003','restartMetric003')
    post.EXPECTED_SESSION='PG8226-BATCH-PROMETHEUS'
    post.PMD_CONTEXT_WITNESS=dict(path='PG7824-restart-metric-review-v1/manifest.json',sha256='18c6eaaf7ab5dc0add2edebe8a6e01a5ed601d34da293e089066282ed914415f')
    file=post.host.BASE/post.PMD_CONTEXT_WITNESS['path']
    post.require(post.host.sha(file)==post.PMD_CONTEXT_WITNESS['sha256'],'full original static rationale proof')
    prior=json.loads(file.read_bytes())
    post.PMD_CONTEXT=[r for r in prior['staticDispositions'] if r['sourcePath'].endswith('/BatchMetricRecorder.java')]
    post.require(len(post.PMD_CONTEXT)==1 and post.PMD_CONTEXT[0]['raw']['class']=='BatchMetricRecorder'
                 and post.PMD_CONTEXT[0]['raw']['rule']=='AvoidSynchronizedStatement'
                 and post.PMD_CONTEXT[0]['raw']['beginline']=='67','only one exact existing private-owner-lock raw row')
    post.main()
