import unittest
from pyflakes.api import check
import pg6014_constants_whole as t


class OrdinaryCurrentWholeDefinitionTest(unittest.TestCase):
    def test_complete3973_driver_and_finite_fixture_namespace_only(self):
        server=t.server_source(t.SOURCE,'0'*64)
        self.assertIn('PG6014',server);self.assertNotIn('PG5944',server)
        for held in('systemctl','qemu-system','virsh','sudo ','/opt/schubert-nk/current','--recover','--resume'):
            self.assertNotIn(held,server)
        driver=t.driver_source({'host':'fixture-only','boot':'not-runtime-proof','matchingActiveJobs':[],'freeBytes':20*1024**3,'availableKiB':8*1024**2})
        names=sorted(k for k in vars(t.RUNTIME.previous.driver)if k.isidentifier()and not k.startswith('__')and k!='main')
        self.assertEqual(0,check('='.join(names)+'=None\nserver_source=None\n'+driver,'<complete currentwhole driver namespace>'))
        for required in('pg6014-constants-six-v1','pg6014-full.py',"'tests': 3973","'suites': 592","'mainClasses': 1666"):
            self.assertIn(required,driver)
        self.assertEqual(67,len({r['path']for p in t.plans()for r in p['sourcePlans']}))


if __name__=='__main__':unittest.main()
