"""Literal independent key multiset cases and mapping initializer regression."""
import hashlib,json,unittest
from pg3646_root_browser_bridge_diagnostic import compare


def digest(row):return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()


class Hashes(unittest.TestCase):
    def test_equal_added_removed_and_changed(self):
        a={'id':1};b={'id':2};c={'id':1,'v':1}
        for left,right,removed,added in [([a],[a],0,0),([a],[a,b],0,1),([a,b],[a],1,0),([a],[c],1,1)]:
            value=compare(left,[digest(r)for r in right]);self.assertEqual(removed,value['rootRowsAbsentFromBrowserBefore']);self.assertEqual(added,value['browserBeforeRowsNotInRoot'])

    def test_duplicate_type_and_bad_digest(self):
        a={'id':1}
        for rows,hashes in [([a,a],[digest(a)]),([a],[digest(a),digest(a)]),([a],['foreign']),([a],[None]),(None,[]),([],{})]:
            with self.assertRaises(ValueError):compare(rows,hashes)


if __name__=='__main__':unittest.main()
