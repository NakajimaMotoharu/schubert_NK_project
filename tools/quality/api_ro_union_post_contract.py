"""Positive four-counter scope plus explicit fourteen-owner-PMD review; raw counts never normalized."""
import re


def require(value,message):
    if not value:raise ValueError(message)


def zero(value):return type(value) is int and value==0


def reviewed(record,source,tests,suites,classes,review):
    require(review["source"]==source and zero(review["actualExit"]),"actual same-source reviewed witness")
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
    require(zero(record['unclassified']) and zero(review['unclassified']) and zero(review['actualViolationsOutstanding']),'no unclassified or unknown default')
    require(record['classifiedPmdContext']==review['staticDispositions'] and len(review['staticDispositions'])==review['rawPmd']==14,'exact individually reviewed fourteen raw rows')
    require(set(record['staticRaw'])=={'pmd','checkstyle','spotbugs'},'three explicit static analyses')
    for name,row in record['staticRaw'].items():
        require(row['timedOut'] is False and zero(row['processingErrors']),'every actual static analysis completed')
        if name=='pmd':
            require(type(row['actualExit']) is int and row['actualExit']==4 and type(row['findings']) is int and row['findings']==14,'actual PMD14/exit4 retained')
            require(row['rawFindings']==[value['raw'] for value in review['staticDispositions']],'all actual raw PMD exactly joined, not hidden')
        else:
            require(zero(row['actualExit']) and zero(row['findings']) and row['rawFindings']==[],'actual CS/SB zero, not a waiver')
    return totals
