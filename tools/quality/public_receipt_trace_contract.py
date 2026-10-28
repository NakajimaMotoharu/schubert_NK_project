"""One reviewed immutable public Test writes one fixed vector into its fresh owned CWD only."""
import hashlib
import re

TEST_PATH = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionReceiptIdTest.java'
TEST_SHA = '95ecae1fb73ba439d3150b37083f087fde857f49dfa7a1c0e67f5bf4ac69e1c3'
FILE = 'target/question-receipt-traces/PT-QST-RID008.txt'
EXPECTED = (b'forward=0123456789ABCDEFGHJKMNPQRS\n'
    b'reverse=ZYXWVTSRQPNMKJHGFEDCBA9876\nlength=26\nalphabetSize=32\n'
    b'randomDrawsPerId=26\nownerOrTimeInput=false\n')

def reviewed(path,text):
    if path != TEST_PATH or hashlib.sha256(text.encode()).hexdigest() != TEST_SHA:
        return False
    imports = set(re.findall(r'^import\s+(java\.nio\.file\.[^;]+);',text,re.MULTILINE))
    return (imports == {'java.nio.file.Files','java.nio.file.Path'}
        and text.count('Files.createDirectories(directory)') == 1
        and text.count('Files.writeString(') == 1
        and text.count('Path.of("target/question-receipt-traces")') == 1
        and text.count('directory.resolve("PT-QST-RID008.txt")') == 1)

def check(cwd):
    entries = list(cwd.rglob('*'))
    assert not any(p.is_symlink() for p in entries)
    dirs = sorted(str(p.relative_to(cwd)) for p in entries if p.is_dir())
    files = sorted(str(p.relative_to(cwd)) for p in entries if p.is_file())
    assert dirs == ['target','target/question-receipt-traces'] and files == [FILE]
    actual = (cwd/FILE).read_bytes(); assert actual == EXPECTED
    return dict(path=FILE,sha256=hashlib.sha256(actual).hexdigest(),length=len(actual),directories=dirs,
        observedOwnedCwdFiles=1,wholeHostFilesystemAuditPerformed=False,rawRandomCandidateSaved=False,
        testId='PT-QST-RID008',classification='FIXED_PUBLIC_NON_AUTHORIZATION_VECTOR_ONLY')
