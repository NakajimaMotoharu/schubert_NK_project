"""Inspect qualified original JVM/source only: startup UNKNOWN loop, liveness fences and ABI."""
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6186_native_ownership_order import methods, instructions, one_call
from pg6084_web_factory_order import narrow_or_wide_literal_body
from classfile_field_flags import fields
from pg6384_web_fatal_callback_retry_qualification import original_source

QUALIFICATION_SHA = '7896c2a6d7d650cf2a67f9270e0ad039360c7a5ba073cf84685adddc578295f7'
WEB = 'dev.codex.schubert.nk.web.bootstrap.WebLogApplicationRuntime'
SHARED = 'dev.codex.schubert.nk.api.file.ServiceProcessResources'


def retention(code):
    ops = instructions(code)
    close = one_call({'scope': code}, 'AutoCloseable.close:')[0][1]
    diagnostic = one_call({'scope': code}, 'Consumer.accept:')[0][1]
    tick = one_call({'scope': code}, 'Runnable.run:')[0][1]
    fences = [pc for _, pc, _ in one_call({'scope': code}, 'Reference.reachabilityFence:', 4)]
    backward = [(pc, int(arg.strip())) for pc, op, arg in ops if op == 'goto' and int(arg.strip()) < pc]
    if len(backward) != 1:
        raise ValueError('one unconditional retaining backedge')
    back, target = backward[0]
    if not close < diagnostic < target <= tick < min(fences) <= max(fences) < back:
        raise ValueError('one close/diagnose, then finite tick and four liveness fences inside loop')
    if any(op in ('return', 'areturn', 'athrow') for pc, op, _ in ops if target <= pc <= back):
        raise ValueError('no owner unwind from retention loop')
    if any(op in ('new', 'anewarray', 'newarray', 'multianewarray', 'invokedynamic') for _, op, _ in ops):
        raise ValueError('no new retention frame/array/callback allocation after acquisition')
    catches = re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+Class java/lang/(Exception|Error)\s*$', code)
    if len(catches) != 2 or {kind for _, _, _, kind in catches} != {'Exception', 'Error'} or len({at for _, _, at, _ in catches}) != 1 or any(not int(a) <= close < int(b) for a, b, _, _ in catches):
        raise ValueError('both checked/unchecked Error close failures enter the same holding frame')
    return dict(closeOffset=close, diagnosticOffset=diagnostic, loopTarget=target, tickOffset=tick,
        fenceOffsets=fences, backedgeOffset=back, loopReturnOrThrow=0, newRetentionAllocations=0)


def bootstrap(block, verbose, expected):
    indices = re.findall(r'// InvokeDynamic #(\d+):', block)
    if len(indices) != 1:
        raise ValueError('one exact prepared policy callback')
    section = verbose.split('BootstrapMethods:', 1)[1]
    match = re.search(r'(?m)^  '+indices[0]+r':[^\n]*\n(?:(?!  \d+:|InnerClasses:)[^\n]*\n)*', section)
    if match is None or expected not in match.group():
        raise ValueError('prepared callback has exact protected target')
    return re.sub(r'#\d+', '#CP', match.group())


def read_jar(root, module, cls, verbose=False):
    jar = root/('src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
    text = subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-v' if verbose else '-c', '-s', '-classpath', str(jar), cls], text=True)
    return jar, text


def main():
    source = original_source(); qp = BASE/'PG6384-web-fatal-callback-retry-qualification-v1/manifest.json'
    if QUALIFICATION_SHA is None or sha(qp) != QUALIFICATION_SHA:
        raise ValueError('bind genuine original22 public qualification before review publication')
    q = json.loads(qp.read_bytes()); pp = W/'pg6384-web-fatal-callback-retry-qualification-v1/manifest.safe.json'
    if not (q['source'] == source and q['actualExit'] == 0 and (q['tests'], q['suites'], q['physicalMain']) == (22, 8, 1667) and sha(pp) == q['privateManifestSha256']):
        raise ValueError('actual original22/all8511667/sixJar qualification')
    proof = json.loads(pp.read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all current Main equal original source')
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all original Main/Test/gates fixed')
    run = W/'pg6382-web-fatal-callback-retry-v1/source'; old = W/'pg6348-web-lifetime-selected-v1/source'
    owners = {m+':'+c.replace('.', '/')+'.class' for m, c in (('web', WEB), ('bootstrap', SHARED))}
    old_public = json.loads((BASE/'PG6350-web-lifetime-qualification-v1/manifest.json').read_bytes())
    old_path = W/'pg6350-web-lifetime-qualification-v1/manifest.safe.json'
    if sha(old_path) != old_public['privateManifestSha256']:
        raise ValueError('immutable old Main comparison proof')
    before_proof = json.loads(old_path.read_bytes())
    current, before = proof['allPhysicalMainSha256'], before_proof['allPhysicalMainSha256']
    changed = {k for k in current if current[k] != before.get(k)}
    if set(current) != set(before) or changed != owners:
        raise ValueError('exact two physical Main changes, all other1665 unchanged')
    reviews = {}
    for module, cls in (('web', WEB), ('bootstrap', SHARED)):
        jar, text = read_jar(run, module, cls); _, previous_text = read_jar(old, module, cls)
        left, right = methods(previous_text), methods(text)
        with zipfile.ZipFile(jar) as z:
            actual = {module+':'+n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.class')}
            flags = fields(z.read(cls.replace('.', '/')+'.class')) if module == 'web' else None
        if actual != {k: v for k, v in current.items() if k.startswith(module+':')}:
            raise ValueError('every original Jar class still qualified')
        public = lambda blocks: {k for k in blocks if k.startswith('  public ')}
        if module == 'web':
            if public(left) != public(right):
                raise ValueError('Web public ABI unchanged')
            additions = set(right)-set(left)
            if len(additions) != 2 or not any('closeStartupResource(' in k for k in additions) or '  static {};' not in additions:
                raise ValueError('only private owner close and pre-acquisition clinit added')
            existing = [k for k in left if ' closeAfterFailure(' not in k]
            if any(narrow_or_wide_literal_body(left[k]) != narrow_or_wide_literal_body(right[k]) for k in existing):
                raise ValueError('all other Web methods/exception edges unchanged')
            clinit = right['  static {};']
            for token in ('unknownReleaseDiagnosticPolicy:', 'unknownReleaseObservationPolicy:'):
                one_call({'clinit': clinit}, 'ServiceProcessResources.'+token)
            if any(flags[name]['flags'] != 0x1a for name in (b'UNKNOWN_DIAGNOSTIC', b'UNKNOWN_INTERVAL')):
                raise ValueError('private static final policy fields')
            entry = next(v for k, v in right.items() if ' closeAfterFailure(' in k)
            one_call({'entry': entry}, 'Objects.requireNonNull:', 2)
            one_call({'entry': entry}, 'closeStartupResource:', 2)
            if any(op in ('new', 'anewarray', 'newarray', 'invokedynamic') for _, op, _ in instructions(entry)):
                raise ValueError('ordered close entry has no after-acquisition array/callback allocation')
            reviews['web'] = dict(publicAbiUnchanged=True, otherMethodBodiesAndEdgesUnchanged=len(existing),
                privateStaticFinalPolicyFields=True, classInitializationBeforeStaticFactory=True,
                retention=retention(next(v for k, v in right.items() if ' closeStartupResource(' in k)))
        else:
            added = public(right)-public(left)
            if not public(left) <= public(right) or len(added) != 2 or not all(any(name+'(' in k for k in added) for name in ('unknownReleaseDiagnosticPolicy', 'unknownReleaseObservationPolicy')):
                raise ValueError('exact two internal prepared-policy factories, no old public API removed')
            _, verbose = read_jar(run, module, cls, True)
            diagnostic = next(v for k, v in right.items() if ' unknownReleaseDiagnosticPolicy(' in k)
            observation = next(v for k, v in right.items() if ' unknownReleaseObservationPolicy(' in k)
            b1 = bootstrap(diagnostic, verbose, SHARED.replace('.', '/')+'.diagnoseUnknownRelease:')
            b2 = bootstrap(observation, verbose, SHARED.replace('.', '/')+'.lambda$unknownReleaseObservationPolicy$')
            observe = next(v for k, v in right.items() if ' lambda$unknownReleaseObservationPolicy$' in k)
            one_call({'observation': observe}, 'observeUnknownInterval:')
            if not all('Field '+name+':' in observe for name in ('UNKNOWN_OBSERVATION', 'UNKNOWN_FALLBACK')):
                raise ValueError('fixed protected observation/fallback, no user policy substitution')
            keep = [k for k in left if any(' '+name+'(' in k for name in ('retainUnknownRelease', 'diagnoseUnknownRelease', 'observeUnknownInterval', 'waitUnknownInterval', 'observeUnconfirmed'))]
            if len(keep) != 6 or any(narrow_or_wide_literal_body(left[k]) != narrow_or_wide_literal_body(right[k]) for k in keep):
                raise ValueError('every original retention/diagnostic/fallback method unchanged')
            reviews['shared'] = dict(publicFactoriesAdded=sorted(added), existingProtectedMethodBodiesUnchanged=sorted(keep),
                diagnosticBootstrap=b1, observationBootstrap=b2, compilerPrivateLambdaRenumberingNotPublicAbi=True)
    result = dict(actualExit=0, source=source, qualificationSha256=sha(qp), ownershipReviewed=True,
        originalSelectedTests=22, changedPhysical=sorted(changed), unchangedPhysical=1665, proofs=reviews,
        scope='ORIGINAL_SOURCE_JVM_NOT_REAL_RUNTIME_NATIVE_OR_PT_ALTERNATIVE', testsExecuted=0, additionalBuildsIssued=0,
        productionClassesExecuted=0, vmActions=0, formalAccepted=False, ptAlternativeCompleted=0,
        residualRisks=['factory-before-handoff/native/root ownership and true terminal remain separate',
                       'allSource/currentWhole/F03/global100/CHR/451 and rollouts still required'])
    os.umask(0o077); out = BASE/'PG6380-web-startup-order-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=source, changedPhysical=2, unchangedPhysical=1665, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
