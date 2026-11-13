"""Six witnessed static-analysis symbols, absent from every product runtime.

No product type is loaded or initialized. This module opens no application JAR
and supplies no Root/native/owner authority or execution permission.
"""
from pathlib import Path
import copy
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[2]
RUNS = R.parent / 'pgpt-runs/PG379'
BASE = 'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame'
CHILD = 'dev/codex/schubert/nk/bootstrap/ChildStartupContext'
CLOCK = 'dev/codex/schubert/nk/storage/LinuxMonotonicClock'
NAMES = {CHILD, CHILD + '$MaintenanceParent', BASE + '$Clock', BASE + '$Parent',
         BASE + '$ParentProbe', CLOCK}
SOURCE_PATHS = ['src/schubert-nk-bootstrap/src/main/java/' + CHILD + '.java',
                'src/schubert-nk-storage/src/main/java/' + CLOCK + '.java']
WITNESS = 'evidence/01_PT/018_NK-OPS-001/evidence/PG28428-six-analysis-symbols-exact-byte-witness-v1/manifest.json'
AUDIT = 'evidence/01_PT/018_NK-OPS-001/evidence/PG28424-six-static-types-public-source-provenance-audit-v1/manifest.json'
CACHE = RUNS / 'pg28428-six-analysis-symbols-exact-byte-witness-v1/classes'


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def syntax(c):
    option = c.get('reviewedAnalysisOnlyContext')
    if option is None:
        return
    require(isinstance(option, dict) and set(option) == {'witness'} and
            c.get('reviewedGuardSignature') is not None, 'exact analysis-only context option')
    pin = option['witness']
    require(isinstance(pin, dict) and set(pin) == {'path', 'sha256'} and
            pin['path'] == WITNESS and isinstance(pin['sha256'], str) and
            re.fullmatch('[0-9a-f]{64}', pin['sha256']) and
            pin in c.get('closureProofs', []), 'pinned six-symbol witness')
    require(not {n + '.class' for n in NAMES} & set(c.get('physicalClasses', [])),
            'analysis symbols never runtime/report classes')
    require(NAMES <= set(c.get('forbiddenInitializedClasses', [])),
            'all analysis symbols must remain initialization-forbidden')
    require(not set(SOURCE_PATHS) & set(c.get('mainSources', [])),
            'native context source is not an ordinary caller compile unit')


def checked(c):
    """Public metadata/source checks precede all six cached class data accesses."""
    if c.get('reviewedAnalysisOnlyContext') is None:
        return None
    syntax(c)
    pin = c['reviewedAnalysisOnlyContext']['witness']
    path = R / pin['path']
    require(digest(path) == pin['sha256'], 'analysis witness bytes')
    witness = json.loads(path.read_text())
    require(witness.get('actualExit') == 0 and witness.get('productTestsExecuted') == 0 and
            witness.get('productClassLoadInitOrNativeCalls') == 0 and
            witness.get('actualFourOrRootTestsOrAppJarAccess') == 0 and
            witness.get('unknownClassNamesAllowed') is False, 'metadata-only static symbols')
    provenance = witness.get('sourceProvenance', {})
    require(provenance.get('path') == AUDIT and
            digest(R / AUDIT) == provenance.get('sha256'), 'public source provenance pin')
    audit = json.loads((R / AUDIT).read_text())
    require(audit.get('actualExit') == 0 and audit.get('safetyHoldsUnchanged') is True and
            audit.get('unknownAdditionalTypesAllowed') is False, 'bounded source/HOLD audit')
    require(set(witness.get('classes', {})) == NAMES and
            set(audit.get('allowedExactAnalysisOnlyClasses', {})) == NAMES,
            'exact six analysis class names')
    expected_sources = set(SOURCE_PATHS) | {
        'src/schubert-nk-bootstrap/src/main/java/' + BASE + '.java'}
    require({p['path'] for p in audit['publicSources']} == expected_sources,
            'exact three unchanged public source files')
    for pin in audit['publicSources']:
        source = R / pin['path']
        require(source.is_file() and not source.is_symlink() and
                digest(source) == pin['sha256'] and
                pin['originalNormalCompileSourceHashMatched'] is True,
                'current source unchanged from normal compile')
    for name in NAMES:
        row = witness['classes'][name]
        require(row.get('ownedCopy') == str(CACHE / (name + '.class')) and
                row.get('purpose') == 'ANALYSIS_ONLY_NO_RUNTIME_CLASS_LOADING_OR_INITIALIZATION' and
                row.get('classMajor') == 69 and isinstance(row.get('sha256'), str) and
                re.fullmatch('[0-9a-f]{64}', row['sha256']) and
                row.get('source') == audit['allowedExactAnalysisOnlyClasses'][name]['source'],
                'exact class data path/source/hash/purpose before stat')
    return witness


def create_carrier(c, work):
    witness = checked(c)
    require(witness is not None, 'explicit analysis context required')
    carrier = work / 'analysis-only-six-symbols.jar'
    with zipfile.ZipFile(carrier, 'x', compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(NAMES):
            path = CACHE / (name + '.class')
            require(path.is_file() and not path.is_symlink(), 'regular exact analysis class data')
            value = path.read_bytes()
            require(hashlib.sha256(value).hexdigest() == witness['classes'][name]['sha256'],
                    'analysis class data bytes')
            archive.writestr(zipfile.ZipInfo(name + '.class', (1980, 1, 1, 0, 0, 0)), value)
    return dict(witness=c['reviewedAnalysisOnlyContext']['witness'],
                carrier=dict(path=str(carrier), sha256=digest(carrier)),
                classes={n: witness['classes'][n]['sha256'] for n in sorted(NAMES)},
                purpose='STATIC_ANALYZER_AUX_ONLY_NEVER_PRODUCT_RUNTIME')


def analyzer_root(compiler_root, carrier_path):
    """Add exactly one analysis-only dependency; the compiler tree stays unchanged."""
    root = copy.deepcopy(compiler_root)
    ns = compiler_root.tag.split('}')[0] + '}' if '}' in compiler_root.tag else ''
    deps = root.find(ns + 'dependencies')
    require(deps is not None, 'owned compiler dependencies required')
    dep = ET.SubElement(deps, ns + 'dependency')
    for name, value in [('groupId', 'dev.codex.schubert.quality'),
                        ('artifactId', 'analysis-only-six-symbols'), ('version', '1'),
                        ('scope', 'system'), ('systemPath', str(carrier_path))]:
        ET.SubElement(dep, ns + name).text = value
    return root


def create_owned_context(c, work):
    value = create_carrier(c, work)
    pom = work / 'spotbugs-analysis-only-context.pom.xml'
    require(not pom.exists(), 'new-only owned analyzer POM')
    root = ET.parse(work / 'pom.xml').getroot()
    ET.ElementTree(analyzer_root(root, value['carrier']['path'])).write(
        pom, encoding='unicode', xml_declaration=True)
    value['analyzerPom'] = dict(path=str(pom), sha256=digest(pom))
    return value


def validate_analyzer_root(compiler_root, actual, carrier_path):
    expected = analyzer_root(compiler_root, carrier_path)
    require(ET.tostring(expected) == ET.tostring(actual),
            'only the explicit analysis dependency added to compiler POM')


def validate_prepared(c, manifest, work):
    value = manifest.get('analysisOnlyContext')
    if c.get('reviewedAnalysisOnlyContext') is None:
        require(value is None, 'no implicit analysis dependency')
        return
    witness = checked(c)
    require(isinstance(value, dict) and
            value['witness'] == c['reviewedAnalysisOnlyContext']['witness'] and
            value['purpose'] == 'STATIC_ANALYZER_AUX_ONLY_NEVER_PRODUCT_RUNTIME' and
            value['classes'] == {n: witness['classes'][n]['sha256'] for n in sorted(NAMES)},
            'exact analysis-only dependency receipt')
    carrier = work / 'analysis-only-six-symbols.jar'
    require(value['carrier'] == dict(path=str(carrier), sha256=digest(carrier)) and
            str(carrier) not in manifest['dependencies'], 'analysis carrier absent runtime dependencies')
    require(not {n + '.class' for n in NAMES} & set(manifest['physicalClassHashes']),
            'analysis classes absent product class directories')
    if 'analyzerPom' in value:
        pom = work / 'spotbugs-analysis-only-context.pom.xml'
        require(value['analyzerPom'] == dict(path=str(pom), sha256=digest(pom)),
                'exact owned analyzer POM')
        validate_analyzer_root(ET.parse(work / 'pom.xml').getroot(),
                               ET.parse(pom).getroot(), str(carrier))
