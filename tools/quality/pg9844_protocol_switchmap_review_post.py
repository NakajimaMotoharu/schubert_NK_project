"""Independent Python exec bits and JDK bytecode offsets validate the static handler/probe map."""
import copy
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from jacoco_readonly_exec_subset import decode, selftest
from host_tool_invocation import capture, verify

ROOT = data.ROOT
WORK = ROOT.parent / 'pgpt-runs/PG379'
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
SLOT = WORK / 'pg9844-protocol-switchmap-review-post-v1'
OUT = BASE / 'PG9844-protocol-switchmap-review-post-v1'


def jdk_handlers(text):
    result = {}
    pieces = re.split(r'(?m)^class ([\w.$]+) \{\s*$',text)
    if len(pieces) != 9:
        raise ValueError('exact four JDK class blocks')
    for index in range(1,len(pieces),2):
        name,body = pieces[index].replace('.','/'),pieces[index+1]
        instructions = {int(m.group(1)):(m.group(2),m.group(3) or '') for m in
            re.finditer(r'^\s+(\d+):\s+(\w+)(?:\s+([^\n]*))?$',body,re.MULTILINE)}
        table = re.findall(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+Class\s+(\S+)\s*$',body,re.MULTILINE)
        rows = []
        for begin,end,target,kind in table:
            begin,end,target = int(begin),int(end),int(target)
            if kind != 'java/lang/NoSuchFieldError' or instructions[end][0] != 'goto':
                raise ValueError('only compiler missing-field handler with explicit merge')
            join = int(instructions[end][1].split()[0])
            if not re.fullmatch(r'astore(?:_\d+)?',instructions[target][0]):
                raise ValueError('handler exception discard only')
            if [pc for pc in instructions if target <= pc < join] != [target]:
                raise ValueError('no extra handler instruction')
            references = []
            for pc,(opcode,operand) in instructions.items():
                if begin <= pc < end and opcode == 'getstatic':
                    ref = re.search(r'// Field ([\w/$]+)\.([\w$]+):(\S+)',operand)
                    if ref:
                        references.append(ref.groups())
            if len(references) != 1:
                raise ValueError('one enum field in the independent raw bytecode span')
            enum,field,descriptor = references[0]
            rows.append(dict(enumType=enum,enumField=field,fieldDescriptor=descriptor,
                tryBeginByteOffset=begin,tryEndByteOffset=end,handlerByteOffset=target,mergeByteOffset=join,
                handlerType=kind,handlerBody='ASTORE_ONLY_EXCEPTION_DISCARD'))
        if not rows or name in result:
            raise ValueError('all four complete nonduplicate handler tables')
        result[name] = rows
    return result


def validate(manifest,mapping,decoded,jdk):
    names = set(manifest['classes'])
    if names != set(decoded['classes']) or names != set(jdk) or len(names) != 4 or len(mapping) != 16:
        raise ValueError('full exact scope')
    if manifest['rawHitProbes'] != 25 or manifest['rawMissedProbes'] != 16:
        raise ValueError('no raw coverage correction')
    if any(manifest[k] for k in ('generatedInstructionCoverageQualified','exclusionReviewApprovalGranted',
        'newExclusionSettings','currentRuntimeEnumBomOrClassloaderVerified','historicalSuccessTransferred',
        'coverageUnion','productTestsExecuted','newAccepted','formalUpdated','wholeG01Accepted','whole451Accepted')):
        raise ValueError('static review is not execution, exemption or acceptance')
    for name in names:
        old = manifest['classes'][name]
        independent = decoded['classes'][name]
        if old['crc64'] != independent['crc64'] or old['totalRawProbes'] != independent['probeCount']:
            raise ValueError('independent raw class CRC/probe count')
        rows = sorted((r for r in mapping if r['className'] == name),key=lambda r:r['handlerOrdinal'])
        if len(rows) != len(jdk[name]) or [r['handlerOrdinal'] for r in rows] != list(range(len(rows))):
            raise ValueError('complete per-class original handler order')
        ids = [r['missedProbeId'] for r in rows]
        if len(ids) != len(set(ids)) or set(ids) != set(independent['missedProbeIds']):
            raise ValueError('independent actual missed bits, no shifted or duplicated ID')
        if old['rawHitProbes'] != len(independent['hitProbeIds']) or old['rawMissedProbes'] != len(ids):
            raise ValueError('original hit/miss count retained')
        for row,other in zip(rows,jdk[name],strict=True):
            if any(row[k] != other[k] for k in ('enumType','enumField','fieldDescriptor','handlerType')):
                raise ValueError('independent JDK enum-field/handler semantics')
            if row['body'] != other['handlerBody'] or not row['historicalProbeWasMissed'] or row['targetExecutedByReview']:
                raise ValueError('empty handler only, no runtime claim')


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    proof_sha = '4159dc3dda26a447e147b3c689de36e2052662fada0d9a87374a5fec4b208bed'
    proof = data.read_checked(BASE / 'PG9842-protocol-switchmap-review-v2/manifest.json',proof_sha)
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE and proof['historicalExecutionSource'] == 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
    mapping = data.read_checked(BASE / 'PG9842-protocol-switchmap-review-v2/handler-probe-map.json',proof['handlerProbeMapSha256'])
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',proof['normalManifestSha256'])
    raw = (WORK / 'pg9722-protocol-module-host-v1/jacoco.exec').read_bytes()
    assert data.sha(raw) == proof['originalExecSha256']
    vectors = selftest()
    decoded = decode(raw,set(proof['classes']))
    assert decoded['sessions'][0]['labelBytesHex'] == b'PG9722-PROTOCOL-FULL-MODULE'.hex()
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    os_mode = __import__('os')
    os_mode.umask(0o077)
    SLOT.mkdir()
    steps.SLOT = SLOT
    command = [str(ROOT.parent / 'toolchain/jdk-25.0.4/bin/javap'),'-c','-p','-classpath',str(jar),
        *[name.replace('/','.') for name in sorted(proof['classes'])]]
    receipt = steps.step('independent-jdk-bytecode',command)
    assert receipt['actualExit'] == 0 and not receipt['timedOut']
    jdk_text = (SLOT / 'independent-jdk-bytecode.stdout').read_text()
    jdk = jdk_handlers(jdk_text)
    validate(proof,mapping,decoded,jdk)
    negatives = []
    for label,edit in (
        ('probe-id-shifted',lambda m,r:r[0].update(missedProbeId=r[0]['missedProbeId']+1)),
        ('duplicate-handler',lambda m,r:r.append(copy.deepcopy(r[0]))),
        ('handler-missing',lambda m,r:r.pop()),
        ('enum-field-renamed',lambda m,r:r[0].update(enumField='UNSUPPORTED_FIELD')),
        ('fake-coverage-zero',lambda m,r:m.update(rawMissedProbes=0)),
        ('runtime-promoted',lambda m,r:m.update(currentRuntimeEnumBomOrClassloaderVerified=True)),
        ('exemption-promoted',lambda m,r:m.update(exclusionReviewApprovalGranted=True)),
        ('old-execution-promoted',lambda m,r:m.update(productTestsExecuted=102))):
        m,r = copy.deepcopy(proof),copy.deepcopy(mapping)
        edit(m,r)
        try:
            validate(m,r,decoded,jdk)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('bad static review claim accepted: ' + label)
    assert vectors == 12 and len(negatives) == 8
    assert data.sha((WORK / 'pg9722-protocol-module-host-v1/jacoco.exec').read_bytes()) == proof['originalExecSha256']
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    verify(invocation)
    OUT.mkdir()
    with (OUT / 'independent-jdk-bytecode.txt').open('x') as stream:
        stream.write(jdk_text)
    data.write(OUT / 'independent-probes.json',decoded['classes'])
    data.write(OUT / 'independent-handler-byte-offsets.json',jdk)
    result = dict(actualExit=0,source=SOURCE,historicalExecutionSource=proof['historicalExecutionSource'],invocation=invocation,
        reviewManifestSha256=proof_sha,originalExecSha256=proof['originalExecSha256'],independentJdkStage=receipt,
        independentExecParserSha256=data.sha((ROOT / 'tools/quality/jacoco_readonly_exec_subset.py').read_bytes()),
        execParserVectors=vectors,reviewClaimNegativeVectors=negatives,classes=4,handlerSites=16,distinctEnumFields=10,
        historicalRawHits=25,historicalRawMisses=16,allSixteenMissedBitsHaveIndependentEmptyHandlerAndEnumFieldProof=True,
        binaryProbeTableSha256=data.sha((OUT / 'independent-probes.json').read_bytes()),
        jdkByteOffsetTableSha256=data.sha((OUT / 'independent-handler-byte-offsets.json').read_bytes()),
        actualRuntimeBomClassloaderVerification=False,generatedInstructionCoverageQualified=False,reviewApprovalGranted=False,
        newExclusionSettings=False,productTestsExecuted=0,targetClassesDefinedOrInitialized=False,
        actualExternalOperations=0,newAccepted=0,formalUpdated=False,wholeG01Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,classes=4,handlerSites=16,rawMissesUnchanged=16,execParserVectors=12,negativeClaimVectors=8,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
