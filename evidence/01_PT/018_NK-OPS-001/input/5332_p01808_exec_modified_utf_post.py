"""Independently confirm the decoder against Java's full UTF-16 code-unit range."""

from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import runpy
from struct import pack
import subprocess
from tempfile import TemporaryDirectory

EVIDENCE = Path('evidence/01_PT/018_NK-OPS-001/evidence')
WRITER_SAMPLE = """import java.io.DataOutputStream;

class AllModifiedUtfCodeUnits {
    public static void main(String[] args) throws Exception {
        var output = new DataOutputStream(System.out);
        for (int base = 0; base < 65536; base += 4096) {
            var values = new char[4096];
            for (int i = 0; i < values.length; i++) {
                values[i] = (char) (base + i);
            }
            output.writeUTF(new String(values));
        }
        output.flush();
    }
}
"""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def main():
    red = EVIDENCE / 'PG40256-p01808-exec-modified-utf-red-v1'
    green = EVIDENCE / 'PG40258-p01808-exec-modified-utf-green-v1'
    before = json.loads((red / 'manifest.json').read_bytes())
    after = json.loads((green / 'manifest.json').read_bytes())
    assert ref(red / 'manifest.json') == after['previous']
    assert sha(gzip.decompress(Path(before['rawLogArchive']['path']).read_bytes())) == before['outputSha256']
    assert before['vectorsFailed'] == 18 and after['vectorsPassed'] == 20
    tool = Path('tools/quality/jacoco_readonly_exec_subset.py')
    assert ref(tool) in after['files']
    writer = json.loads((red / 'writer-proof.json').read_bytes())
    assert sha((red / 'writer-proof.json').read_bytes()) == before['writerProofSha256']
    java = Path(writer['java']['path'])
    assert ref(java) == writer['java']
    with TemporaryDirectory(prefix='pg40260-codeunits-') as tmp:
        file = Path(tmp) / 'AllModifiedUtfCodeUnits.java'
        file.write_text(WRITER_SAMPLE)
        completed = subprocess.run([str(java), str(file)], capture_output=True, check=True, timeout=30)
    assert not completed.stderr
    output = completed.stdout
    decode = runpy.run_path(str(tool))['decode']
    header = bytes.fromhex('01c0c01007')
    times = pack('>qq', 17, 18)
    selected = bytes.fromhex('11 0000000000000001 0001 58 01 01')
    nonselected = bytes.fromhex('11 0000000000000002')
    offset = 0
    for base in range(0, 65536, 4096):
        length = int.from_bytes(output[offset:offset + 2], 'big')
        expected = sum(1 if 0 < value <= 127 else 2 if value <= 2047 else 3
                       for value in range(base, base + 4096))
        assert length == expected
        field = output[offset:offset + 2 + length]
        stream = header + b'\x10' + field + times + selected + nonselected + field + b'\x01\x00'
        assert decode(stream, {'X'}) == {
            'classes': {'X': {
                'crc64': '1', 'probeCount': 1, 'hitProbeIds': [0], 'missedProbeIds': [],
            }},
            'sessions': [{
                'labelBytesHex': field[2:].hex(), 'startMillis': 17, 'endMillis': 18,
            }],
            'totalClassRecords': 2,
        }
        offset += len(field)
    assert offset == len(output)
    folder = EVIDENCE / 'PG40260-p01808-exec-modified-utf-independent-v1'
    folder.mkdir()
    result = dict(actualExit=0, toolSource=after['source'], productionCoreMain=after['productionCoreMain'],
                  red=ref(red / 'manifest.json'), green=ref(green / 'manifest.json'), java=writer['java'],
                  verifier=ref(Path(__file__)), syntheticWriterSourceSha256=sha(WRITER_SAMPLE.encode()),
                  syntheticWriterOutputSha256=sha(output), encodingFields=16, totalJavaCodeUnits=65536,
                  fieldPositions=['session label', 'nonselected class name'],
                  targetClassCRC='1', firstUncorrectedNegativeFailures=18, selectedCorrectedMethods=4,
                  changedToolRegressionMethods=after['runs']['changed-tool-regression']['cases'],
                  nativeOperations=0, productTests=0, coverage=None, newFormalAcceptance=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = folder / 'manifest.json'
    with out.open('x') as dest:
        dest.write(json.dumps(result, indent=2) + '\n')
    print(ref(out))


if __name__ == '__main__':
    main()
