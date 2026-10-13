"""Actual15-source static closure, current generation only, exact GC rejects partial/foreign."""
import unittest
from pg2030_fresh_normal_warning_owned_stop_sources import sources,projection_source


class Stop(unittest.TestCase):
    def test_whole_generated_sources_and_exact_parent_schema(self):
        values=sources();self.assertEqual(15,len(values))
        raw=values['pg2030_native_owned_stop.py']
        self.assertTrue("receipt['normalUnit0or10']is True"in raw);self.assertTrue('107890801314'in raw)
        self.assertTrue('Root'not in projection_source())
        ns={};exec(projection_source(),ns);fields=dict(ns['EXPECTED']);self.assertTrue(ns['qualify_warning_parent'](fields)['currentManagerGc'])
        self.assertTrue(ns['qualify_warning_parent']({**fields,'SuccessExitStatus':'10'},True)['normalUnit0or10'])
        for key in fields:
            with self.assertRaises(ValueError):ns['qualify_warning_parent']({**fields,key:'foreign'})
        with self.assertRaises(ValueError):ns['qualify_warning_parent']({**fields,'SuccessExitStatus':''},True)
        self.assertTrue('managerFailureRetained=true'not in values['Pg2030NativeStop.java'])
        for source in values.values():self.assertTrue('4148e3e8-f107-431a-ab27-d6e6d1f2030e'not in source)


if __name__=='__main__':unittest.main()
