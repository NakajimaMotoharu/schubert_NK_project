"""Second same-source live peer A01; authenticated issued receipt, not wrapper success."""
import ast
from pathlib import Path
from pg876_a01_current import code as previous
R=Path(__file__).resolve().parent
def code():
 raw=previous().replace('pg876','pg884').replace('PG876','PG884').replace('pg871','pg881').replace('pg872-ordinary-once-v1','pg882-ordinary-once-v1').replace('pg870-ordinary-before-v1','pg880-ordinary-before-v1')
 marker="assert (W/'pg882-ordinary-once-v1.exit').read_bytes()==b'0\\n'"
 assert raw.count(marker)==1
 raw=raw.replace(marker,"assert (W/'pg882-ordinary-once-v1.exit').read_bytes()==b'1\\n'\n    issuedProof=json.loads((W/'pg883-issued-identity-v1.safe.json').read_bytes());assert issuedProof['actualExit']==0 and issuedProof['issuedClientExit']==0 and issuedProof['wrapper882ActualExit']==1 and issuedProof['wrapperNormalInferred']is False and issuedProof['productionSource']==SOURCE")
 ast.parse(raw);return raw
if __name__=='__main__':
 env={'__file__':str(R/'pg884_a01_current.py'),'__name__':'current862_second_A01'};exec(compile(code(),'<new live sameparent75f A01>','exec'),env);env['main']()
