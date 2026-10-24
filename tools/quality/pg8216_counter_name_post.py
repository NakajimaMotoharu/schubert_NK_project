"""New fixed-source actual40/5, exact six Main/static/CRC and four generated methods."""
import scoped_prometheus_post as post

if __name__=='__main__':
    post.common.SOURCE='6246c954d6d0ac7171bf009663bb2e6539d8be32'
    post.common.COMPILE=post.host.W/'pg8212-counter-name-six-compile-v1'
    post.common.COMPILE_SHA='db14f540178f960e7aa2c08303867340a2643e6c9f9f0c73c23fd245f675f7d6'
    post.RUN=post.host.W/'pg8214-counter-name-host-v1'
    post.RAW_SHA='e7c14378ecebe856fc3f09d06a32ea407135bf8f77d707c75b0553ac43875193'
    post.SLOT=post.host.W/'pg8216-counter-name-post-v1'
    post.OUT=post.host.BASE/'PG8216-counter-name-post-v1'
    p=post.PREFIX
    post.NAMES={p+'InboxReplayMetricRecorder',p+'OperationMismatchMetricRecorder',
                p+'OperationMismatchMetricRecorder$Operation',p+'MqRedeliveryMetricRecorder',
                p+'MqMessageMetricRecorder',p+'MqMessageMetricRecorder$Stage'}
    post.SOURCE_PATHS={'src/schubert-nk-api/src/main/java/'+n.split('$',1)[0]+'.java' for n in post.NAMES}
    post.COUNTS={'InboxReplayMetricRecorderTest':8,'OperationMismatchMetricRecorderTest':8,
                'MqRedeliveryMetricRecorderTest':8,'MqMessageMetricRecorderTest':8,
                'ApiPrometheusCounterContractTest':8}
    post.GENERATED={p+'OperationMismatchMetricRecorder$Operation':['values','valueOf'],
                    p+'MqMessageMetricRecorder$Stage':['values','valueOf']}
    post.ENUM_TYPES=set(post.GENERATED)
    post.WITNESS_CASE_PREFIXES=('apicnt008','mqEvent003')
    post.EXPECTED_SESSION='PG8214-COUNTER-NAME'
    post.main()
