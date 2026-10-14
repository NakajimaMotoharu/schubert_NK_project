import ast
import unittest
from unittest.mock import patch
import pg2684_operation_current_noargs_once as admission
from pg2682_operation_current_observer import source,SOURCE
from pg2684_operation_current_noargs_once import body
from pg2686_operation_current_live_binding import body as binding


class NewResourceCurrent(unittest.TestCase):
    def test_new_source_observer_and_fresh_admission(self):
        for fn in [source,body]:
            raw=fn('a'*64);ast.parse(raw)
            for marker in [SOURCE,'a'*64,'PG2654','pg2682']:self.assertIn(marker,raw)
            self.assertNotIn('pg2538',raw)
        self.assertIn('pg2680-operation-publication-post-v1',source('a'*64))
        self.assertIn('require(len(records)==28)',body('a'*64))
        self.assertIn('pg2684-operation-current-noargs-once-v2',body('a'*64))
        self.assertIn('originalBudgetSeconds',body('a'*64))
        self.assertIn('1800',body('a'*64))

    def test_reject_historical_root_and_unknown_bom(self):
        raw=binding();ast.parse(raw)
        for marker in ['PG2654','b29fb3e5-2c46-4eac-b8f3-d03b986338e3','d0219581-24e4-4136-ac90-39d54e704378']:
            self.assertIn(marker,raw)
        for value in [False,'','x'*64,'a'*63]:
            for fn in [source,body]:
                with self.assertRaises(ValueError):fn(value)

    def test_default_bom_is_new_dependency_never_old_factory(self):
        new='552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37'
        old='2f3275b09f26b46932fc3e8eaf269023256e9078027611d617639f43b191395f'
        with patch.object(admission,'candidate_bom',return_value=new),patch.object(admission.previous,'candidate_bom',side_effect=AssertionError('old default dependency forbidden')):
            default=admission.body();explicit=admission.body(new)
        self.assertEqual(default,explicit)
        self.assertIn(new,default);self.assertNotIn(old,default)


if __name__=='__main__':unittest.main()
