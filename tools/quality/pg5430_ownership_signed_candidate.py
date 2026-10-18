"""Host-only exact current qualified candidate; not deployment authority or F03 acceptance."""
import ast
import hashlib
import inspect
import json
import re
import pg4980_ssc304_signed_candidate as previous
import pg5416_ownership_whole_qualification as qualification
from pg5416_ownership_whole_qualification import SOURCE,ROOT,W,SLOT

prior=previous.prior
P,T=previous.P,ROOT
OLD_SOURCE=previous.SOURCE
OLD_BOM='78a6f8631f188303dd28b4470868564599beda23e9cc5b5a983c7535fea56ef4'
OLD,NEXT=W/'pg4980-release-v1',W/'pg5430-release-v1'
FROZEN,SIG=W/'pg5430-frozen-six-v1',P/'pg5430-manifest-v1.sig'
GATE=None
SIGNED_DELTA=None
require,grouped=previous.require,previous.grouped


def validate_gate(outer,source):
    require(type(outer) is dict and type(outer.get('actualExit')) is int and outer['actualExit']==0)
    gate=outer['result']
    expected={'actualExit':0,'productionSource':source,'tests':3896,'suites':562,'mainClasses':1664,
        'FESFlakyNotRun':0,'staticSixModules':0,'allSixMainBuildsPassed':True,'allSixFormatBeforeAnyPt':True,
        'allOriginalCaseIdentitiesRetained':True,'oldNativeImported':False,'candidateNativePending':True,
        'F03Accepted':False,'formalAccepted':False,'global100':False}
    require(all(type(gate.get(key)) is type(value) and gate[key]==value for key,value in expected.items()))
    declared,actual,aliases=qualification.qualified_added_cases()
    require(gate['declaredNewCases']==[list(row) for row in declared] and gate['newCases']==[list(row) for row in actual]
        and gate['newCaseInvocationAliases']==aliases and gate['testClassAliases']=={})
    require(set(gate['jarHashes'])==set(prior.MODULES) and all(re.fullmatch('[0-9a-f]{64}',value) for value in gate['jarHashes'].values()))
    physical=grouped(gate['allPhysicalMainSha256'])
    require(sum(map(len,physical.values()))==1664 and sum(row['tests'] for row in gate['modules'].values())==3896
        and sum(row['suites'] for row in gate['modules'].values())==562
        and all(gate['modules'][module]['mainClasses']==len(physical[module]) for module in prior.MODULES))
    require(re.fullmatch('[0-9a-f]{64}',gate['formatBeforePtProofSha256']) is not None)
    return gate


def delta(before,after,expected_old,expected_new):
    require(set(before)==set(after)==set(prior.MODULES))
    flat=lambda values:{module+':'+name:digest for module,rows in values.items() for name,digest in rows.items()}
    old,new=flat(before),flat(after)
    require(old==expected_old and new==expected_new and len(old)==1650 and len(new)==1664)
    removed=set(old)-set(new);added=set(new)-set(old)
    require(removed=={'batch:dev/codex/schubert/nk/batch/platform/BackupArchiveProcess$StdinOwner.class'} and len(added)==15)
    modified={name for name in old.keys()&new.keys() if old[name]!=new[name]}
    return {'added':sorted(added),'removed':sorted(removed),'modified':sorted(modified),
        'unchangedOldClasses':len(old)-len(modified)-len(removed),'oldPhysicalMain':1650,'newPhysicalMain':1664}


def verify_delta(before,after):
    global SIGNED_DELTA
    require(GATE is not None)
    baseline=json.loads((W/'pg4970-ssc304-whole-qualified-v1/manifest.safe.json').read_bytes())
    require(baseline['actualExit']==0 and baseline['result']['productionSource']==OLD_SOURCE)
    SIGNED_DELTA=delta(before,after,baseline['result']['allPhysicalMainSha256'],GATE['allPhysicalMainSha256'])
    return 1664


def qualification_matches(outer):
    return (hashlib.sha256((W/SLOT/'qualify.private.py').read_bytes()).hexdigest()==outer['payloadSha256']
        and outer['wholeReplayed'] is False)


def receive(module):
    require(GATE is not None and module in prior.MODULES)
    template=previous.previous.old.old
    raw=inspect.getsource(template.receive).replace('PG4420','PG5414').replace('pg4432','pg5430')
    namespace={**vars(template),'prior':prior,'GATE':GATE,'FROZEN':FROZEN,'OLD':OLD,'require':require}
    exec(compile(raw,'<qualified current3896 Jar receiver>','exec'),namespace)
    return namespace['receive'](module)


def main_source():
    raw=previous.main_source()
    replacements={'pg4980':'pg5430','PG4980':'PG5430','pg4860':'pg4980','PG4860':'PG4980',
        previous.SOURCE:SOURCE,'pg4970-ssc304-whole-qualified-v1':SLOT}
    for index,key in enumerate(replacements):raw=raw.replace(key,'__SIGN5430_'+str(index)+'__')
    for index,value in enumerate(replacements.values()):raw=raw.replace('__SIGN5430_'+str(index)+'__',value)
    class Rebase(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value) is int and node.value in (3791,553,1650):
                return ast.copy_location(ast.Constant({3791:3896,553:562,1650:1664}[node.value]),node)
            return node
        def visit_Dict(self,node):
            self.generic_visit(node)
            names={key.value:index for index,key in enumerate(node.keys) if isinstance(key,ast.Constant)}
            if 'addedClasses' in names:
                node.values[names['addedClasses']]=ast.Constant(15)
                node.values[names['changedClasses']]=ast.parse("len(SIGNED_DELTA['modified'])+len(SIGNED_DELTA['added'])+len(SIGNED_DELTA['removed'])",mode='eval').body
                extra={'removedClasses':ast.Constant(1),'oldPhysicalMain':ast.Constant(1650),
                    'signedBaseClassDelta':ast.Name(id='SIGNED_DELTA',ctx=ast.Load()),
                    'F03Accepted':ast.Constant(False),'newSourceNativeQualified':ast.Constant(False),
                    'deploymentAuthority':ast.Constant(False),'candidatePurpose':ast.Constant('PGPT_QUALIFICATION_ONLY')}
                for key,value in extra.items():node.keys.append(ast.Constant(key));node.values.append(value)
            return node
    raw=ast.unparse(ast.fix_missing_locations(Rebase().visit(ast.parse(raw))))
    marker="{'VERSION', 'operations/batch.jar'} <= changed"
    require(raw.count(marker)==1)
    return raw.replace(marker,"{'VERSION', 'operations/batch.jar', 'operations/lib/schubert-nk-storage-0.1.0-SNAPSHOT.jar', 'operations/lib/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar'} <= changed",1)


def main():
    global GATE
    outer=json.loads((W/SLOT/'manifest.safe.json').read_bytes());GATE=validate_gate(outer,SOURCE)
    require(qualification_matches(outer))
    diagnostic=json.loads((W/'pg5424-ownership-static-v1/manifest.safe.json').read_bytes())
    require(diagnostic['actualExit']==0 and diagnostic['productionSource']==SOURCE and diagnostic['result']['sameCurrentSixJarAbi'] is True
        and diagnostic['result']['pmd']['processingErrors']==0 and diagnostic['result']['checkstyle']['actualExit']==0
        and diagnostic['result']['checkstyle']['findings']==0 and diagnostic['result']['F03Accepted'] is False)
    scope=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5422-factory-whole-scope-v1/manifest.json'
    require(hashlib.sha256(scope.read_bytes()).hexdigest()=='a30198c0408c2e09e54e84816897156e5eeb7207a94543a41fd73c200e4e8718')
    contract=json.loads(scope.read_bytes())
    require(contract['source']==SOURCE and contract['actualExit']==0 and contract['wholeSourceQualified'] is True
        and contract['readonlyCandidatesUnknown']==0 and contract['newSourceNativeQualified'] is False)
    namespace={**vars(prior),'__file__':__file__,'PRODUCTION':SOURCE,'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,
        'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,'SIG':SIG,'validate_gate':validate_gate,'verify_delta':verify_delta,
        'receive':receive,'qualification_matches':qualification_matches,'SIGNED_DELTA':None}
    # The frozen function resolves the delta written by verify_delta, not a stale copied binding.
    def check_delta(before,after):
        result=verify_delta(before,after);namespace['SIGNED_DELTA']=SIGNED_DELTA;return result
    namespace['verify_delta']=check_delta
    exec(compile(main_source(),'<host-only current ownership candidate>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
