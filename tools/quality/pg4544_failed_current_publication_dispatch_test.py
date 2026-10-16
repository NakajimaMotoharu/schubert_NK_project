"""Full148 namespace/physical staging and same finite preflight qualification."""
import builtins
import io
import json
import symtable
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4544_failed_current_publication_dispatch as d


class FiniteDispatch(unittest.TestCase):
    def test_actual148_certificate_family_and_rejected_old_scope_or_missing_file(self):
        value=json.loads((d.role.W/'pg4548-frozen-v1.safe.json').read_bytes());d.qualify_fixed(value)
        for key,v in [('actualExit',False),('productionSource',d.role.SOURCE),('candidateSource',d.role.CURRENT)]:
            changed={**value,key:v}
            with self.subTest(key=key),self.assertRaises(ValueError):d.qualify_fixed(changed)
        changed={**value,'fileHashes':{n:h for n,h in value['fileHashes'].items()if n!='Pg4540TransitionTest.class'}}
        with self.assertRaises(ValueError):d.qualify_fixed(changed)

    def test_real_emitted_operator_all_globals_known_and_transfer_consumer_same(self):
        raw=d.source();table=symtable.symtable(raw,'<actual dispatcher>','exec').get_children()[0]
        ns={**vars(d.previous.previous.previous),'role':d.role,'TARGET':d.TARGET,'generated':d.generated,'GUEST':d.GUEST,'REMOTE':d.REMOTE,'STAGE':d.STAGE,'qualify_fixed':d.qualify_fixed}
        missing=[s.get_name()for s in table.get_symbols()if s.is_global()and s.is_referenced()and s.get_name()not in ns and not hasattr(builtins,s.get_name())]
        self.assertEqual([],missing)
        self.assertIn('pg4548-frozen-v1.safe.json',raw);self.assertIn('pg4544-stage-v1.exit',raw);self.assertIn('Pg4540TransitionTest',raw)
        self.assertIn(d.REMOTE+'/'+d.role.TOOLS+'.tar',d.STAGE)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG3976',d.STAGE)
        self.assertEqual(0,check("DIGEST='literal'\nFILES={}\n"+d.STAGE,'<full stage>',Reporter(io.StringIO(),io.StringIO())))


if __name__=='__main__':unittest.main()
