"""Join481 narrow source facts to original3955 XML; known BUG1494 prevents specification acceptance."""
import ast
import copy
import inspect
import json
import os
from collections import Counter,defaultdict
import pg5792_current_static_whole_join as previous
from static_disposition_overlay import BASE,load
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5808_rollback_whole import SOURCE,W

QUALIFIED='42bdfb97cdc1f3b1944e28e144e91993ed2f05bc269a289ba6f20e6d7f29a376'
CASES='53e4c0275a33d18a408f9ca86851b1ae8fd12e1d1d22aab13d8899b8dc513dc6'


def qualification_source():
    raw=inspect.getsource(previous.qualified_whole)
    for old,new in(('PG5780-current3939-cases','PG5808-current3955-cases'),('pg5782-jms-primary-qualified-v1','pg5814-rollback-qualified-v1'),('pg5780-jms-primary-six-v1','pg5808-rollback-six-v1')):
        if raw.count(old)!=1:raise ValueError('exact original public/private binding')
        raw=raw.replace(old,new,1)
    class Counts(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3939,583,1664):return ast.copy_location(ast.Constant({3939:3955,583:587,1664:1665}[node.value]),node)
            return node
    return ast.unparse(ast.fix_missing_locations(Counts().visit(ast.parse(raw))))


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'W':W,'QUALIFIED_PUBLIC_SHA':QUALIFIED,'CURRENT_CASES_SHA':CASES}
    exec(compile(qualification_source(),'<qualified original3955 local reader>','exec'),scope);qp,cp,q,cases=scope['qualified_whole']()
    bp=BASE/'PG5820-identity14-v3/manifest.json';bsha='a64aaa208d14e5b519dc5e11df7bdb2a449e180e9743ed86ac066089790c5b4c';rows=load(bp,bsha,SOURCE)
    oldq=BASE/'PG5780-current3939-cases/qualification.json';oldcp=oldq.with_name('cases.json')
    if sha(oldq)!='1a5a5db819bde6bf01c85b4bb43017b8aae15bd59407b66adfbc4f5a0ca23c45'or sha(oldcp)!='6b8489660ecb397be6e020893eb3257df216ed5845923c4c93c832451b99bfbb':raise ValueError('original3939 identity only, never PASS import')
    historical={c['testId']:c for c in json.loads(oldcp.read_bytes())};index=defaultdict(list)
    for c in cases:index[(c['class'],c['caseNameSha256'])].append(c)
    result=[];joined=static_only=0;refs_unique=set()
    for row in rows:
        if row['status']!='SOURCE_REBOUND_CURRENT_WHOLE_PENDING':result.append(row);continue
        if sha(ROOT/row['sourcePath'])!=row['sourceSha256']:raise ValueError('entire current source still fixed')
        sources=[historical[i]for i in row.get('historicalCaseIds',[])]
        if row.get('historicalWholeCaseRefs'):
            if sources:raise ValueError('one provenance of current case references')
            sources=[historical[r['testId']]for r in row['historicalWholeCaseRefs']]
        if row.get('currentSelectedCaseRefs'):
            if sources:raise ValueError('new constructor uses selected identities only, not old PASS')
            sources=row['currentSelectedCaseRefs']
        refs=[previous.current_reference(r,index)for r in sources]
        if not refs:
            if row['priorDisposition']!='CONTEXT_NOT_APPLICABLE'or row['rule']!='DoNotUseThreads':raise ValueError('individual required contract needs actual current original XML refs')
            static_only+=1
        value=copy.deepcopy(row);value.update(status=row['priorDisposition'],currentWholeCaseRefs=refs,currentWholeJoinPending=False,currentQualificationSha256=sha(qp),currentCasesSha256=sha(cp),reviewSource=SOURCE,historicalPtImportedAsCurrent=False,staticContextPremiseOnly=not refs,BUG1494Resolved=False)
        result.append(value);joined+=1;refs_unique.update(r['testId']for r in refs)
    if joined!=481 or static_only!=239 or len(result)!=1595:raise ValueError('all481 individual reasons, unchanged239 static-only context premises, all1595 retained')
    out=BASE/'PG5824-current-static3955-v1';os.umask(0o077);out.mkdir();fp=out/'findings.json'
    with fp.open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value={'actualExit':0,'source':SOURCE,'priorPendingManifestSha256':bsha,'currentWholeQualificationSha256':sha(qp),'currentWholeCasesSha256':sha(cp),'currentWholeTests':3955,'currentRawFindings':1595,'sourceAndWholeJoinedDispositions':joined,'staticContextPremiseOnly':static_only,'uniqueCurrentCaseReferences':len(refs_unique),'statusCounts':dict(Counter(r['status']for r in result)),'inventoryFile':'findings.json','inventorySha256':sha(fp),'newDispositionsCreated':0,'executedPtAdded':0,'ptAlternativeCompleted':0,'historicalPtImportedAsCurrent':False,'sourceCodeChanged':False,'analyzerReexecuted':False,'rawWarningsRemoved':0,'BUG1494Resolved':False,'wholePassIsNotSpecificationAcceptance':True,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'findingsSha256':sha(fp)}))


if __name__=='__main__':main()
