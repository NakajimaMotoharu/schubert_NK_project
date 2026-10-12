"""Actual consumer graph executes positive and rejects missing/foreign/path inputs."""
import hashlib
import pathlib
import tempfile
import unittest
from pg1860_warning_actual_graph_sources import sources
from pg1861_warning_actual_graph_compile import validate_actual_graph


class Graph(unittest.TestCase):
    def test_real_validator_all_imports_and_required_class_names(self):
        generated=sources('b'*64,'c'*64)
        with tempfile.TemporaryDirectory(prefix='pg1861-graph-')as directory:
            target=pathlib.Path(directory)
            pins={}
            for name,raw in generated.items():
                if not name.endswith('.py'):continue
                if name in ['pg1860_native_refs.py','pg1860_input_preflight.py']:raw='BUNDLE_HASH="a"\n'+raw
                (target/name).write_text(raw);pins[name]=hashlib.sha256(raw.encode()).hexdigest()
            for name in ['Pg1860UnusedStage.class','Pg1860UnusedStage$References.class']:pins[name]='a'*64
            self.assertTrue(validate_actual_graph(target,pins))
            for missing in ['Pg1860UnusedStage.class','pg1860_native_refs.py','pg1860_warning_parent_projection.py']:
                changed=dict(pins);changed.pop(missing)
                with self.subTest(missing=missing),self.assertRaises(ValueError):validate_actual_graph(target,changed)
            changed=dict(pins);changed['../escape.class']='a'*64
            with self.assertRaises(ValueError):validate_actual_graph(target,changed)
            p=target/'pg1860_parent_receipt.py';p.write_text(p.read_text()+'\nimport foreign_dependency\n')
            with self.assertRaises(ValueError):validate_actual_graph(target,pins)


if __name__=='__main__':unittest.main()
