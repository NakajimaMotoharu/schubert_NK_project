"""Independent final geometry/current post checks do not use the grow producer."""
import ast
import unittest
from pg2013_online_capacity_independent_post import payload


class CapacityPost(unittest.TestCase):
    def test_literal_geometry_and_complete_current_oracle(self):
        raw=payload();ast.parse(raw)
        for required in ["geometry['lastlba']==saved['lastlba']+16777216", "after_root['size']==before_root['size']+16777216", "free>=12*1024**3", "sameBootAfterOnlineCapacityGrow", "allClientAdvisoryFlock0", "existingFileNoRewrite", "lines[-2:] == [b'0', b'0']"]:
            self.assertTrue(required in raw,required)
        for forbidden in ['block_resize', 'growpart', 'resize2fs', 'from pg2012', 'import pg2012']:
            self.assertTrue(forbidden not in raw, 'independent of grow producer: '+forbidden)


if __name__=='__main__':unittest.main()
