"""Exact independent unchanged originals and sole finite runtime delta, correct complete markers."""
import ast
import unittest
from pg2060_fresh_runtime_retirement_independent_post import payload,SEALS


class Post(unittest.TestCase):
    def test_actual_same_data_and_normal_returned_scopes(self):
        raw=payload({n:'a'*64 for n in SEALS});ast.parse(raw)
        for wanted in ['allTenAlreadyTerminal=true','runtimeRetiredOnly=true','same_except_runtime','json.loads(prior_raw)==before','exactRuntimeEntryRetired','all24UnchangedTwice','allClientAdvisoryFlock0','manager.UnrefUnit(u)','bus.close()']:
            self.assertTrue(wanted in raw,wanted)
        self.assertLess(raw.index("require(runtime_contract['same_except_runtime']"),raw.index('bus = dbus.SystemBus(private=True)',raw.index("require(runtime_contract['same_except_runtime']")))


if __name__=='__main__':unittest.main()
