import json
import unittest
import pg5150_native_fd_bytecode as role


class NativeProof(unittest.TestCase):
    def test_original_real_manifest_envelope_and_incomplete_foreign_reference_rejected(self):
        reference=json.loads(role.selected.FACTORY_FULL.read_bytes())
        self.assertEqual(len(role.reference_hashes(reference)),1654)
        for bad in ({},reference['result'],{**reference,'actualExit':1},
                    {**reference,'result':{**reference['result'],'productionSource':'foreign'}}):
            with self.assertRaises(ValueError):role.reference_hashes(bad)

    def test_old_class_identity_must_match_original_whole_reference_not_merely_exist(self):
        role.require_reference({'class':'fixed-old-sha'},'class','fixed-old-sha')
        for expected,actual in (({},'fixed-old-sha'),({'class':'fixed-old-sha'},'foreign-sha')):
            with self.assertRaises(ValueError):role.require_reference(expected,'class',actual)

    def test_package_private_header_is_eligible_but_close_proof_is_not(self):
        for prefix in ('','public ','private '):
            wanted={'header':prefix+'void close() throws IOException;'}
            self.assertIs(role.dual_close([wanted,{'header':'void closeProof();'}]),wanted)
            with self.assertRaises(ValueError):role.dual_close([wanted,wanted])
        with self.assertRaises(ValueError):role.dual_close([{'header':'void closeProof();'}])

    def test_preallocation_and_exact_factory_count_cannot_be_inferred_from_constructor_alone(self):
        valid=[{'header':'factory','ops':[(0,'new','File$Owner'),(3,'dup',''),
               (4,'invokespecial','File$Owner."<init>":(Supplier)V'),(7,'areturn','')]}]
        self.assertEqual(role.constructor_factories(valid,'File$Owner',1)[0]['allocationPc'],0)
        for methods,count in ((valid,2),([{'header':'bad','ops':valid[0]['ops'][1:]}],1)):
            with self.assertRaises(ValueError):role.constructor_factories(methods,'File$Owner',count)

    def test_nested_debug_equivalence_retains_every_opcode_handler_and_literal(self):
        original=[{'header':'void close();','ops':[(0,'ldc','#1 // String literal'),(2,'return','')],'handlers':[]}]
        changed=[{'header':'void close();','ops':[(0,'ldc','#92    // String literal'),(2,'return','')],'handlers':[]}]
        role.same_methods(original,changed)
        for row in ({**changed[0],'ops':[(0,'ldc','#92 // String literal '),(2,'return','')]},
                    {**changed[0],'handlers':[(0,2,2,'any')]},
                    {**changed[0],'header':'void other();'}):
            with self.assertRaises(ValueError):role.same_methods(original,[row])


if __name__=='__main__':unittest.main()
