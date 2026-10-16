"""Independent SSH argument, fixed phase and old-failure receipt oracles; no VM actions."""
import ast
import shlex
import unittest
import pg4188_exact_partial_recover as subject


class CoordinatorTest(unittest.TestCase):
    def test_remote_shell_roundtrip_keeps_program_and_ack_separate(self):
        hashes={n:str(i)*64 for i,n in enumerate(['keeper.py','partial.py','post.py'])}
        for name,mode in [('keeper.py','recover'),('partial.py','inspect'),('partial.py','recover'),('post.py',None)]:
            args=subject.remote_args(name,hashes,mode)
            self.assertEqual(subject.SSH,args[:-1])
            parsed=shlex.split(args[-1])
            self.assertEqual(['sudo','-n','python3','-B','-c'],parsed[:5])
            self.assertEqual([mode]if mode else[],parsed[6:])
            tree=ast.parse(parsed[5]);constants={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body[:3]}
            self.assertEqual({'ROOT':subject.GUEST,'EXPECTED':hashes,'NAME':name},constants)
            self.assertNotIn('CONTINUE',parsed[5])
        for name,mode in [('keeper.py','proof'),('post.py','recover'),('../keeper.py','recover'),('partial.py',None)]:
            with self.assertRaises(ValueError):subject.remote_args(name,hashes,mode)

    def test_actual_old143_never_normalized_or_transferred_from_other_run(self):
        receipt={'actualExit':143,'oldParentNormal':False,'formalAccepted':False,
                 'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
                 'payloadSha256':'5fdbfff67a9aa71aeab60ae897a4e9a23f3038ae7dc6f86dc5f648c201116fe3'}
        self.assertEqual(receipt,subject.original_receipt(receipt))
        for key,value in [('actualExit',0),('actualExit',True),('oldParentNormal',True),('formalAccepted',True),('source','old'),('payloadSha256','other')]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):subject.original_receipt({**receipt,key:value})
        for key in receipt:
            with self.subTest(missing=key),self.assertRaises(ValueError):subject.original_receipt({k:v for k,v in receipt.items()if k!=key})


if __name__=='__main__':unittest.main()
