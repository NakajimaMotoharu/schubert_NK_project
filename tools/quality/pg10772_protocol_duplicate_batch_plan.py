"""59 fixed Protocol Test fixture literals, same-value constants only; no target execution."""
import difflib
import json
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10772-protocol-duplicate-batch-plan-v1'
NAMES = {
    'LGNRSP01':'LOGIN_RESPONSE_LAYOUT','Retry after秒':'RETRY_AFTER_FIELD','利用者message':'USER_MESSAGE_FIELD',
    'test':'IO_FAILURE_MESSAGE','audio/ogg':'AUDIO_OGG_MIME','video/mp4':'VIDEO_MP4_MIME','audio/mpeg':'AUDIO_MPEG_MIME',
    'media-1':'MEDIA_ID_TEXT','MUSIC':'MUSIC_KIND_TEXT','.ogg':'OGG_EXTENSION','.mp4':'MP4_EXTENSION',
    'music/':'MUSIC_DIRECTORY_PREFIX','stored':'STORED_LABEL','video/a.mp4':'VIDEO_RELATIVE_PATH','a.mp4':'VIDEO_FILE_NAME',
    'false':'FALSE_TEXT','LOGREQ01':'LOG_REQUEST_LAYOUT','GAMRSP01':'GAME_RESPONSE_LAYOUT',
    'LGNREQ01':'LOGIN_REQUEST_LAYOUT','DATA':'DATA_AREA_TEXT','Name':'FIELD_NAME_TEXT','rule':'FIELD_RULE_TEXT',
    'ABCREQ01':'CUSTOM_REQUEST_LAYOUT','ABCRSP01':'CUSTOM_RESPONSE_LAYOUT','name':'SAMPLE_FIELD_NAME',
    'SRCRSP01':'SCENARIO_SEARCH_RESPONSE_LAYOUT','Audio ID':'AUDIO_ID_FIELD','Audio display path':'AUDIO_DISPLAY_PATH_FIELD',
    'File byte長':'FILE_BYTE_LENGTH_FIELD','File record件数':'FILE_RECORD_COUNT_FIELD',
    'Entry sequence':'ENTRY_SEQUENCE_FIELD','Audio sequence':'AUDIO_SEQUENCE_FIELD','Username':'USERNAME_FIELD',
    'UCRREQ01':'USER_CREATE_REQUEST_LAYOUT','Initial Password':'INITIAL_PASSWORD_FIELD',
    'LGSREQ01':'LOG_SEARCH_REQUEST_LAYOUT','From日時':'FROM_TIME_FIELD','To日時':'TO_TIME_FIELD',
    'NTDRSP01':'NOTIFICATION_DETAIL_RESPONSE_LAYOUT','処理開始日時':'PROCESSING_STARTED_FIELD',
    '内部状態':'INTERNAL_STATE_FIELD','COMPLETED':'COMPLETED_STATE_TEXT','通知区分':'NOTIFICATION_KIND_FIELD',
    '質問削除済み':'QUESTION_DELETED_FIELD','質問本文':'QUESTION_TEXT_FIELD','回答本文':'ANSWER_TEXT_FIELD',
    '回答日時':'ANSWER_TIME_FIELD','受付ID':'RECEIPT_ID_FIELD','INVALID':'INVALID_TEXT',
    'value':'VALUE_FIELD_NAME','safe':'SAFE_TEXT','ERROR=ERROR':'ERROR_ENUM_TEXT',
    '9999-12-31T14:59:59.999Z':'MAXIMUM_INSTANT_TEXT','synthetic protocol':'PROTOCOL_FAILURE_MESSAGE'}


def inputs():
    normal = data.read_checked(data.BASE/'PG10756-protocol-semantic-six-compile-v1/manifest.json',
        '5273ae8b8a1bc9bb275793444b298801943eb5dba30f027be706913c7056fbc9')
    assert normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    index = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/manifest.json',
        '465c7c64bc75923d275436c72656ddc5b537f2c15982a71a0b4681a19ef03627')
    records = json.loads((data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes())
    assert len(records) == 9409 and index['actualExit'] == 0
    rows = [r for r in records if r['path'].startswith('src/schubert-nk-protocol/')
        and r['rule'] == 'AvoidDuplicateLiterals' and not r['path'].endswith('/SemanticFieldValueTest.java')]
    assert len(rows) == 59
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
    assert sum(len(v) for v in table.values()) == 59
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
        sourceChanges=changes,constantsAdded=59,referencesReplaced=sum(r['references'] for rows in table.values() for r in rows),
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,
        independentInversePending=True,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
