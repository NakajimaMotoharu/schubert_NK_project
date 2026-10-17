"""Host-only new SSC304 signed candidate after original full/static; never runtime authority."""
import ast
import hashlib
import inspect
import json
import re
import pg4860_ssc301_302_signed_candidate as previous
import pg4970_ssc304_whole_qualification as qualified
from pg4968_ssc304_full import SOURCE,ROOT,W

prior=previous.prior
P,T=previous.P,ROOT
OLD_SOURCE=previous.SOURCE
OLD_BOM='08300d492e9eb5ba6e31eb646c21e51fc3eb4d30680e205c2adcd35c92d298b2'
OLD,NEXT=W/'pg4860-release-v1',W/'pg4980-release-v1'
FROZEN,SIG=W/'pg4980-frozen-six-v1',P/'pg4980-manifest-v1.sig'
GATE=None
require,grouped=previous.require,previous.grouped


def validate_gate(outer,source):
    require(type(outer)is dict and type(outer.get('actualExit'))is int and outer['actualExit']==0)
    gate=outer['result']
    expected={'actualExit':0,'productionSource':source,'tests':3791,'suites':553,'mainClasses':1650,
        'FESFlakyNotRun':0,'staticSixModules':0,'allSixMainBuildsPassed':True,'allSixFormatBeforeAnyPt':True,
        'allOriginalCaseIdentitiesRetained':True,'oldNativeImported':False,'candidateNativePending':True,
        'F03Accepted':False,'formalAccepted':False,'global100':False}
    require(all(type(gate.get(k))is type(v)and gate[k]==v for k,v in expected.items()))
    require(gate['newCases']==[list(v)for v in qualified.added_cases()]and gate['testClassAliases']=={})
    require(set(gate['jarHashes'])==set(prior.MODULES)and all(re.fullmatch('[a-f0-9]{64}',h)for h in gate['jarHashes'].values()))
    actual=grouped(gate['allPhysicalMainSha256'])
    require(set(gate['modules'])==set(prior.MODULES)and type(gate.get('unchangedPhysicalClasses'))is int
        and gate['unchangedPhysicalClasses']==1646)
    require(sum(map(len,actual.values()))==1650 and sum(v['tests']for v in gate['modules'].values())==3791
        and sum(v['suites']for v in gate['modules'].values())==553
        and all(gate['modules'][m]['mainClasses']==len(actual[m])for m in prior.MODULES))
    rows=gate['changedClasses']
    require(len(rows)==len({r['class']for r in rows})==4
        and {r['class']for r in rows if r['action']=='MODIFIED'}==qualified.MODIFIED
        and {r['class']for r in rows if r['action']=='ADDED_INTERNAL_INTERFACE'}==qualified.INTERFACES)
    require(re.fullmatch('[a-f0-9]{64}',gate['formatBeforePtProofSha256'])is not None)
    return gate


def verify_delta(before,after):
    require(GATE is not None and set(before)==set(after)==set(prior.MODULES))
    flat=lambda value:{m+':'+n:h for m,rows in value.items()for n,h in rows.items()}
    rows,unchanged=qualified.physical_difference(flat(before),flat(after),GATE['allPhysicalMainSha256'])
    require(rows==GATE['changedClasses']and unchanged==1646)
    return 1650


def qualification_matches(outer):
    raw=(W/'pg4970-ssc304-whole-qualified-v1/qualify.private.py').read_bytes()
    return hashlib.sha256(raw).hexdigest()==outer['payloadSha256']and outer['wholeReplayed']is False


def receive(module):
    require(GATE is not None and module in prior.MODULES)
    raw=inspect.getsource(previous.old.old.receive).replace('PG4420','PG4968').replace('pg4432','pg4980')
    ns={**vars(previous.old.old),'prior':prior,'GATE':GATE,'FROZEN':FROZEN,'OLD':OLD}
    exec(compile(raw,'<actual qualified SSC304 Jar transfer>','exec'),ns)
    return ns['receive'](module)


def main_source():
    raw=previous.main_source()
    changes={'pg4860':'pg4980','PG4860':'PG4980','pg4702':'pg4860','PG4702':'PG4860',
        previous.SOURCE:SOURCE,'pg4846-ssc301-302-whole-qualified-v1':'pg4970-ssc304-whole-qualified-v1'}
    for index,key in enumerate(changes):raw=raw.replace(key,'__SIGN4980_'+str(index)+'__')
    for index,value in enumerate(changes.values()):raw=raw.replace('__SIGN4980_'+str(index)+'__',value)
    tree=ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node,ast.Constant)and type(node.value)is int and node.value in {3761,551,1647}:
            node.value={3761:3791,551:553,1647:1650}[node.value]
        if isinstance(node,ast.Dict):
            for index,key in enumerate(node.keys):
                if isinstance(key,ast.Constant)and key.value=='addedClasses':node.values[index]=ast.Constant(3)
    raw=ast.unparse(ast.fix_missing_locations(tree))
    marker="{'VERSION', 'api/api.jar', 'operations/batch.jar'} <= changed"
    require(raw.count(marker)==1)
    return raw.replace(marker,"{'VERSION', 'operations/batch.jar'} <= changed",1)


def main():
    global GATE
    outer=json.loads((W/'pg4970-ssc304-whole-qualified-v1/manifest.safe.json').read_bytes())
    GATE=validate_gate(outer,SOURCE);require(qualification_matches(outer))
    diagnostic=json.loads((W/'pg4976-ssc304-static-v1/manifest.safe.json').read_bytes())
    require(diagnostic['actualExit']==0 and diagnostic['productionSource']==SOURCE
        and diagnostic['result']['sameCurrentSixJarAbi']is True
        and diagnostic['result']['pmd']['processingErrors']==0
        and diagnostic['result']['checkstyle']['actualExit']==0
        and diagnostic['result']['checkstyle']['findings']==0
        and diagnostic['result']['F03Accepted']is False)
    require(not any(p.exists()for p in(NEXT,FROZEN,SIG,W/'pg4980-candidate-build-v1.safe.json')))
    ns={**vars(prior),'__file__':__file__,'PRODUCTION':SOURCE,'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,
        'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,'SIG':SIG,'validate_gate':validate_gate,'verify_delta':verify_delta,
        'receive':receive,'qualification_matches':qualification_matches}
    exec(compile(main_source(),'<host-only SSC304 exact signed candidate>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
