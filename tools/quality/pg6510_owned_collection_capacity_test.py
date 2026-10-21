import subprocess
import inspect
import tempfile
from pathlib import Path
import unittest
from pyflakes.api import checkPath
import pg6510_owned_collection_capacity as subject


class Capacity(unittest.TestCase):
    def test_path_hash_contract_fixed_vector_and_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'literal'
            # Test-only fixed vector; no private artifact or production expected value generation.
            path.write_bytes(b'abc')
            self.assertEqual('ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',subject.path_sha(path))
            with self.assertRaises(AttributeError): subject.path_sha(b'abc')
        self.assertIn('currentWholeQualificationSha256=path_sha(qp)',inspect.getsource(subject.main))

    def test_four_actual_current_compiled_shapes_without_running_pt(self):
        shapes = subject.compiled_shapes()
        self.assertEqual(4,len(shapes))
        capacities = {r['className'].rsplit('.',1)[-1]:r['capacityProof'].get('capacity',3) for r in shapes}
        self.assertEqual({'ApiMessagingRuntime':3,'SyncRequestConsumers':4,'ApiBrokerContexts':3,'MorningStartupLaunchOwner':2},capacities)
        self.assertEqual(0,checkPath(subject.__file__))

    def test_smaller_context_backing_array_and_factory_capacity_rejected(self):
        jar = subject.W/'pg6498-web-owned-component-v5/source/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
        for cls, function, literal, replacement in (
            ('api.messaging.inbound.SyncRequestConsumers',subject.sync_capacity,'iconst_4','iconst_3'),
            ('api.messaging.config.ApiBrokerContexts',subject.factory_capacity,'iconst_3','iconst_2')):
            raw = subprocess.check_output([str(subject.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jar),'dev.codex.schubert.nk.'+cls],text=True)
            bodies = [v for v in subject.methods(raw).values() if 'java/util/ArrayList."<init>"' in v]
            self.assertEqual(1,len(bodies))
            with self.assertRaises(ValueError): function(bodies[0].replace(literal,replacement,1))


if __name__ == '__main__': unittest.main()
