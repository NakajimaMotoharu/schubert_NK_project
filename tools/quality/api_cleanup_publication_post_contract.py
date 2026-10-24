"""Exact two-class cache scope, including a genuinely branchless Entry and two explicit private-lock reviews."""
import re

PREFIX='dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationSource'
CLASSES={PREFIX,PREFIX+'$Entry'}


def require(value,message):
    if not value:raise ValueError(message)


def zero(value):return type(value) is int and value==0


def qualify(value,source,review):
    require(value['source']==source==review['source'] and zero(value['actualExit']) and zero(review['actualExit']),'exact successful source/review')
    require(type(value['tests']) is int and value['tests']==34 and type(value['suites']) is int and value['suites']==2,'actual34/2')
    require(set(value['executableClasses'])==CLASSES,'include whole Entry, not a metadata exclusion')
    totals={k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for name,row in value['executableClasses'].items():
        require(isinstance(row['crc64'],str) and re.fullmatch('[0-9a-f]{1,16}',row['crc64']),'real physical CRC')
        require(set(row['counters'])==set(totals),'actual explicit four counters')
        for kind,counter in row['counters'].items():
            require(set(counter)=={'missed','covered'} and zero(counter['missed']) and type(counter['covered']) is int,'no missed/unknown/bool')
            if name==PREFIX+'$Entry' and kind=='BRANCH':
                require(counter['covered']==0,'branchless private data holder remains zero/zero, not fake100')
            else:require(counter['covered']>0,'nonvacuous actual executable counter')
            totals[kind]['covered']+=counter['covered']
    require(value['counters']==totals and all(row['covered']>0 for row in totals.values()),'nonvacuous aggregate four100 from actual class sum')
    require(zero(value['actualCrcMismatch']) and type(value['actualSessions']) is int and value['actualSessions']==1,'one exact exec/session, CRC0')
    for name in ('coverageUnion','customExclusionsAdded','suppressionsAdded','formalUpdated','whole451Accepted'):
        require(value[name] is False,'no union/exclusion/suppression/whole gate')
    require(zero(value['unclassified']) and zero(review['unclassified']) and zero(review['actualViolationsOutstanding']),'unknown not zero default')
    require(value['classifiedPmdContext']==review['staticDispositions'] and len(review['staticDispositions'])==2,'exact explicit row decision')
    require(set(value['staticRaw'])=={'pmd','checkstyle','spotbugs'},'three real analyses')
    for name,row in value['staticRaw'].items():
        require(row['timedOut'] is False and zero(row['processingErrors']),'no partial analysis')
        if name=='pmd':
            require(type(row['actualExit']) is int and row['actualExit']==4 and type(row['findings']) is int and row['findings']==2,'retain real PMD2/exit4')
            require(row['rawFindings']==[item['raw'] for item in review['staticDispositions']],'raw XML exactly joins the independently reviewed required private lock')
        else:require(zero(row['actualExit']) and zero(row['findings']) and row['rawFindings']==[],'CS/SpotBugs actual0')
    return totals
