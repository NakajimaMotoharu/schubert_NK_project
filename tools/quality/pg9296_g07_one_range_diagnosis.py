"""One public reported range only. No scanner, target access, candidate output or acceptance."""
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
W=ROOT.parent/'pgpt-runs/PG379'
OUT=BASE/'PG9296-g07-one-range-diagnosis-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
CONTENT='05d73a7974da8df92228160b96d91e7a006768f3'
BINARY=ROOT.parent/'toolchain/gitleaks-8.30.1-linux-x64/gitleaks'
BINARY_SHA='88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509'
PUBLIC_SOURCE='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ServiceDeadlineArgumentTest.java'
PUBLIC_COMMIT='f817b004781e6c32aa2d384dd12855cad7175ddc'
PUBLIC_OBJECT='4f83b36b1d2a35af220312d02ba5157efc1bc15f'
PUBLIC_SHA='7d86c386f2583fd4ae26d5e5d3fe0f3d7e402087837da57a785b7cb4b7654124'
ENV={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    pins={
      'scan':('PG8968-public-blob-scan-v1/manifest.json','f8e16b697c1c509791c6674bb17661c54e8685c0f04425bed8bf7ea86a94a739'),
      'classified':('PG8980-public-finding-provenance-v1/manifest.json','fe4175077735018f5b500306e09c7300917a814c53196a2378e1b1e887b6f5ae'),
      'tokens':('PG9000-public-token-provenance-v1/manifest.json','c3216ab47b1ebe8a9da9c6587b1784b99b89a46390e1f0c61c80154dcc9f1847'),
      'tokenPost':('PG9002-public-token-provenance-post-v1/manifest.json','3af5c448f053d77bac336122f4f7372e7bffa41aacea24052456f07c06f7a177')}
    proof={}
    for key,(path,digest) in pins.items():
        assert sha((BASE/path).read_bytes())==digest; proof[key]=json.loads((BASE/path).read_bytes())
    scan=proof['scan']; classified=proof['classified']
    assert scan['contentCommit']==CONTENT and scan['findings']==40086 and scan['rawOutputPersisted'] is False
    assert proof['tokens']['remainingUnclassified']==8379 and proof['tokens']['cumulativeFalsePositiveProof']==31707
    class_file=BASE/'PG8980-public-finding-provenance-v1/classifications.json'
    assert sha(class_file.read_bytes())==classified['classificationSha256']
    rows=[row for row in json.loads(class_file.read_bytes()) if row['reason']=='EXACT_CAPTURE_NOT_BOUND_TO_FINDING_RANGE']
    assert len(rows)==1; row=rows[0]
    assert row['disposition']=='UNCLASSIFIED' and row['ruleId']=='linear-client-secret' and row['startLine']==row['endLine']==1680
    assert row['path']=='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8634-api-web-custom-payload-host-v1/manifest.json'
    finding_path=BASE/'PG8968-public-blob-scan-v1/findings.json'
    assert sha(finding_path.read_bytes())==scan['findingsSha256']
    key=lambda item:tuple(item[field] for field in ('path','ruleId','startLine','endLine','inputSha256'))
    original=Counter(key(item) for item in json.loads(finding_path.read_bytes()))
    assert original[key(row)]==1
    inventory_path=BASE/'PG8968-public-blob-scan-v1/inventory.json'
    assert sha(inventory_path.read_bytes())==scan['inventorySha256']
    entry=next(item for item in json.loads(inventory_path.read_bytes())['rows'] if item['path']==row['path'])
    assert entry['sha256']==row['inputSha256']
    data=(W/'pg8968-public-blob-scan-v1/tracked'/row['path']).read_bytes()
    assert sha(data)==row['inputSha256']=='5f09c33d46e0a3a9de6ab0259a0fd4c110e2aff7c95570f9cc6ed4cfebbeafac'
    assert subprocess.check_output(['git','cat-file','blob',entry['gitObject']],cwd=ROOT,env=ENV)==data
    text=data.decode('utf-8'); meta=json.loads(data); line=data.splitlines(keepends=True)[1679]
    assert not any(chr(code) in text for code in (11,12,13,28,29,30,133,8232,8233))
    assert meta['source']==PUBLIC_COMMIT
    assert meta['begin']['sourceHashes'][PUBLIC_SOURCE]==PUBLIC_SHA
    assert subprocess.run(['git','merge-base','--is-ancestor',PUBLIC_COMMIT,CONTENT],cwd=ROOT,env=ENV,check=False).returncode==0
    oid=subprocess.check_output(['git','rev-parse',PUBLIC_COMMIT+':'+PUBLIC_SOURCE],cwd=ROOT,env=ENV).decode().strip()
    assert oid==PUBLIC_OBJECT
    blob=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT,env=ENV); assert sha(blob)==PUBLIC_SHA
    expected=b'      '+json.dumps(PUBLIC_SOURCE).encode()+b': '+json.dumps(sha(blob)).encode()+b',\n'
    assert line==expected
    config_meta=json.loads((BASE/'PG8979-gitleaks-rule-provenance-v1/manifest.json').read_bytes())
    tag_bytes=Path(config_meta['path']).read_bytes()
    assert sha(tag_bytes)==config_meta['configSha256']=='e163e53b9e7e8a8511e77271e2b323ed057759542a6d988258afe3a1fa329caf'
    assert tomllib.loads((W/'pg8968-public-blob-scan-v1/default.toml').read_text())=={'extend':{'useDefault':True}}
    binary=BINARY.read_bytes(); assert sha(binary)==BINARY_SHA
    parity={}
    for name in ('linear-client-secret','generic-api-key'):
        needle=('id = '+json.dumps(name)).encode(); assert binary.count(needle)==1
        position=binary.index(needle); low=binary.rfind(b'[[rules]]',0,position); high=binary.find(b'[[rules]]',position)
        rules=tomllib.loads(binary[low:high].decode('utf-8'))['rules']
        assert len(rules)==1 and rules[0]['id']==name
        parity[name]=all(rules[0].get(field)==config_meta['rules'][name].get(field) for field in ('id','regex','entropy','keywords'))
        assert parity[name]
    regex=re.compile(config_meta['rules']['linear-client-secret']['regex'],re.ASCII)
    assert not list(regex.finditer(text))
    # Fictitious RAM-only vectors. Never persist candidate values or candidate hashes.
    literal='0123456789abcdef'*2
    framed='linear = '+chr(34)+literal+chr(34)
    doubled='linear = '+chr(34)+literal+literal+chr(34)
    assert regex.search(framed).group(1)==literal
    assert regex.search(doubled) is None
    assert regex.search(doubled[:len('linear = ')+1+32]).group(1)==literal
    assert regex.search('opaque = '+chr(34)+literal+chr(34)) is None
    verify(invocation); OUT.mkdir()
    result=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,
      historicalContentCommit=CONTENT,historicalScanSource=scan['source'],reportedTuple={field:row[field] for field in ('path','ruleId','startLine','endLine','inputSha256')},
      originalFindingMultiplicity=1,reportedRangeIsOneWholeJsonMember=True,wholeLineEqualsIndependentPublicSourceMetadata=True,
      publicSourceProof=dict(path=PUBLIC_SOURCE,commit=PUBLIC_COMMIT,gitObject=PUBLIC_OBJECT,sha256=sha(blob)),
      wholeTextRuleMatchCount=0,lineSeparatorMismatch=False,selectedEmbeddedRulesEqualPinnedTag=parity,
      publicBinarySha256=BINARY_SHA,tagConfigSha256=sha(tag_bytes),syntheticRegexVectors=4,
      actualScannerFragmentBoundaryReconstructed=False,actualCaptureReconstructed=False,
      unresolvedHypotheses=['FRAGMENT_DEPENDENT_BOUNDARY_CONTEXT','REPORTED_POSITION_OR_REGEX_ENGINE_CONTEXT'],
      publicSourceWorkflowWitness=dict(url='https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/sources/file.go',
        observedDefaultBufferBytes=100000,observedSafeBoundaryExtension=True,rawFileSha256=None,
        source='WEB_READ_ONLY_NOT_RAW_BYTES_HASHED_NOT_ACTUAL_FRAGMENT_ATTESTATION'),
      publicDirectoryLookupUnavailable=dict(url='https://github.com/gitleaks/gitleaks/tree/v8.30.1/sources',
        outcome='WEB_FETCH_RESTRICTED_URL',retried=False,alternativeChannelUsed=False),
      additionalPublicMetadataRangeProof=1,additionalFalsePositives=0,historicalPublicProof31707Unchanged=True,
      remainingUnclassified=8379,oneNoExactCaptureStillUnclassified=True,actualSecretCount=None,
      candidateValuesPersisted=False,candidateHashesPersisted=False,contextPersisted=False,scannerExecuted=False,
      wholeScanReplayed=False,privateRawRead=False,productTestsExecuted=0,productCoverage=None,newMain=0,
      whole451SecretGateAccepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(result,stream,ensure_ascii=False,sort_keys=True,indent=2); stream.write('\n')
    print(json.dumps(dict(actualExit=0,publicMetadataRangeProof=1,additionalFalsePositives=0,remainingUnclassified=8379,
      actualCaptureReconstructed=False,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
