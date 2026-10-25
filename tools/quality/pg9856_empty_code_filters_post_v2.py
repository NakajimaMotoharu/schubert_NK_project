"""Independent original JDK disassembly and pinned-library mechanism review, not target execution."""
from collections import Counter
import copy
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
SLOT = ROOT.parent/'pgpt-runs/PG379/pg9856-empty-code-filters-post-v1'
OUT = BASE/'PG9856-empty-code-filters-post-v2'
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'


def disassembly(text, keys):
    rows = []
    blocks = re.split(r'(?m)^Compiled from "[^"\n]+"\s*$',text)
    if blocks[0].strip() or len(blocks) != 32:
        raise ValueError('exact31 JDK original class blocks')
    for body in blocks[1:]:
        header = re.search(r'(?m)^[^\n]*\bclass ([\w.$]+)[^\n]*\{\s*$',body)
        if header is None:
            raise ValueError('JDK class identity required')
        name = header.group(1).replace('.','/')
        key = keys[name]
        signature = descriptor = None
        code = None

        def finish():
            if code is not None:
                if descriptor is None or signature is None:
                    raise ValueError('complete method identity')
                label = '<clinit>' if signature == 'static {};' else signature.split('(',1)[0].split()[-1]
                if label.replace('.','/') == name:
                    label = '<init>'
                rows.append(dict(physicalKey=key,name=label,descriptor=descriptor,instructions=code))
        for line in body[header.end():].splitlines():
            if line.startswith('  ') and not line.startswith('   ') and line.rstrip().endswith(';'):
                finish()
                signature,descriptor,code = line.strip(),None,None
            elif line.startswith('    descriptor: '):
                descriptor = line.split(': ',1)[1].strip()
            elif line.strip() == 'Code:':
                code = []
            elif line == '}':
                finish()
                signature=descriptor=code=None
            elif code is not None:
                match = re.match(r'^\s+(\d+):\s+([a-z][a-z0-9_]*)(?:\s+(.*))?$',line)
                if match:
                    code.append(dict(byteOffset=int(match.group(1)),opcode=match.group(2),operand=match.group(3) or ''))
        if signature is not None:
            finish()
    if len(rows) != 49 or len({(r['physicalKey'],r['name'],r['descriptor']) for r in rows}) != 49:
        raise ValueError('all original49 methods required')
    return rows


def validate(proof, methods, contexts, jdk):
    if any(proof[k] for k in ('targetClasspathContainsProduct','targetDefinedOrInitialized','productTestsExecuted',
        'newExclusionSettings','exclusionReviewApprovalGranted','currentCoverageComputed','rawMissedProbesRewritten',
        'historicalSuccessTransferred','newAccepted','formalUpdated','wholeG01Accepted','whole451Accepted')):
        raise ValueError('filter facts cannot promote execution, raw coverage, exemption or acceptance')
    primary = {(r['physicalKey'],r['name'],r['descriptor']):r for r in methods}
    observed = {(r['physicalKey'],r['name'],r['descriptor']):r for r in jdk}
    if len(primary) != len(methods) or len(primary) != 49 or set(primary) != set(observed) or len(contexts) != 31:
        raise ValueError('all exact whole classes/methods')
    result = []
    for key,row in observed.items():
        original = primary[key]
        code = row['instructions']
        opcodes = [r['opcode'] for r in code]
        if original['realOpcodeInstructions'] != len(code) or original['standardFilterIgnoredOpcodes'] != len(code) or original['remainingOpcodes'] != 0:
            raise ValueError('every original real instruction equals recorded standard ignored range')
        context = contexts[key[0]]
        if context['asmFlags'] & 0x1000:
            if row['name'] != '<clinit>' or row['descriptor'] != '()V':
                raise ValueError('synthetic helper clinit only')
            mechanism = 'SyntheticClassFilter'
        elif row['name'] == '<init>':
            if row['descriptor'] != '()V' or not original['methodFlags'] & 2 or opcodes != ['aload_0','invokespecial','return']:
                raise ValueError('private empty noarg constructor exact original shape')
            if context['superName']+'."<init>":()V' not in code[1]['operand']:
                raise ValueError('direct noarg superclass constructor only')
            mechanism = 'PrivateEmptyNoArgConstructorFilter'
        else:
            expected = {'toString':['aload_0','invokedynamic','areturn'],
                'hashCode':['aload_0','invokedynamic','ireturn'],
                'equals':['aload_0','aload_1','invokedynamic','ireturn']}
            if context['superName'] != 'java/lang/Record' or opcodes != expected.get(row['name']):
                raise ValueError('generated record object method exact original shape')
            mechanism = 'RecordsFilter'
        result.append({**row,'mechanism':mechanism,'reviewApprovalGranted':False})
    return result


def main():
    invocation = capture(Path(__file__))
    assert SLOT.is_dir() and not OUT.exists()
    primary_sha = 'e7bd95804e49ae9a47e1d3422d7af901c2bfaff0278141913919bc6152aed548'
    proof = data.read_checked(BASE/'PG9854-empty-code-standard-filters-v1/manifest.json',primary_sha)
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE and proof['opcodeInstructions'] == 794
    methods = data.read_checked(BASE/'PG9854-empty-code-standard-filters-v1/method-filter-ranges.json',proof['methodRangesSha256'])
    contexts = data.read_checked(BASE/'PG9854-empty-code-standard-filters-v1/class-filter-contexts.json',proof['contextsSha256'])
    keys = {k.split(':',1)[1].removesuffix('.class'):k for k in contexts}
    assert len(keys) == len(contexts) == 31
    normal = data.read_checked(BASE/'PG9812-cleanup-values-six-compile-v1/manifest.json',proof['normalManifestSha256'])
    paths = {j['path']:j['sha256'] for j in normal['jars'].values()}
    paths.update(proof['libraryHashes'])
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in paths.items())
    original_post = ROOT/'tools/quality/pg9856_empty_code_filters_post.py'
    assert data.sha(original_post.read_bytes()) == 'b7b4c51304f140582ed0f5855cbd1cb281074cbc04cd4db5a4bdf545741216d4'
    stages = []
    for label,digest in (
        ('original31-bytecode','a39e7c5a5d4c6a14a0235713b615e09c03389e0ad194051ad0328baffa297452'),
        ('pinned-standard-filters','bd6039999e5bb43b4f10bff1d0050fdff32006e60a29bab1c01b4398a69ace8a')):
        receipt = json.loads((SLOT/(label+'-exit.safe.json')).read_bytes())
        assert receipt['actualExit'] == 0 and not receipt['timedOut']
        assert data.sha((SLOT/(label+'.stdout')).read_bytes()) == digest == receipt['stdoutSha256']
        assert data.sha((SLOT/(label+'.stderr')).read_bytes()) == receipt['stderrSha256']
        stages.append(receipt)
    text = (SLOT/'original31-bytecode.stdout').read_text()
    jdk_rows = disassembly(text,keys)
    result = validate(proof,methods,contexts,jdk_rows)
    filter_text = (SLOT/'pinned-standard-filters.stdout').read_text()
    for token in ('getClassAccess','4096','IFilterOutput.ignore','// String <init>','// String ()V',
        '// String java/lang/Record','isToString','isHashCode','isEquals','getSuperClassName'):
        if token not in filter_text:
            raise ValueError('pinned library mechanism not independently read: '+token)
    negatives = []
    for name,edit in (
        ('missing-method',lambda p,m,c,j:m.pop()),
        ('false-zero-code',lambda p,m,c,j:m[0].update(realOpcodeInstructions=0)),
        ('missing-ignore',lambda p,m,c,j:m[0].update(standardFilterIgnoredOpcodes=0)),
        ('wrong-jdk-opcode',lambda p,m,c,j:j[next(i for i,r in enumerate(j) if r['name']=='<init>')]['instructions'][0].update(opcode='WRONG')),
        ('wrong-super',lambda p,m,c,j:c.update({k:{**v,'superName':'foreign/Base','asmFlags':0} for k,v in c.items()})),
        ('exemption-approved',lambda p,m,c,j:p.update(exclusionReviewApprovalGranted=True)),
        ('raw-rewritten',lambda p,m,c,j:p.update(rawMissedProbesRewritten=True)),
        ('coverage-promoted',lambda p,m,c,j:p.update(currentCoverageComputed=True))):
        p,m,c,j = map(copy.deepcopy,(proof,methods,contexts,jdk_rows))
        edit(p,m,c,j)
        try:
            validate(p,m,c,j)
        except ValueError:
            negatives.append(name)
        else:
            raise AssertionError('false filter explanation accepted: '+name)
    assert len(negatives) == 8 and all(data.sha(Path(p).read_bytes()) == h for p,h in paths.items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'independent-method-mechanisms.json',result)
    (OUT/'original31-bytecode.txt').write_text(text)
    (OUT/'pinned-standard-filters.txt').write_text(filter_text)
    manifest = dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=primary_sha,reusedOriginalJdkStages=stages,newJdkStages=[],
        originalPostFailure=dict(actualExit=1,sourceSha256='b7b4c51304f140582ed0f5855cbd1cb281074cbc04cd4db5a4bdf545741216d4',diagnostic='quoted ()V display marker assumption rejected'),
        classes=31,codeMethods=49,originalOpcodes=794,standardFilterRemainingOpcodes=0,
        mechanismMethodCounts=dict(Counter(r['mechanism'] for r in result)),claimRejectionVectors=negatives,
        independentMethodMechanismsSha256=data.sha((OUT/'independent-method-mechanisms.json').read_bytes()),
        originalDisassemblySha256=data.sha(text.encode()),pinnedFilterBytecodeSha256=data.sha(filter_text.encode()),
        javapClasspathIsInputDataNotExecutableTargetClasspath=True,targetDefinedOrInitialized=False,
        productTestsExecuted=0,newExclusionSettings=False,exclusionReviewApprovalGranted=False,
        measuredCoverageComputed=False,rawMissedProbesRewritten=False,historicalSuccessTransferred=False,
        newAccepted=0,formalUpdated=False,wholeG01Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',manifest)
    print(json.dumps(dict(actualExit=0,classes=31,methods=49,mechanisms=manifest['mechanismMethodCounts'],
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
