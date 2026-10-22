import unittest
import xml.etree.ElementTree as ET
import pg6926_db_fixture_red_original as p


class DbFixtureOriginalFailureTest(unittest.TestCase):
    def test_production_corpus_not_characterization_or_tests(self):
        good = 'src/schubert-nk-api/src/main/java/Public.java'
        rows = {good: 'good', 'program/characterization/src/main/java/Public.java': 'harness',
                'other/src/schubert-nk-api/src/main/java/Public.java': 'other',
                'src/schubert-nk-api/src/test/java/Public.java': 'test'}
        self.assertEqual({good: 'good'}, p.production_main(rows))

    def xml(self):
        root = ET.Element('testsuite', name='PublicFixtureTest')
        bad = ET.SubElement(root, 'testcase', name=p.METHOD)
        ET.SubElement(bad, 'failure', type='org.opentest4j.AssertionFailedError', message=p.MESSAGE)
        ET.SubElement(root, 'testcase', name='normal')
        ET.SubElement(root, 'testcase', name='configuration')
        ET.SubElement(root, 'system-out').text = 'PT-DBFIX-1633-A02 ownedResidualStop=true\n'
        return root

    def test_only_exact_leak_and_completed_owned_stop_are_counterexample(self):
        self.assertTrue(p.inspect_failure(self.xml(), 'PublicFixtureTest', 'PT-DBFIX-1633-A02')['fixtureOnlyResidualStopConfirmed'])
        for attr, bad in (('type', 'java.sql.SQLException'), ('message', 'cleanup or wrong oracle')):
            xml = self.xml()
            xml.find('testcase/failure').set(attr, bad)
            with self.assertRaises(ValueError):
                p.inspect_failure(xml, 'PublicFixtureTest', 'PT-DBFIX-1633-A02')
        for text in ('', 'PT-DBFIX-1633-A02 ownedResidualStop=false\n'):
            xml = self.xml()
            xml.find('system-out').text = text
            with self.assertRaises(ValueError):
                p.inspect_failure(xml, 'PublicFixtureTest', 'PT-DBFIX-1633-A02')


if __name__ == '__main__':
    unittest.main()
