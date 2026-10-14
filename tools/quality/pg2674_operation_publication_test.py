import unittest
from pg2674_operation_publication_sources import sources,TOOLS,SAVE,CURRENT,CURRENT_BOM,BEFORE
from pg2658_operation_candidate_sources import SOURCE


class FinitePublicationPreparation(unittest.TestCase):
    def test_current_candidate_and_all_phase_roles(self):
        raw='\n'.join(sources('a'*64).values())
        for m in [CURRENT,SOURCE,CURRENT_BOM,BEFORE,TOOLS,SAVE,'a'*64,'0.1.0-PG2512','0.1.0-PG2654']:
            self.assertIn(m,raw)
        self.assertNotIn('c'*64,raw)
        self.assertNotIn('NORMAL_DAEMON_RELOAD',raw)


if __name__=='__main__':unittest.main()
