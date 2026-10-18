import ast
import inspect
import unittest
from pyflakes.api import checkPath
import pg5550_snapshot_required_whole as entry


class Whole(unittest.TestCase):
    def test_complete_standalone_current_counts_without_quality_relaxation(self):
        raw=entry.server_source(entry.SOURCE,'a'*64)
        values={n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)and type(n.value)is int}
        self.assertTrue({3900,563,1664}<=values);self.assertNotIn(3896,values)
        for marker in('PG5550-six-v1','source-full-PG5550',entry.SOURCE,'spotless','spotbugs','jacoco'):self.assertIn(marker,raw)
        self.assertNotIn('PG5414',raw);self.assertNotIn('skipTests=true',raw)

    def test_original_source_pin_and_actual_new_only_job_preflight(self):
        raw=inspect.getsource(entry.main)
        self.assertLess(raw.index('fresh=preflight()'),raw.index("previous.driver.main"))
        self.assertIn("path.open('x')",raw);self.assertIn('operatorBranch',raw)
        source=inspect.getsource(entry.preflight)
        for marker in('matchingActiveJobs','availableKiB','freeBytes','argvSha256','/proc/sys/kernel/random/boot_id'):self.assertIn(marker,source)
        for text in('systemctl','kill(','pkill','force=True'):self.assertNotIn(text,source)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
