"""Independent old-token preservation and two public diagnostic/null oracles; no target execution."""
import copy
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

OUT=data.BASE/'PG12526-public-record-oracle-source-post-v1'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest.java'
NEW=('obsdata003ConfigurationAndJournalDiagnosticsHideIndependentPublicCanaries','obsdata004NonNullConfigurationValuesRejectEachMissingFieldBeforeOwnership')


def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def golden_contract(value):
    expected={'configurationDiagnostic':'EffectiveConfigurations[non-secret=<redacted>]','journalDiagnostic':'BrokerJournalSummary[redacted]','missingConfigurationFields':['apiSha256','webSha256','roots','apiYaml','webYaml'],'missingContentsFields':['commonYaml','serviceYaml']}
    if value!=expected:raise ValueError('independent prior diagnostic and seven field golden required')


def inverse(before,after):
    tokens=raw(after)
    for declaration in ['import static org.junit.jupiter.api.Assertions.assertFalse;','import java.util.List;']:
        seq=raw(declaration);matches=[i for i in range(len(tokens)-len(seq)+1) if tokens[i:i+len(seq)]==seq]
        if len(matches)!=1:raise ValueError('exact two new input/assertion imports required')
        i=matches[0];del tokens[i:i+len(seq)]
    bodies={}
    for name,prefix in [(NEW[0],['@','Test','void']),(NEW[1],['@','Test','void']),('diagnosticRoots',['private','static','StorageRootLayout'])]:
        matches=[(a,b) for a,b,n in functions(list(zip(tokens,range(len(tokens))))) if n==name]
        if len(matches)!=1:raise ValueError('one complete approved new method required')
        a,b=matches[0]
        if tokens[a-3:a]!=prefix:raise ValueError('fixed complete declaration and active Test required')
        body=tokens[a:b+1];bodies[name]=body
        if name==NEW[0]:
            snippets=['List.of("PUBLIC-RECORD-CANARY-ALPHA","PUBLIC-RECORD-CANARY-BETA")','assertEquals("EffectiveConfigurations[non-secret=<redacted>]",configurationText);','assertEquals("BrokerJournalSummary[redacted]",journalText);','configurations.toString()','new BrokerJournalEvidence.Summary(5,journalDigest).toString()','List.of(marker,apiDigest,webDigest,journalDigest,commonYaml,serviceYaml)','assertFalse(configurationText.contains(forbidden));','assertFalse(journalText.contains(forbidden));','String absolutePath="/public-diagnostic/"+marker+"/"+leaf;','assertFalse(configurationText.contains(absolutePath));','assertFalse(journalText.contains(absolutePath));']
        elif name==NEW[1]:
            snippets=['for(int missing=0;missing<5;missing++)','assertThrows(NullPointerException.class,()->new RootReleaseAdmission.EffectiveConfigurations(','field==0?null:apiDigest','field==1?null:webDigest','field==2?null:roots','field==3?null:contents','field==4?null:contents','assertThrows(NullPointerException.class,()->new ServiceConfigFiles.Contents(null,serviceYaml));','assertThrows(NullPointerException.class,()->new ServiceConfigFiles.Contents(commonYaml,null));']
        else:
            snippets=['String prefix="/public-diagnostic/"+marker+"/";','new StorageRootLayout(']+['Path.of(prefix+"'+leaf+'")' for leaf in ('asset','transfer','backup','log','artemis','staging')]
        for snippet in snippets:
            seq=raw(snippet)
            if not any(body[i:i+len(seq)]==seq for i in range(len(body)-len(seq)+1)):raise ValueError('complete independent golden/assertions/null fields and lexical input table required')
        if any(x in body for x in ('Files','ProcessBuilder','ClassLoader','getRuntime','production','inspect','capture','System')):raise ValueError('only public value and lexical input construction, never external ownership')
        del tokens[a-3:b+1]
    if tokens!=raw(before):raise ValueError('all original two methods/helpers/constants and oracle tokens preserved')
    return bodies


def main():
    invocation=capture(__file__);assert not OUT.exists()
    p=data.BASE/'PG12524-public-record-oracle-plan-v1';plan=data.read_checked(p/'manifest.json','c6d8ebd9aaf16f7f0edd1c9db95359e9d96d4c49eb6d56520f4899d1bd17de28')
    golden=data.read_checked(p/'golden.json',plan['independentGoldenSha256']);golden_contract(golden)
    normal=data.read_checked(data.BASE/'PG12500-pure-resource-profile-six-compile-v1/manifest.json','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c')
    snapshot=Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    before=(snapshot/TEST).read_text();after=(data.ROOT/TEST).read_text()
    assert plan['sourceChanges']==[dict(path=TEST,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()))]
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=TEST)
    bodies=inverse(before,after)
    old=re.findall(r'@Test\s+void (\w+)\(',before);new=re.findall(r'@Test\s+void (\w+)\(',after)
    assert len(old)==2 and len(new)==4 and set(new)==set(old)|set(NEW)
    mutants=[after.replace('assertEquals(','assertNotEquals(',1),after.replace('@Test','@Disabled',1),after.replace('"EffectiveConfigurations[non-secret=<redacted>]"','"wrong-diagnostic"',1),after.replace('"BrokerJournalSummary[redacted]"','"wrong-summary"',1),after.replace('"PUBLIC-RECORD-CANARY-ALPHA"','"wrong-canary"',1),after.replace('assertFalse(configurationText.contains(forbidden))','assertTrue(configurationText.contains(forbidden))',1),after.replace('String absolutePath = "/public-diagnostic/"','String absolutePath = "relative/"',1),after.replace('field == 4 ? null : contents','field == 3 ? null : contents',1),after.replace('new ServiceConfigFiles.Contents(null, serviceYaml)','new ServiceConfigFiles.Contents(commonYaml, serviceYaml)',1),after.replace('assertThrows(\n          NullPointerException.class,','assertThrows(\n          IllegalArgumentException.class,',1),after.replace('Path.of(prefix + "asset")','Path.of(prefix + "transfer")',1),after.replace('@Test\n  void '+NEW[0],'@Disabled\n  void '+NEW[0],1),after[:-2]+'  void unreviewedMethod() {}\n}\n']
    source_negatives=0
    for bad in mutants:
        assert bad!=after
        try:inverse(before,bad)
        except ValueError:source_negatives+=1
        else:raise AssertionError('changed old oracle/new diagnostic/null/permission method accepted')
    golden_negatives=0
    for field,wrong in [('configurationDiagnostic','wrong'),('missingConfigurationFields',['apiSha256']),('missingContentsFields',['commonYaml'])]:
        bad=copy.deepcopy(golden);assert bad[field]!=wrong;bad[field]=wrong
        try:golden_contract(bad)
        except ValueError:golden_negatives+=1
        else:raise AssertionError('changed independent golden accepted')
    assert source_negatives==13 and golden_negatives==3
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256='c6d8ebd9aaf16f7f0edd1c9db95359e9d96d4c49eb6d56520f4899d1bd17de28',independentGoldenSha256=plan['independentGoldenSha256'],sourceChanges=plan['sourceChanges'],originalMethods=old,expectedMethods=new,newTestIds=['PT-OPS-OBSDATA-003','PT-OPS-OBSDATA-004'],approvedNewMethodTokenSha256={n:data.sha('\0'.join(ts).encode()) for n,ts in bodies.items()},allOtherOriginalTokensRestored=True,allMainAndOtherInputsPreserved=True,sourceMetadataNegativeVectors=source_negatives,goldenNegativeVectors=golden_negatives,metadataNegativeVectors=source_negatives+golden_negatives,newMissingFieldVectors=7,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':main()
