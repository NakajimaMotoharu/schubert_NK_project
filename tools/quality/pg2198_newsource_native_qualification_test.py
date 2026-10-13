import unittest
import pg2198_newsource_native_qualification as p


class Qualification(unittest.TestCase):
    def test_actual_transport_and_server_one_current_source(self):
        s=p.server();t=p.source()
        for value in ['PG2198-native-v1','source-full-PG2124','runs/PG2124-six-v1','3631','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8']:self.assertIn(value,s)
        for value in ['pg2196-newsource-native-catalog-v1','pg2198-newsource-native-qualified-v1','pg2125-metadata-boundary-full-qualified-v1']:self.assertIn(value,t)
        self.assertNotIn('PG2104-native-v1',s)
        self.assertNotIn('source-full-PG1844',s)
        self.assertEqual(p.entry().__globals__['CODE'],s)
        self.assertEqual(p.entry().__globals__['SOURCE'],p.SOURCE)
        self.assertIn('classByteMismatch',s)


if __name__=='__main__':unittest.main()
