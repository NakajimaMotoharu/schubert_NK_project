"""Explicit scoped_prometheus_post schema contract; missing or unknown never becomes zero/PASS."""
import re


def require(value,message):
    if not value:raise ValueError(message)


def zero(value):return type(value) is int and value==0


def clean(record,source,tests,suites,classes):
    require(isinstance(source,str) and re.fullmatch('[0-9a-f]{40}',source),'explicit immutable source required')
    require(record['source']==source and zero(record['actualExit']),'actual source and completed post required')
    require(type(record['tests']) is int and record['tests']==tests and type(record['suites']) is int and record['suites']==suites,'exact current test/suite counts')
    require(set(record['executableClasses'])==set(classes),'exact declared executable class names')
    totals={kind:dict(missed=0,covered=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for row in record['executableClasses'].values():
        require(isinstance(row['crc64'],str) and re.fullmatch('[0-9a-f]{1,16}',row['crc64']),'physical CRC required')
        require(set(row['counters'])==set(totals),'explicit four counters')
        for kind,counter in row['counters'].items():
            require(set(counter)=={'missed','covered'},'exact counter fields')
            require(zero(counter['missed']) and type(counter['covered']) is int and counter['covered']>0,'no missed or vacuous executable counter')
            totals[kind]['covered']+=counter['covered']
    require(set(record['counters'])==set(totals),'exact aggregate counter kinds')
    for counter in record['counters'].values():
        require(set(counter)=={'missed','covered'} and zero(counter['missed']) and type(counter['covered']) is int,'explicit aggregate types, not boolean aliases')
    require(record['counters']==totals,'aggregate must equal actual class counter sum')
    require(zero(record['actualCrcMismatch']) and type(record['actualSessions']) is int and record['actualSessions']==1,'one current session/no CRC mismatch')
    for key in ('coverageUnion','customExclusionsAdded','suppressionsAdded','formalUpdated','whole451Accepted'):
        require(record[key] is False,'no union/exclusion/suppression/formal or whole-gate inference')
    require(zero(record['unclassified']) and record['classifiedPmdContext']==[],'clean raw-only component scope, no implicit disposition')
    require(set(record['staticRaw'])=={'pmd','checkstyle','spotbugs'},'three explicit static analyses')
    for row in record['staticRaw'].values():
        require(zero(row['actualExit']) and row['timedOut'] is False and zero(row['findings']) and zero(row['processingErrors']),'every actual static analysis completed clean')
        require(row['rawFindings']==[],'no hidden raw static finding')
    return totals
