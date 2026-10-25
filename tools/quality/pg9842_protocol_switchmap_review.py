"""Static byte-array/old-probe mapping only; target jar is not on the reader classpath."""
import json
import os
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
WORK = ROOT.parent / 'pgpt-runs/PG379'
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
OLD_SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
SLOT = WORK / 'pg9842-protocol-switchmap-review-v1'
OUT = BASE / 'PG9842-protocol-switchmap-review-v1'


def entries(value):
    path = Path(value['path'])
    assert data.sha(path.read_bytes()) == value['sha256']
    with zipfile.ZipFile(path) as archive:
        return {n:data.sha(archive.read(n)) for n in archive.namelist() if not n.endswith('/')}


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    old_sha = 'c5e2b600dfadfca7c1a8a889fec5d605e775b7e75e36955bc4a70cf5298290b5'
    old = data.read_checked(BASE / 'PG9726-protocol-generated-shape-post-v1/manifest.json',old_sha)
    normal_sha = 'e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95'
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',normal_sha)
    prior = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    assert old['actualExit'] == normal['actualExit'] == prior['actualExit'] == 0
    assert old['source'] == prior['source'] == OLD_SOURCE and normal['source'] == SOURCE
    assert not old['strictGeneratedInstructionCoverageQualified']
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    current = entries(normal['jars']['protocol'])
    assert current == entries(prior['jars']['protocol']) and sum(n.endswith('.class') for n in current) == 176
    assert all(current[n + '.class'] == r['physicalClassSha256'] for n,r in old['classes'].items())
    post = data.read_checked(BASE / 'PG9724-protocol-module-post-v2/manifest.json',
        '5eb3672c1838e6ef522e57f724392e946c437b0499967f7623d889504227cd77')
    original_exec = WORK / 'pg9722-protocol-module-host-v1/jacoco.exec'
    assert data.sha(original_exec.read_bytes()) == post['execSha256']
    deps = old['libraryHashes']
    assert len(deps) == 4 and all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    libraries = list(map(Path,deps))
    core = next(p for p in libraries if p.name == 'org.jacoco.core-0.8.15.jar')
    helper = ROOT / 'tools/quality/architecture/ProtocolSwitchMapApplicabilityReview.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = ROOT.parent / 'toolchain'
    os.umask(0o077)
    SLOT.mkdir()
    reader = SLOT / 'reader'
    reader.mkdir()
    cp = os.pathsep.join(map(str,[reader,*libraries]))
    jar = Path(normal['jars']['protocol']['path'])
    assert str(jar) not in cp and all('/schubert-nk-' not in str(p) for p in libraries)
    data.write(SLOT / 'begin.safe.json',dict(source=SOURCE,historicalExecutionSource=OLD_SOURCE,invocation=invocation,
        historicalShapeManifestSha256=old_sha,normalManifestSha256=normal_sha,originalExecSha256=post['execSha256'],
        helperSha256=helper_sha,libraryHashes=deps,readerClasspath=cp,targetJarAbsentFromClasspath=True,
        targetJarPath=str(jar),targetJarSha256=normal['jars']['protocol']['sha256'],actualExternalOperations=0))
    steps.SLOT = SLOT
    stages = [steps.step('compile-static-reader',[str(tc / 'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    stages.append(steps.step('map-original-probes',[str(tc / 'jdk-25.0.4/bin/java'),'-Xmx256m','-cp',cp,helper.stem,str(original_exec),str(jar)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    for label,name in (('read-standard-filter','org.jacoco.core.internal.analysis.filter.SyntheticClassFilter'),
        ('read-no-classloading-writer','org.jacoco.core.instr.Instrumenter$1')):
        stages.append(steps.step(label,[str(tc / 'jdk-25.0.4/bin/javap'),'-c','-p','-classpath',str(core),name]))
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in stages)
    filter_text = (SLOT / 'read-standard-filter.stdout').read_text()
    assert all(v in filter_text for v in ('getClassAccess','4096','iand','getFirst','getLast','IFilterOutput.ignore'))
    writer_text = (SLOT / 'read-no-classloading-writer.stdout').read_text()
    assert 'getCommonSuperClass' in writer_text and 'IllegalStateException' in writer_text and 'Class.forName' not in writer_text
    classes,handlers,enums = {},[],{}
    lines = (SLOT / 'map-original-probes.stdout').read_text().splitlines()
    assert lines[0] == 'TOOL_SELFTEST\t6' and lines[-1] == 'TOTAL\t25\t16\tNO_TARGET_EXECUTION\tNO_COVERAGE_PROMOTION'
    for line in lines[1:-1]:
        f = line.split('\t')
        if f[0] == 'CLASS':
            _,name,crc,total,hit,miss,count = f
            before = old['classes'][name]
            assert crc == before['crc64'] and int(hit) == before['rawHitProbes'] and int(miss) == before['rawMissedProbes']
            assert int(total) == int(hit) + int(miss) and int(count) == int(miss) and name not in classes
            classes[name] = dict(crc64=crc,totalRawProbes=int(total),rawHitProbes=int(hit),rawMissedProbes=int(miss),
                noSuchFieldHandlerCount=int(count),physicalClassSha256=before['physicalClassSha256'])
        elif f[0] == 'HANDLER':
            _,name,number,probe,enum,field,descriptor,index = f
            assert name in old['classes'] and descriptor == 'L' + enum + ';'
            handlers.append(dict(className=name,handlerOrdinal=int(number),missedProbeId=int(probe),enumType=enum,
                enumField=field,fieldDescriptor=descriptor,originalAsmInstructionListIndex=int(index),
                handlerType='java/lang/NoSuchFieldError',body='ASTORE_ONLY_EXCEPTION_DISCARD',
                enumFieldPresentInCurrentArtifact=True,historicalProbeWasMissed=True,targetExecutedByReview=False))
        else:
            assert f[0] == 'ENUM' and len(f) == 3 and f[1] not in enums
            enums[f[1]] = dict(constants=f[2],classSha256=current[f[1] + '.class'])
    assert set(classes) == set(old['classes']) and len(handlers) == len({(r['className'],r['missedProbeId']) for r in handlers}) == 16 and len(enums) == 3
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items()) and data.sha(helper.read_bytes()) == helper_sha
    assert data.sha(original_exec.read_bytes()) == post['execSha256'] and entries(normal['jars']['protocol']) == current
    verify(invocation)
    OUT.mkdir()
    for name in ('map-original-probes.stdout','read-standard-filter.stdout','read-no-classloading-writer.stdout'):
        with (OUT / name).open('xb') as stream:
            stream.write((SLOT / name).read_bytes())
    data.write(OUT / 'handler-probe-map.json',handlers)
    result = dict(actualExit=0,source=SOURCE,historicalExecutionSource=OLD_SOURCE,invocation=invocation,
        historicalShapeManifestSha256=old_sha,normalManifestSha256=normal_sha,originalExecSha256=post['execSha256'],
        helperSha256=helper_sha,libraryHashes=deps,classes=classes,enumDefinitions=enums,metadataSelftestVectors=6,
        rawHitProbes=25,rawMissedProbes=16,allMissedProbesMappedToEmptyMissingEnumFieldHandlers=True,
        handlerProbeMapSha256=data.sha((OUT / 'handler-probe-map.json').read_bytes()),stages=stages,
        standardFilterMechanism='ACC_SYNTHETIC_4096_FULL_METHOD_IGNORE_FIRST_TO_LAST',
        all176CurrentProtocolClassBytesSameAsHistoricalInput=True,targetAbsentFromReaderClasspath=True,
        targetClassesDefinedOrInitialized=False,targetMethodsExecuted=0,productTestsExecuted=0,
        generatedInstructionCoverageQualified=False,exclusionReviewApprovalGranted=False,newExclusionSettings=False,
        currentRuntimeEnumBomOrClassloaderVerified=False,historicalSuccessTransferred=False,coverageUnion=False,
        actualExternalOperations=0,newAccepted=0,formalUpdated=False,wholeG01Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,classes=4,mappedMissedProbes=16,rawHitProbes=25,rawMissedProbes=16,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
