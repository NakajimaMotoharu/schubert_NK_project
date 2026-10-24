"""Exact original48/6 API supplied Gauge SDK quality; no product test replay."""
import scoped_prometheus_post as post

if __name__=='__main__':
    post.RUN=post.host.W/'pg8198-api-prometheus-gauge-host-v1'
    post.RAW_SHA='fbcba8a8cd09f6976c45efbba08ff07cd3d8432e0639ba5bbc66eaee4906d7da'
    post.SLOT=post.host.W/'pg8200-api-prometheus-gauge-post-v1'
    post.OUT=post.host.BASE/'PG8200-api-prometheus-gauge-post-v1'
    p=post.PREFIX
    post.NAMES={p+'OutboxRowsMetricRecorder'+s for s in ('','$Status','$Counts')}
    post.NAMES|={p+'OutboxAgeMetricRecorder'+s for s in ('','$Ages')}
    post.NAMES|={p+'AsyncJobMetricRecorder'+s for s in ('','$State','$Snapshot')}
    post.NAMES|={p+'DbPoolMetricRecorder'+s for s in ('','$State','$Counts')}
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+n.split('$',1)[0]+'.java' for n in post.NAMES}
    post.COUNTS={'OutboxRowsMetricRecorderTest':8,'OutboxAgeMetricRecorderTest':8,
                'AsyncJobMetricRecorderTest':8,'DbPoolMetricRecorderTest':8,
                'GeneratedMetricValueContractTest':8,'ApiPrometheusGaugeContractTest':8}
    post.GENERATED={
        p+'OutboxRowsMetricRecorder$Status':['values','valueOf'],
        p+'OutboxRowsMetricRecorder$Counts':['pending','sent','error','equals','hashCode','toString'],
        p+'OutboxAgeMetricRecorder$Ages':['pending','sent','error','equals','hashCode','toString'],
        p+'AsyncJobMetricRecorder$State':['values','valueOf'],
        p+'DbPoolMetricRecorder$State':['values','valueOf'],
        p+'DbPoolMetricRecorder$Counts':['active','idle','pending','maximum','equals','hashCode','toString']}
    post.ENUM_TYPES={p+'OutboxRowsMetricRecorder$Status',p+'AsyncJobMetricRecorder$State',p+'DbPoolMetricRecorder$State'}
    post.WITNESS_CASE_PREFIXES=('genMetric001','genMetric002','genMetric003','genMetric004','genMetric005','genMetric006','genMetric008','outboxAge008')
    post.EXPECTED_SESSION='PG8198-API-PROMETHEUS-GAUGE'
    post.main()
