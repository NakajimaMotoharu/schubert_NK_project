import inspect
import unittest
from pyflakes.api import checkPath
import pg5566_private_monitor_selected as entry


class SelectedMonitor(unittest.TestCase):
    def test_extra_nested_debug_bytes_are_retained_not_silently_ignored(self):
        required={k:'a'*64 for k in entry.EXPECTED_CHANGES}
        sibling='batch:dev/codex/schubert/nk/batch/platform/BackupUnitStartClient$Policy.class'
        required[sibling]='a'*64
        after={k:'b'*64 for k in required}
        changed,okay,pending=entry.physical_delta(required,after,'green')
        self.assertTrue(okay);self.assertEqual(len(changed),7);self.assertEqual(pending,[sibling])
        self.assertFalse(entry.physical_delta(required,required,'green')[1])
        self.assertFalse(entry.physical_delta(required,after,'red')[1])
        bad={**required,'api:unexpected.class':'a'*64};wrong={**after,'api:unexpected.class':'b'*64}
        self.assertFalse(entry.physical_delta(bad,wrong,'green')[1])
        with self.assertRaises(ValueError):entry.physical_delta(required,{},'green')

    def test_exact_source_inventory_all_affected_and_dependencies(self):
        red=entry.inventory(entry.ROOT,'red');green=entry.inventory(entry.ROOT,'green')
        self.assertEqual(sum(map(len,red.values())),29)
        self.assertEqual(sum(map(len,green.values())),71)
        self.assertEqual(len(entry.EXPECTED_CHANGES),6)
        self.assertTrue(set(entry.OWNERS)<=green.keys())

    def test_fixed_source_no_failure_or_unknown_count_promoted(self):
        raw=inspect.getsource(entry.main)
        for fact in("phases==[0,1]","phases==[0,0]","actual==expected","'coverageWholeAccepted':False","'oldNativeImported':False"):
            self.assertIn(fact,raw)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)

    def test_all_consumers_of_common_test_helper_have_test_scope_not_production_copy(self):
        import xml.etree.ElementTree as ET
        ns={'m':'http://maven.apache.org/POM/4.0.0'}
        for module in('web','batch'):
            tree=ET.parse(entry.ROOT/('src/schubert-nk-'+module+'/pom.xml'))
            deps=[d for d in tree.findall('m:dependencies/m:dependency',ns)if d.findtext('m:artifactId',namespaces=ns)=='schubert-nk-bootstrap'and d.findtext('m:type',namespaces=ns)=='test-jar']
            self.assertEqual(len(deps),1);self.assertEqual(deps[0].findtext('m:scope',namespaces=ns),'test')
        self.assertEqual(len(list(entry.ROOT.glob('src/*/src/test/java/**/CallerMonitorProbe.java'))),1)


if __name__=='__main__':unittest.main()
