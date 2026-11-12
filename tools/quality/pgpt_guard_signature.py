"""One witnessed real Guard interface, never replacement owner/native authority.

The original outer class is a compiler symbol only. The runtime/report component
contains only the real interface, with every uncovered default branch retained.
No application JAR is opened and no product class is loaded by this module.
"""
from pathlib import Path
import hashlib
import json
import re
import zipfile

R = Path(__file__).resolve().parents[2]
RUNS = R.parent / 'pgpt-runs/PG379'
BASE = 'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame'
GUARD = BASE + '$Guard'
SOURCE = 'src/schubert-nk-bootstrap/src/main/java/' + BASE + '.java'
SOURCE_SHA = '48645538321f59775ceca14b6c4ee201db6cbad142e7ca7551e35145f886f4e7'
CLASS_SHA = {
    BASE: 'cf12980ffcb4982da0b9cd5425730825a5cd8762bfdcdc581aa3cf6ab18b46ea',
    GUARD: '53f2b39f586ec6ee172b0e3009d46638a60ca8f1ce8ad442f497affa6cbd869b',
}
FORBIDDEN_INIT = {BASE, 'dev/codex/schubert/nk/bootstrap/ChildStartupContext',
                  'dev/codex/schubert/nk/storage/LinuxMonotonicClock'}
WITNESS = 'evidence/01_PT/018_NK-OPS-001/evidence/PG28388-real-guard-exact-byte-signature-witness-v1/manifest.json'
CACHE = RUNS / 'pg28388-real-guard-exact-byte-signature-witness-v1/compile-signatures'


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def syntax(c):
    option = c.get('reviewedGuardSignature')
    if option is None:
        return
    require(isinstance(option, dict) and set(option) == {'witness', 'source'},
            'exact Guard signature option')
    for key in ['witness', 'source']:
        pin = option[key]
        require(isinstance(pin, dict) and set(pin) == {'path', 'sha256'} and
                isinstance(pin['sha256'], str) and
                re.fullmatch('[0-9a-f]{64}', pin['sha256']), 'Guard pin schema')
    require(option['witness']['path'] == WITNESS and
            option['witness'] in c.get('closureProofs', []), 'explicit witnessed real Guard')
    require(option['source'] == dict(path=SOURCE, sha256=SOURCE_SHA),
            'exact unchanged Guard source, no substitute')
    physical = c.get('physicalClasses', [])
    require(GUARD + '.class' in physical and
            not any(n.startswith(BASE) and n != GUARD + '.class' for n in physical),
            'only Guard interface runtime/report physical class')
    require(SOURCE not in c.get('mainSources', []), 'outer is not a fresh compiled runtime source')
    forbidden = c.get('forbiddenInitializedClasses', [])
    require(isinstance(forbidden, list) and FORBIDDEN_INIT <= set(forbidden),
            'outer and native factory initialization forbidden')


def validate_witness(c, witness, pre, current_source_sha):
    """Pure metadata qualification; caller pins public bytes before any class access."""
    syntax(c)
    require(witness.get('actualExit') == 0 and witness.get('productTestsExecuted') == 0 and
            witness.get('productClassesLoadedOrInitialized') is False and
            witness.get('appJarOrActualFourOrRootProtectedClassAccess') == 0,
            'metadata-only real-class witness')
    require(witness.get('sourceFrame') == c['reviewedGuardSignature']['source'] and
            current_source_sha == SOURCE_SHA, 'current same-source Guard signature')
    require(witness.get('guardCurrentCrcMatchesPriorPositive') == 'b5b153f7fd9d91fa',
            'original positive Guard CRC witness')
    require(pre.get('normalCompileSource') == 'd8ff9efb16a7da1b073bdf9770487e3e6415b636' and
            pre.get('normalCompileExit') == 0 and
            pre.get('sourceByteSameCurrentAndNormalCompile') is True and
            pre.get('positiveGuardCrc') == 'b5b153f7fd9d91fa',
            'original normal compiler/source receipt')
    classes = witness.get('classes')
    require(isinstance(classes, dict) and set(classes) == set(CLASS_SHA),
            'exact two real compiler-symbol class names')
    for name, sha in CLASS_SHA.items():
        row = classes[name]
        require(row.get('sha256') == sha and
                row.get('ownedCopy') == str(CACHE / (name + '.class')) and
                row.get('runtimeUse') == ('GUARD_INTERFACE_ONLY' if name == GUARD else
                                         'COMPILE_SYMBOL_ONLY_FORBIDDEN_RUNTIME_INITIALIZATION'),
                'exact class hash/path/purpose before stat')


def checked(c):
    """Public receipt/source reads only; no cached class access at this stage."""
    if c.get('reviewedGuardSignature') is None:
        return None
    syntax(c)
    pin = c['reviewedGuardSignature']['witness']
    path = R / pin['path']
    require(digest(path) == pin['sha256'], 'Guard witness hash')
    witness = json.loads(path.read_text())
    prepin = witness.get('preconditions', {})
    require(prepin.get('path') == WITNESS.rsplit('/', 1)[0] +
            '/preconditions-before-class-access.safe.json', 'fixed public provenance receipt')
    prepath = R / prepin['path']
    require(digest(prepath) == prepin.get('sha256'), 'Guard provenance hash')
    source = R / SOURCE
    require(source.is_file() and not source.is_symlink(), 'regular unchanged source')
    validate_witness(c, witness, json.loads(prepath.read_text()), digest(source))
    for name in c['mainSources'] + [t['path'] for t in c['testSources']]:
        validate_closed_text((R / name).read_text())
    return witness


def validate_closed_text(text):
    require(not re.search(r'\b(?:ChildStartupContext|LinuxMonotonicClock)\b|'
                          r'\.parentsGuard\s*\(|'
                          r'\bnew\s+(?:\w+\.)*MaintenanceOwnerFrame\s*\(', text),
            'no outer/native construction or owner factory in closed caller')


def create_compile_carrier(c, work):
    witness = checked(c)
    if witness is None:
        return None
    data = {}
    for name, sha in CLASS_SHA.items():
        path = CACHE / (name + '.class')
        require(path.is_file() and not path.is_symlink(), 'regular exact witnessed class')
        value = path.read_bytes()
        require(hashlib.sha256(value).hexdigest() == sha, 'witnessed class bytes unchanged')
        data[name] = value
    carrier = work / 'guard-compile-signatures.jar'
    with zipfile.ZipFile(carrier, 'x', compression=zipfile.ZIP_STORED) as output:
        for name, value in data.items():
            output.writestr(zipfile.ZipInfo(name + '.class', (1980, 1, 1, 0, 0, 0)), value)
    return dict(witness=c['reviewedGuardSignature']['witness'],
                source=c['reviewedGuardSignature']['source'],
                compileCarrier=dict(path=str(carrier), sha256=digest(carrier)),
                compileClassHashes=dict(CLASS_SHA), runtimeClass=GUARD,
                runtimeClassSha256=CLASS_SHA[GUARD],
                priorPositiveGuardCrc='b5b153f7fd9d91fa')


def copy_runtime_interface(signature, work):
    if signature is None:
        return
    value = (CACHE / (GUARD + '.class')).read_bytes()
    require(hashlib.sha256(value).hexdigest() == CLASS_SHA[GUARD], 'real Guard runtime bytes')
    target = work / 'target/classes' / (GUARD + '.class')
    require(not target.exists(), 'compiler must not create a replacement Guard')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(value)


def validate_prepared(c, manifest, work):
    signature = manifest.get('guardSignature')
    if c.get('reviewedGuardSignature') is None:
        require(signature is None, 'no implicit signature dependency')
        return
    checked(c)
    require(isinstance(signature, dict) and
            signature['witness'] == c['reviewedGuardSignature']['witness'] and
            signature['source'] == c['reviewedGuardSignature']['source'] and
            signature['compileClassHashes'] == CLASS_SHA and
            signature['runtimeClass'] == GUARD and
            signature['runtimeClassSha256'] == CLASS_SHA[GUARD], 'exact prepared signature receipt')
    carrier = work / 'guard-compile-signatures.jar'
    require(signature['compileCarrier'] == dict(path=str(carrier), sha256=digest(carrier)),
            'immutable owned compile-only carrier')
    require(str(carrier) not in manifest['dependencies'], 'compile carrier never runtime dependency')
    require(manifest['physicalClassHashes'].get(GUARD + '.class') == CLASS_SHA[GUARD] and
            BASE + '.class' not in manifest['physicalClassHashes'],
            'report/runtime real interface only, no outer')
