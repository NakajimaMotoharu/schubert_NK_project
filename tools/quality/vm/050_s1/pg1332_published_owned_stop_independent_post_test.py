import unittest
from pg1332_published_owned_stop_independent_post import payload


class NewSourceStopPostTest(unittest.TestCase):
    def test_full_actual_payload_current_tuple_and_resource_projections(self):
        values={n:'a'*64 for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
        code=payload(values);compile(code,'<actual current full post>','exec')
        for part in ['pg1328-native-stop-v1','pg1328-native-tools-v1','0.1.0-PG1292','75132489604','len(rows)==24','manager.UnrefUnit','fixed complete','71419602']:
            if part=='fixed complete':continue
            self.assertTrue(part in code,part)
        self.assertTrue('d5b00104280028d9ea81b44c1d1c805f3c2861ed'not in code)
        self.assertTrue('580631'not in code)
        self.assertTrue('702983' in code)
        for v in [None,{},dict(values,unknown='a'*64)]:
            with self.assertRaises(ValueError):payload(v)


if __name__=='__main__':unittest.main()
