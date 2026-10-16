"""Independent preservation of complete nested Root/Browser oracle and historical data."""
import ast
import unittest
from pyflakes.api import check
import pg3870_current_resume_composite as composite
import pg3872_current_resume_parent_projection as parent


def constants(raw):
    return{node.targets[0].id:ast.literal_eval(node.value)for node in ast.parse(raw).body if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in {'ORACLE','GUARD','CHAIN','ROOT_ORACLE','BROWSER_ORACLE'}}


class WholeComposite(unittest.TestCase):
    def test_nested_current_resume_oracles_and_old_data_stay_exact(self):
        value=composite.root.live();binding={**value['binding'],'rootPid':value['rootPid']}
        original=composite.root.seal_payload(binding)
        chain={'before':{'history':[{'source':'4856b3fcaeb4cae983d77757a38dc0bf56a693e2','run':'0dc63b79-3f9a-450c-b2a6-56f86272d272'}]},'after':{'history':[]},'context':{}}
        raw=composite.compose(original,chain,'b'*64);self.assertEqual(0,check(raw,'<current resume complete composite>'))
        outer=constants(raw);inner=constants(outer['ORACLE']);self.assertEqual(chain,inner['CHAIN'])
        self.assertEqual(constants(original)['GUARD'],outer['GUARD'])
        self.assertEqual(constants(original)['ORACLE'],inner['ROOT_ORACLE'])
        for text in [composite.SOURCE,composite.BOM,'/'+composite.root.SEAL+'/before.private.json',"require(new==CHAIN['after'])"]:self.assertIn(text,outer['ORACLE'])
        projected=parent.payload('a'*64,composite.BOM);ast.parse(projected);self.assertIn(composite.SLOT,projected);self.assertNotIn('pg3816-',projected)
        with self.assertRaises(ValueError):parent.payload('a'*64,'f'*64)


if __name__=='__main__':unittest.main()
