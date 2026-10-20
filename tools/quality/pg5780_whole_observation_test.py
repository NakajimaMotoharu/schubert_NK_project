"""Pure generation/foreign identity checks; never connects or starts a job."""
import unittest
from pg5780_whole_observation import observer_source,SOURCE


class ObservationBinding(unittest.TestCase):
    def test_current_labels_and_exact_runner_basename(self):
        value={'source':SOURCE,'tests':3939,'suites':583,'mainClasses':1664,'archiveSha256':'a'*64}
        raw=observer_source(value)
        self.assertIn('/tools/pg5780-full.py',raw);self.assertIn('runs/PG5780-six-v1',raw)
        self.assertNotIn('pg5754',raw);self.assertNotIn('PG5754',raw)
        self.assertIn("'a"+'a'*63+"'",raw)
        for changes in({'source':'foreign'},{'tests':3932},{'archiveSha256':'unknown'}):
            with self.assertRaisesRegex(ValueError,'original local begin'):observer_source({**value,**changes})


if __name__=='__main__':unittest.main()
