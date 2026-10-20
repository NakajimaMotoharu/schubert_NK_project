"""No blanket equality waiver: wrong method/type/expression remains unreviewed."""
import unittest
from pg5768_reference_identity_review import contract


class NarrowIdentityReview(unittest.TestCase):
    def test_request_only_same_verified_handle_not_value_fields(self):
        f={'method':'reply','leftExpression':'saved.request','rightExpression':'request','leftType':'dev.codex.schubert.nk.api.application.admin.UserQueryRequest','rightType':'dev.codex.schubert.nk.api.application.admin.UserQueryRequest'}
        self.assertEqual('REQUEST_HANDLE',contract('UserQueryReplayService',f)[0])
        for changes in({'method':'capture'},{'leftExpression':'saved.name'},{'rightType':'java.lang.String'}):
            with self.assertRaises(ValueError):contract('UserQueryReplayService',{**f,**changes})

    def test_thread_and_exception_are_exact_reviewed_contracts(self):
        f={'method':'shutdown','leftExpression':'Thread.currentThread()','rightExpression':'owner','leftType':'java.lang.Thread','rightType':'java.lang.Thread'}
        self.assertEqual('THREAD_OWNER',contract('ApiProcessLifetime',f)[0])
        with self.assertRaises(ValueError):contract('ForeignClass',f)
        with self.assertRaises(ValueError):contract('ApiProcessLifetime',{**f,'leftExpression':'another'})
        e={'method':'closeAfterFailure','leftExpression':'closing','rightExpression':'startupFailure','leftType':'java.lang.Throwable','rightType':'java.lang.Throwable'}
        self.assertEqual('THROWABLE_CHAIN',contract('SyncRequestConsumers',e)[0])
        with self.assertRaises(ValueError):contract('SyncRequestConsumers',{**e,'rightExpression':'unrelated'})


if __name__=='__main__':unittest.main()
