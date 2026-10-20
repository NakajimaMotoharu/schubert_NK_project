import unittest
import pg6098_jms_individual_static_review as p


class IndividualSiteTest(unittest.TestCase):
    def test_locked_volatile_and_unknown_site_are_not_blanket_accepted(self):
        self.assertIsNone(p.site_role('ArtemisReplyConsumers', 23, 'AvoidUsingVolatile'))
        self.assertIsNone(p.site_role('ArtemisReplyConsumers', 999, 'AvoidCatchingGenericException'))
        self.assertIsNone(p.site_role('DifferentOwner', 24, 'AvoidUsingVolatile'))
        self.assertIn('ready reads stopping', p.site_role('ArtemisReplyConsumers', 24, 'AvoidUsingVolatile'))

    def test_cleanup_and_retry_have_distinct_reviewed_obligations(self):
        self.assertIn('confirmed', p.site_role('QuestionWorkConsumers', 73, 'EmptyCatchBlock'))
        self.assertIn('notification', p.site_role('QuestionWorkConsumers', 68, 'EmptyCatchBlock'))
        self.assertIn('one close', p.site_role('WebBrokerContexts', 94, 'AvoidCatchingGenericException'))


if __name__ == '__main__':
    unittest.main()
