import unittest
import pg6576_jdbc_boundary_map as subject


class BoundaryMapDefinitionTest(unittest.TestCase):
    def test_non_sql_markers_and_nested_bodies_are_explicit(self):
        raw='''// catch(SQLException ignored) { return false; }
        try {} catch(SQLException outer) {
          try {} catch(RuntimeException inner) { throw new Catalog(); }
          throw unavailable();
        }
        try {} catch(CapacityException capacity) { return capacity.getSuppressed(); }'''
        rows=subject.bodies(raw)
        self.assertEqual(3,len(rows))
        self.assertEqual(['outer','inner','capacity'],[r['header'][-1] for r in rows])
        self.assertIn('unavailable',rows[0]['body']);self.assertIn('new',rows[1]['body'])

    def test_literals_and_invalid_syntax_cannot_add_or_lose_sites(self):
        self.assertEqual([],subject.bodies('String x="catch(SQLException e) { }";'))
        with self.assertRaises(ValueError):subject.bodies('catch(SQLException e) {')

    def test_changed_cardinality_requires_explicit_remap(self):
        self.assertEqual([(1,2)],subject.align([1],[2]))
        with self.assertRaisesRegex(ValueError,'explicit remap'):subject.align([1],[2,3])


if __name__=='__main__':unittest.main()
