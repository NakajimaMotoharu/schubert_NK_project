"""Missing public parent only; all existing prepared SDK pins/parents preflight before placement."""
import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg8240_prometheus_maven_coordinates as prior
from host_tool_invocation import capture, verify

if __name__ == '__main__':
    invocation=capture(Path(__file__))
    slot=prior.SLOT.parent/'pg8669-standard-sdk-parent-coordinates-v1'
    out=prior.OUT.parent/'PG8669-standard-sdk-parent-coordinates-v1'
    assert not slot.exists() and not out.exists()
    source=prior.OUT.parent/'PG8170-prometheus-sdk-prepare-v1/manifest.json'
    assert prior.sha(source)=='371004a7bcadce5d398059e765ef8f3dc876a7ea004fced60ba8ceb05fad123a'
    sdk=json.loads(source.read_text())
    prepared=[]
    parents=set()
    for coordinate,item in sdk['downloaded'].items():
        group,artifact,version=coordinate.split(':')
        for kind in ('pom','jar'):
            path=Path(item[kind]['path'])
            assert prior.sha(path)==item[kind]['sha256']
            prepared.append((coordinate,path,prior.M2/group.replace('.','/')/artifact/version/path.name))
            if kind=='pom':
                data=path.read_bytes()
                assert b'<!DOCTYPE' not in data and b'<!ENTITY' not in data
                parent=ET.fromstring(data).find('m:parent',prior.NS)
                if parent is not None:
                    parents.add(tuple(parent.findtext('m:'+key,namespaces=prior.NS) for key in ('groupId','artifactId','version')))
    assert parents=={('io.prometheus','client_java','1.7.0'),('io.prometheus','prometheus-metrics-tracer','1.7.0')}
    before=[]
    for coordinate,path,target in prepared:
        if target.exists():
            assert not target.is_symlink() and prior.sha(target)==prior.sha(path)
            before.append(dict(path=str(target),sha256=prior.sha(target)))
    slot.mkdir()
    prior.SLOT=slot
    parent_rows=prior.parent(('io.prometheus','prometheus-metrics-tracer','1.7.0'))
    for group,artifact,version in parents:
        assert (prior.M2/group.replace('.','/')/artifact/version/(artifact+'-'+version+'.pom')).is_file()
    rows=[dict(coordinate=coordinate,**prior.place(path,target)) for coordinate,path,target in prepared]
    assert all(prior.sha(Path(row['path']))==row['sha256'] for row in before)
    verify(invocation)
    out.mkdir()
    value=dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,preparedManifestSha256=prior.sha(source),entries=rows,parentEntries=parent_rows,preservedBefore=before,publicParentDownloads=len(list(slot.glob('*.exit.safe.json'))),sdkDownloads=0,overwrites=0,productTests=0,targetInitialized=False,actualVmActions=0,targetNetworkOperations=0)
    prior.save(slot/'manifest.json',value)
    prior.save(out/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,entries=len(rows),manifestSha256=prior.sha(out/'manifest.json'))))
