import json
import subprocess
import unittest
from pyflakes.api import checkPath
import pg6328_outbox_graph_order as subject


class CurrentGraphProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        jar=subject.W/'pg6324-web-graph-selected-v1/source/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
        blocks=subject.methods(subprocess.check_output([str(subject.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jar),
            'dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcher'],text=True))
        cls.code=next(v for k,v in blocks.items()if' preserveFatal('in k)

    def test_actual_helper_and_saved_four_boundaries_not_runtime_acceptance(self):
        proof=subject.graph_policy(self.code)
        self.assertEqual(0,proof['actualIoOrCleanupCalls']);self.assertEqual(4,proof['diagnosticGetterCalls'])
        m=json.loads((subject.BASE/'PG6328-outbox-graph-order-v1/manifest.json').read_bytes())
        self.assertEqual('aed19c6dca368e9717309d6f744d7917c6b7b32c',m['source'])
        self.assertEqual(4,len(m['fourBoundaryProofs']));self.assertEqual(5,len(m['changedPhysical']))
        self.assertTrue(m['helperExecutableEqual']);self.assertFalse(m['formalAccepted'])
        self.assertFalse(m['reportDebugOnly']['rawEqual']);self.assertTrue(m['reportDebugOnly']['lineNumberNormalizedEqual'])
        self.assertEqual(0,m['productionClassesExecuted']);self.assertEqual(0,m['testsExecuted'])
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_mutation_missing_identity_or_edge_unknown_call_and_no_fatal_exit_rejected(self):
        variants=(self.code.replace('Collections.newSetFromMap:','Collections.emptySet:'),
            self.code.replace('JMSException.getLinkedException:','JMSException.toString:'),
            self.code.replace('athrow','areturn'),
            self.code+'\n  999: invokevirtual #CP // Method java/lang/Throwable.addSuppressed:(Ljava/lang/Throwable;)V',
            self.code+'\n  999: invokestatic #CP // Method java/lang/Thread.sleep:(J)V')
        for index,bad in enumerate(variants):
            with self.subTest(vector=index),self.assertRaises(ValueError):subject.graph_policy(bad)


if __name__=='__main__':unittest.main()
