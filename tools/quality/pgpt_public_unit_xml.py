"""Publish owned JUnit evidence with bounded environment metadata; never edit the source."""
import hashlib
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

UNIT_ENV_PROPERTY_NAMES = frozenset({
    'os.name', 'os.arch', 'java.version', 'file.encoding', 'user.timezone',
})


def copy_public_evidence(source, destination):
    source = Path(source)
    destination = Path(destination)
    original = None
    if source.name.startswith('TEST-') and source.suffix == '.xml':
        content = source.read_bytes()
        original = hashlib.sha256(content).hexdigest()
        tree = ET.ElementTree(ET.fromstring(content))
        if tree.getroot().tag not in {'testsuite', 'testsuites'}:
            raise ValueError('owned standard JUnit XML required')
        for parent in tree.getroot().iter():
            for child in list(parent):
                if child.tag in {'system-out', 'system-err'}:
                    parent.remove(child)
                elif child.tag == 'properties':
                    pairs = [(p.get('name'), p.get('value')) for p in child
                             if p.tag == 'property' and p.get('name') in UNIT_ENV_PROPERTY_NAMES
                             and p.get('value') is not None]
                    child.clear()
                    for name, value in pairs:
                        ET.SubElement(child, 'property', {'name': name, 'value': value})
        with destination.open('xb') as output:
            tree.write(output, encoding='utf-8', xml_declaration=True)
    else:
        with source.open('rb') as content, destination.open('xb') as output:
            shutil.copyfileobj(content, output)
    return dict(sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                originalUnitXmlSha256=original)
