"""Current25 source trace; historical program docs and actual execution witnesses kept distinct."""
import pg7080_current_monitoring_trace as previous


if __name__=='__main__':
    trace=previous.configure()
    trace.SOURCE='71c6be37c1a0038314b66565b1188d6488bc7c8d'
    trace.OUT=trace.host.BASE/'PG7092-registry-missing-trace-v1'
    trace.COMPONENT_LABEL='PG7086-registry-missing-post-v1'
    trace.PHYSICAL_LABEL='PG7090-registry-missing-six-post-v1'
    trace.PINS={trace.COMPONENT_LABEL:'cb4c69760e6af1839fe1a8433445183f198ab7555005c9a979fc777cca30d353',
      trace.PHYSICAL_LABEL:'63949a081586eb21c52e790267c74e4069633b30bcc5b2d3752290e5910c645a',
      'PG7038-c02-four-template-post-v1':'86e8d32bf2b07f73bb57e727be495f1f27b190a58979f872c50c848cfd22d9ef',
      'PG7042-c06-config-template-post-v1':'8866f08d6f317aca3ebd75415ca8ee2b9ca2b28c3762675aa95648375ec73250'}
    trace.COMPONENT_TESTS=73
    trace.COMPONENT_SUITES=11
    trace.SOURCE_COUNT=25
    trace.CONTRACTS['MonitoringMissingObservation']=('MONMISSING001..003',1567,1568)
    trace.SUPPLEMENTARY_CONTRACTS={
      'AlertLifecycle':[('ALERTCONT001..002',1563,1564)],
      'AlertRegistry':[('MONMISSING001..003',1567,1568)],
      'MonitoringPolicyEngine':[('MONMISSING001..003',1567,1568)]}
    trace.main()
