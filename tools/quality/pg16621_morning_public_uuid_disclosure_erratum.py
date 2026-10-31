"""Finite public-ID effect erratum; preserve every original execution and counter byte."""
import copy
import json
import uuid
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
POST=('PG16620-morning-pure-data-original-33-post-v1','a878d423f42737c284f3f7aa6cea59619e0da023340a532f5d3f24e93f3e2424')
QUAL=('PG16622-morning-pure-data-original-33-independent-v1','899f8f79bb5adee3815c59d5549bcff6d6aa968c11a16717b4383c93caaf0874')
FIXTURES=json.loads("{\"src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-failed-v2-golden.txt\":\"eda4285f0df2c54a4ca10946013dbfc145440da6999637ca035f56ec86a66d4a\",\"src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-new-v2-golden.txt\":\"842b41b0e1f131f65fef2127bee72ae840e94dfa67c4c3240799608d8a553b1c\",\"src/schubert-nk-batch/src/test/resources/ops/issuer-prestart-reused-v2-golden.txt\":\"f5877b39aece1cbbd31e9016fdb34ea65fb4ddc933e93428ab4d6b2f0ad6849e\"}")
OUT=data.BASE/'PG16621-morning-public-uuid-disclosure-erratum-v1'
EFFECT=dict(effectivePublicSyntheticUuidFixture=True,effectiveSyntheticIdentifiersFromFixedPublicFixtures=True,effectiveLiveIdentifierUsedAsTestInput=False,actualAuthenticationOrSessionIssued=False,actualSecretKeysLoaded=False,interpretation='FIXED_PUBLIC_PROOF_IDS_NOT_LIVE_BOOT_SESSION_PERMIT_OR_AUTHORITY')
def require(ok,why):
    if not ok:raise ValueError(why)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,q=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in [POST,QUAL]]
    require(p['actualExit']==q['actualExit']==0 and p['source']==q['source']==SOURCE and q['postSha256']==POST[1] and q['semanticNegativeVectors']==41,'unchanged actual qualification')
    require(p['publicSyntheticUuidFixture'] is False and p['publicDigestOnly'] is p['cryptoOrKeyOperationsInvoked'] is True and p['actualSecretKeysLoaded'] is p['actualAuthenticationOrSessionIssued'] is False,'only erroneous auxiliary UUID flag')
    keys={'boot_id','epoch_id','run_id','activation_id','morning_invocation_id','broker_invocation_id'};observed={}
    for path,pin in FIXTURES.items():
        blob=(data.ROOT/path).read_bytes();require(data.sha(blob)==pin,'fixed public golden')
        found=set()
        for line in blob.decode('ascii').splitlines():
            key,sep,value=line.partition('=')
            if key in keys:
                require(sep and key not in found,'one typed identity field');uuid.UUID(value);found.add(key)
        require(found==keys,'six fixed UUID proof fields');observed[path]=sorted(found)
    source=data.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningPrestartEvidenceTest.java'
    require(data.sha(source.read_bytes())=='b58a35ec59e2f413756b7acb5bcf779939348df891d8cb12937b9af0fbc18440' and 'getResourceAsStream("/ops/issuer-prestart-" + mode + "-v2-golden.txt")' in source.read_text(),'unchanged selected golden oracle')
    require(sum(v['classname'].endswith('.MorningPrestartEvidenceTest') and v['result']=='PASS' for v in p['cases'])==5,'actual selected whole golden tests passed')
    def contract(value):require(json.dumps(value,sort_keys=True)==json.dumps(EFFECT,sort_keys=True),'closed truthful effect interpretation')
    contract(EFFECT);labels=[]
    for key,value in EFFECT.items():
        bad=copy.deepcopy(EFFECT);bad[key]=not value if type(value) is bool else 'BAD'
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false disclosure accepted')
    for value in [{},dict(EFFECT,actualRootAccepted=True)]:
        try:contract(value)
        except ValueError:labels.append('shape')
        else:raise ValueError('incomplete or extra disclosure')
    for row in [p,q]:verify(row['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bug='BUG2184',horizontal='YKT1931',originalPost=list(POST),originalIndependent=list(QUAL),originalPublicSyntheticUuidFixture=False,previousIndependentEffectFlagWasNotChecked=True,effectiveDisclosure=EFFECT,independentGoldenFileHashes=FIXTURES,observedSyntheticUuidFieldNames=observed,metadataNegativeVectors=len(labels),negativeLabels=labels,rawIdentifierValuesRecorded=False,originalQualificationAndCountersUnchanged=True,priorManifestRetained=True,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print('metadataNegativeVectors',len(labels))
if __name__=='__main__':main()
