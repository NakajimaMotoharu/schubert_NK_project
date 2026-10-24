"""SS311/411 limited bootstrap and distinct app exposition owners, metadata only."""
import re
import xml.etree.ElementTree as ET

NS = {'m': 'http://maven.apache.org/POM/4.0.0'}


def require(value, message):
    if not value:
        raise ValueError(message)


def pom(data):
    require(b'<!DOCTYPE' not in data and b'<!ENTITY' not in data, 'no POM DTD/entity')
    root = ET.fromstring(data)
    return dict(artifact=root.findtext('m:artifactId', namespaces=NS),
                dependencies=[tuple(node.findtext('m:' + key, namespaces=NS) or '' for key in ('groupId', 'artifactId', 'version')) + (node.findtext('m:scope', namespaces=NS) or 'compile',) for node in root.findall('m:dependencies/m:dependency', NS)])


def java(data):
    package = re.findall(r'^package ([A-Za-z0-9_.]+);$', data, re.M)
    types = re.findall(r'^public final class ([A-Za-z0-9_]+)', data, re.M)
    require(len(package) == len(types) == 1, 'one canonical app package/public final class')
    return dict(package=package[0], type=types[0], imports=re.findall(r'^import ([A-Za-z0-9_.]+);$', data, re.M))


def validate(model):
    require(set(model) == {'bootstrap', 'api', 'web'}, 'three exact module responsibility inputs')
    shared = model['bootstrap']
    require(shared['artifact'] == 'schubert-nk-bootstrap', 'exact limited shared artifact')
    require(not any(group.startswith(('io.prometheus', 'io.micrometer')) for group, _, _, _ in shared['dependencies']), 'no new bootstrap metric SDK responsibility')
    require(not shared['metricJavaImports'] and not shared['legacyMonitoringPaths'], 'no bootstrap metric source or package remains')
    for role, name, sdk_type in (('api', 'ApiDurationMetricExporter', 'DistributionSummary'),
                                  ('web', 'WebDurationMetricExporter', 'Timer')):
        app = model[role]
        require(app['artifact'] == 'schubert-nk-' + role, 'exact app artifact owner')
        required = ('io.prometheus', 'prometheus-metrics-exposition-textformats', '1.7.0', 'compile')
        require(app['dependencies'].count(required) == 1, 'one exact approved app SDK coordinate')
        other = 'schubert-nk-web' if role == 'api' else 'schubert-nk-api'
        edges = [entry for entry in app['dependencies'] if entry[:2] == ('dev.codex.schubert', other)]
        expected = [('dev.codex.schubert', 'schubert-nk-api', '${project.version}', 'test')] if role == 'web' else []
        require(edges == expected, 'no production app cross dependency; preserve only exact existing PT-IDEM-016 test edge')
        source = app['java']
        require(source['package'] == 'dev.codex.schubert.nk.' + role + '.monitoring' and source['type'] == name, 'fixed application-local exposition owner')
        require('io.micrometer.core.instrument.' + sdk_type in source['imports'], 'correct application observation type/unit boundary')
        forbidden = 'Timer' if role == 'api' else 'DistributionSummary'
        require('io.micrometer.core.instrument.' + forbidden not in source['imports'], 'no generic shared application type mode')
        require(not any(value.startswith('dev.codex.schubert.nk.' + ('web' if role == 'api' else 'api') + '.') or value.startswith('dev.codex.schubert.nk.bootstrap.monitoring.') for value in source['imports']), 'no forbidden application/shared-monitoring imports')
