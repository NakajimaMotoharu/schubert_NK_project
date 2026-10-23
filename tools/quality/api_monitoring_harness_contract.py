"""API clone must retain every validated Batch harness semantic except literal role/artifact/resource routing."""
import xml.etree.ElementTree as ET

def verify_api_harness(before,after):
    expected=ET.fromstring(before);actual=ET.fromstring(after)
    expected.find('{*}artifactId').text='monitoring-api-jobs-pt'
    build=expected.find('{*}build')
    if build is None:raise ValueError('original validated build required')
    build.find('{*}sourceDirectory').text='${project.basedir}/../../../src/schubert-nk-api/src/main/java'
    build.find('{*}testSourceDirectory').text='${project.basedir}/../../../src/schubert-nk-api/src/test/java'
    resources=build.find('{*}testResources')
    if resources is None:raise ValueError('original explicit Batch fixture routing required')
    build.remove(resources)
    plugins=build.find('{*}plugins')
    compiler=next(p for p in plugins if p.findtext('{*}artifactId')=='maven-compiler-plugin')
    compiler.find('{*}configuration/{*}includes/{*}include').text='dev/codex/schubert/nk/api/monitoring/**/*.java'
    compiler.find('{*}configuration/{*}testIncludes/{*}testInclude').text='dev/codex/schubert/nk/api/monitoring/*Test.java'
    for root in (expected,actual):
        for node in root.iter():
            node.text=node.text.strip() if node.text and node.text.strip() else None
            node.tail=None
    if ET.tostring(expected)!=ET.tostring(actual):raise ValueError('all parent/compiler/ordinaryPT/four100/static semantics unchanged')
    return dict(originalArtifact='monitoring-component-pt',apiArtifact='monitoring-api-jobs-pt',
      sourceRoleChangedOnly=True,unusedFixtureResourceRoutingRemoved=True,allOtherSemanticBytesUnchanged=True,
      fourCountersMinimum='1.0',skipBypassAdded=False,exclusionsAdded=False)
