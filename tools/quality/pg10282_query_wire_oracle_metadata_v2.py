"""Independent UI236 sequential fields vs Test-only JDK helper. Never run original PT."""
from pathlib import Path
import itertools
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10282-query-wire-oracle-metadata-v2'
OUT = data.BASE/'PG10282-query-wire-oracle-metadata-v2'
ORACLE = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionQueryWireOracle.java'


def field(width, value=''):
    raw = str(value).encode('ascii')
    assert len(raw) <= width
    return raw.ljust(width,b' ')


def expected(layout, code, count):
    # Sequential UI table widths, not Java helper offsets or a production encoder.
    good = code in ('0000','0200')
    profiles = {'QSSREQ01':('QSSRSP01',48,672), 'NTSREQ01':('NTSRSP01',48,624),
        'QSDREQ01':('QSDRSP01',8352,0), 'NTDREQ01':('NTDRSP01',8896,0)}
    reply,size,width = profiles[layout]
    stamp = '20261001090000123'
    if size == 48:
        body = (b'000001050'+f'{count:09d}000001{(1 if count else 0):09d}{count:09d}'.encode()+field(6)
            if good else b'0'*42+field(6))
        records = count if good else 0
        if records:
            if layout == 'QSSREQ01':
                record = b''.join([field(12,'9'*12),field(26,'0'*26),field(64,'u1'),
                    field(512,'question'),field(12,'UNANSWERED'),field(17,stamp),field(17),field(12)])
            else:
                record = b''.join([field(12,'9'*12),field(26,'0'*26),field(12,'ACCEPTED'),
                    field(12,'RECEIVED'),field(17,stamp),field(17,stamp),field(512,'question'),field(1,'0'),field(15)])
            assert len(record) == width
            body += record
    elif layout == 'QSDREQ01':
        records = 0
        body = b''.join([field(12,'9'*12 if good else '0'*12),field(26,'0'*26 if good else ''),
            field(64,'u1' if good else ''),field(12,'UNANSWERED' if good else ''),
            field(4096,'question' if good else ''),field(4096),field(17,stamp if good else '0'*17),
            field(17),field(12)])
    else:
        records = 0
        body = b''.join([field(12,'9'*12 if good else '0'*12),field(26,'0'*26 if good else ''),
            field(12,'ACCEPTED' if good else ''),field(12,'RECEIVED' if good else ''),
            field(17,stamp if good else '0'*17),field(17),field(17),field(17),field(17),
            field(1,'0' if good else ''),field(4096,'question' if good else ''),field(4096),
            field(16),field(512),field(12,'9'*12 if good else ''),field(16)])
    assert len(body) == size + records*width
    header = b''.join([b'SCHBNK01001',reply.encode(),b'001SS',
        b'00000000-0000-0065-0000-000000000065',b'00000000-0000-0064-0000-000000000064',
        b'20261001090001123',b'b'*64,f'0256{size:06d}{width:06d}{records:06d}{256+len(body):09d}'.encode(),
        code.encode(),field(44)])
    assert len(header) == 256
    return header+body


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    paths = [ORACLE,'tools/quality/architecture/QuestionQueryWireOracleMetadata.java']
    hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    text = (data.ROOT/ORACLE).read_text()
    assert 'import dev.codex.' not in text and 'QuestionQueryRequest' not in text
    assert all(forbidden not in text for forbidden in ('Class.forName','java.sql','javax.crypto','ProcessBuilder'))
    SLOT.mkdir(mode=0o700)
    reader = SLOT/'reader'
    reader.mkdir()
    cases = []
    for layout,code,count in itertools.product(('QSSREQ01','QSDREQ01','NTSREQ01','NTDREQ01'),('0000','0200','0104'),(0,1)):
        raw = expected(layout,code,count)
        cases.append(dict(layout=layout,code=code,count=count,length=len(raw),sha256=data.sha(raw)))
    vector = SLOT/'vectors.tsv'
    with vector.open('x') as stream:
        stream.write(''.join('\t'.join(str(r[k]) for k in ('layout','code','count','length','sha256'))+'\n' for r in cases))
    tc = data.ROOT.parent/'toolchain/jdk-25.0.4/bin'
    steps.SLOT = SLOT
    stages = [steps.step('compile-oracle-metadata',[str(tc/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-d',str(reader),*[str(data.ROOT/p) for p in paths]])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('check-independent-vectors',[str(tc/'java'),'-cp',str(reader),
        'dev.codex.schubert.nk.api.application.question.QuestionQueryWireOracleMetadata',str(vector)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    assert (SLOT/'check-independent-vectors.stdout').read_text().strip() == 'METADATA\t24\t5\tfresh-array\tPRODUCT_PT=0'
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    verify(invocation)
    OUT.mkdir()
    (OUT/'vectors.tsv').write_bytes(vector.read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,qualification='DECLARED_TEST_HELPER_METADATA_NOT_PRODUCT_PT',
        sourceHashes=hashes,invocation=invocation,stages=stages,vectors=cases,
        vectorSha256=data.sha(vector.read_bytes()),metadataVectors=24,metadataNegativeVectors=5,
        mutationIsolationChecked=True,classpath=str(reader),productionClassesAvailable=False,
        originalProductTestsExecuted=0,coverageMeasured=False,externalActions=0,newAccepted=0,
        formalUpdated=False,effortPercent=None,bug='BUG-1811',ykt='YKT-1562'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
