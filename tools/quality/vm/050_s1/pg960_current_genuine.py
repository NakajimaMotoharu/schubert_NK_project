"""New eeae/0bb4 parent genuine only, old Root completed results never reused."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg875_capture_genuine import payload as previous,W,P
R=Path(__file__).resolve().parent
def payload():
    raw=previous()
    values=(('19022204-8a9e-418d-ba2a-9967ff923dc2','eeae04ea-713c-4f2d-888d-358fb4bed274'),('2026-10-09T18:28:14.612111Z','2026-10-09T23:31:22.087768Z'),('cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d','091663ce-1cf4-47e7-8311-218ebb0c8653'),('3592151','3844442'),('09167719cb0445fea8da5a6fdbaa3b0f','0bb4d6f3b9e74cdc91c553748a4cd018'),('189291','213904'),('183192933299','201380374989'),('pg872-ordinary-once-v1','pg957-ordinary-once-v1'),('pg870-ordinary-before-v1','pg954-ordinary-before-v1'),('a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980','72d51bd2b7db519b89160881b6b6a1322ee4d8ef68d94bc6b23e6c9724cdb3aa'),('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),('0.1.0-PG862','0.1.0-PG932'),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'),("len(baseline['rows']['schubert.batch_runs'])==564","len(baseline['rows']['schubert.batch_runs'])==584"),('pg875-completed-readonly-v1','pg960-completed-readonly-v1'),('PG875-completed-readonly-v1','PG960-completed-readonly-v1'))
    for a,b in values:assert a in raw,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
def source():
    raw=(R/'pg875_capture_genuine.py').read_text();raw=raw[raw.index("if __name__=='__main__':"):]
    return raw.replace('pg875','pg960').replace('PG875','PG960').replace('pg871','pg956').replace('pg876','pg961')
if __name__=='__main__':
    exec(compile(source(),'<960 actual new current genuine>','exec'),globals())
