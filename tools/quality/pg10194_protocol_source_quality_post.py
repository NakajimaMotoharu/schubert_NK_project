"""Current module evidence and unchanged-byte static join; strict generated coverage stays unqualified."""
from collections import Counter
import json
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from class_counter_applicability import classify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10194-protocol-source-quality-post-v1'
    assert not out.exists()
    def read(name,digest):
        return data.read_checked(data.BASE/name/'manifest.json',digest)
    normal = read('PG10169-cancel-six-compile-v2','1d11a7d6ef608ca39d5808e7f6d8cfaed4c77ee5be4e593f70d1c48aafd9d06c')
    post = read('PG10190-protocol-module-post-v1','106f53ac1f742c1fa58049ccbcc02fe8e15ff35de605a9e529ab6d775d33f326')
    generated = read('PG10192-protocol-generated-shape-post-v1','1cf1a02ad4ad066c11e30f4a82ec0f59326560a471b822ad622abb96d3b6628d')
    assert normal['source'] == post['source'] == generated['source'] == '5e8255bcf8f309d05fb091cee2e9ad810b276c87'
    assert normal['actualExit'] == post['actualExit'] == generated['actualExit'] == normal['testsExecuted'] == 0
    assert post['actualTests'] == 102 and post['suites'] == 22 and post['wholeModuleFour100']
    detail = data.read_checked(data.BASE/'PG10190-protocol-module-post-v1/whole-module-counters.json',post['moduleCounterDetailsSha256'])
    classifications = {n:classify(row['counters']) for n,row in detail['physicalClasses'].items()}
    assert classifications == post['counterApplicability']
    counts = Counter(classifications.values())
    assert counts == {'FOUR100_MEASURED_APPLICABLE':159,'NO_COUNTERS_NOT_A_MEASURED_PASS':10}
    assert post['four100ExecutableClassCount'] == counts['FOUR100_MEASURED_APPLICABLE']
    assert len(generated['classes']) == 4 and not generated['strictGeneratedInstructionCoverageQualified']
    raw_hit = sum(r['rawHitProbes'] for r in generated['classes'].values())
    raw_miss = sum(r['rawMissedProbes'] for r in generated['classes'].values())
    assert all(r['notCountedAsIndividuallyFour100'] for r in generated['classes'].values())
    old_base = data.ROOT/'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
    corrected = data.read_checked(old_base/'PG9728-protocol-counter-count-correction-v1/manifest.json',
        'd8acceac54b0b8e6edafd0ba15c4039adf9f5a15408e5f5ca8f13fc77129e6f2')
    classifier = 'tools/quality/class_counter_applicability.py'
    assert data.sha((data.ROOT/classifier).read_bytes()) == corrected['invocation']['loadedProjectPythonSources'][classifier]
    static = data.read_checked(old_base/'PG9666-pagination-static-v2/manifest.json',
        '41807eb5d29a989424939246359f8eb7f9162bd03c7fbc4d1f2bd8932546de08')
    prior = static['results']['protocol']
    assert prior['findings'] == prior['processingErrors'] == prior['receipt']['actualExit'] == 0
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    with zipfile.ZipFile(jar) as archive:
        current = {n:data.sha(archive.read(n)) for n in archive.namelist() if n.endswith('.class')}
    assert current == prior['physicalClasses'] and len(current) == 176
    assert prior['pomSha256'] == normal['begin']['inputHashes']['src/schubert-nk-protocol/pom.xml']
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in prior['dependencyHashes'].items())
    report = old_base/'PG9666-pagination-static-v2/current-v2-spotbugs-protocol.xml'
    assert data.sha(report.read_bytes()) == prior['reportSha256']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    verify(invocation)
    out.mkdir()
    data.write(out/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        actualTests=post['actualTests'],suites=post['suites'],physicalMainClasses=len(current),
        currentRawJacocoFour100=True,measuredFour100Classes=counts['FOUR100_MEASURED_APPLICABLE'],
        noCounterClassesNotPass=counts['NO_COUNTERS_NOT_A_MEASURED_PASS'],packageAnnotations=7,noCodeInterfaces=6,
        generatedCodeClasses=4,currentGeneratedRawHitProbes=raw_hit,currentGeneratedRawMissedProbes=raw_miss,
        strictGeneratedInstructionCoverageQualified=False,coverageExemptionApproved=False,
        standardCounters=post['wholeModuleCounters'],legacyClassCountCorrectionReusedNotReexecuted=True,
        originalClassifierMetadataVectorsReference=str((old_base/'PG9728-protocol-counter-count-correction-v1/manifest.json').relative_to(data.ROOT)),
        originalClassifierMetadataVectorsSha256='d8acceac54b0b8e6edafd0ba15c4039adf9f5a15408e5f5ca8f13fc77129e6f2',
        inheritedProtocolSpotbugsFindings=0,inheritedProtocolSpotbugsExactPhysicalClasses=176,
        inheritedSpotbugsReportSha256=prior['reportSha256'],staticAnalysisReexecuted=False,
        allModuleSourcePmdQualified=False,wholeF03Accepted=False,
        newTestIds=0,productTestsExecutedByPost=0,historicalDynamicSuccessTransferred=False,coverageUnion=False,
        newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=post['actualTests'],suites=post['suites'],
        standardMeasuredFour100Classes=counts['FOUR100_MEASURED_APPLICABLE'],rawGeneratedMiss=raw_miss,
        strictGeneratedQualified=False,manifestSha256=data.sha((out/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
