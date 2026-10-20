import unittest
import pg5960_readiness_boundaries_review as t


class BoundedReadinessContractTest(unittest.TestCase):
    def fixture(self):
        return (t.GUARD+'primary = failure; connection.close();\n'+t.GUARD+'primary = failure; context.close();\n'
                '} catch (RuntimeException failure) {\n} catch (SQLException | RuntimeException failure) {')

    def test_fail_closed_on_throwable_redaction_lost_guard_or_duplicate_close(self):
        text = self.fixture(); t.require_source_contract(text)
        for bad in (text.replace('!(primary instanceof Error)', '(primary instanceof Error)'), text+'getCause(', text+'catch (Throwable', text+'connection.close();', text.replace('primary = failure;', '')):
            with self.assertRaises(ValueError):
                t.require_source_contract(bad)


if __name__ == '__main__':
    unittest.main()
