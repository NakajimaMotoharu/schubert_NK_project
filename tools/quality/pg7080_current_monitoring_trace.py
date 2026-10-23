"""Trace all current timed-monitoring additions without changing historical acceptance."""
import pg7052_monitoring_addition_trace as trace


if __name__=='__main__':
    trace.SOURCE='d96df9f09b46dee9aa75276d474e118609ee890c'
    trace.OUT=trace.host.BASE/'PG7080-current-monitoring-trace-v1'
    trace.COMPONENT_LABEL='PG7070-timed-filesystem-post-v2'
    trace.PHYSICAL_LABEL='PG7074-timed-filesystem-six-post-v1'
    trace.PINS={trace.COMPONENT_LABEL:'55456e2cb24d49f35766b3a17179c56a0e133a484592235529eb4eb7f61ac25a',
      trace.PHYSICAL_LABEL:'0feff9c36b9e44a63d9f0f7351ec830b3b1015e205f20de80a9fa34cb5ae8884',
      'PG7038-c02-four-template-post-v1':'86e8d32bf2b07f73bb57e727be495f1f27b190a58979f872c50c848cfd22d9ef',
      'PG7042-c06-config-template-post-v1':'8866f08d6f317aca3ebd75415ca8ee2b9ca2b28c3762675aa95648375ec73250'}
    trace.COMPONENT_TESTS=70
    trace.COMPONENT_SUITES=10
    trace.SOURCE_COUNT=24
    trace.PHYSICAL_COUNT=20
    trace.CONTRACTS.update(ContinuousConditionWindow=('MONWINDOW001..008',1561,1562),
      TimedFilesystemMonitor=('TIMEDFS001..006',1563,1564),AlertContinuity=('ALERTCONT001..002',1563,1564))
    trace.main()
