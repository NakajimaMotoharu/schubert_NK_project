"""Independent capture/multiset and existing owned class-byte checks, no classification guessing."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json
import re
import zipfile
R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001/evidence'
SRC=B/'PG22320-g07-owned-class-byte-provenance-v1'
OUT=B/'PG22322-g07-owned-class-byte-independent-post-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
key=lambda x:tuple(x[k] for k in ['path','ruleId','startLine','endLine','inputSha256'])
def main():
    assert not OUT.exists();assert sha(SRC/'manifest.json')=='49d485be71643da747e3300c2ff6ee676f460a796ccb7787ef93f2923025fd6c';m=load(SRC/'manifest.json');assert m['actualExit']==0 and m['productTestsExecuted']==m['newAccepted']==m['additionalFalsePositives']==m['newSourceProofs']==0
    for n,h in m['files'].items():assert sha(SRC/n)==h
    assert sha(R/m['producer']['path'])==m['producer']['sha256'] and not load(SRC/'updates.json')
    p=R/m['originalManifest']['path'];assert sha(p)==m['originalManifest']['sha256'];text=p.read_text();doc=json.loads(text)
    origin=B/'provisional/PG9888-g07-capture-shape-v1';assert sha(origin/'residual-metadata-shapes.json')==m['originalResidualSha256'];original=Counter(key(x) for x in load(origin/'residual-metadata-shapes.json'));which=(str(p.relative_to(R)),'generic-api-key',1,1,sha(p));assert original[which]==73
    prior=[]
    for slot in ['PG22160-g07-three-public-test-symbols-v1','PG22170-g07-four-selector-symbols-v1','PG22184-g07-two-public-class-references-v2']:
        pm=load(B/slot/'manifest.json');assert sha(B/slot/'updates.json')==pm['updatesSha256'];prior.extend(load(B/slot/'updates.json'))
    previous=Counter(key(x) for x in prior);assert sum(previous.values())==9 and which not in previous and all(n<=original[k] for k,n in previous.items()) and sum((original-previous).values())==4484
    rule=B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)==m['ruleManifestSha256'];rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);captures=list(rx.finditer(text));proofs=load(SRC/'capture-provenance.json');assert len(captures)==len(proofs)==84
    assert len({(x.start(1),x.end(1)) for x in captures})==84 and [list(x.span(1)) for x in captures]==[x['captureCharacterSpan'] for x in proofs]
    start=text.index('"allPhysicalMainSha256"');begin=text.index(':',start)+1
    while text[begin].isspace():begin+=1
    mapping,used=json.JSONDecoder().raw_decode(text[begin:]);assert mapping==doc['allPhysicalMainSha256']
    normal=Path(m['normalManifest']['path']);assert sha(normal)==m['normalManifest']['sha256'];nm=load(normal);archives={};counts=Counter();outside=0
    try:
        for module,j in m['normalJars'].items():assert j==nm['jars'][module] or (j['path']==nm['jars'][module]['path'] and j['sha256']==nm['jars'][module]['sha256']);assert sha(j['path'])==j['sha256'];archives[module]=zipfile.ZipFile(j['path'])
        for capture,proof in zip(captures,proofs):
            s,e=capture.span(1)
            if proof['status']=='UNRESOLVED_NON_CLASS_OR_AMBIGUOUS_TOKEN':
                assert not begin<=s<e<=begin+used
                outside+=1;counts[proof['status']]+=1;continue
            module=proof['module'];entry=proof['classEntry'];assert proof['jsonRole']=='ALL_PHYSICAL_MAIN_SHA256_STRING_VALUE' and proof['normalJarSha256']==nm['jars'][module]['sha256']
            assert all(x not in entry for x in ['SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness','RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest'])
            assert mapping[module][entry]==capture.group(1) and begin<=s<e<=begin+used and text[s-1]=='"' and text[e]=='"'
            # The immediate JSON key and complete quoted value identify the source token independently.
            local=text[begin:s-1];assert re.search(re.escape(json.dumps(entry))+r'\s*:\s*$',local)
            assert entry in archives[module].namelist();equal=hashlib.sha256(archives[module].read(entry)).hexdigest()==capture.group(1)
            expected='PROVEN_OWNED_MAIN_CLASS_DIGEST' if equal else 'CURRENT_OWNED_CLASS_BYTE_DIFFERS';assert proof['status']==expected;counts[expected]+=1
    finally:
        for jar in archives.values():jar.close()
    assert dict(counts)==m['captureStatusCounts']=={'CURRENT_OWNED_CLASS_BYTE_DIFFERS':19,'PROVEN_OWNED_MAIN_CLASS_DIGEST':28,'UNRESOLVED_NON_CLASS_OR_AMBIGUOUS_TOKEN':37} and outside==37
    assert not m['fullExactCaptureClosure'] and m['previousUnclassified']==m['remainingUnclassified']==4484 and m['actualSecretCount'] is None and m['binaryClosed']==0 and m['binaryTotal']==22
    OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str((SRC/'manifest.json').relative_to(R)),sha256=sha(SRC/'manifest.json')),originalFindingMultiplicity=73,exactCaptures=84,provedClassDigests=28,currentClassByteDifferences=19,otherFieldOrUnresolvedCaptures=37,independentClassTokenAndByteChecks=True,previousUpdatesRetained=9,newFalsePositives=0,remainingUnclassified=4484,productTestsExecuted=0,scannerExecuted=False,remoteAccess=False,privateRawRead=False,classExtracted=False,valuesOrValueHashesWritten=False,newAccepted=0,currentWholeG07Qualified=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,provedCaptures=28,unknownCaptures=56,newFalsePositives=0,remaining=4484,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
