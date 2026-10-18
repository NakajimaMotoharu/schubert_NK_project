import unittest
from pyflakes.api import checkPath
import pg5554_thread_rule_applicability as entry


def pom(packaging='',extra=''):
    return'<project xmlns="http://maven.apache.org/POM/4.0.0"><artifactId>schubert-nk-api</artifactId>'+packaging+extra+'</project>'


class Applicability(unittest.TestCase):
    def test_jar_is_not_sufficient_enterprise_runtime_and_foreign_artifacts_refused(self):
        self.assertEqual(entry.descriptor(pom(),'schubert-nk-api')['packaging'],'jar (Maven default)')
        self.assertEqual(entry.descriptor(pom('<packaging>jar</packaging>'),'schubert-nk-api')['packaging'],'jar')
        for bad in(pom('<packaging>war</packaging>'),pom('<packaging>ejb</packaging>'),pom(extra='<name>ManagedExecutorService</name>'),pom(extra='<name>jakarta.jakartaee-api</name>')):
            with self.assertRaises(ValueError):entry.descriptor(bad,'schubert-nk-api')
        with self.assertRaises(ValueError):entry.descriptor(pom(),'foreign')

    def test_actual_primary_rule_and_all_six_declared_own_process_context(self):
        rule=entry.rule();self.assertIn('J2EE server',rule['description']);self.assertEqual(rule['version'],'7.28.0')
        context=entry.architecture();self.assertEqual(len(context['poms']),6);self.assertEqual(len(context['ownUnitLaunchers']),3)
        self.assertEqual(len(context['ownProcessEntries']),3);self.assertEqual(context['managedEnterpriseReferencesFound'],0)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
