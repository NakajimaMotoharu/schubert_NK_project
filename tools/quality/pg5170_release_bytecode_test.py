import unittest
import pg5170_release_bytecode as role


class ReleaseDelta(unittest.TestCase):
    def test_all_required_outer_changes_and_bounded_optional_debug_only(self):
        keys=[role.entry.PREFIX+name+'.class' for name in role.FACTORIES]
        debug=role.entry.PREFIX+'StartupReleaseManifest$Snapshot.class'
        before={key:'old' for key in keys};before.update({debug:'stable','other':'stable'})
        after={**before,**{key:'new' for key in keys}}
        self.assertEqual(role.physical_delta(before,after),[])
        self.assertEqual(role.physical_delta(before,{**after,debug:'debug-only'}),[debug])
        for bad in (before,{**after,'other':'foreign'},{**after,'unexpected':'extra'}):
            with self.assertRaises(ValueError):role.physical_delta(before,bad)


if __name__=='__main__':unittest.main()
