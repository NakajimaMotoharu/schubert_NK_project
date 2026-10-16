"""UI236 literal byte vectors, independent crypto and all24 same-day deletion/skip."""
import copy
import unittest
import zlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pg2078_current_same_day_rows_oracle_test import SameDay,RUN,CUT,UPPER
import pg4742_same_day_query_oracle as target


class Queries(unittest.TestCase):
    def fixture(self,rid='QSDRSP01',error=False):
        row=dict(message_id='11111111-2222-4333-8444-555555555555',request_layout_id=rid[:3]+'REQ01',request_version='001',response_layout_id=rid,response_version='001',owner_user_id=1,response_key_version='v1',fingerprint_key_version='v1',request_fingerprint_hmac='a'*64,processing_state='ERROR'if error else'COMPLETED',result_ref_type='NONE',result_ref_id=None,result_ref_uuid=None,operation_token=None,created_at='2026-10-11T03:00:00Z',completed_at='2026-10-11T03:00:01Z',expires_at='2026-10-12T03:00:01Z')
        ns=target.namespace(bytes(32));layout=ns['LAYOUTS'][rid]
        body=bytearray(b' '*(256+layout['dataLength']))
        for offset,value in [(0,('SCHBNK01001'+rid+'001SS').encode()),(24,b'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'),(60,row['message_id'].encode()),(96,b'20261011120001000'),(113,b'a'*64),(177,b'0256'),(181,('%06d'%layout['dataLength']).encode()),(187,('%06d'%layout['recordLength']).encode()),(193,b'000000'),(199,('%09d'%len(body)).encode()),(208,b'0104'if error else b'0000')]:body[offset:offset+len(value)]=value
        if rid=='QSDRSP01':
            for offset,value in [(256,b'000000000001'),(268,b'01ARZ3NDEKTSV4RRFFQ69G5FAV'),(294,b'Owner'),(358,b'UNANSWERED'),(370,b'Question'),(8562,b'20261011120000000')]:body[offset:offset+len(value)]=value
        else:body[256:298]=b'000001050000000000000001000000000000000000'
        if error:
            for name,offset,length,kind,required in layout['dataFields']:body[256+offset:256+offset+length]=(b'0'if kind=='N'else b' ')*length
        nonce=bytes(12);encrypted=AESGCM(bytes(32)).encrypt(nonce,zlib.compress(body),ns['aad'](row))
        row['response_body_encrypted']='\\x'+(b'NKENC1\1\2v1'+nonce+encrypted).hex()
        return ns,row,body

    def test_literal_query_crypto_semantics_and_corruptions(self):
        for rid,error in [('QSDRSP01',False),('QSDRSP01',True),('NTSRSP01',False)]:
            ns,row,body=self.fixture(rid,error);layout=ns['LAYOUTS'][rid]
            ns['validate_query'](row,body,layout)
            self.assertEqual(body,ns['plaintext'](row,bytes(32)))
            for offset in [0,60,96,177,181,193,208,212,256]:
                bad=bytearray(body);bad[offset]=ord('!')
                with self.subTest(rid=rid,offset=offset),self.assertRaises(ValueError):ns['validate_query'](row,bad,layout)

    def test_complete_same_day_retains_notification_deletes_query_and_protects_missing_session(self):
        ns,row,body=self.fixture();before,after=SameDay().fixture()
        before['schubert.request_inbox'].append(row)
        notification=dict(id=1,state='CANCELLED',state_changed_at='2026-10-12T00:00:00Z',question_id=77)
        before['schubert.notifications']=[notification];after['schubert.notifications']=copy.deepcopy(before['schubert.notifications'])
        progress=after['schubert.inbox_inspection_progress'][0];progress.update(inspected_count=2,deleted_count=1,after_message_id=row['message_id'])
        batch=next(r for r in after['schubert.batch_runs']if r['run_id']==RUN and r['step']=='CLEAN_INBOX_OUTBOX');batch.update(target_count=3,success_count=2)
        result=ns['qualify'](before,after,RUN,CUT,UPPER)
        self.assertEqual(7,result['newSkippedSteps']);self.assertEqual(1,result['expectedInboxProtected'])
        bad=copy.deepcopy(after);bad['schubert.notifications']=[]
        with self.assertRaises(ValueError):ns['qualify'](before,bad,RUN,CUT,UPPER)
        bad=copy.deepcopy(after);bad['schubert.request_inbox'].append(row)
        with self.assertRaises(ValueError):ns['qualify'](before,bad,RUN,CUT,UPPER)
        bad=copy.deepcopy(after);bad['schubert.inbox_inspection_progress'][0]['deleted_count']=0
        with self.assertRaises(ValueError):ns['qualify'](before,bad,RUN,CUT,UPPER)

    def test_literal_scope_frame_admin_user_legacy_and_forbidden_routes(self):
        ns,row,body=self.fixture()
        for scope in [b'U',b'A']:
            frame=bytearray(b'NKQRY1\0'+scope+body)
            self.assertEqual(body,ns['query_wire']('QSDRSP01',frame))
            ns['validate_query'](row,ns['query_wire']('QSDRSP01',frame),ns['LAYOUTS']['QSDRSP01'])
        self.assertEqual(body,ns['query_wire']('QSDRSP01',body))
        for rid,frame in [('NTSRSP01',bytearray(b'NKQRY1\0A'+body)),('QSDRSP01',bytearray(b'NKQRY1\0X'+body)),('QSDRSP01',bytearray(b'NKQRY1\0A')),('QSDRSP01',bytearray(b'NKQRY0\0A'+body))]:
            with self.assertRaises(ValueError):ns['query_wire'](rid,frame)


if __name__=='__main__':unittest.main()
