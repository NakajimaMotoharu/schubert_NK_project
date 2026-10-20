"""Join immutable original XML/static/review proofs; never upgrades formal PGPT or coverage."""
import json
import os
from pg5940_private_lock_compile import BASE, W, sha
from pg6040_remaining33_whole import SOURCE

REFS = {
 'whole': ('PG6040-current3976-cases/qualification.json', '0d11101550922d207fec3ba3f1d2fa9bbb3b35a5b5fabfc83cdb35a6ea950788'),
 'cases': ('PG6040-current3976-cases/cases.json', 'af2845e1a6c82581975e6a3362db9392696092542467040236d73212736528f1'),
 'static': ('PG6044-remaining33-static-v2/manifest.json', '9221ffadcdc28435bee4e2cb7a289f97dc813b24132c2e2fcc43bb53a0d1ea23'),
 'review': ('PG6048-current-jdbc24-v2/manifest.json', '087cc73138dcb3f91f082510c9c2b6dc6a8f390e569a4cbaba1f6d75fccf3c4a')}


def validate(whole, static, review, physical):
    if not (whole['productionSource'] == static['source'] == review['source'] == SOURCE
            and whole['actualExit'] == static['actualExit'] == review['actualExit'] == 0
            and (whole['tests'], whole['suites'], whole['mainClasses'], whole['sourceFiles']) == (3976, 593, 1667, 851)
            and whole['FESFlakyNotRun'] == whole['staticSixModules'] == 0 and whole['returnedOriginalTerminalExact']
            and static['currentWholeQualificationSha256'] == REFS['whole'][1]
            and review['currentWholeQualificationSha256'] == REFS['whole'][1]
            and review['currentWholeCasesSha256'] == REFS['cases'][1]
            and static['pmdRawFindings'] == review['currentRawFindings'] == 1296
            and static['pmdProcessingErrors'] == static['checkstyleFindings'] == 0
            and physical['auxClassHashes'] == whole['allPhysicalMainSha256']
            and physical['allSourceHashes'] == whole['allSourceHashes']
            and static['additionalBuildsIssued'] == static['testsExecuted'] == 0
            and review['sourceAndWholeJoinedDispositions'] == 606):
        raise ValueError('one current source/run complete technical chain only')


def main():
    values = {}
    for key, (relative, digest) in REFS.items():
        path = BASE/relative
        if sha(path) != digest:
            raise ValueError('immutable technical-chain input')
        values[key] = json.loads(path.read_bytes())
    physical_path = W/'pg6044-remaining33-static-v2/manifest.safe.json'
    if sha(physical_path) != values['static']['privateManifestSha256']:
        raise ValueError('actual original Jar/source physical proof')
    validate(values['whole'], values['static'], values['review'], json.loads(physical_path.read_bytes()))
    value = dict(actualExit=0, source=SOURCE, references={k: dict(path=p, sha256=h) for k, (p, h) in REFS.items()},
        tests=3976, suites=593, mainClasses=1667, sourceFiles=851, currentOrdinaryRegressionTechnicallyQualified=True,
        currentStaticPhysicalVerificationComplete=True, rawStaticWarnings=1296, sourceAndWholeJoinedDispositions=606,
        unreviewedStaticWarnings=690, globalFour100=values['whole']['global100'], allStaticApplicabilityResolved=False,
        formalAccepted=False, formalBaseline='PT-WEB-20260925-24/1964PT/53scope', pgptAllComplete=False,
        openFunctionalBug='BUG1530/SSC310', nativeQualified=False, chrFinalQualified=False, effortPercent=None,
        ptAlternativeCompleted=0, vmActions=0, additionalBuildsIssued=0, testsExecuted=0)
    out = BASE/'PG6050-current3976-technical-seal-v1'; os.umask(0o077); out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, technicalQualified=True, formalAccepted=False,
        globalFour100=value['globalFour100'], manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
