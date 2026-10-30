"""Independent guard AST/minimal-pin fix and immutable old4 disclosure; no Product execution."""
import ast
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import reviewed_whole_pure_source_post_v3 as guard

PIN='f88a4e4ae812291db25fbb40084381bfd6dadc349c4bf2e3635597d03f137234'
OUT=data.BASE/'PG15476-nonsecret-digest-disclosure-post-v1'
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def checked(folder,pin):return data.read_checked(data.BASE/folder/'manifest.json',pin)
def tree(text):return ast.dump(ast.parse(text),include_attributes=False)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    m=checked('PG15475-nonsecret-digest-disclosure-v2',PIN)
    p=checked(*m['disclosureCorrection']['originalPost']);raw=checked(*m['disclosureCorrection']['originalRaw']);oldind=checked(*m['disclosureCorrection']['originalIndependent']);r=checked(*m['registryReference'])
    require(m['actualExit']==p['actualExit']==raw['actualExit']==oldind['actualExit']==r['actualExit']==0 and m['source']==p['source']==r['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c','genuine source/evidence')
    library={version:(data.ROOT/('tools/quality/reviewed_whole_pure_source_post_v'+str(version)+'.py')).read_bytes() for version in [1,2,3]}
    require(data.sha(library[1])=='dedda4f153010fa22719a6aefd6406dc90a862e710f9097db90bc4ba38975341' and data.sha(library[2])==m['sharedV2Sha256']=='4e23c3fe151c8c42c535589f9c2f39533ea7dfa000e3b036a17aaae779f08bee' and data.sha(library[3])==m['sharedV3Sha256']=='f41c2d98d5611a4519e2cc71de74998a6c24a491570242664767318e219e145f','distinct exact versions/pins')
    require(subprocess.check_output(['git','show','HEAD:tools/quality/reviewed_whole_pure_source_post_v2.py'],cwd=data.ROOT)==library[2],'unchanged Git v2, not runtime invented expected')
    old=(data.ROOT/'tools/quality/pg15474_nonsecret_digest_disclosure.py').read_text();new=(data.ROOT/'tools/quality/pg15475_nonsecret_digest_disclosure_v2.py').read_text()
    require(data.sha(old.encode())=='036bc2366c8c7c190e0789b5632ee22d92c50ccdfae26531e407064c28081cb9' and old.replace("V2='dedda4f153010fa22719a6aefd6406dc90a862e710f9097db90bc4ba38975341'","V2='4e23c3fe151c8c42c535589f9c2f39533ea7dfa000e3b036a17aaae779f08bee'").replace('PG15474-nonsecret-digest-disclosure-v1','PG15475-nonsecret-digest-disclosure-v2')==new,'BUG2130 old pin failure retained/minimal correction only')
    require("data.sha(shared.encode())=='4e23c3fe151c8c42c535589f9c2f39533ea7dfa000e3b036a17aaae779f08bee'" in (data.ROOT/'tools/quality/pg15441_auth_context_codec_seven_independent_v2.py').read_text(),'existing independent explicit v2 pin nonapplicable')
    base=ast.parse(library[2]);current=ast.parse(library[3]);current.body[0].value=copy.deepcopy(base.body[0].value)
    defs=[x for x in current.body if isinstance(x,ast.FunctionDef) and x.name=='validate_reviewed_effect_text'];require(len(defs)==1,'one new pure guard')
    current.body.remove(defs[0]);function=next(x for x in current.body if isinstance(x,ast.FunctionDef) and x.name=='verify_profile')
    expected_calls=ast.parse("""for definition in profile['sources'].values():
    validate_reviewed_effect_text((data.ROOT/definition['path']).read_text())
for path in original.TESTS.values():
    if not path.is_relative_to(data.ROOT/'src') or '/src/test/java/' not in str(path):raise ValueError('reviewed original src test only')
    validate_reviewed_effect_text(path.read_text())
""").body
    require([ast.dump(x,include_attributes=False) for x in function.body[2:4]]==[ast.dump(x,include_attributes=False) for x in expected_calls],'guard before old assessment/output creation')
    del function.body[2:4];removed=0
    for node in ast.walk(current):
        if isinstance(node,ast.Call):
            matches=[x for x in node.keywords if x.arg=='effectDisclosureGuardVersion']
            for value in matches:
                require(isinstance(value.value,ast.Constant) and value.value.value==3,'typed new guard marker');node.keywords.remove(value);removed+=1
    require(removed==1 and ast.dump(current,include_attributes=False)==ast.dump(base,include_attributes=False),'all other profile/analysis/counter/output AST unchanged')
    guard_checks=[]
    for phrase in ['MessageDigest.getInstance("SHA-256")','WebStartupInputs fixture','new ApiConfigurationLoader(source, map)','SecureRandom rng','new AuthContextCodec()','javax.crypto.Mac field']:
        try:guard.validate_reviewed_effect_text(phrase)
        except ValueError:guard_checks.append(phrase)
        else:raise ValueError('known digest/crypto helper false-negative')
    for phrase in ['class MessageDigestWrapper {}','class SecureRandomness {}','final class Fields { long id; }']:
        require(guard.validate_reviewed_effect_text(phrase) is True,'word boundary pure values');guard_checks.append(phrase)
    normal=checked('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3');hashes=normal['begin']['inputHashes']
    all_registered=[];unregistered=[];extra_hit=[]
    existing=set()
    for row in m['scannedOriginalPostReferences']:
        value=checked(row['name'],row['sha256']);existing|={c['classname'] for c in value.get('cases',[])}
    markers=['ApiNonSecretConfig','WebNonSecretConfig','ApiStartupInputs','WebStartupInputs','ApiConfigurationLoader','WebConfigurationLoader']
    for fqn in r['suiteNames']:
        paths=[path for path in hashes if path.endswith('/src/test/java/'+fqn.replace('.','/')+'.java')]
        if not paths:unregistered.append(fqn);continue
        require(len(paths)==1,'exact registered current suite')
        path=paths[0];b=(data.ROOT/path).read_bytes();require(data.sha(b)==hashes[path],'all current registered suite source pins');all_registered.append(dict(test=fqn,path=path,sha256=hashes[path]))
        if fqn not in existing:
            require(not any(v in b.decode() for v in markers),'other resource family has no known config helper');extra_hit.append(fqn)
    require(len(all_registered)==225 and len(unregistered)==1 and len(extra_hit)==8 and m['registeredCurrentSuiteCount']==217 and len(m['knownHelperScan'])==3,'225 registered/one tool suite, extra8 families nonapplicable')
    original_preserved={k:p[k] for k in m['preservedOriginalQualification']}
    require(wire(original_preserved)==wire(m['preservedOriginalQualification']) and p['cases']==raw['cases'] and p['totals']=={'LINE':{'missed':2,'covered':11},'METHOD':{'missed':1,'covered':3},'CLASS':{'missed':0,'covered':2},'BRANCH':{'missed':0,'covered':0}} and oldind['semanticNegativeVectors']==24,'all old source/run/counter/gap/XML retained')
    require('cryptoOrKeyOperationsInvoked' not in (data.ROOT/'tools/quality/pg15344_api_startup_inputs_independent.py').read_text(),'old independent did not verify effect field, not falsely credited')
    for path,row in m['callerHelperSourceProof'].items():require(data.sha((data.ROOT/path).read_bytes())==hashes[path]==row['sha256'] and row['sourceLines'],'all concrete original unchanged source edges')
    fixed=copy.deepcopy(m['disclosureCorrection'])
    def contract(value):
        require(wire(value['disclosureCorrection'])==wire(fixed) and value['disclosureCorrection']['originalCryptoOrKeyOperationsInvoked'] is False and value['disclosureCorrection']['effectiveCryptoOrKeyOperationsInvoked'] is True and value['disclosureCorrection']['effectiveOnlyReviewedPureValueSuites'] is False,'exact truthful appended digest correction')
        require(wire(value['preservedOriginalQualification'])==wire(original_preserved) and value['source']==p['source'] and value['sharedV2Sha256']==data.sha(library[2]) and value['sharedV3Sha256']==data.sha(library[3]),'old evidence/gaps and distinct guard pins')
        require(value['guardMetadataChecks']==31 and value['productTestsExecuted']==value['newUniqueMethods']==value['newSourcePrograms']==value['newAccepted']==0 and value['boundedScanNotWholeTransitiveCallGraph'] is True and value['formalUpdated'] is value['whole451Accepted'] is value['wholeF03Accepted'] is False and value['effortPercent'] is None,'no replay/progress/formal/HOLD credit')
    contract(m);negative=[]
    for key,value in [('source','OLD'),('disclosureCorrection',{}),('preservedOriginalQualification',{}),('sharedV2Sha256',data.sha(library[1])),('sharedV3Sha256',data.sha(library[2])),('guardMetadataChecks',0),('productTestsExecuted',4),('newUniqueMethods',4),('newSourcePrograms',1),('newAccepted',1),('boundedScanNotWholeTransitiveCallGraph',False),('formalUpdated',True),('whole451Accepted',True),('wholeF03Accepted',True),('effortPercent',1)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except (ValueError,KeyError):negative.append(key)
        else:raise ValueError('false disclosure metadata')
    for key,value in [('effectiveCryptoOrKeyOperationsInvoked',False),('actualSecretKeysLoaded',True),('actualCredentialValuesUsed',True),('productTestsReexecuted',4),('priorManifestRetained',False),('effectiveOnlyReviewedPureValueSuites',True)]:
        bad=copy.deepcopy(m);bad['disclosureCorrection'][key]=value
        try:contract(bad)
        except ValueError:negative.append('disclosure-'+key)
        else:raise ValueError('false corrected effect')
    for v in [m,p,oldind,r]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=m['source'],invocation=invocation,correctionManifestSha256=PIN,disclosureCorrection=fixed,preservedOriginalQualificationSha256=data.sha(wire(original_preserved).encode()),metadataNegativeVectors=len(negative),negativeLabels=negative,independentGuardChecks=len(guard_checks),minimalGuardAstDiffConfirmed=True,minimalPinFixConfirmed=True,currentRegisteredSuiteSources=all_registered,unregisteredSourceSuites=unregistered,otherFamilyEightNoKnownHelperTerms=extra_hit,all225RegisteredCurrentSuitesIncludedInKnownHelperScan=True,boundedScanNotWholeTransitiveCallGraph=True,oldOriginalTestMethods=4,productTestsExecuted=0,newUniqueMethods=0,newSourcePrograms=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,relatedBugs=['BUG-2129','BUG-2130'],relatedYkts=['YKT-1876','YKT-1877']))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,metadataNegativeVectors=len(negative),guardMetadataChecks31=m['guardMetadataChecks'],independentGuardChecks=len(guard_checks),allRegisteredSuites=len(all_registered))))
if __name__=='__main__':main()
