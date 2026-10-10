import unittest
from pg1212_current_stop_v2_dispatch import source


class DispatcherTest(unittest.TestCase):
    def test_whole_actual_namespace_without_main_side_effects(self):
        env={'__name__':'qualified_current_dispatch','__file__':__file__}
        exec(compile(source(),'<actual isolated dispatch namespace>','exec'),env)
        p=env['proof']();env['bindings'](p)
        env['archive_members']([('only.class','file')],{'only.class'})
        with self.assertRaises(ValueError):env['archive_members']([('../outside','file')],{'only.class'})
        self.assertTrue('pg1212-fixed-stage-v1' in env['STAGE'])
        self.assertTrue('pg1208-native-tools-v1' in env['STAGE'])
        self.assertFalse('inspect.getsource' in env['STAGE'])


if __name__=='__main__':unittest.main()
