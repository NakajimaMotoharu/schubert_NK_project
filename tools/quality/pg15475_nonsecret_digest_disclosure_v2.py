"""Metadata-only source-bound SHA256 disclosure correction; never reexecutes Product tests."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import reviewed_whole_pure_source_post_v3 as guard

OUT=data.BASE/'PG15475-nonsecret-digest-disclosure-v2'
REG=('PG15464-current1831-hasher-public-value-registry-v1','a5f265660960abfe3014bb08d7e9ba46b3e2e30ba3d3dbddbf3532a106c4f1a0')
POST=('PG15342-api-startup-inputs-four-post-v2','22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3')
RAW=('PG15340-api-startup-inputs-four-pt-v1','40ecce1446324f21b6c9f260aa102dcf6d57409a0479c0e7f38c50c6054a9fc7')
IND=('PG15344-api-startup-inputs-independent-v1','1c139ccf95f4f32b714ff0ace5caa34cf1faf8f7f09a879b329c539163149c30')
V2='4e23c3fe151c8c42c535589f9c2f39533ea7dfa000e3b036a17aaae779f08bee'
V3='f41c2d98d5611a4519e2cc71de74998a6c24a491570242664767318e219e145f'
WORDS=['MessageDigest','Cipher','Mac','SecretKeyFactory','SecretKeySpec','KeyFactory','KeyGenerator','KeyStore','SecureRandom','Security','ContextHash','AuthContextCodec','PasswordHasher','ApiNonSecretConfig','WebNonSecretConfig','ApiConfigurationLoader','WebConfigurationLoader','ApiStartupInputs','WebStartupInputs']
CHAIN=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiStartupInputsTest.java','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs.java','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiConfigurationLoader.java','src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfig.java']
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    r,p,raw,ind=map(read,[REG,POST,RAW,IND])
    require(all(v['actualExit']==0 and v['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' for v in [r,p,raw,ind]) and ind['postSha256']==POST[1] and ind['semanticNegativeVectors']==24,'original source/raw/post/ind retained')
    require(p['cryptoOrKeyOperationsInvoked'] is False and p['onlyReviewedPureValueSuites'] is True and p['originalManifestSha256']==RAW[1] and p['cases']==raw['cases'] and p['execSha256']==raw['execSha256'],'genuine incorrect effect field, not speculative')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'));hashes=normal['begin']['inputHashes'];chain={}
    for path in CHAIN:
        b=(data.ROOT/path).read_bytes();require(data.sha(b)==hashes[path]==raw['begin']['sourceHashes'][path],'unchanged exact caller/helper chain')
        chain[path]=dict(sha256=hashes[path],sourceLines=[dict(line=i,text=line.strip()) for i,line in enumerate(b.decode().splitlines(),1) if any(v in line for v in ['new ApiStartupInputs(source, ENV).load()','assertEquals("DEBUG", result.config()','ApiNonSecretConfig.parse(','new Values(config.load(), credentials)','return ApiNonSecretConfig.parse','MessageDigest.getInstance("SHA-256")','.digest(bytes.toString().getBytes(StandardCharsets.UTF_8))'])])
    require(all(chain[path]['sourceLines'] for path in CHAIN),'every concrete edge and digest byte semantics')
    actual=[]
    for filename,pin in p['xmlHashes'].items():
        b=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(b)==pin==raw['xmlHashes'][filename],'original XML untouched')
        root=ET.fromstring(b);require(int(root.get('tests'))==4 and all(int(root.get(k))==0 for k in ['failures','errors','skipped']),'original4 genuine FES0')
        actual.extend(c.get('name') for c in root.findall('testcase') if not list(c))
    require(len(actual)==4 and 'opsApiInput001CombinesIndependentFixedInputs' in actual and 'opsApiInput004NullContracts' in actual,'successful concrete load and direct parse paths')
    lib2=data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v2.py';lib3=data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v3.py'
    require(data.sha(lib2.read_bytes())==V2 and data.sha(lib3.read_bytes())==V3,'old immutable/new guard source')
    checks=[]
    for word in WORDS:
        try:guard.validate_reviewed_effect_text('class Fixture { '+word+' field; }')
        except ValueError:checks.append('reject-'+word)
        else:raise ValueError('crypto lexical guard missed known type')
    for text in ['final class Plain { int value; }','class X { int hashCode; }','class XMessageDigest2 {}','class SecureRandomness {}']:
        require(guard.validate_reviewed_effect_text(text) is True,'ordinary values/word boundaries remain allowed');checks.append('allow-'+text)
    for value in [None,1,{},b'code']:
        try:guard.validate_reviewed_effect_text(value)
        except ValueError:checks.append('reject-type-'+type(value).__name__)
        else:raise ValueError('source text type guard')
    for path in CHAIN:
        try:guard.validate_reviewed_effect_text((data.ROOT/path).read_text())
        except ValueError:checks.append('reject-original-chain-'+path)
        else:raise ValueError('known actual crypto/helper must use dedicated profile')
    # Bounded universe: all current post references with registered normal Test bodies.
    markers=['ApiNonSecretConfig','WebNonSecretConfig','ApiStartupInputs','WebStartupInputs','ApiConfigurationLoader','WebConfigurationLoader']
    scan=[];references=[];scanned_suites=set();unregistered=set()
    for row in r['originalPostReferences']:
        original=read((row['name'],row['sha256']));hits=[]
        for fqn in sorted({v['classname'] for v in original.get('cases',[])}):
            suffix='/src/test/java/'+fqn.replace('.','/')+'.java'
            paths=[path for path in hashes if path.endswith(suffix)]
            if not paths:unregistered.add(fqn);continue
            require(len(paths)==1,'unambiguous registered source')
            path=paths[0];b=(data.ROOT/path).read_bytes();require(data.sha(b)==hashes[path],'all scanned current Test pins')
            scanned_suites.add(fqn);text=b.decode();terms=[v for v in markers if v in text]
            if terms:hits.append(dict(test=fqn,path=path,sha256=hashes[path],knownHelperTerms=terms))
        references.append(dict(name=row['name'],sha256=row['sha256']))
        if hits:scan.append(dict(name=row['name'],sha256=row['sha256'],effectFieldState='UNSPECIFIED' if 'cryptoOrKeyOperationsInvoked' not in original else original['cryptoOrKeyOperationsInvoked'],hits=hits))
    require({x['name'] for x in scan}=={'PG15224-nonsecret-config-fourteen-post-v1','PG15302-api-config-readiness-eleven-post-v1',POST[0]} and [x['name'] for x in scan if x['effectFieldState'] is False]==[POST[0]],'finite known helper scan: false1/unspecified2, not entire call graph proof')
    preserved={k:copy.deepcopy(p[k]) for k in ['source','originalManifestSha256','cases','xmlHashes','execSha256','sessionIdentity','physicalClasses','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','totals','missedLines','owners','reportedEnvironment','targetUnitFour100','strictFour100GateExit']}
    disclosure=dict(originalPost=list(POST),originalRaw=list(RAW),originalIndependent=list(IND),effectDisclosureDomain='REVIEWED_PRODUCT_AND_ORIGINAL_TEST_BODY_NOT_EVIDENCE_HASHING_OR_SDK_INTERNAL_BOOTSTRAP',originalCryptoOrKeyOperationsInvoked=False,effectiveCryptoOrKeyOperationsInvoked=True,effectiveOnlyReviewedPureValueSuites=False,cryptoOperationKind='SHA256_PUBLIC_NONSECRET_CANONICAL_CONFIG_NO_KEYS',actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,priorManifestRetained=True,originalSuccessfulPathsAndUnchangedCodeConfirmDigest=True,productTestsReexecuted=0,previousIndependentEffectFlagWasNotChecked=True)
    for value in [r,p,ind]:verify(value['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=r['source'],invocation=invocation,registryReference=list(REG),disclosureCorrection=disclosure,preservedOriginalQualification=preserved,callerHelperSourceProof=chain,sharedV2Sha256=V2,sharedV3Sha256=V3,guardMetadataChecks=len(checks),guardCheckLabels=checks,knownHelperScan=scan,scannedOriginalPostReferences=references,registeredCurrentSuiteCount=len(scanned_suites),unregisteredSourceSuites=sorted(unregistered),boundedScanNotWholeTransitiveCallGraph=True,productTestsExecuted=0,newUniqueMethods=0,newSourcePrograms=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,relatedBug='BUG-2129',relatedYkt='YKT-1876'))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,guardMetadataChecks=len(checks),knownHelperPostHits=len(scan),explicitFalseCorrections=1,unregisteredSourceSuiteCount=len(unregistered),registeredCurrentSuiteCount=len(scanned_suites))))
if __name__=='__main__':main()
