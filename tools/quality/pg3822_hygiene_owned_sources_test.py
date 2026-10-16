import ast
import unittest
from immutable_payload_binding import bind_preserving_payloads
import pg3822_hygiene_owned_sources as tool
import pg3826_hygiene_owned_dispatch as dispatch
import pg3828_hygiene_owned_post as post


class CurrentOwnedBinding(unittest.TestCase):
    def test_all_embedded_oracles_and_snapshot_literals_unchanged(self):
        chain={'history':[{'source':tool.previous.SOURCE,'literal':'pg3600/Pg3600/pg3490'}]}
        oracle='CHAIN='+repr(chain)+'\nSOURCE='+repr(tool.previous.SOURCE)+'\n'
        raw='SOURCE='+repr(tool.previous.SOURCE)+'\nTOOLS='+repr(tool.previous.TOOLS)+'\nORACLE='+repr(oracle)+'\nGUARD='+repr('history pg3600 '+tool.previous.SOURCE)+'\n'
        result=tool.bind(raw);tree=ast.parse(result);values={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)}
        self.assertEqual(tool.SOURCE,values['SOURCE']);self.assertEqual(tool.TOOLS,values['TOOLS'])
        self.assertEqual(oracle,values['ORACLE']);self.assertEqual('history pg3600 '+tool.previous.SOURCE,values['GUARD'])
        for key in ['context','emit','emit_receipt','sources']:self.assertIn(key,tool.namespace())
        for key in ['stage','run_action','main']:self.assertIn(key,dispatch.namespace())
        for key in ['entry','emit','payload']:self.assertIn(key,post.namespace())
        java='class Pg3600X {String source="'+tool.previous.SOURCE+'";}'
        self.assertIn('class Pg3822X',tool.final_bind(java));self.assertIn(tool.SOURCE,tool.final_bind(java))
        with self.assertRaises(ValueError):bind_preserving_payloads('ORACLE="x"\n__PGPT_IMMUTABLE_PAYLOAD_0__\n',lambda v:v)
        with self.assertRaises(ValueError):bind_preserving_payloads('ORACLE="x"\n',lambda v:v.replace('__PGPT_IMMUTABLE_PAYLOAD_0__','broken'))


if __name__=='__main__':unittest.main()
