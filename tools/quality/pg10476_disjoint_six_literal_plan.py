"""Disjoint six-source49String/four fault-mode Test constants; existing public PMD binding and reversible tokens only."""
from pathlib import Path
import difflib
import json
import re
import sys
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from pg10130_uid_oracle_preflight import tokens
from pg10410_result_code_literal_plan import class_marker

OUT = data.BASE/'PG10476-disjoint-six-literal-plan-v1'
BASE_SOURCE = '73c18457afce837ecfc3687fc7aae84c04cca2c1'
NAMES = {'UserCommandServiceTest': ['EXPECTED_ADMIN_ROLE'], 'AnimationControllerTest': ['FIXTURE_MENU_PATH', 'FIXTURE_MAIN_PATH', 'FIXTURE_OVA_PATH', 'FIXTURE_SUCCESS_CODE', 'EXPECTED_MENU_VIEW', 'EXPECTED_LIST_VIEW', 'EXPECTED_PAGE_ATTRIBUTE', 'FIXTURE_MAIN_SECTION', 'FIXTURE_HTTP_GET', 'FIXTURE_FAILURE_MESSAGE', 'EXPECTED_HREF_ATTRIBUTE'], 'MusicControllerTest': ['FIXTURE_MENU_PATH', 'FIXTURE_SUCCESS_CODE', 'EXPECTED_SECTIONS_VIEW', 'EXPECTED_PAGE_ATTRIBUTE', 'FIXTURE_HTTP_GET', 'FIXTURE_FAILURE_MESSAGE', 'FIXTURE_CATEGORY_PREFIX', 'FIXTURE_ESCAPED_TEXT', 'EXPECTED_MENU_TITLE_SELECTOR', 'EXPECTED_MENU_ITEM_SELECTOR'], 'ScenarioSearchControllerTest': ['FIXTURE_SUCCESS_CODE', 'EXPECTED_SECOND_GAME_CODE', 'EXPECTED_PAGE_ATTRIBUTE', 'EXPECTED_SEARCH_VIEW', 'FIXTURE_SEARCH_PREFIX', 'FIXTURE_GAME_PREFIX', 'FIXTURE_SPEAKER_PREFIX', 'FIXTURE_INVALID_INPUT', 'FIXTURE_HTTP_GET', 'FIXTURE_SEARCH_PATH'], 'AnimationTemplateTest': ['FIXTURE_READER', 'EXPECTED_MENU_VIEW', 'FIXTURE_PUBLIC_CSRF', 'EXPECTED_HREF_ATTRIBUTE', 'EXPECTED_LIST_VIEW', 'EXPECTED_SUBTITLE_SELECTOR', 'EXPECTED_ANIMATION_ROW_SELECTOR'], 'MusicHierarchyTemplateTest': ['FIXTURE_READER', 'FIXTURE_BGM', 'EXPECTED_MENU_VIEW', 'FIXTURE_PUBLIC_CSRF', 'EXPECTED_SUBTITLE_SELECTOR', 'EXPECTED_MENU_TITLE_SELECTOR', 'EXPECTED_MENU_ITEM_SELECTOR', 'EXPECTED_HREF_ATTRIBUTE', 'EXPECTED_SECTIONS_VIEW', 'FIXTURE_CATEGORY_PREFIX']}


def restored(text, constants):
    result = tokens(text)
    for name, row in constants.items():
        literal, kind = row['literal'], row['type']
        declaration = tokens('private static final '+kind+' '+name+' = '+literal+';')
        starts = [i for i in range(len(result)) if result[i:i+len(declaration)] == declaration]
        if len(starts) != 1:
            raise ValueError('exact declaration required: '+name)
        i, = starts
        result[i:i+len(declaration)] = []
        result = [part for value in result for part in (tokens(literal) if value == name else [value])]
    return result


def plan():
    static = data.read_checked(data.BASE/'PG10394-role-literal-static-v1/manifest.json',
        '0b1be65fb8da3963f2565090880365c7091fecc39578ccc17b13dbbc25299f38')
    document = ET.parse(data.BASE/'PG10394-role-literal-static-v1/pmd.xml').getroot()
    changes = {}
    for cls, names in NAMES.items():
        path, = [p for p in static['sourceHashes'] if Path(p).stem == cls]
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == static['sourceHashes'][path]
        node, = [n for n in document if n.get('name') == str(data.ROOT/path)]
        findings = [n for n in node if n.get('rule') == 'AvoidDuplicateLiterals']
        assert len(findings) == len(names)
        constants = {}
        for finding, name in zip(findings, names):
            assert name not in tokens(text)
            literal, = [m.group() for m in LEX.finditer(text) if m.group().startswith('"') and
                text.count('\n',0,m.start())+1 == int(finding.get('beginline')) and
                m.start()-text.rfind('\n',0,m.start()) == int(finding.get('begincolumn'))]
            constants[name] = dict(literal=literal,type='String')
        reverse = {v['literal']:n for n,v in constants.items()}
        spans = [(m.start(),m.end(),reverse[m.group()]) for m in LEX.finditer(text) if m.group() in reverse]
        updated = text
        for low, high, value in reversed(spans):
            updated = updated[:low]+value+updated[high:]
        if cls in {'AnimationControllerTest','MusicControllerTest'}:
            for name,literal in [('FIXTURE_THROW_MODE','3'),('FIXTURE_CORRELATION_MISMATCH_MODE','1')]:
                before = 'if (kind == '+literal+')'
                assert updated.count(before) == 1 and name not in tokens(updated)
                updated = updated.replace(before,'if (kind == '+name+')')
                constants[name] = dict(literal=literal,type='int')
        marker = class_marker(updated, cls)
        declarations = ''.join('  private static final '+v['type']+' '+n+' = '+v['literal']+';\n' for n,v in constants.items())
        updated = updated.replace(marker,marker+'\n'+declarations,1)
        assert restored(updated, constants) == tokens(text)
        changes[path] = dict(beforeSha256=data.sha(text.encode()),plannedSha256=data.sha(updated.encode()),
            constants=constants,literalReferenceCount=len(spans),before=text,after=updated)
    assert sum(len(v['constants']) for v in changes.values()) == 53
    return changes


def main():
    assert not OUT.exists()
    changes = plan()
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,baseSource=BASE_SOURCE,
        sourceChanges={p:{k:v for k,v in row.items() if k not in ('before','after')} for p,row in changes.items()},
        exactTokenRestorationBeforeFormatting=True,constantCount=53,productTestsExecuted=0,externalActions=0,
        bug='BUG-1834',ykt='YKT-1585',newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    value = json.loads((OUT/'manifest.json').read_bytes())
    changes = plan()
    assert value['sourceChanges'] == {p:{k:v for k,v in r.items() if k not in ('before','after')} for p,r in changes.items()}
    patch = '*** Begin Patch\n'
    for p, row in changes.items():
        change = ''.join(list(difflib.unified_diff(row['before'].splitlines(True),row['after'].splitlines(True)))[2:])
        change = re.sub(r'^@@.*@@\s*$', '@@',change,flags=re.M)
        patch += '*** Update File: '+str(data.ROOT/p)+'\n'+change
    return patch+'*** End Patch\n'


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
