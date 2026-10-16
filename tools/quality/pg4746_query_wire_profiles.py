"""Read-only non-secret layout/length/kind diagnostics; no wire/id/plaintext export."""
import types
from pyflakes.api import check
import pg4744_same_day_query_preflight as prior
import pg4250_current_admission_image as transport
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4746-query-wire-profiles-v1'


def payload():
    raw=prior.payload();start=raw.index("before=json.loads(raw)['rows'];now=")
    raw=raw[:start]+r'''
before=json.loads(raw)['rows'];profiles=[]
try:
 for row in before['schubert.request_inbox']:
  if row['response_layout_id']not in {'UDTRSP01','QSDRSP01','NTSRSP01'}:continue
  body=plaintext(row,KEY)
  try:
   kind=bytes(body[22:24]);kind=kind.decode()if re.fullmatch(b'[A-Z]{2}',kind)else'UNKNOWN'
   profiles.append({'layout':row['response_layout_id'],'byteLength':len(body),'canonicalPrefix':body[:11]==b'SCHBNK01001','headerLayoutVersion':body[11:22]==(row['response_layout_id']+'001').encode(),'kind':kind,'referenceEnvelope':body[:6]==b'NKREF1'})
  finally:body[:]=b'\0'*len(body)
finally:KEY[:]=b'\0'*len(KEY)
print(json.dumps({'actualExit':0,'profiles':profiles,'rawExported':False,'rootStartIssued':False,'formalAccepted':False}))
'''
    if check(raw,'<nonsecret query shape>'):raise ValueError('complete emitted namespace')
    compile(raw,'<limited query shape>','exec');return raw


def main():
    authenticate_host()
    execute=types.FunctionType(transport.execute.__code__,{**vars(transport),'SOURCE':prior.current.SOURCE})
    return execute(SLOT,payload(),45)


if __name__=='__main__':raise SystemExit(main())
