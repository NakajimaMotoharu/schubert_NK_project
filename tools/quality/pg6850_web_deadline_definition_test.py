import unittest
from unittest.mock import patch
import pg6850_web_deadline_selected as p


class WebDeadlineDefinitionTest(unittest.TestCase):
    def test_actual42_and_fifteen_suites(self):
        cases,counts=p.inventory();self.assertEqual((42,15),(sum(counts.values()),len(counts)))
        self.assertEqual(6,len(cases))
        with patch.object(p,'EXPECTED',(42,14)),self.assertRaises(ValueError):p.inventory()

    def test_red_has_no_main_and_green_only_web(self):
        for green,paths in((False,{p.TEST}),(True,{p.MAIN,p.TEST})):
            text='\n'.join(sorted(paths))+'\n'
            with patch.object(p.subprocess,'check_output',side_effect=[text,'']):p.guard('candidate',green)
            with patch.object(p.subprocess,'check_output',return_value=text+'src/Unexpected.java\n'),self.assertRaises(ValueError):p.guard('candidate',green)


if __name__=='__main__':unittest.main()
