"""One identifier repair and closed independent meaning table for all54 Test constants."""
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from pg10130_uid_oracle_preflight import tokens

SOURCE = 'a82c44a678cce0ded7fda59cf84a2276ded51e30'
TARGET = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/AnimationControllerTest.java'
OLD = 'FIXTURE_WIRE_TIMESTAMP'
NEW = 'FIXTURE_MENU_TYPE_CODE'
OUT = data.BASE/'PG10504-anm-type-name-plan-v1'
SS = 'documents/300_SS/320_メッセージング/323_全電文layout・Java・DB対応表.md'


def meaning(name,literal,kind):
    value = json.loads(literal) if kind == 'String' else int(literal)
    exact = {
        'FIXTURE_MENU_TYPE_CODE': ('ANM','ANIMATION_MENU_PROTOCOL_PREFIX_THREE_BYTES'),
        'EXPECTED_ADMIN_ROLE': ('ADMIN','LITERAL_DISPLAY_ROLE'),
        'FIXTURE_SUCCESS_CODE': ('0000','FOUR_DIGIT_SUCCESS_RESULT'),
        'EXPECTED_SECOND_GAME_CODE': ('NUKITASHI2','SECOND_GAME_WIRE_CODE'),
        'FIXTURE_READER': ('reader','SYNTHETIC_ACTOR_NAME'),
        'FIXTURE_PUBLIC_CSRF': ('public-csrf','PUBLIC_SYNTHETIC_CSRF_INPUT'),
        'FIXTURE_BGM': ('BGM','DISPLAY_CATEGORY_LITERAL'),
        'FIXTURE_MAIN_SECTION': ('main','ANIMATION_LIST_SECTION'),
        'FIXTURE_HTTP_GET': ('GET','HTTP_METHOD'),
        'FIXTURE_FAILURE_MESSAGE': ('synthetic','SYNTHETIC_FAILURE_DIAGNOSTIC'),
        'FIXTURE_ESCAPED_TEXT': ('<b>&','ESCAPING_TEST_RAW_TEXT'),
        'FIXTURE_INVALID_INPUT': ('bad','SYNTHETIC_INVALID_FILTER'),
        'FIXTURE_THROW_MODE': (3,'SYNTHETIC_THROW_MODE'),
        'FIXTURE_CORRELATION_MISMATCH_MODE': (1,'SYNTHETIC_CORRELATION_MISMATCH_MODE')}
    if name in exact:
        expected,label = exact[name]
        if value != expected:
            raise ValueError('literal/meaning mismatch')
        return label
    if name.endswith('_PATH') and value in {'/animation','/animation/main','/animation/ova','/music','/search'}:
        return 'EXPLICIT_HTTP_ROUTE'
    if name.endswith('_VIEW') and value in {'animation','animation-list','music','music-sections','search'}:
        return 'EXPLICIT_TEMPLATE_VIEW_NAME'
    if name.endswith('_SELECTOR') and value in {'.menu-item strong','.menu-item','.subtitle','.animation-row'}:
        return 'EXPLICIT_DOM_SELECTOR'
    if name.endswith('_ATTRIBUTE') and value in {'page','href'}:
        return 'EXPLICIT_MODEL_KEY_OR_DOM_ATTRIBUTE'
    if name.endswith('_PREFIX') and value in {'MCT','SRC','GAM','SPK'}:
        return 'THREE_BYTE_PROTOCOL_PREFIX'
    if name == 'FIXTURE_CATEGORY_PREFIX' and value == 'cat':
        return 'SYNTHETIC_CATEGORY_NAME_SERIES_PREFIX'
    raise ValueError('unreviewed or misleading Test constant name')


def check(text,previous):
    current = tokens(text)
    if current.count(NEW) != 6 or OLD in current:
        raise ValueError('six exact renamed references required')
    if [OLD if t == NEW else t for t in current] != tokens(previous):
        raise ValueError('identifier-only change required')


def main():
    assert not OUT.exists() and len(OLD) == len(NEW) == 22
    literal_plan = data.read_checked(data.BASE/'PG10477-disjoint-six-literal-plan-v2-v1/manifest.json',
        'c5fecebd4b814e14e8f0d487e36ce062340da72f333085168f1f132e101fb5f5')
    normal = data.read_checked(data.BASE/'PG10480-disjoint-six-literal-compile-v1/manifest.json',
        '11ca97be3c74142b3acfcac9c2612c0dd9230be17a4d91c5140a2abc28fbb179')
    previous = (data.ROOT/TARGET).read_text()
    assert data.sha(previous.encode()) == normal['begin']['inputHashes'][TARGET]
    assert previous.count(OLD) == tokens(previous).count(OLD) == 6 and NEW not in tokens(previous)
    updated = previous.replace(OLD,NEW)
    check(updated,previous)
    assert previous.count('"20260920090000000"') == updated.count('"20260920090000000"') == 2
    approved = subprocess.check_output(['git','show','origin/main:'+SS],cwd=data.ROOT)
    assert approved == (data.ROOT/SS).read_bytes() and b'ANMREQ01' in approved and b'ANMRSP01' in approved
    rows = []
    for path,row in literal_plan['sourceChanges'].items():
        assert data.sha((data.ROOT/path).read_bytes()) == normal['begin']['inputHashes'][path]
        for name,constant in row['constants'].items():
            reviewed = NEW if name == OLD else name
            purpose = meaning(reviewed,constant['literal'],constant['type'])
            rows.append(dict(path=path,originalName=name,name=reviewed,type=constant['type'],
                literalSha256=data.sha(constant['literal'].encode()),purpose=purpose,renamed=name != reviewed))
    assert len(rows) == 54 and sum(r['renamed'] for r in rows) == 1
    negatives = []
    for label,name,value in [('old-timestamp-name',OLD,'"ANM"'),('wrong-prefix',NEW,'"ANL"'),
        ('timestamp-not-prefix',NEW,'"20260920090000000"')]:
        try:
            meaning(name,value,'String')
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('incorrect naming/value domain accepted')
    for label,damaged in [('old-identifier',updated.replace(NEW,OLD)),('wrong-literal',updated.replace('"ANM"','"ANL"'))]:
        try:
            check(damaged,previous)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('incorrect source change accepted')
    target = Path(normal['jars']['web']['path']).parent/'test-classes/dev/codex/schubert/nk/web/session/AnimationControllerTest.class'
    needle = b'\x01'+len(OLD).to_bytes(2,'big')+OLD.encode()
    assert target.read_bytes().count(needle) == 1
    OUT.mkdir()
    data.write(OUT/'meaning-review.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,baseSource=SOURCE,path=TARGET,
        beforeSha256=data.sha(previous.encode()),plannedSha256=data.sha(updated.encode()),oldName=OLD,newName=NEW,
        exactIdentifierOccurrences=6,literalValueUnchanged=True,allOtherTokensUnchanged=True,
        reviewedConstants=54,unchangedOtherConstantMeanings=53,approvedSs=SS,approvedSsSha256=data.sha(approved),
        meaningReviewSha256=data.sha((OUT/'meaning-review.json').read_bytes()),metadataNegativeVectors=negatives,
        beforeTestClassSha256=data.sha(target.read_bytes()),expectedClassDifference='ONE_EQUAL_LENGTH_UTF8_FIELD_NAME_ENTRY_ONLY',
        productTestsExecuted=0,originalControllerDynamicPtStatus='NOT_EXECUTED_HOLD',externalActions=0,
        bug='BUG-1837',ykt='YKT-1588',newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
