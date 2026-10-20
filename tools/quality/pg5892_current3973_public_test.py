import hashlib
import unittest
import pg5892_current3973_public as target
from pg5890_terminal_serial_selected_public import TERMINAL_CASES


class AllSixTerminalCurrentTraceTest(unittest.TestCase):
    def test_all_designs_require_one_actual_xml_each(self):
        import re
        designs=[{'class':c,'method':m,'designTestId':'PT-JMS-TERM'+re.match(r'term(\d{3})',m).group(1)}for c,m in sorted(TERMINAL_CASES)]
        cases=[{'class':r['class'],'caseNameSha256':hashlib.sha256(r['method'].encode()).hexdigest(),'testId':'case'+r['designTestId'],'xmlSha256':'a'*64}for r in designs];new=set(target.added_cases())
        alltrace,newtrace=target.terminal_trace(cases,{'caseTrace':designs},new)
        self.assertEqual(6,len(alltrace));self.assertEqual(2,len(newtrace))
        for broken in(cases[:-1],cases+[cases[0]]):
            with self.assertRaises(ValueError):target.terminal_trace(broken,{'caseTrace':designs},new)
        raw=target.payload({});self.assertIn('PG5886',raw);self.assertNotIn('PG5860',raw);self.assertNotIn('Popen',raw)


if __name__=='__main__':unittest.main()
