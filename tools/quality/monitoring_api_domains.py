"""Pure parameterized source/role/byte ownership validation; never runs target classes or supplies PT evidence."""
from pg7192_heap_quality_review import anchors

def require(value,message):
    if not value:raise ValueError(message)

def validate_domains(trace,current,physical,previous,*,previous_count,physical_count,test_count,current_executable):
    require(len(previous)==previous_count and len(trace['sourceRows'])==previous_count+2,
      'exact declared previous sources and two new files')
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=previous_count,introduced=2))
    paths={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==physical_count and len({r['className'] for r in trace['physicalRows']})==physical_count,
      'all unique declared physical owners')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no transferred counters')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==test_count and row['componentCounterScope']=='ALL_CURRENT_API_EXECUTABLES_ONLY',
              'current API exact actual witness')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],
              'normal POM not executed PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS',
          'historical source has no current PT')
    roles={'api':('CURRENT_API_QUALIFIED',physical['currentApi']),
      'batch':('HISTORICAL_BATCH_BYTE_ONLY',physical['historicalBatch']),
      'web':('HISTORICAL_WEB_BYTE_ONLY',physical['historicalWeb'])}
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);label,proof=roles[role];executable=not entry.endswith('package-info.class')
        path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['qualificationDomain']==label and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='api' and executable)
          and row['sha256']==proof['physicalClasses'][row['className']] and row['sourcePath']==path and row['owner']==paths[path]['owner'],
          'all true role/source/bytes/owner/current flags')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==current_executable
      ==len(current['executableClasses']),'only actual current API executables')
    return counts
