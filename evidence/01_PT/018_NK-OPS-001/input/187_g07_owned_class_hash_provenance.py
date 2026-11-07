"""Original minified-line capture closure from owned Main Jar metadata only, no scan or execution."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import zipfile
R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001/evidence'
OUT=B/'PG22320-g07-owned-class-byte-provenance-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
    assert not OUT.exists()
    original=B/'provisional/PG3954-current-boundary-qualified-v1/manifest.json';assert sha(original)=='60b36e321b16806b428b1948ca78374b27089f807f5b22abc2df7d22c70bf766'
    origin=B/'provisional/PG9888-g07-capture-shape-v1';assert sha(origin/'manifest.json')=='6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb';assert sha(origin/'residual-metadata-shapes.json')==load(origin/'manifest.json')['residualMetadataSha256']
    residual=load(origin/'residual-metadata-shapes.json');path=str(original.relative_to(R));rows=[x for x in residual if x['path']==path];assert len(rows)==73 and all(x['ruleId']=='generic-api-key' and x['startLine']==x['endLine']==1 and x['inputSha256']==sha(original) for x in rows)
    rule=B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';regex=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII)
    text=original.read_text();doc=json.loads(text);matches=list(regex.finditer(text));assert len(matches)==84 and len({m.group(1) for m in matches})==84 and all(re.fullmatch('[0-9a-f]{64}',m.group(1)) for m in matches)
    field=re.search(r'"allPhysicalMainSha256"\s*:\s*',text);assert field;mapping,end=json.JSONDecoder().raw_decode(text[field.end():]);assert mapping==doc['allPhysicalMainSha256'] and sum(len(v) for v in mapping.values())==1643
    normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['actualExit']==0 and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
    jars={};archives={};tokens=[]
    try:
        for module,entries in mapping.items():
            jp=nm['jars'][module];assert sha(jp['path'])==jp['sha256'];archives[module]=zipfile.ZipFile(jp['path']);jars[module]=dict(path=jp['path'],sha256=jp['sha256'])
            raw_object=text[field.end():field.end()+end];module_tokens=list(re.finditer(re.escape(json.dumps(module))+r'\s*:\s*',raw_object));assert len(module_tokens)==1
            start=field.end()+module_tokens[0].end();data,length=json.JSONDecoder().raw_decode(text[start:]);assert data==entries
            for entry,digest in entries.items():
                pattern=re.escape(json.dumps(entry))+r'\s*:\s*('+re.escape(json.dumps(digest))+r')';found=list(re.finditer(pattern,text[start:start+length]));assert len(found)==1
                token=found[0];tokens.append(dict(start=start+token.start(1)+1,end=start+token.end(1)-1,module=module,entry=entry,declared=digest))
        proofs=[]
        for match in matches:
            candidates=[x for x in tokens if x['start']<=match.start(1) and match.end(1)<=x['end']]
            if len(candidates)!=1:
                proofs.append(dict(captureCharacterSpan=[match.start(1),match.end(1)],status='UNRESOLVED_NON_CLASS_OR_AMBIGUOUS_TOKEN'));continue
            token=candidates[0];assert match.start(1)==token['start'] and match.end(1)==token['end'] and match.group(1)==token['declared']
            entry=token['entry'];module=token['module'];assert entry.startswith('dev/codex/schubert/nk/') and entry.endswith('.class') and '..' not in Path(entry).parts
            if any(x in entry for x in ['SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness','RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest']):
                status='HELD_MEMBER_EXCLUDED_BEFORE_READ'
            elif entry not in archives[module].namelist():status='NO_CURRENT_OWNED_CLASS_ENTRY'
            elif hashlib.sha256(archives[module].read(entry)).hexdigest()!=token['declared']:status='CURRENT_OWNED_CLASS_BYTE_DIFFERS'
            else:status='PROVEN_OWNED_MAIN_CLASS_DIGEST'
            proofs.append(dict(captureCharacterSpan=[match.start(1),match.end(1)],status=status,module=module,classEntry=entry,normalJarSha256=jars[module]['sha256'],jsonRole='ALL_PHYSICAL_MAIN_SHA256_STRING_VALUE'))
    finally:
        for archive in archives.values():archive.close()
    assert len(proofs)==84
    complete=all(x['status']=='PROVEN_OWNED_MAIN_CLASS_DIGEST' for x in proofs);updates=[]
    if complete:
        for row in rows:updates.append(dict(**{k:row[k] for k in ['path','ruleId','startLine','endLine','inputSha256']},disposition='FALSE_POSITIVE_PROVEN_PUBLIC_CLASS_DIGEST',fullExactCaptureClosure=True,allExactLineCaptures=84,proofKind='TYPED_CLASS_HASH_FIELD_MATCHES_OWNED_MAIN_CLASS_BYTES'))
    OUT.mkdir();(OUT/'capture-provenance.json').write_text(json.dumps(proofs,indent=2)+'\n');(OUT/'updates.json').write_text(json.dumps(updates,indent=2)+'\n')
    counts={k:sum(x['status']==k for x in proofs) for k in sorted({x['status'] for x in proofs})};manifest=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalManifest=dict(path=path,sha256=sha(original)),originalResidualSha256=sha(origin/'residual-metadata-shapes.json'),ruleManifestSha256=sha(rule),normalManifest=dict(path=str(normal),sha256=sha(normal),source=nm['source']),normalJars=jars,historicalScanSource=load(origin/'manifest.json')['historicalScanSource'],contentCommit=load(origin/'manifest.json')['contentCommit'],originalAmbiguousFindingRows=73,exactLineCaptures=84,captureStatusCounts=counts,fullExactCaptureClosure=complete,additionalFalsePositives=len(updates),previousUnclassified=4484,remainingUnclassified=4484-len(updates),actualSecretCount=None,binaryClosed=0,binaryTotal=22,productTestsExecuted=0,scannerExecuted=False,targetsExecuted=False,privateRawRead=False,remoteAccess=False,classExtracted=False,valuesOrValueHashesWritten=False,newAccepted=0,currentWholeG07Qualified=False,newSourceProofs=0,files={n:sha(OUT/n) for n in ['capture-provenance.json','updates.json']},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,statusCounts=counts,newFalsePositives=len(updates),remaining=manifest['remainingUnclassified'],manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
