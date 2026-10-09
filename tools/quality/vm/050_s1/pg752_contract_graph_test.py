"""Actual extracted reference functions/import graph, not mere syntax; no Root capability."""
from pathlib import Path
import pg752_sources as p
import types
import unittest

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=(R/'pg717_contract_graph_test.py').read_text()
    raw=p.bind(raw).replace('pg717_sources','pg752_sources')
    raw=raw.replace('pg680-owner-six-host-v1','pg713-expiry-six-host-v1')
    raw=raw.replace("b'activation_id=c6815985',b'activation_id=d6815985'", "b'activation_id=ab8895ca',b'activation_id=bb8895ca'")
    raw=raw.replace("p.bind(p.previous.bind((R / 'pg624_completed_contract_test.py').read_text()))",
                    "p.bind(p.previous.bind(p.previous.previous.bind((R / 'pg624_completed_contract_test.py').read_text())))")
    mod=types.ModuleType('pg752_graph_actual');mod.__file__=str(R/'pg752_contract_graph_test.py')
    exec(compile(raw,'<sealed current751/nine proof graph>','exec'),mod.__dict__)
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromModule(mod))
    assert result.testsRun==3
    raise SystemExit(0 if result.wasSuccessful()else 1)
