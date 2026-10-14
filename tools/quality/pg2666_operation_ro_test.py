import unittest
from pg2666_operation_ro_sources import sources,TOOLS,SAVE,CLASS
from pg2667_operation_ro_compile import compiler
from pg2658_operation_candidate_sources import CURRENT,SOURCE,BEFORE


class NewReadonlyPreparation(unittest.TestCase):
    def test_complete_actual_ro_roles(self):
        values=sources('a'*64);raw='\n'.join(values.values())
        for m in [CURRENT,SOURCE,BEFORE,TOOLS,SAVE,CLASS,'0.1.0-PG2654','0.1.0-PG2512']:self.assertIn(m,raw)
        self.assertIn('pg2664-operation-unused-post-v1',compiler())
        self.assertIn('pg2659-frozen',compiler())


if __name__=='__main__':unittest.main()
