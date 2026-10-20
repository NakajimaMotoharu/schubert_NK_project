"""Check emitted namespace and fourteen finite case inventory before Maven issue."""
import unittest
from pyflakes.api import check
from pg5774_jms_primary_selected import runner_source,CASES
from pg5732_enum48_selected import ROOT,PACKAGE,test_names


class FinitePlan(unittest.TestCase):
    def test_full_namespace_and_unrelaxed_inventory(self):
        prelude='from pg5732_enum48_selected import subprocess,ROOT,os,tarfile,PACKAGE,test_names,TC,sha,utc,json,hashlib,Path,ET,MODULES\nfrom pg5774_jms_primary_selected import CASES,TARGETS,red_qualified\nSLOT="synthetic"\nPHASE="red"\n'
        self.assertEqual(0,check(prelude+runner_source(),'finite14-complete'))
        counts={m:sum(len(test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((PACKAGE+c).replace('.','/')+'.java')))for c in names)for m,names in CASES.items()}
        self.assertEqual({'protocol':3,'storage':1,'bootstrap':1,'api':5,'web':2,'batch':2},counts)
        raw=runner_source();self.assertNotIn('-DskipTests',raw);self.assertIn("'expectedTests':14",raw)
        self.assertIn('targetFour100RequiredBeforeProgramCompletion=True',raw)


if __name__=='__main__':unittest.main()
