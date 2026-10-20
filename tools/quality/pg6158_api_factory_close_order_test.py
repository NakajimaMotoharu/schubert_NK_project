"""Independent malformed range/order vectors for the read-only JVM configuration checker."""
import unittest
from pg6158_api_factory_close_order import configuration


def fixture():
    names=['setCallTimeout','setClientFailureCheckPeriod','setConnectionTTL','setInitialConnectAttempts',
        'setReconnectAttempts','setRetryInterval','setRetryIntervalMultiplier','setMaxRetryInterval',
        'setConsumerWindowSize','setBlockOnDurableSend','setPreAcknowledge','setUseTopologyForLoadBalancing']
    code='0: invokeinterface #1 // InterfaceMethod java/util/function/Supplier.get:()Ljava/lang/Object;\n'
    code+=''.join(str(i)+': invokevirtual #2 // Method org/apache/activemq/artemis/jms/client/ActiveMQConnectionFactory.'+name+':(I)V\n' for i,name in enumerate(names,1))
    code+='30: invokevirtual #3 // Method org/apache/activemq/artemis/jms/client/ActiveMQConnectionFactory.close:()V\n'
    code+='1 13 15 Class java/lang/RuntimeException\n1 13 15 Class java/lang/Error\n30 31 32 Class java/lang/RuntimeException\n30 31 32 Class java/lang/Error\n'
    return code


class ConfigurationCheck(unittest.TestCase):
    def check_code(self, code):
        return configuration({'  static Factory configureOwned(Profile, Supplier);':code})

    def test_all_twelve_and_both_independent_handlers(self):
        p=self.check_code(fixture()); self.assertEqual(list(range(1,13)),p['setterOffsets']);self.assertEqual(30,p['closeOffset'])

    def test_missing_last_setter_protection(self):
        with self.assertRaises(ValueError):self.check_code(fixture().replace('1 13 15 Class java/lang/Error','1 12 15 Class java/lang/Error'))

    def test_acquire_must_not_be_in_owned_range(self):
        with self.assertRaises(ValueError):self.check_code(fixture().replace('1 13 15 Class','0 13 15 Class'))

    def test_changed_setter_order_is_not_accepted(self):
        with self.assertRaises(ValueError):self.check_code(fixture().replace('setConsumerWindowSize','setCallTimeout'))

    def test_second_close_is_not_accepted(self):
        with self.assertRaises(ValueError):self.check_code(fixture()+'33: invokevirtual #3 // Method org/apache/activemq/artemis/jms/client/ActiveMQConnectionFactory.close:()V\n')


if __name__=='__main__':unittest.main()
