"""Independent source/document review of frozen dispatch design, never product execution."""
from pathlib import Path
from copy import deepcopy
import datetime
import hashlib
import importlib.util
import json
import re
import subprocess

R = Path(__file__).resolve().parents[4]
B = R / 'evidence/01_PT/018_NK-OPS-001'
P = B / 'evidence/PG23912-request-dispatch14-static-design-v1'
O = B / 'evidence/PG23914-request-dispatch14-static-independent-v1'
load = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
EXPECTED = {
    'GAMREQ01': ('SCN', 'GAMES', 'games', None, 'Inline'),
    'SPKREQ01': ('SCN', 'SPEAKERS', 'speakers', 'SpeakerListRequestData', 'Inline'),
    'RTEREQ01': ('SCN', 'ROUTES', 'routes', 'RouteListRequestData', 'Inline'),
    'SCFREQ01': ('SCN', 'FILES', 'files', 'ScenarioFileListRequestData', 'Inline'),
    'SRCREQ01': ('SCN', 'SEARCH', 'search', 'ScenarioSearchRequestData', 'Inline'),
    'SCNREQ01': ('SCN', 'DETAIL', 'detail', 'ScenarioDetailRequestData', 'Detail'),
    'AUDREQ01': ('MED', 'AUDIO', 'audioMetadata', 'AudioDescriptorRequestData', 'DIRECT_OPTIONAL'),
    'ANMREQ01': ('MED', 'MENU', 'animationMenu', None, 'PRESENT_OPTIONAL'),
    'ANLREQ01': ('MED', 'ANIMATION', 'animationList', 'AnimationListRequestData', 'PRESENT_OPTIONAL'),
    'VIDREQ01': ('MED', 'VIDEO', 'videoMetadata', 'VideoDescriptorRequestData', 'DIRECT_OPTIONAL'),
    'MCTREQ01': ('MED', 'CATEGORIES', 'musicCategories', None, 'PRESENT_OPTIONAL'),
    'MCSREQ01': ('MED', 'SECTIONS', 'musicSections', 'MusicSectionRequestData', 'PRESENT_OPTIONAL'),
    'MTRREQ01': ('MED', 'TRACKS', 'musicTracks', 'MusicTrackRequestData', 'PRESENT_OPTIONAL'),
    'MEDREQ01': ('MED', 'MUSIC', 'musicMetadata', 'MusicDescriptorRequestData', 'DIRECT_OPTIONAL'),
}


def validate_rows(rows, fields):
    assert len(rows) == len({v['layout'] for v in rows}) == len({v['id'] for v in rows}) == 14
    assert {v['layout'] for v in rows} == set(EXPECTED)
    for row in rows:
        expected = EXPECTED[row['layout']]
        assert tuple(row[k] for k in ('domain', 'kind', 'repositoryMethod', 'requestDto', 'projection')) == expected
        assert row['canonicalOrderedFields'] == fields[row['layout']]
        assert row['responseLayout'] == row['layout'][:3] + 'RSP01'
        assert row['queryConnection'] == 'BORROWED_CALLER_OWNED'
        assert row['transactionOwner'] == 'OUTER_APPLICATION_SERVICE'
        assert row['staticReviewStatus'] == 'STATIC_PT_DESIGN_REVIEW_COMPLETE'
        assert row['dynamicStatus'] == 'NOT_EXECUTED_HOLD'
        assert row['ptPass'] is False and row['actualDbProven'] is False
        assert row['dynamicExceptionBehaviorProven'] is False
        assert len(row['plannedNegativeCases']) == 5 and 'NOT_EXECUTED_HOLD' in row['residualRisk']


def independent_method(text, name):
    # A separate line/indent method delimiter, not producer's brace parser.
    lines = text.splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith('  public ') and ' ' + name + '(' in line)
    last = next(i for i in range(first + 1, len(lines)) if lines[i] == '  }')
    body = '\n'.join(lines[first:last + 1])
    marks = list(re.finditer(r'(?m)^\s+case ([A-Z]+(?:, [A-Z]+)*) ->', body))
    result = {}
    for i, match in enumerate(marks):
        segment = body[match.end():marks[i + 1].start() if i + 1 < len(marks) else len(body)]
        for kind in match[1].split(', '):
            assert kind not in result
            result[kind] = segment
    return body, result


def main():
    assert not O.exists()
    m = load(P / 'manifest.json')
    assert m['actualExit'] == 0 and m['productTestsExecuted'] == 0
    assert m['compilerOrJvmExecuted'] is False and m['ptExecutionExempt'] is False and m['measuredCoverage'] is None
    cpath = R / m['config']['path']
    assert sha(cpath) == m['config']['sha256']
    cfg = load(cpath)
    ss = next(v for v in cfg['authority'] if Path(v['path']).name.startswith('323_'))
    for ref in cfg['authority']:
        p = R / ref['path']
        assert sha(p) == ref['sha256']
        assert p.read_bytes() == subprocess.check_output(['git', 'show', 'origin/main:' + ref['path']], cwd=R)
    document = (R / ss['path']).read_text()
    section = document.split('### 9.1 ')[1].split('### 9.3 ')[0]
    fields = {}
    for line in section.splitlines():
        match = re.fullmatch(r'\| ([A-Z]{3}REQ01) \| (.+) \|', line)
        if match:
            layout = match[1]
            pairs = [a + '/' + b for a, b in re.findall(r'([A-Za-z][A-Za-z0-9]*)/(X1|N1)', match[2])]
            if layout == 'SPKREQ01':
                assert 'optional' in match[2]
                pairs = [p + '?' for p in pairs]
            if layout == 'SRCREQ01':
                assert '以上optional' in match[2]
                pairs = [p + '?' if i < 6 else p for i, p in enumerate(pairs)]
            fields[layout] = pairs
    assert set(fields) == set(EXPECTED)
    assert sha(R / m['cases']['path']) == m['cases']['sha256']
    rows = load(R / m['cases']['path'])
    validate_rows(rows, fields)
    normal = load(R / cfg['normalIndex']['path'])
    role_checks = []
    for ref in cfg['sources']:
        path = R / ref['path']
        assert sha(path) == ref['sha256']
        assert path.read_bytes() == subprocess.check_output(['git', 'show', cfg['source'] + ':' + ref['path']], cwd=R)
        text = path.read_text()
        query, segments = independent_method(text, 'query')
        _, canonical = independent_method(text, 'canonical')
        assert set(segments) == set(canonical) == {x[1] for x in EXPECTED.values() if x[0] == ref['domain']}
        for row in [v for v in rows if v['domain'] == ref['domain']]:
            part = segments[row['kind']]
            assert re.findall(r'repository\.(\w+)\(', part) == [row['repositoryMethod']]
            if row['requestDto']:
                assert '(' + row['requestDto'] + ') values.data()' in part
            if row['projection'] in ('Inline', 'Detail'):
                assert 'ScenarioQuerySnapshot.' + row['projection'] + '(' in part
            else:
                assert ('Optional.of(' in part) == (row['projection'] == 'PRESENT_OPTIONAL')
        for arg in ('repository', 'connection', 'actor'):
            assert query.index(f'Objects.requireNonNull({arg}, "{arg}")') < query.index('return switch')
        assert 'catch' not in query
        assert not any('.' + method + '(' in query for method in ('close', 'commit', 'rollback', 'executeQuery', 'executeUpdate', 'getConnection'))
        physical = [v for v in normal.values() if v['path'] == ref['path']]
        assert len(physical) == 2
        assert all(v['sha256'] != ref['sha256'] for v in physical)
        role_checks.append(dict(path=ref['path'],sourceRoleBoundToGit=True,physicalClassEntries=len(physical),classHashNotSourceHash=True))
    # Finite horizontal check: prior contributor helpers compare source-to-source roles.
    previous = load(B / 'input/570_mon006_contributors27_scope.json')
    for ref in previous['manualDecisions']:
        assert sha(R / ref['path']) == ref['sourceSha256']
    negatives = []
    changes = [('repositoryMethod', 'wrong'), ('requestDto', 'WrongDto'), ('projection', 'Detail'),
               ('layout', 'BADREQ01'), ('canonicalOrderedFields', ['wrong/X1']),
               ('queryConnection', 'OWNED'), ('transactionOwner', 'REPOSITORY'),
               ('dynamicStatus', 'PASS'), ('ptPass', True), ('actualDbProven', True),
               ('dynamicExceptionBehaviorProven', True)]
    for field, value in changes:
        mutated = deepcopy(rows)
        mutated[0][field] = value
        try:
            validate_rows(mutated, fields)
        except (AssertionError, KeyError):
            negatives.append(field)
        else:
            raise AssertionError('accepted metadata mutation: ' + field)
    for label, mutated in [('missing', rows[:-1]), ('duplicate', rows[:-1] + [rows[0]])]:
        try:
            validate_rows(mutated, fields)
        except AssertionError:
            negatives.append(label)
        else:
            raise AssertionError('accepted metadata mutation: ' + label)
    # Test only our new text parser, never a product class/Test/fixture.
    path = B / 'input/577_request_dispatch14_static_review.py'
    spec = importlib.util.spec_from_file_location('static_dispatch_review_definition_only', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    variants = 0
    for ref in cfg['sources']:
        text = (R / ref['path']).read_text()
        for width in (0, 3, 11):
            changed = re.sub(r'(?m)^\s+};$', ' ' * width + '};', text)
            for method in ('query', 'canonical'):
                assert module.branches(changed, method)[1] == module.branches(text, method)[1]
            variants += 1
    O.mkdir()
    out = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],
               producerManifest=dict(path=str((P / 'manifest.json').relative_to(R)),sha256=sha(P / 'manifest.json')),
               staticDesignCases=14,sourceFiles=2,scenarioCases=6,mediaCases=8,independentSsCanonicalTables=True,
               independentSourceDispatchParser=True,sourcePhysicalRoleChecks=role_checks,prior27SourceHashRoleChecked=True,
               metadataNegativeChecks=negatives,parserIndentVariants=variants,
               staticReviewStatus='STATIC_PT_DESIGN_REVIEW_COMPLETE',dynamicStatus='NOT_EXECUTED_HOLD',
               productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,
               sourceMutation=False,refusalRetry=False,ptExecutionExempt=False,measuredCoverage=None,
               newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,
               tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (O / 'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,staticDesignCases=14,metadataNegatives=len(negatives),parserVariants=variants,manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
