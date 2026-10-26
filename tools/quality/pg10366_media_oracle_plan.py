"""Prepare only UUID plumbing in three existing test sources; never execute them."""
import difflib
import re
import subprocess
from pathlib import Path
import g07_host_class_provenance_inputs as data

BEFORE = 'b120eebab4bbe1f8d02c245a06e51e0783a616c5'
BASE = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/media/'
NAMES = ('MediaReplayFixture.java','MediaStageFixture.java','MediaReplayServiceTest.java')
PATHS = tuple(BASE+n for n in NAMES)


def original(path):
    return subprocess.check_output(['git','show',BEFORE+':'+path],cwd=data.ROOT).decode()


def transformed(path, text):
    if path.endswith('MediaReplayFixture.java'):
        old = 'static byte[] wire(\n      String prefix,\n      MediaRequest request,'
        new = 'static byte[] wire(\n      String prefix,\n      UUID correlation,'
        assert text.count(old) == 1
        text = text.replace(old,new)
        old = 'put(body, 60, request.header().messageId().toString());'
        assert text.count(old) == 1
        return text.replace(old,'put(body, 60, correlation.toString());')
    if path.endswith('MediaStageFixture.java'):
        old = '            MediaRequest.decode(request),'
        assert text.count(old) == 1
        return text.replace(old,'            request.header().messageId(),')
    assert path.endswith('MediaReplayServiceTest.java')
    pattern = r'(\bwire\(\s*(?:prefix|"MED"),\s*)(request|current)(\s*,)'
    matches = re.findall(pattern,text)
    assert len(matches) == 10 and [r[1] for r in matches].count('current') == 1
    return re.sub(pattern,lambda m:m[1]+m[2]+'.header().messageId()'+m[3],text)


def emit():
    print('*** Begin Patch')
    for path in PATHS:
        before = original(path)
        assert (data.ROOT/path).read_text() == before
        after = transformed(path,before)
        diff = list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]
        assert diff
        print('*** Update File: '+str(data.ROOT/path))
        for line in diff:
            print('@@' if line.startswith('@@') else line)
    print('*** End Patch')


if __name__ == '__main__':
    emit()
