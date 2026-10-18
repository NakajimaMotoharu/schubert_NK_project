import copy
import hashlib
import unittest
import pg5146_scope_classification as role


class ScopeClassification(unittest.TestCase):
    def fixture(self):
        names=role.ROOT_FIXED|role.CALLER_FIXED|{'LinuxFileLock.java','LinuxSealedProof.java',
             'LinuxStartupAdmission.java','LinuxExecDescriptors.java','Unreviewed.java'}
        data={name:b'unchanged original' for name in names}
        data['LinuxExecDescriptors.java']=b'ResourceScope.use(borrowedRelease, action);'
        data['LinuxStartupAdmission.java']=b'ResourceScope.use(admissionRelease, proofRelease);'
        rows=[{'path':name,'sourceSha256':hashlib.sha256(data[name]).hexdigest(),'sites':[{'line':1}]} for name in sorted(names)]
        return rows,data

    def test_original_rows_partition_without_accepting_unreviewed_or_new_cleanup_as_acquisition(self):
        rows,data=self.fixture()
        self.assertEqual(role.classify(rows,data.__getitem__,native=True,evidence_ref='fixed-proof'),
                         {'FIXED_LIMITED':10,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':1})
        unknown=next(row for row in rows if row['path']=='Unreviewed.java')['sites'][0]
        self.assertEqual(unknown['classification'],'UNKNOWN')
        self.assertIsNone(unknown['retestEvidence'])
        self.assertFalse(unknown['fixed'])

    def test_changed_unreviewed_and_unclassified_new_scope_never_get_implicit_credit(self):
        rows,data=self.fixture()
        for path in ('Unreviewed.java','LinuxStartupAdmission.java'):
            changed=copy.deepcopy(data);changed[path]+=b'ResourceScope.use(unreviewed, action);'
            with self.assertRaises(ValueError):role.classify(copy.deepcopy(rows),changed.__getitem__,native=True)


if __name__=='__main__':unittest.main()
