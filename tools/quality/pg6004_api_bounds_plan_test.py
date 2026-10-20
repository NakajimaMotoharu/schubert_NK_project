import unittest
from pg6004_api_bounds_plan import private_source


class RecordEnumConstantPlacementTest(unittest.TestCase):
    def test_enum_constant_stays_before_private_field_and_no_constructor_changes(self):
        original='public enum ArtemisConnectionFactoryProvider {\n  INSTANCE;\n  int verify(int port) { if (port > 65535) return 1; return 0; }\n}\n'
        after=private_source(original,[('if (port > 65535)','if (port > MAXIMUM_TCP_PORT)',1)],['private static final int MAXIMUM_TCP_PORT = 65535;'])
        self.assertLess(after.index('INSTANCE;'),after.index('private static final'))
        self.assertIn('public enum ArtemisConnectionFactoryProvider',after);self.assertNotIn('final class',after)

    def test_record_components_and_compact_constructor_are_kept(self):
        original='public record OutboxDlqMetadata(int deliveryCount) {\n  public OutboxDlqMetadata { if (deliveryCount < 1) throw new IllegalArgumentException(); }\n}\n'
        after=private_source(original,[('if (deliveryCount < 1)','if (deliveryCount < MINIMUM_DELIVERY_COUNT)',1)],['private static final int MINIMUM_DELIVERY_COUNT = 1;'])
        self.assertIn('public record OutboxDlqMetadata(int deliveryCount) {',after)
        self.assertIn('public OutboxDlqMetadata {',after);self.assertNotIn('final class',after)
        with self.assertRaises(ValueError):private_source(original,[('missing','new',1)],['private static final int LIMIT = 1;'])


if __name__=='__main__':unittest.main()
