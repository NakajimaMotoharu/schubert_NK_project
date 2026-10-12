"""Literal UI236 golden, independent emitted namespace, reference rollback negatives."""
import ast
import unittest
from pg1768_next_day_inbox_oracle import payload


class Inbox(unittest.TestCase):
    def test_golden_user_reference_and_each_corrupt_region(self):
        raw=payload();tree=ast.parse(raw);nodes=[]
        for n in tree.body:
            if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CUT'for t in n.targets):break
            nodes.append(n)
        env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<emitted independent oracle>','exec'),env)
        row={'message_id':'11111111-1111-4111-8111-111111111111','request_layout_id':'UPWREQ01','response_layout_id':'UPWRSP01','request_version':'001','response_version':'001','processing_state':'COMPLETED','result_ref_type':'USER','owner_user_id':1,'result_ref_uuid':None,'result_ref_id':7,'operation_token':'33333333-3333-4333-8333-333333333333','fingerprint_key_version':'v1','request_fingerprint_hmac':'a'*64,'created_at':'2026-10-01T00:00:00Z','completed_at':'2026-10-01T00:00:01Z','expires_at':'2026-10-08T00:00:01Z'}
        wire=bytearray(b'SCHBNK01001UPWRSP01001SS'+b'22222222-2222-4222-8222-222222222222'+row['message_id'].encode()+b'20261001090001000'+b'a'*64+b'0256'+b'000024'+b'000000'+b'000000'+b'000000280'+b'0000'+b' '*44+b'000000000007000000003'+b' '*3)
        self.assertEqual(280,len(wire));env['validate_upw'](row,wire,[{'id':7,'version':4}])
        for offset in [0,11,22,60,96,113,177,181,187,208,212,256,268,277]:
            bad=bytearray(wire);bad[offset]=ord('!')
            with self.subTest(offset=offset),self.assertRaises(ValueError):env['validate_upw'](row,bad,[{'id':7,'version':4}])
        for users in [[],[{'id':7,'version':2}],[{'id':7,'version':None}],[{'id':7,'version':3},{'id':7,'version':3}]]:
            with self.assertRaises(ValueError):env['validate_upw'](row,wire,users)


if __name__=='__main__':unittest.main()
