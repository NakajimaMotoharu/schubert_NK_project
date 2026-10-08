"""Current driver/new parent route only, no real HTTP or browser."""
import unittest
from pg654_a01_current import code


class Binding(unittest.TestCase):
    def test_same_driver_baseline_new_generation_and_before_after(self):
        v=code();compile(v,'<new route>','exec')
        for x in ('pg650-fresh-parent-v2','pg650-start-v2','pg651-watch-private-v1','PG654-native-a01-v1','pg654-chr-a01-native-v1',
                  '122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d', 'NativeNkA01Capture',
                  'before[u]', 'after[u]', 'baseline_sha', '1800000000', 'sameCapturedParentApiWebCaddyBeforeAfter'):
            self.assertIn(x,v)
        for x in ('pg637-fresh-resume-v2','PG641-native-a01-v1','daemon-reload',"['systemctl','start'","['systemctl','stop'"):
            self.assertNotIn(x,v)


if __name__=='__main__':unittest.main()
