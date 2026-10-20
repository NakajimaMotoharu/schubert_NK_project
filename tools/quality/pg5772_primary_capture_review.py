"""Exact approved JDBC primary-capture catches; no generic-catch blanket waiver."""
import copy
import hashlib
import json
import os
import re
from pathlib import Path
from pg5756_private_contract_qualification import SOURCE,ROOT,W,BASE
from pg5540_snapshot_scratch_selected import sha

OUT=BASE/'PG5772-primary-capture27-v1'


def retained_body(text,end,param,primary):
    name=param.split()[-1]
    match=re.match(r'\s*\)\s*\{\s*'+re.escape(primary)+r'\s*=\s*'+re.escape(name)+r'\s*;\s*throw\s+'+re.escape(name)+r'\s*;\s*\}\s*finally\s*(\{)',text[end:])
    if not match:raise ValueError('exact two-statement capture/same-primary rethrow followed by finally')
    return text[:end+match.start(1)].count('\n')+1,hashlib.sha256(text[end:end+match.end()].encode()).hexdigest()


def physical_owner(path,mapping):
    prefix=path.split('/')[1].removeprefix('schubert-nk-')+':'+path.split('/src/main/java/')[1][:-5]
    return{k:v for k,v in mapping.items()if k==prefix+'.class'or k.startswith(prefix+'$')}


def main():
    base=BASE/'PG5764-current-static-whole-v1/findings.json';prior=BASE/'PG5768-reference-identity35-v1/manifest.json';decisionsp=prior.with_name('decisions.json')
    if sha(base)!='2b758e909aff50e50962d97a0dbe0bce1224c4ac6670008b9129a1d8163a3c93'or sha(prior)!='9ba9f2af5c8d4c578bf3c645288759ef64bc3e6f818ac88117703c0c81f65484'or sha(decisionsp)!='d34e3f2ac12769a2351795e738524bc00797fed227786ccd5f1ae25065298ae5':raise ValueError('exact419 prior decisions/base, no overwritten raw findings')
    rows=json.loads(base.read_bytes());olddecisions={r['findingId']:r for r in json.loads(decisionsp.read_bytes())};rows=[olddecisions.get(r['findingId'],r)for r in rows]
    cp=W/'pg5770-current-catch-facts-v1/manifest.safe.json'
    if sha(cp)!='63e865210e51cdb6dcae78f0784d970b1bc1fa38aae403acab4f9e843b69d7e5':raise ValueError('actual current1090 catch facts')
    catch=json.loads(cp.read_bytes());oldp=W/'pg5592-current-failure-facts-v1/manifest.safe.json';old=json.loads(oldp.read_bytes())
    qp=BASE/'PG5754-current3932-cases/qualification.json';casep=qp.with_name('cases.json')
    if sha(qp)!='ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18'or sha(casep)!='f0e533df0ecea383f5e7cf0639d27f98c36691de11f644278df00ec0438a7276':raise ValueError('actual current3932 source/cases')
    q=json.loads(qp.read_bytes());cases=json.loads(casep.read_bytes());oldq=json.loads((BASE/'PG5588-current3905-cases/qualification.json').read_bytes())
    if not(catch['source']==SOURCE==q['productionSource']and catch['actualExit']==catch['compileExit']==catch['independentFixtureExit']==0 and catch['identity']['physicalMainSha256']==q['allPhysicalMainSha256']and q['tests']==3932):raise ValueError('current all849 compiler/all1664 actual same-source whole')
    if old['actualExit']!=0 or old['source']!=oldq['productionSource']or old['identity']['physicalMainSha256']!=oldq['allPhysicalMainSha256']:raise ValueError('original historical typed proof correspondence, never old PT import')
    for name in('SourceJdbcClosePrecedenceInventory.java','SourceCatchContextInventory.java'):
        if sha(ROOT/'tools/quality'/name)!=old['identity']['helperSha256'][name]:raise ValueError('exact original narrow typed helper unchanged')
    if {p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}!=catch['identity']['sourceHashes']:raise ValueError('all849 Main immutable')
    jdbc=old['results']['SourceJdbcClosePrecedenceInventory']['rows']
    if len(jdbc)!=27:raise ValueError('all27 exact approved typed finally shapes')
    decisions=[];scopes=[];used=set()
    for shape in jdbc:
        path=shape['path'];text=(ROOT/path).read_text()
        if sha(ROOT/path)!=old['identity']['sourceHashes'][path]:raise ValueError('no source change in exact retained JDBC scope')
        owner=physical_owner(path,q['allPhysicalMainSha256'])
        if not owner or owner!=physical_owner(path,oldq['allPhysicalMainSha256']):raise ValueError('all owning actual physical classbytes unchanged')
        matches=[]
        for fact in catch['rows']:
            if fact['path']!=path or fact['type']!='java.sql.SQLException|java.lang.RuntimeException|java.lang.Error'or fact['finalDirect']!='true'or fact['sameThrows']!='1'or any(fact[k]!='0'for k in('otherThrows','returns','assignments','breaks','continues')):continue
            end=int(fact['end']);param=text[int(fact['start']):end]
            try:line,bodyhash=retained_body(text,end,param,shape['primary'])
            except ValueError:continue
            if line==int(shape['firstLine']):matches.append((fact,bodyhash))
        if len(matches)!=1:raise ValueError('one current same-primary catch for each exact finally shape')
        fact,bodyhash=matches[0];suite=Path(path).stem+'Test'
        refs=[{'testId':c['testId'],'xmlSha256':c['xmlSha256'],'class':c['class'],'caseNameSha256':c['caseNameSha256']}for c in cases if c['class'].endswith('.'+suite)or c['class'].endswith('.JdbcResourceFailuresTest')]
        if not any(r['class'].endswith('.'+suite)for r in refs):raise ValueError('own actual current method suite required, not helper tests only')
        hits=[]
        for row in rows:
            if row['sourcePath']!=path or row['rule']!='AvoidCatchingGenericException'or row['status']!='NOT_REVIEWED_CURRENT_SOURCE':continue
            a=sum(len(s)+1 for s in text.splitlines()[:int(row['beginline'])-1])+int(row['begincolumn'])-1
            b=sum(len(s)+1 for s in text.splitlines()[:int(row['endline'])-1])+int(row['endcolumn'])-1
            if int(fact['start'])<=a<b<=int(fact['end']):hits.append(row)
        if len(hits)!=2:raise ValueError('exact RuntimeException/Error diagnostics, not other catch or wrapper')
        for row in hits:
            if row['findingId']in used or row['sourceSha256']!=catch['identity']['sourceHashes'][path]:raise ValueError('no duplicate disposition/source drift')
            used.add(row['findingId']);new=copy.deepcopy(row);new.update(status='REQUIRED_CONTRACT',reason='SS312/331/342, SSC063/199: this exact two-statement catch retains the original Throwable in its local primary and immediately rethrows that same instance. Its typed finally closes the same Statement/ResultSet once and calls JdbcResourceFailures.replace(primary,secondary). Removing the broad primary capture would lose defined known/unknown/fatal close precedence. No successful return, NPE normalization, diagnostic leakage or general catch waiver.',currentCatchFact=fact,retainedBodySha256=bodyhash,unchangedTypedFinallyFact=shape,currentPhysicalClasses=owner,currentWholeCaseRefs=refs,currentQualificationSha256=sha(qp),rawWarningRetained=True,reviewSource=SOURCE,ptAlternativeCompleted=False)
            decisions.append(new)
        scopes.append({'path':path,'method':fact['method'],'catchFirstLine':fact['firstLine'],'finally':shape,'sourceSha256':sha(ROOT/path),'retainedBodySha256':bodyhash,'currentOwnerClassCount':len(owner),'diagnostics':2})
    if len(decisions)!=54 or len(used)!=54:raise ValueError('only27 exact primary captures/54 diagnostics')
    value={'actualExit':0,'source':SOURCE,'baseManifestPath':prior.relative_to(ROOT).as_posix(),'baseManifestSha256':sha(prior),'priorOverlaySha256':sha(decisionsp),'currentCatchFactsSha256':sha(cp),'historicalTypedJdbcFactsSha256':sha(oldp),'historicalTypeProofReauthenticatedByExactSourceAndAllOwnerBytes':True,'historicalPtImportedAsCurrent':False,'currentWholeQualificationSha256':sha(qp),'newIndividualDispositions':54,'approvedPrimaryCaptureScopes':27,'scopes':scopes,'rawFindings':1582,'statusCounts':{'CONTEXT_NOT_APPLICABLE':261,'REQUIRED_CONTRACT':208,'FALSE_POSITIVE':4,'NOT_REVIEWED_CURRENT_SOURCE':1109},'productionChanges':0,'testExecutionsIssued':0,'wholeReplayed':False,'ptAlternativeCompleted':0,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    os.umask(0o077);OUT.mkdir()
    for name,data in(('manifest.json',value),('decisions.json',decisions)):
        with(OUT/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='scopes'}));print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'decisionsSha256':sha(OUT/'decisions.json')}))


if __name__=='__main__':main()
