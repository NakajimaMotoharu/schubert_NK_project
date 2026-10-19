"""Current qualified3905 host candidate only; no deployment/start authority or F03 pass."""
import ast
import hashlib
import inspect
import json
import re
import symtable
import subprocess
import zipfile
from pg4426_relocated_jar_contract import records
import pg5430_ownership_signed_candidate as previous
import pg5574_monitor_whole_qualification as qualification
from pg5590_current_static_projection import SOURCE,ROOT,W,BASE

prior=previous.prior
P,T=previous.P,ROOT
OLD_SOURCE='29612b2a484a5ab7418e02a491c4360af7444626'
OLD_BOM='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6'
OLD,NEXT=W/'pg5430-release-v1',W/'pg5598-release-v1'
FROZEN,SIG=W/'pg5598-frozen-six-v1',P/'pg5598-manifest-v1.sig'
GATE=None
SIGNED_DELTA=None
CONTAINER_PROOFS={}
require,grouped=previous.require,previous.grouped
CHANGED=set(qualification.PHYSICAL_KINDS)|{'api:dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.class'}


def validate_gate(outer,source):
    require(type(outer)is dict and type(outer.get('actualExit'))is int and outer['actualExit']==0)
    gate=outer['result']
    expected={'actualExit':0,'productionSource':source,'tests':3905,'suites':563,'mainClasses':1664,
      'FESFlakyNotRun':0,'staticSixModules':0,'allSixMainBuildsPassed':True,'allSixFormatBeforeAnyPt':True,
      'allOriginalCaseIdentitiesRetained':True,'oldNativeImported':False,'candidateNativePending':True,
      'F03Accepted':False,'formalAccepted':False,'global100':False}
    require(all(type(gate.get(k))is type(v)and gate[k]==v for k,v in expected.items()))
    added=[list(v)for v in qualification.added_cases()]
    require(gate['declaredNewCases']==gate['newCases']==added and len(added)==5 and gate['testClassAliases']=={} and gate['newCaseInvocationAliases']=={})
    require(set(gate['jarHashes'])==set(prior.MODULES)and all(re.fullmatch('[0-9a-f]{64}',v)for v in gate['jarHashes'].values()))
    physical=grouped(gate['allPhysicalMainSha256'])
    require(set(gate['modules'])==set(prior.MODULES)and sum(map(len,physical.values()))==1664
      and sum(r['tests']for r in gate['modules'].values())==3905 and sum(r['suites']for r in gate['modules'].values())==563
      and all(gate['modules'][m]['mainClasses']==len(physical[m])for m in prior.MODULES))
    require(re.fullmatch('[0-9a-f]{64}',gate['formatBeforePtProofSha256'])is not None)
    return gate


def delta(before,after,expected_old,expected_new):
    require(set(before)==set(after)==set(prior.MODULES))
    flat=lambda value:{module+':'+name:digest for module,rows in value.items()for name,digest in rows.items()}
    old,new=flat(before),flat(after)
    require(old==expected_old and new==expected_new and len(old)==len(new)==1664 and set(old)==set(new))
    modified={name for name in old if old[name]!=new[name]}
    require(modified==CHANGED)
    return{'added':[],'removed':[],'modified':sorted(modified),'unchangedOldClasses':1652,'oldPhysicalMain':1664,'newPhysicalMain':1664,
      'declaredCodeChanges':7,'debugOnlyPhysicalChanges':5,'debugDifferencesRetained':True}


def verify_delta(before,after):
    global SIGNED_DELTA
    require(GATE is not None)
    old=json.loads((W/'pg5416-ownership-whole-qualified-v2/manifest.safe.json').read_bytes())
    require(old['actualExit']==0 and old['result']['productionSource']==OLD_SOURCE)
    SIGNED_DELTA=delta(before,after,old['result']['allPhysicalMainSha256'],GATE['allPhysicalMainSha256'])
    return 1664


def qualification_matches(outer):
    return hashlib.sha256((W/qualification.SLOT/'qualify.private.py').read_bytes()).hexdigest()==outer['payloadSha256']and outer['wholeReplayed']is False


def verify_candidate_container(before,after,old_classes,new_classes,module,qualified_jar_sha256):
    require(re.fullmatch('[0-9a-f]{64}',qualified_jar_sha256)is not None
      and hashlib.sha256(after.read_bytes()).hexdigest()==qualified_jar_sha256)
    a,b=records(before),records(after)
    require({k:v['sha256']for k,v in a.items()if k.endswith('.class')}==old_classes
      and{k:v['sha256']for k,v in b.items()if k.endswith('.class')}==new_classes and set(a)==set(b))
    changed={k for k in new_classes if old_classes.get(k)!=new_classes[k]}
    if module=='batch':
        member='META-INF/maven/dev.codex.schubert/schubert-nk-batch/pom.xml';path='src/schubert-nk-batch/pom.xml'
        expected=[]
        for source,digest in((OLD_SOURCE,'d61df303d71a6f62c9c16f45ed7cf34c56fca65c44a195a17a595b247308db6d'),
          (SOURCE,'83f2ee9a80d1993f4a05cf91fe9c64155383b51435447634800dee6c99a65517')):
            raw=subprocess.check_output(['git','show',source+':'+path],cwd=ROOT)
            require(hashlib.sha256(raw).hexdigest()==digest);expected.append(raw)
        with zipfile.ZipFile(before)as old,zipfile.ZipFile(after)as new:require(old.read(member)==expected[0]and new.read(member)==expected[1])
        changed.add(member)
    actual_changed={name for name in a if a[name]['sha256']!=b[name]['sha256']}
    require(actual_changed==changed)
    metadata=[]
    for name in a:
        old,new=a[name],b[name]
        require(old['header']==new['header']and old['descriptorKind']==new['descriptorKind'])
        old_meta,new_meta=old['metadata'],new['metadata']
        require(old_meta[:-1]==new_meta[:-1])
        if old_meta[-1]!=new_meta[-1]:
            # ZIP member mode is not filesystem release/Unit authorization.
            # Only ordinary nonexecutable source/POM members may inherit the
            # canonical extraction/analysis/Maven copy umasks; all actual bytes
            # are additionally pinned to the independent whole Jar SHA above.
            source=ROOT/('src/schubert-nk-'+module+'/src/main/resources')/name
            pom='META-INF/maven/dev.codex.schubert/schubert-nk-'+module+'/pom.xml'
            require(not name.endswith(('.class','/'))and(source.is_file()or name==pom))
            old_mode,new_mode=old_meta[-1]>>16,new_meta[-1]>>16
            require(old_meta[-1]&65535==new_meta[-1]&65535 and old_mode==0o100664 and new_mode==0o100644)
            metadata.append({'member':name,'oldExternalAttr':old_meta[-1],'newExternalAttr':new_meta[-1],'sourceBackedNonexecutable':True})
        if name not in changed:require(old['compressed']==new['compressed'])
    with zipfile.ZipFile(before)as left,zipfile.ZipFile(after)as right:
        first,second=left.namelist(),right.namelist()
    return{'allMembersValidated':True,'physicalClasses':len(new_classes),'exactBatchTestScopePomMetadata':module=='batch','oldNativeImported':False,
      'wholeQualifiedJarSha256':qualified_jar_sha256,'sameMemberSet':True,'oldMemberOrderSha256':hashlib.sha256(json.dumps(first).encode()).hexdigest(),
      'newMemberOrderSha256':hashlib.sha256(json.dumps(second).encode()).hexdigest(),'memberOrderChanged':first!=second,'metadataDifferences':metadata,
      'allUnchangedCompressedPayloadsIdentical':True,'jarRewritten':False}


def receive(module):
    require(GATE is not None and module in prior.MODULES)
    template=previous.previous.previous.old.old
    raw=inspect.getsource(template.receive).replace('PG4420','PG5588').replace('pg4432','pg5598')
    def validate_container(before,after,old,new):
        require(module not in CONTAINER_PROOFS)
        value=verify_candidate_container(before,after,old,new,module,GATE['jarHashes'][module]);CONTAINER_PROOFS[module]=value
        return value
    scope={**vars(template),'prior':prior,'GATE':GATE,'FROZEN':FROZEN,'OLD':OLD,'require':require,'verify_relocated_container':validate_container}
    exec(compile(raw,'<actual current3905 qualified Jar receiver>','exec'),scope)
    return scope['receive'](module)


def main_source():
    raw=previous.main_source()
    replacements={'pg5430':'pg5598','PG5430':'PG5598','pg4980':'pg5430','PG4980':'PG5430',
      previous.SOURCE:SOURCE,'pg5416-ownership-whole-qualified-v2':qualification.SLOT}
    for i,key in enumerate(replacements):raw=raw.replace(key,'__SIGN5598_'+str(i)+'__')
    for i,value in enumerate(replacements.values()):raw=raw.replace('__SIGN5598_'+str(i)+'__',value)
    class Rebase(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in(3896,562):return ast.copy_location(ast.Constant({3896:3905,562:563}[node.value]),node)
            return node
        def visit_Dict(self,node):
            node=self.generic_visit(node)
            changes={'addedClasses':0,'removedClasses':0,'oldPhysicalMain':1664,'semanticChangedClasses':7,'debugOnlyChangedClasses':5}
            for key,value in zip(node.keys,node.values):
                if isinstance(key,ast.Constant)and key.value in changes:
                    require(isinstance(value,ast.Constant));value.value=changes[key.value]
            if any(isinstance(key,ast.Constant)and key.value=='candidatePurpose'for key in node.keys):
                node.keys.append(ast.Constant('containerPhysicalProofs'));node.values.append(ast.Name(id='CONTAINER_PROOFS',ctx=ast.Load()))
            return node
    raw=ast.unparse(ast.fix_missing_locations(Rebase().visit(ast.parse(raw))))
    old="{'VERSION', 'operations/batch.jar', 'operations/lib/schubert-nk-storage-0.1.0-SNAPSHOT.jar', 'operations/lib/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar'} <= changed"
    require(raw.count(old)==1)
    raw=raw.replace(old,"{'VERSION', 'api/api.jar', 'web/web.jar', 'operations/batch.jar', 'operations/lib/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar'} <= changed",1)
    marker='require(verify_delta(before, after) == 1664)'
    require(raw.count(marker)==1)
    return raw.replace(marker,marker+'\n    require(set(CONTAINER_PROOFS) == set(MODULES))',1)


def main():
    global GATE
    outer=json.loads((W/qualification.SLOT/'manifest.safe.json').read_bytes());GATE=validate_gate(outer,SOURCE);require(qualification_matches(outer))
    diagnostic=json.loads((W/'pg5578-monitor-static-v1/manifest.safe.json').read_bytes())
    require(diagnostic['actualExit']==0 and diagnostic['productionSource']==SOURCE and diagnostic['result']['sameCurrentSixJarAbi']is True
      and diagnostic['result']['pmd']['processingErrors']==0 and diagnostic['result']['checkstyle']['actualExit']==0
      and diagnostic['result']['checkstyle']['findings']==0 and diagnostic['result']['F03Accepted']is False)
    scope_path=BASE/'PG5596-current-factory-scope-v1/manifest.json';contract=json.loads(scope_path.read_bytes())
    require(contract['actualExit']==0 and contract['source']==SOURCE and contract['wholeSourceQualified']and contract['readonlyCandidatesUnknown']==0
      and contract['currentWholeCases']==3905 and contract['currentWholeMain']==1664 and not contract['newSourceNativeQualified'])
    namespace={**vars(prior),'__file__':__file__,'PRODUCTION':SOURCE,'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,
      'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,'SIG':SIG,'validate_gate':validate_gate,'verify_delta':verify_delta,
      'receive':receive,'qualification_matches':qualification_matches,'SIGNED_DELTA':None,'CONTAINER_PROOFS':CONTAINER_PROOFS}
    def checked_delta(before,after):
        count=verify_delta(before,after);namespace['SIGNED_DELTA']=SIGNED_DELTA;return count
    namespace['verify_delta']=checked_delta
    raw=main_source()
    # Check real global symbols, not co_names (which also contains attributes).
    required={s.get_name()for s in symtable.symtable(raw,'<candidate>','exec').get_children()[0].get_symbols()if s.is_global()and s.is_referenced()}
    require(required<=set(namespace)|set(dir(__import__('builtins'))))
    exec(compile(raw,'<current signed candidate>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
