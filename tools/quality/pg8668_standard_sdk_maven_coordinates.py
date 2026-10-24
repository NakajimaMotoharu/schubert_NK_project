"""Place only already checked SDK bytes in unused Maven coordinates; no download or overwrite."""
import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg8240_prometheus_maven_coordinates as prior
from host_tool_invocation import capture, verify

if __name__ == '__main__':
    invocation=capture(Path(__file__))
    slot=prior.SLOT.parent/'pg8668-standard-sdk-maven-coordinates-v1'
    out=prior.OUT.parent/'PG8668-standard-sdk-maven-coordinates-v1'
    assert not slot.exists() and not out.exists()
    manifest=prior.OUT.parent/'PG8170-prometheus-sdk-prepare-v1/manifest.json'
    assert prior.sha(manifest)=='371004a7bcadce5d398059e765ef8f3dc876a7ea004fced60ba8ceb05fad123a'
    sdk=json.loads(manifest.read_text())
    rows=[]
    for coordinate,item in sdk['downloaded'].items():
        group,artifact,version=coordinate.split(':')
        for kind in ('pom','jar'):
            source=Path(item[kind]['path'])
            assert prior.sha(source)==item[kind]['sha256']
            if kind=='pom':
                data=source.read_bytes()
                assert b'<!DOCTYPE' not in data and b'<!ENTITY' not in data
                parent=ET.fromstring(data).find('m:parent',prior.NS)
                if parent is not None:
                    values=[parent.findtext('m:'+key,namespaces=prior.NS) for key in ('groupId','artifactId','version')]
                    pg,pa,pv=values
                    assert (prior.M2/pg.replace('.','/')/pa/pv/(pa+'-'+pv+'.pom')).is_file()
            target=prior.M2/group.replace('.','/')/artifact/version/source.name
            rows.append(dict(coordinate=coordinate,kind=kind,preparedSha256=item[kind]['sha256'],**prior.place(source,target)))
    verify(invocation)
    slot.mkdir()
    out.mkdir()
    value=dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,preparedManifestSha256=prior.sha(manifest),entries=rows,publicDownloads=0,overwrites=0,productTests=0,targetInitialized=False,actualVmActions=0,actualNetworkActions=0)
    prior.save(slot/'manifest.json',value)
    prior.save(out/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,entries=len(rows),manifestSha256=prior.sha(out/'manifest.json'))))
