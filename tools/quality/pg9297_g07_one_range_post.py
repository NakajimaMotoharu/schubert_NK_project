"""Independent Git blob/manual JSON-line oracle; a public line is not capture acceptance."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
RAW=BASE/'PG9296-g07-one-range-diagnosis-v1/manifest.json'
RAW_SHA='e1de541969ec807893a234c5a4e3fd23f74c4bf162728ab1c5582b68682615cf'
OUT=BASE/'PG9297-g07-one-range-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
EXPECTED_FIELDS=set((
  'actualCaptureReconstructed actualExit actualScannerFragmentBoundaryReconstructed actualSecretCount '
  'additionalFalsePositives additionalPublicMetadataRangeProof candidateHashesPersisted candidateValuesPersisted '
  'contextPersisted effortPercent formalUpdated historicalContentCommit historicalPublicProof31707Unchanged '
  'historicalScanSource invocation lineSeparatorMismatch newAccepted newMain oneNoExactCaptureStillUnclassified '
  'originalFindingMultiplicity privateRawRead productCoverage productTestsExecuted publicBinarySha256 '
  'publicDirectoryLookupUnavailable publicSourceProof publicSourceWorkflowWitness remainingUnclassified '
  'reportedRangeIsOneWholeJsonMember reportedTuple scannerExecuted selectedEmbeddedRulesEqualPinnedTag source '
  'syntheticRegexVectors tagConfigSha256 timeUTC unresolvedHypotheses whole451SecretGateAccepted '
  'wholeLineEqualsIndependentPublicSourceMetadata wholeScanReplayed wholeTextRuleMatchCount witnesses').split())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def validate(value):
    if set(value)!=EXPECTED_FIELDS or value['source']!=SOURCE or value['actualExit']!=0:
        raise ValueError('closed evidence schema and current manufacturing source')
    for field in ('actualCaptureReconstructed','actualScannerFragmentBoundaryReconstructed','candidateHashesPersisted',
                  'candidateValuesPersisted','contextPersisted','formalUpdated','lineSeparatorMismatch','privateRawRead',
                  'scannerExecuted','whole451SecretGateAccepted','wholeScanReplayed'):
        if value[field] is not False: raise ValueError('unknown capture never becomes acceptance or scanner replay')
    if value['actualSecretCount'] is not None or value['productCoverage'] is not None or value['effortPercent'] is not None:
        raise ValueError('unknown measurements remain null')
    if value['additionalFalsePositives']!=0 or value['remainingUnclassified']!=8379 or value['oneNoExactCaptureStillUnclassified'] is not True:
        raise ValueError('range proof must not decrement unclassified capture count')
    if value['newAccepted']!=0 or value['newMain']!=0 or value['productTestsExecuted']!=0:
        raise ValueError('no product test or formal delta')
    if value['originalFindingMultiplicity']!=1 or value['additionalPublicMetadataRangeProof']!=1:
        raise ValueError('one public line only')
    reported=value['reportedTuple']; source=value['publicSourceProof']
    if set(reported)!={'path','ruleId','startLine','endLine','inputSha256'} or reported['startLine']!=1680 or reported['endLine']!=1680:
        raise ValueError('exact original reported line')
    if source!=dict(path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ServiceDeadlineArgumentTest.java',
      commit='f817b004781e6c32aa2d384dd12855cad7175ddc',gitObject='4f83b36b1d2a35af220312d02ba5157efc1bc15f',
      sha256='7d86c386f2583fd4ae26d5e5d3fe0f3d7e402087837da57a785b7cb4b7654124'):
        raise ValueError('explicit independently verified public source object')
    if value['publicDirectoryLookupUnavailable']['retried'] is not False or value['publicDirectoryLookupUnavailable']['alternativeChannelUsed'] is not False:
        raise ValueError('unavailable public directory lookup was not retried')

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists() and sha(RAW.read_bytes())==RAW_SHA
    value=json.loads(RAW.read_bytes()); validate(value)
    env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'}
    proof=value['publicSourceProof']; record=value['reportedTuple']
    blob=subprocess.check_output(['git','cat-file','blob',proof['gitObject']],cwd=ROOT,env=env)
    assert sha(blob)==proof['sha256']
    target=subprocess.check_output(['git','show',value['historicalContentCommit']+':'+record['path']],cwd=ROOT,env=env)
    assert sha(target)==record['inputSha256']
    lines=target.split(b'\n')
    assert all(character not in target for character in (b'\r',b'\v',b'\f'))
    actual=lines[1679]+b'\n'
    # Independent manual encoding: fixed ASCII Java path admits no JSON escaping.
    assert re.fullmatch(r'src/[A-Za-z0-9_./-]+\.java',proof['path'])
    expected=b'      "'+proof['path'].encode('ascii')+b'": "'+sha(blob).encode('ascii')+b'",\n'
    assert actual==expected
    parsed=json.loads(target)
    assert parsed['source']==proof['commit'] and parsed['begin']['sourceHashes'][proof['path']]==sha(blob)
    assert value['wholeTextRuleMatchCount']==0
    rule=json.loads((BASE/'PG8979-gitleaks-rule-provenance-v1/manifest.json').read_bytes())['rules'][record['ruleId']]['regex']
    assert list(re.compile(rule,re.ASCII).finditer(target.decode()))==[]
    rejected=[]
    for name,mutate in (
      ('capture-invented',lambda v:v.update(actualCaptureReconstructed=True)),
      ('false-positive-incremented',lambda v:v.update(additionalFalsePositives=1,remainingUnclassified=8378)),
      ('unknown-secret-zeroed',lambda v:v.update(actualSecretCount=0)),
      ('scanner-replay-hidden',lambda v:v.update(scannerExecuted=True)),
      ('wrong-reported-line',lambda v:v['reportedTuple'].update(startLine=1679)),
      ('wrong-public-object',lambda v:v['publicSourceProof'].update(gitObject='0'*40)),
      ('candidate-output-added',lambda v:v.update(Secret='FICTITIOUS_DO_NOT_PUBLISH')),
      ('directory-lookup-retried',lambda v:v['publicDirectoryLookupUnavailable'].update(retried=True))):
        candidate=copy.deepcopy(value); mutate(candidate)
        try: validate(candidate)
        except ValueError: rejected.append(name)
        else: raise AssertionError('unproven capture accepted')
    verify(invocation); OUT.mkdir()
    result=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      diagnosticManifestSha256=RAW_SHA,independentOracle='GIT_CAT_FILE_PUBLIC_SOURCE_AND_GIT_SHOW_SNAPSHOT_MANUAL_ASCII_JSON_MEMBER',
      originalMultiplicity=1,publicMetadataRangeProof=1,rejectedMetadataCases=rejected,
      actualCaptureReconstructed=False,additionalFalsePositives=0,remainingUnclassified=8379,actualSecretCount=None,
      candidateOrContextPersisted=False,scannerExecuted=False,privateRawRead=False,productTestsExecuted=0,productCoverage=None,
      whole451SecretGateAccepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(result,stream,ensure_ascii=False,sort_keys=True,indent=2); stream.write('\n')
    print(json.dumps(dict(actualExit=0,publicMetadataRangeProof=1,additionalFalsePositives=0,remainingUnclassified=8379,
      metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
