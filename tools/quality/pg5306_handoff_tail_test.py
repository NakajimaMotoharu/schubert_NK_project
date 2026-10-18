import unittest
import pg5306_permit_intent_bytecode as role


class TypedReturn(unittest.TestCase):
    def test_only_declaration_matched_cast_then_return_is_permitted(self):
        method={'header':'private static p.Owner create() throws java.io.IOException;',
            'ops':[(0,'invokestatic','handoff'),(3,'checkcast','#5 // class p/Owner'),(6,'areturn','')]}
        self.assertEqual(role.returned_owner(method,0),{'declaredReturnType':'p.Owner','checkcastPc':3,'returnPc':6})
        bad=[[(3,'checkcast','#5 // class p/Foreign'),(6,'areturn','')],
             [(3,'checkcast','#5 // class p/Owner'),(5,'invokevirtual','callback'),(6,'areturn','')],
             [(3,'new','object'),(6,'areturn','')],[(3,'putfield','owner'),(6,'areturn','')],
             [(3,'areturn','')]]
        for tail in bad:
            with self.assertRaises(ValueError):role.returned_owner({**method,'ops':[method['ops'][0],*tail]},0)


if __name__=='__main__':unittest.main()
