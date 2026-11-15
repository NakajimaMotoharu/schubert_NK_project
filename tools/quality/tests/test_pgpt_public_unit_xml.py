"""BUG3086/YKT2558: public synthetic XML only; these tool checks never qualify product PT."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from pgpt_public_unit_xml import copy_public_evidence


class PublicUnitXmlTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)

    def source(self, body, name='TEST-public.xml'):
        path = self.root / name
        path.write_text(body)
        return path

    def test_only_five_independent_property_names_survive(self):
        source = self.source('''<testsuite tests="1" time="0.125"><properties>
          <property name="os.name" value="Linux"/><property name="os.arch" value="amd64"/>
          <property name="java.version" value="25.0.4"/><property name="file.encoding" value="UTF-8"/>
          <property name="user.timezone" value="Asia/Tokyo"/>
          <property name="public.unissued.marker" value="REMOVED_PUBLIC_FIXTURE"/>
          </properties><testcase classname="Public" name="value()" time="0.125"/></testsuite>''')
        destination = self.root / 'published.xml'
        result = copy_public_evidence(source, destination)
        actual = {p.get('name'): p.get('value') for p in ET.parse(destination).findall('./properties/property')}
        self.assertEqual({'os.name': 'Linux', 'os.arch': 'amd64', 'java.version': '25.0.4',
                          'file.encoding': 'UTF-8', 'user.timezone': 'Asia/Tokyo'}, actual)
        self.assertNotIn('REMOVED_PUBLIC_FIXTURE', destination.read_text())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), result['originalUnitXmlSha256'])
        self.assertEqual(hashlib.sha256(destination.read_bytes()).hexdigest(), result['sha256'])

    def test_failure_error_skipped_case_identity_and_time_are_preserved(self):
        source = self.source('''<testsuite tests="3" failures="1" errors="1" skipped="1" time="1.25">
          <testcase classname="Public" name="failure()" time="0.5"><failure message="public failure"/></testcase>
          <testcase classname="Public" name="error()" time="0.5"><error message="public error"/></testcase>
          <testcase classname="Public" name="skip()" time="0.25"><skipped/></testcase></testsuite>''')
        destination = self.root / 'published.xml'
        copy_public_evidence(source, destination)
        before = ET.parse(source).getroot()
        after = ET.parse(destination).getroot()
        self.assertEqual(before.attrib, after.attrib)
        self.assertEqual([ET.tostring(c) for c in before.findall('testcase')],
                         [ET.tostring(c) for c in after.findall('testcase')])

    def test_nested_system_output_and_unneeded_property_attributes_are_removed(self):
        source = self.source('''<testsuites><system-out>REMOVED_PUBLIC_FIXTURE</system-out><testsuite>
          <properties extra="REMOVED_PUBLIC_FIXTURE">REMOVED_PUBLIC_FIXTURE
          <property name="java.version" value="25" extra="REMOVED_PUBLIC_FIXTURE">REMOVED_PUBLIC_FIXTURE</property>
          <property name="user.timezone"/><property name="unknown" value="REMOVED_PUBLIC_FIXTURE"/></properties>
          <testcase name="保持"><system-err>REMOVED_PUBLIC_FIXTURE</system-err></testcase>
          <system-out>REMOVED_PUBLIC_FIXTURE</system-out></testsuite></testsuites>''')
        destination = self.root / 'published.xml'
        copy_public_evidence(source, destination)
        tree = ET.parse(destination)
        self.assertEqual([], tree.findall('.//system-out'))
        self.assertEqual([], tree.findall('.//system-err'))
        self.assertEqual([{'name': 'java.version', 'value': '25'}],
                         [n.attrib for n in tree.findall('.//property')])
        self.assertEqual('保持', tree.find('.//testcase').get('name'))
        self.assertNotIn('REMOVED_PUBLIC_FIXTURE', destination.read_text())

    def test_original_bytes_stay_unchanged_and_public_output_is_deterministic(self):
        source = self.source('<testsuite><properties><property name="unknown" value="public"/></properties></testsuite>')
        original = source.read_bytes()
        first = self.root / 'first.xml'
        second = self.root / 'second.xml'
        self.assertEqual(copy_public_evidence(source, first), copy_public_evidence(source, second))
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(original, source.read_bytes())

    def test_non_junit_coverage_and_log_bytes_remain_exact(self):
        for name, data in [('coverage.xml', b'<report>\n  <counter missed="1"/>\n</report>\n'),
                           ('summary.stdout', b'public summary\n\xff\x00')]:
            with self.subTest(name=name):
                source = self.root / name
                source.write_bytes(data)
                destination = self.root / ('published-' + name)
                result = copy_public_evidence(source, destination)
                self.assertEqual(data, source.read_bytes())
                self.assertEqual(data, destination.read_bytes())
                self.assertIsNone(result['originalUnitXmlSha256'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), result['sha256'])

    def test_malformed_xml_fails_before_output_creation(self):
        source = self.source('<testsuite>')
        destination = self.root / 'published.xml'
        with self.assertRaises(ET.ParseError):
            copy_public_evidence(source, destination)
        self.assertFalse(destination.exists())
        self.assertEqual(b'<testsuite>', source.read_bytes())

    def test_non_junit_root_fails_before_output_creation(self):
        source = self.source('<report/>')
        destination = self.root / 'published.xml'
        with self.assertRaises(ValueError):
            copy_public_evidence(source, destination)
        self.assertFalse(destination.exists())

    def test_existing_public_artifact_is_never_overwritten(self):
        for name, data in [('TEST-existing.xml', b'<testsuite/>'), ('plain.stdout', b'new public')]:
            with self.subTest(name=name):
                source = self.root / name
                source.write_bytes(data)
                destination = self.root / ('published-' + name)
                destination.write_bytes(b'existing public evidence')
                with self.assertRaises(FileExistsError):
                    copy_public_evidence(source, destination)
                self.assertEqual(b'existing public evidence', destination.read_bytes())

    def test_common_profile_pins_the_current_public_exporter_bytes(self):
        from pgpt_closed_host_profile import R, tool_hashes
        name = 'tools/quality/pgpt_public_unit_xml.py'
        self.assertEqual(hashlib.sha256((R / name).read_bytes()).hexdigest(),
                         tool_hashes()[name])


if __name__ == '__main__':
    unittest.main()
