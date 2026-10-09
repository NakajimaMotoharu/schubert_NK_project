import unittest
from pg793_selected_qualify import counters_valid


class Test(unittest.TestCase):
    def test_literal_enum_and_actual_conditional_counter(self):
        empty={'LINE':{'missed':0,'covered':11},'METHOD':{'missed':0,'covered':1},'CLASS':{'missed':0,'covered':1}}
        self.assertTrue(counters_valid('Literal$CompletionPhase',empty));self.assertFalse(counters_valid('Literal$CompletionProgress',empty))
        real={**empty,'BRANCH':{'missed':0,'covered':4}}
        self.assertTrue(counters_valid('Literal$CompletionProgress',real));self.assertFalse(counters_valid('Literal$CompletionPhase',real))
        for name in ('LINE','METHOD','CLASS','BRANCH'):
            bad={**real,name:{'missed':1,'covered':1}};self.assertFalse(counters_valid('Literal$CompletionProgress',bad))
            bad=dict(real);bad.pop(name);self.assertFalse(counters_valid('Literal$CompletionProgress',bad))


if __name__=='__main__':unittest.main()
