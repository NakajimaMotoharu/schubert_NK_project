"""Bind the explicit common-harness finding review to exact current bytes/rows."""
from collections import Counter
import datetime
import hashlib
import json
import re
import xml.etree.ElementTree as ET

import pg6966_chr_adapter_host as host

PMD = {
 'UseConcurrentHashMap':('CONTEXT_NOT_APPLICABLE','method-local synchronous map, no shared publication; actual shared ACTIVE_OUTPUTS uses concurrent set'),
 'AvoidDuplicateLiterals':('REQUIRED_CONTRACT','exact SS355/manifest/schema literal; no new constant-extraction style requirement'),
 'AvoidLiteralsInIfCondition':('REQUIRED_CONTRACT','explicit DIF/target/applicability allowlist literal, independently fixed oracle'),
 'AvoidFieldNameMatchingMethodName':('CONTEXT_NOT_APPLICABLE','immutable final field getter, not recursive method call or local shadow'),
 'AssignmentInOperand':('CONTEXT_NOT_APPLICABLE','single buffered read binds exact digest length; TWR and independent aggregate vectors'),
 'AvoidBranchingStatementAsLastInLoop':('REQUIRED_CONTRACT','labeled continue advances candidate offset after inner mismatch; independent canary search boundaries')}
NP = {('ArtifactComparator','artifactFiles'),('GateCli','lambda$caseIds$0'),('GateCli','lambda$caseIds$1'),
      ('GateCli','lambda$verifySource$1'),('GateContractValidator','lambda$caseIds$0'),
      ('GateContractValidator','lambda$caseIds$1'),('GateContractValidator','lambda$validateRun$0')}
THROWS = {('GateCli',n) for n in ('compareNk','preflight','promoteCurrent','sha256')} | {('GateContractValidator','sha256')}
REVIEW = host.ROOT/'evidence/01_PT/018_NK-OPS-001/1532_CHR共通path是正・静的指摘個別適用性.md'


def classify_pmd(row):
    host.require(row['rule'] in PMD, 'unknown PMD finding must be reviewed, not hidden')
    return PMD[row['rule']]


def classify_spot(kind, clazz, method):
    if kind == 'NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE':
        host.require((clazz,method) in NP,'arbitrary-input parent/name NP is a real open finding, never blanket suppression')
        return 'FALSE_POSITIVE','Files.list direct named child or NOFOLLOW regularFiles filtered path; root directory cannot reach name dereference'
    host.require(kind == 'THROWS_METHOD_THROWS_CLAUSE_BASIC_EXCEPTION' and (clazz,method) in THROWS,
                 'unknown exception or method finding remains unreviewed')
    return 'CONTEXT_NOT_APPLICABLE','common CLI checked-failure propagation boundary, not Production catch/normalization; IO/JCA negative and nonzero caller exit'


def semantic_identity(row):
    value={k:v for k,v in row.items() if k not in ('beginline','endline','begincolumn','endcolumn')}
    if row['rule']=='AvoidDuplicateLiterals':
        match=re.fullmatch(r'The String literal (".*") appears (\d+) times in this file; the first occurrence is on line (\d+)',row['message'])
        host.require(match is not None and int(match[3])==int(row['beginline']), 'exact documented message/structural position agreement')
        value['message']=f'The String literal {match[1]} appears {match[2]} times; first occurrence validated against beginline'
    return tuple(sorted(value.items()))


def main():
    base = host.BASE/'PG6978-chr-path-static-v1/manifest.json'
    old = host.BASE/'PG6970-chr-common-static-v1/manifest.json'
    qualification = host.BASE/'PG6980-chr-path-qualification-v1/manifest.json'
    host.require(host.sha(base) == '8a215d4584831c544d56e17c1ca4e3bf7be8851d751179d3df81d5fef1985efb'
                 and host.sha(qualification) == '0bbc80f788ac9c26caada7f363415a803aa6cef3796222d519467d6d60e34631', 'exact genuine original inputs')
    data,previous,q = [json.loads(p.read_bytes()) for p in (base,old,qualification)]
    host.require(data['source'] == q['source'] and len(data['findings']['pmd'])==43
                 and len(data['findings']['spotbugs'])==13 and not data['findings']['checkstyle']
                 and data['records']['pmd']['processingErrors']==0,'all current raw rows and no parse error')
    host.require(Counter(semantic_identity(r) for r in previous['findings']['pmd']) == Counter(semantic_identity(r) for r in data['findings']['pmd']),
                 'all43 warnings retain exact semantic identity after targeted guard fixes')
    for p,h in q['sourceInputs'].items():host.require(host.sha(host.ROOT/p)==h,'all current original source/Test/fixture bytes')
    target=host.W/'pg6976-chr-path-green-v1/snapshot/program/characterization/target'
    report=target/'spotbugsXml.xml'
    host.require(host.sha(report)==data['records']['spotbugs']['reportSha256'],'original current SpotBugs full XML')
    reviewed=[]
    def add(engine,row,clazz,line,status,reason):
        path='program/characterization/src/main/java/dev/codex/schubert/characterization/'+clazz+'.java'
        text=(host.ROOT/path).read_text().splitlines()
        host.require(1<=line<=len(text) and path in q['sourceInputs'],'exact declared Main/line only')
        snippet='\n'.join(text[max(0,line-2):line+1])
        reviewed.append(dict(engine=engine,rawIdentitySha256=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest(),
                             raw=row,source=path,sourceSha256=q['sourceInputs'][path],line=line,snippet=snippet,
                             status=status,reason=reason,reviewRef=str(REVIEW.relative_to(host.ROOT))))
    for row in data['findings']['pmd']:
        state,reason=classify_pmd(row)
        add('PMD',row,row['class'].split('.')[0],int(row['beginline']),state,reason)
    bugs=ET.parse(report).getroot().findall('BugInstance')
    for row,bug in zip(data['findings']['spotbugs'],bugs):
        method=bug.find('Method');clazz=method.get('classname').rsplit('.',1)[-1];name=method.get('name')
        state,reason=classify_spot(row['type'],clazz,name)
        line=int(bug.findall('SourceLine')[0].get('start'))
        add('SPOTBUGS',row,clazz,line,state,reason)
    host.require(len(bugs)==13 and len(reviewed)==56,'every actual finding individually bound')
    # Independently bind XML session timestamps to actual exec audit and original job window.
    audit=q['stages'][-1]['stdout'];line=next(l for l in audit.splitlines() if l.startswith('SESSION\t'))
    _,start,dump=line.split('\t');sessions=ET.parse(target/'site/jacoco/jacoco.xml').getroot().findall('sessioninfo')
    host.require(len(sessions)==1 and sessions[0].get('start')==start and sessions[0].get('dump')==dump,'XML/actual exec exact session timestamps')
    prior=host.W/'pg6976-chr-path-green-v1';begin=json.loads((prior/'begin.safe.json').read_bytes());end=json.loads((prior/'exit.safe.json').read_bytes())
    host.require(datetime.datetime.fromisoformat(begin['startUTC']).timestamp()*1000<=int(start)<=int(dump)
                 <=datetime.datetime.fromisoformat(end['endUTC']).timestamp()*1000,'actual job/session monotonic window')
    value=dict(actualExit=0,source=q['source'],rawStaticManifestSha256=host.sha(base),originalQualificationSha256=host.sha(qualification),
               semanticReviewPath=str(REVIEW.relative_to(host.ROOT)),semanticReviewSha256=host.sha(REVIEW),
               reviewedRows=reviewed,statusCounts=dict(Counter(r['status'] for r in reviewed)),unknownRows=0,
               actualRawExits={k:v['actualExit'] for k,v in data['records'].items()},rawCounts={'PMD':43,'SPOTBUGS':13,'CHECKSTYLE':0},
               oldRawCounts={'PMD':43,'SPOTBUGS':16},realNullDefectsFixed=3,sessionTimeJoin=True,
               suppressedRows=0,ruleChanges=0,productionSrcChanges=0,F03Accepted=False,formalUpdated=False,newPtCount=0)
    out=host.BASE/'PG6982-chr-static-review-v1';out.mkdir();host.write(out/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,reviewed=56,statusCounts=value['statusCounts'],unknown=0,rawExits=value['actualRawExits'],
                         manifestSha256=host.sha(out/'manifest.json'))))


if __name__=='__main__':
    main()
