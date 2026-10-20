import unittest
import pg5924_direct_boundary_review as t


class ExactBoundaryTest(unittest.TestCase):
    def test_only_original_direct_throw_before_required_checked_handler(self):
        good = ') { throw fatal; } catch (Exception failure) {'
        self.assertEqual(64, len(t.direct_boundary(good, 0, 'Error fatal', 'Exception')))
        for bad in (') { throw other; } catch (Exception failure) {',
                    ') { fatal = other; throw fatal; } catch (Exception failure) {',
                    ') { close(); throw fatal; } catch (Exception failure) {',
                    ') { return; } catch (Exception failure) {',
                    ') { throw fatal; } catch (RuntimeException failure) {',
                    ') { throw new RuntimeException(fatal); } catch (Exception failure) {'):
            with self.assertRaises(ValueError):
                t.direct_boundary(bad, 0, 'Error fatal', 'Exception')


if __name__ == '__main__':
    unittest.main()
