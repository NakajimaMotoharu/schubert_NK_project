"""55 fixed Log/Scenario Web view Test fixture literals, same-value constants only; no target execution."""
import difflib
import json
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10840-web-view-duplicate-plan-v1'
NAMES = {
    'reader':'READER_USERNAME','message':'LOG_MESSAGE_TEXT','search':'SEARCH_ACTION_TEXT','/search':'SEARCH_PATH',
    'page':'PAGE_KEY','log_type':'LOG_TYPE_FIELD_NAME','action':'ACTION_FIELD_NAME','level':'LEVEL_FIELD_NAME',
    'value':'VALUE_ATTRIBUTE','[name=q]':'QUERY_FIELD_SELECTOR','.pagination':'PAGINATION_SELECTOR','href':'HREF_ATTRIBUTE',
    'path':'PATH_FIELD_NAME','from':'FROM_FIELD_NAME','入力値を確認してください。':'INVALID_INPUT_MESSAGE',
    '本文<&>':'SCENARIO_BODY_TEXT','章<script>':'SCENARIO_CHAPTER_TITLE','input':'INPUT_SELECTOR',
    'csrf':'SYNTHETIC_CSRF_TEXT','.script-entry':'SCRIPT_ENTRY_SELECTOR','.script-entry > p':'SCRIPT_BODY_SELECTOR',
    'audio':'AUDIO_SELECTOR','game':'GAME_FIELD_NAME','speaker':'SPEAKER_FIELD_NAME','chapter':'CHAPTER_FIELD_NAME',
    'entry_type':'ENTRY_TYPE_FIELD_NAME','voice':'VOICE_FIELD_NAME','input[name=q]':'QUERY_INPUT_SELECTOR',
    'select[name=speaker] option':'SPEAKER_OPTIONS_SELECTOR','.result-body > p':'RESULT_BODY_SELECTOR','script':'SCRIPT_SELECTOR'}


def inputs():
    normal = data.read_checked(data.BASE/'PG10800-protocol-quality-six-compile-v1/manifest.json',
        'ee02e1c29144a78486897564d0840a86c90bfe96f6fd19f5f75af8fbe4d311b4')
    assert normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    index = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/manifest.json',
        '465c7c64bc75923d275436c72656ddc5b537f2c15982a71a0b4681a19ef03627')
    records = json.loads((data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes())
    assert len(records) == 9409 and index['actualExit'] == 0
    rows = [r for r in records if r['path'].startswith('src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/')
        and r['rule'] == 'AvoidDuplicateLiterals']
    assert len(rows) == 55
    table = {}
    for row in rows:
        path = row['path']
        before = (snapshot/path).read_text()
        assert data.sha(before.encode()) == row['inputSha256'] == normal['begin']['inputHashes'][path]
        match = re.fullmatch(r'The String literal "(.*)" appears ([0-9]+) times in this file; the first occurrence is on line [0-9]+',row['message'])
        assert match is not None
        value = json.loads('"'+match[1]+'"')
        assert value in NAMES
        rendered = {json.dumps(value,ensure_ascii=False),json.dumps(value,ensure_ascii=True)}
        # A Java source may contain non-JSON escapes elsewhere; do not decode those tokens.
        assert '"unrelated'+chr(92)+'s"' not in rendered
        found = [m for m in LEX.finditer(before) if m.group() in rendered]
        assert len(found) == int(match[2]) and before[:found[0].start()].count('\n')+1 == row['line']
        literal = found[0].group()
        assert all(m.group() == literal for m in found)
        name = NAMES[value]
        assert not any(m.group() == name for m in LEX.finditer(before))
        table.setdefault(path,[]).append(dict(id=row['id'],name=name,literal=literal,references=len(found)))
    assert sum(len(v) for v in table.values()) == 55
    return normal,snapshot,table


def transformed(before,stem,rows):
    names = {r['literal']:r['name'] for r in rows}
    result = before
    for match in reversed(list(LEX.finditer(before))):
        if match.group() in names:
            result = result[:match.start()]+names[match.group()]+result[match.end():]
    header = 'class '+stem+' {\n'
    assert result.count(header) == 1
    declarations = ''.join('  private static final String '+r['name']+' = '+r['literal']+';\n' for r in rows)
    return result.replace(header,header+declarations,1)


def emit():
    _,snapshot,table = inputs()
    patch = '*** Begin Patch\n'
    for path,rows in table.items():
        before = (snapshot/path).read_text()
        assert (data.ROOT/path).read_text() == before
        after = transformed(before,Path(path).stem,rows)
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'
        patch += '\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal,snapshot,table = inputs()
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes = []
    for path,rows in table.items():
        before,after = (snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert canonical(after) == canonical(transformed(before,Path(path).stem,rows))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=changes,constantsAdded=55,referencesReplaced=sum(r['references'] for rows in table.values() for r in rows),
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,
        independentInversePending=True,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
