"""Host-only signed candidate, actual1643 Main qualified by source family; no VM operation."""
import ast
import hashlib
import inspect
import json
import re
import pg3420_outbox_signed_candidate as previous
import pg3734_hygiene_full_six as whole
import pg3738_hygiene_whole_qualification as qualification
from pg2428_question_signed_candidate import verify_container

W,P,T=previous.W,previous.P,previous.T;SOURCE=whole.SOURCE
OLD=W/'pg3420-release-v1';NEXT=W/'pg3748-release-v1';FROZEN=W/'pg3748-frozen-six-v1';SIG=P/'pg3748-manifest-v1.sig'
OLD_SOURCE=previous.SOURCE;OLD_BOM='dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72'
GATE=None


def require(value):
    if not value:raise ValueError('exact qualified hygiene signed candidate refused')


def validate_gate(outer,source):
    require(type(outer)is dict and type(outer.get('actualExit'))is int and outer['actualExit']==0 and type(outer.get('result'))is dict);g=outer['result'];expected={'actualExit':0,'productionSource':source,'tests':3714,'suites':545,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0,'allSixMainBuildsPassed':True,'allOriginalCaseIdentitiesRetained':True,'oldNativeImported':False,'candidateNativePending':True,'F03Accepted':False,'formalAccepted':False,'global100':False}
    require(all(type(g.get(k))is type(v)and g[k]==v for k,v in expected.items()));require(g.get('newCases')==[list(x)for x in whole.NEW_CASES]);require({m:(v['tests'],v['suites'],v['mainClasses'])for m,v in g['modules'].items()}==whole.EXPECTED)
    require(set(g['jarHashes'])==set(previous.prior.MODULES)and all(re.fullmatch('[0-9a-f]{64}',h)for h in g['jarHashes'].values()));require(set(g['allPhysicalMainSha256'])==set(g['jarHashes'])and sum(len(v)for v in g['allPhysicalMainSha256'].values())==1643)
    changed=g['changedClasses'];require(type(changed)is list and len(changed)>0);seen=set()
    for row in changed:
        key=row['module']+':'+row['class'];require(row['module']in g['jarHashes']and key not in seen and row['class'].endswith('.class')and row['sourcePath'].startswith('src/schubert-nk-'+row['module']+'/src/main/java/'));seen.add(key)
        require(re.fullmatch('[0-9a-f]{64}',row['oldSha256'])and g['allPhysicalMainSha256'][row['module']].get(row['class'])==row['newSha256']and row['oldSha256']!=row['newSha256'])
    return g


def verify_delta(before,after):
    require(GATE is not None and set(before)==set(after)==set(previous.prior.MODULES));require(after==GATE['allPhysicalMainSha256']);actual={}
    for m in before:
        require(before[m].keys()==after[m].keys())
        for n,h in before[m].items():
            if h!=after[m][n]:actual[m+':'+n]=(h,after[m][n])
    expected={r['module']+':'+r['class']:(r['oldSha256'],r['newSha256'])for r in GATE['changedClasses']};require(actual==expected and sum(len(v)for v in after.values())==1643);return 1643


def qualification_matches(outer):
    original=json.loads((W/'pg3734-server-six-v1/manifest.safe.json').read_bytes());raw=qualification.qualification_payload(original);actual=W/'pg3738-hygiene-whole-qualified-v1/qualify.private.py';return actual.read_text()==raw and hashlib.sha256(raw.encode()).hexdigest()==outer['payloadSha256']


def receive(module):
    require(GATE is not None and module in previous.prior.MODULES)
    raw=inspect.getsource(previous.prior.transfer.receive).replace('PG1532','PG3734').replace('pg1535','pg3748');ns={**previous.prior.transfer.__dict__,'FROZEN':FROZEN};exec(compile(raw,'<one exact qualified Jar receive>','exec'),ns);path=ns['receive'](module)
    oldpath={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar'}.get(module)
    if oldpath is None:oldpath=next(r['path']for r in json.loads((OLD/'RELEASE-MANIFEST.json').read_bytes())['artifacts']if r['path'].endswith('/'+path.name))
    verify_container(OLD/oldpath,path,{r['class']for r in GATE['changedClasses']if r['module']==module});return path


def main_source():
    raw=previous.main_source()
    for a,b in [('pg3420','pg3748'),('PG3420','PG3748'),('pg2802','pg3420'),('PG2802','PG3420'),(previous.SOURCE,SOURCE),('pg3414-outbox-full-qualified-v1','pg3738-hygiene-whole-qualified-v1')]:raw=raw.replace(a,b)
    tree=ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node,ast.Constant)and type(node.value)is int and node.value==3712:node.value=3714
        if isinstance(node,ast.Dict):
            for k,v in zip(node.keys,node.values):
                if isinstance(k,ast.Constant)and k.value=='changedClasses':vnew=ast.parse("len(gate['changedClasses'])",mode='eval').body;node.values[node.keys.index(k)]=vnew
                if isinstance(k,ast.Constant)and k.value in {'semanticChangedClasses','debugOnlyChangedClasses'}:node.values[node.keys.index(k)]=ast.Constant(None)
    return ast.unparse(ast.fix_missing_locations(tree))


def main():
    global GATE
    whole.validate(previous.prior.subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip());outer=json.loads((W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes());GATE=validate_gate(outer,SOURCE);require(qualification_matches(outer))
    ns={**previous.prior.__dict__,'__file__':__file__,'PRODUCTION':SOURCE,'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,'SIG':SIG,'validate_gate':validate_gate,'verify_delta':verify_delta,'receive':receive,'qualification_matches':qualification_matches};exec(compile(main_source(),'<host-only unused hygiene candidate>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
