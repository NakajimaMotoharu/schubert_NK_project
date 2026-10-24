"""Bounded public Maven imported descriptor closure, never change the selected test runtime."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
import pg8240_prometheus_maven_coordinates as prep
from host_tool_invocation import capture, verify


def fields(path):
    data = path.read_bytes()
    if b'<!DOCTYPE' in data or b'<!ENTITY' in data:
        raise ValueError('descriptor DTD/entity rejected')
    doc = ET.fromstring(data)
    properties = {node.tag.split('}', 1)[-1]: node.text or '' for node in doc.findall('m:properties/*', prep.NS)}
    properties['project.version'] = doc.findtext('m:version', namespaces=prep.NS) or ''
    return doc, properties


def resolve(value, properties):
    for _ in range(5):
        keys = re.findall(r'\$\{([^}]+)\}', value)
        if not keys:
            return value
        for key in keys:
            if key not in properties:
                raise ValueError('unresolved imported BOM property')
            value = value.replace('${' + key + '}', properties[key])
    raise ValueError('cyclic imported descriptor property')


if __name__ == '__main__':
    invocation = capture(Path(__file__))
    prep.SLOT = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg8244-prometheus-descriptor-closure-v1')
    prep.OUT = prep.ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8244-prometheus-descriptor-closure-v1'
    prep.SLOT.mkdir(exist_ok=False)
    prep.OUT.mkdir(exist_ok=False)
    queue = [('io.opentelemetry.instrumentation', 'opentelemetry-instrumentation-bom-alpha', '2.28.1-alpha')]
    seen = set()
    rows = []
    edges = []
    while queue:
        coordinate = queue.pop(0)
        if coordinate in seen:
            continue
        if len(seen) >= 12:
            raise ValueError('bounded descriptor discovery exceeded; preserve and review')
        seen.add(coordinate)
        fetched = prep.parent(coordinate)
        rows.extend(fetched)
        for row in fetched:
            doc, properties = fields(Path(row['path']))
            for dependency in doc.findall('m:dependencyManagement/m:dependencies/m:dependency', prep.NS):
                if dependency.findtext('m:scope', namespaces=prep.NS) != 'import':
                    continue
                if dependency.findtext('m:type', namespaces=prep.NS) != 'pom':
                    raise ValueError('unexpected imported dependency type')
                child = tuple(resolve(dependency.findtext('m:' + name, namespaces=prep.NS) or '', properties) for name in ('groupId', 'artifactId', 'version'))
                edges.append(dict(parent=row['coordinate'], imported=child))
                queue.append(child)
    verify(invocation)
    terminals = list(prep.SLOT.glob('*.exit.safe.json'))
    assert len(terminals) == 2 * len(rows)
    value = dict(status='PUBLIC_IMPORTED_DESCRIPTOR_CLOSURE_PREPARED', entries=rows, importEdges=edges, publicArtifactDownloads=len(terminals), productionPT=0, targetActions=0, invocation=invocation, runtimeJunitUnchanged='5.13.4', note='BOMs resolve third-party model only; no parent project/plugin inheritance into NK')
    prep.save(prep.OUT / 'manifest.json', value)
    prep.save(prep.SLOT / 'manifest.json', value)
    print(json.dumps(dict(status=value['status'], coordinates=len(rows), manifestSha256=prep.sha(prep.OUT / 'manifest.json'))))
