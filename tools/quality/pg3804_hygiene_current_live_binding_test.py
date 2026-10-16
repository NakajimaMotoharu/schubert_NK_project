import ast
import unittest
import pg3804_hygiene_current_live_binding as tool


class RootBinding(unittest.TestCase):
    def test_actual_new_peer_not_old_current_or_historical_completion(self):
        raw=tool.body();ast.parse(raw)
        current,_,_=tool.current_tuple()
        for marker in ['PG3748',current['run'],current['activation'],"unit['Job']==EXPECTED['Job']",'originalBudgetSeconds',"active.read_bytes()==raw"]:self.assertTrue(marker in raw,marker)
        self.assertNotIn('PG3420',raw);self.assertNotIn('systemctl start',raw)


if __name__=='__main__':unittest.main()
