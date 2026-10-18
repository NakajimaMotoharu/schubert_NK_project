import json
import re
import unittest
import pg5274_cleanup_factory_bytecode as post
import pg5278_scope_classification_cleanup_factory as role


class InventoryNames(unittest.TestCase):
    def test_new_files_are_exact_original_unclassified_basenames(self):
        root=role.entry.selected.ROOT
        original=root/('evidence/01_PT/'+role.carry.inventory.INVENTORY)
        self.assertEqual(role.entry.selected.sha(original),role.carry.ORIGINAL_SHA)
        names={r['path'].rpartition('/')[2] for r in json.loads(original.read_bytes())['files']}
        previous=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5270-scope-classification-morning-backup-v1/manifest.json'
        fixed=role.carry.fixed_names(json.loads(previous.read_bytes())['files'])
        self.assertEqual(role.NEW_FILES,{'CleanupExpiryExecution.java','CleanupMaintenanceWork.java',
            'CleanupNativeExecution.java','CleanupNativePreflight.java','MaintenanceFileLock.java','TransferCleanup.java'})
        self.assertLessEqual(role.NEW_FILES,names)
        self.assertFalse(role.NEW_FILES&fixed)
        self.assertFalse(role.entry.OUTERS<=names)

    def test_shared_source_pin_is_original_run_not_an_alias(self):
        self.assertEqual(role.SOURCE,post.SOURCE)
        self.assertRegex(role.SOURCE,re.compile(r'^[0-9a-f]{40}$'))
        p=role.entry.selected.ROOT.parent/'pgpt-runs/PG379/pg5272-cleanup-factory-green-v1/manifest.safe.json'
        self.assertEqual(json.loads(p.read_bytes())['sourceSnapshot'],role.SOURCE)


if __name__=='__main__':unittest.main()
