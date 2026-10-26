"""UI236 sequential field vectors vs JDK-only Test helper; original PT is not run."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify
from pg10278_query_wire_oracle_metadata import field

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10316-user-query-oracle-metadata-v1'
OUT = data.BASE/'PG10316-user-query-oracle-metadata-v1'
ORACLE = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserQueryWireOracle.java'


def expected(layout,code,count,total,page,target,optional,page_count,first,last):
    good = code in ('0000','0200')
    stamp = '20261001090000123'
    rows = count if good else 0
    if layout == 'USRREQ01':
        reply,size,width = 'USRRSP01',48,168
        body = (b''.join([field(6,f'{page:06d}'),b'050',field(9,f'{total:09d}'),
            field(6,f'{page_count:06d}'),field(9,f'{first:09d}'),field(9,f'{last:09d}'),field(6)])
            if good else b'0'*42+field(6))
        for n in range(1,rows+1):
            record = b''.join([field(12,f'{n:012d}'),field(64,'u'+str(n)),field(5,'USER'),
                field(8,'ACTIVE'),field(17),field(17),field(17,stamp),field(17,stamp),b'000000000',field(2)])
            assert len(record) == 168
            body += record
    else:
        assert layout == 'UDTREQ01' and count == 0
        reply,size,width = 'UDTRSP01',320,0
        body = b''.join([field(12,f'{target:012d}' if good else '0'*12),
            field(64,'u'+str(target) if good else ''),field(5,'USER' if good else ''),field(8,'ACTIVE' if good else ''),
            field(17,stamp if good and optional else ''),field(17,stamp if good and optional else ''),
            field(17,stamp if good else '0'*17),field(17,stamp if good else '0'*17),field(17,stamp if good else '0'*17),
            b'002' if good and optional else b'000',b'000000000',field(64,'SYSTEM' if good else ''),
            field(64,'SYSTEM' if good else ''),field(6)])
    assert len(body) == size+width*rows
    header = b''.join([b'SCHBNK01001',reply.encode(),b'001SS',
        b'00000000-0000-0065-0000-000000000065',b'00000000-0000-0064-0000-000000000064',
        b'20261001090001123',b'b'*64,f'0256{size:06d}{width:06d}{rows:06d}{256+len(body):09d}'.encode(),code.encode(),field(44)])
    assert len(header) == 256
    return header+body


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    paths = [ORACLE,'tools/quality/architecture/UserQueryWireOracleMetadata.java']
    hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    text = (data.ROOT/ORACLE).read_text()
    assert not any(v in text for v in ('import dev.codex.','UserQueryRequest','java.sql','javax.crypto','Class.forName','ProcessBuilder'))
    # Expected paging values are explicit mathematical examples, not the Java formula.
    scenarios = [('USRREQ01',0,0,1,0,False,1,0,0),('USRREQ01',1,1,1,0,False,1,1,1),
        ('USRREQ01',50,50,1,0,False,1,1,50),('USRREQ01',1,51,2,0,False,2,51,51),
        ('USRREQ01',50,49999950,999999,0,False,999999,49999901,49999950)]
    scenarios += [('UDTREQ01',0,0,0,target,optional,0,0,0)
        for target in (1,999999999999) for optional in (False,True)]
    cases = []
    for layout,count,total,page,target,optional,pages,first,last in scenarios:
        for code in ('0000','0200','0104'):
            raw = expected(layout,code,count,total,page,target,optional,pages,first,last)
            cases.append(dict(layout=layout,code=code,count=count,total=total,page=page,target=target,optional=optional,
                length=len(raw),sha256=data.sha(raw)))
    assert len(cases) == 27
    SLOT.mkdir(mode=0o700)
    reader = SLOT/'reader'
    reader.mkdir()
    vector = SLOT/'vectors.tsv'
    with vector.open('x') as stream:
        stream.write(''.join('\t'.join(str(r[k]).lower() if type(r[k]) is bool else str(r[k])
            for k in ('layout','code','count','total','page','target','optional','length','sha256'))+'\n' for r in cases))
    jdk = data.ROOT.parent/'toolchain/jdk-25.0.4/bin'
    steps.SLOT = SLOT
    stages = [steps.step('compile-oracle-metadata',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-d',str(reader),*[str(data.ROOT/p) for p in paths]])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('check-independent-vectors',[str(jdk/'java'),'-cp',str(reader),
        'dev.codex.schubert.nk.api.application.admin.UserQueryWireOracleMetadata',str(vector)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    assert (SLOT/'check-independent-vectors.stdout').read_text().strip() == 'METADATA\t27\t3\tfresh-array\tPRODUCT_PT=0'
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    verify(invocation)
    OUT.mkdir()
    (OUT/'vectors.tsv').write_bytes(vector.read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=None,qualification='DECLARED_TEST_HELPER_METADATA_NOT_PRODUCT_PT',
        sourceHashes=hashes,invocation=invocation,stages=stages,vectors=cases,vectorSha256=data.sha(vector.read_bytes()),
        metadataVectors=27,metadataNegativeVectors=3,mutationIsolationChecked=True,classpath=str(reader),
        productionClassesAvailable=False,originalProductTestsExecuted=0,coverageMeasured=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None,bug='BUG-1814',ykt='YKT-1565'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
