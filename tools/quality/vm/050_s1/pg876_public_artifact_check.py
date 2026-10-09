"""Fixed independent Current A01 schema/DIF001 only and explicit secret fields."""
import copy,hashlib,json
from pathlib import Path
T=Path(__file__).resolve().parents[4]
def check(actual,baseline):
    assert isinstance(actual,dict)and isinstance(baseline,dict)and set(actual)==set(baseline)
    expected=copy.deepcopy(baseline);expected['title']='schubert NK - ログイン'
    assert actual==expected and actual['status']=='PASS'and actual['statusCode']==200
    assert actual['csrf']=='<TOKEN>'and actual['passwordValue']==''
    assert actual['passwordAutocomplete']=='current-password'and actual['usernameAutocomplete']=='username'
    assert not any(k.lower()in ('set-cookie','cookie','authorization')for k in actual['securityHeaders'])
if __name__=='__main__':
    b=T/'program/characterization/baseline/current/artifacts/CHR-A01.json';raw=b.read_bytes();assert hashlib.sha256(raw).hexdigest()=='df68edfbd59d60fc0d87fcce818401788740153c8b630f790d785f6414001993'
    baseline=json.loads(raw);a=T/'program/characterization/reports/nk/PG876-native-a01-v1/artifacts/CHR-A01.json';actual=json.loads(a.read_bytes());check(actual,baseline)
    for key,value in (('csrf','raw'),('passwordValue','raw'),('passwordAutocomplete','foreign'),('unknown','raw')):
        fixture=copy.deepcopy(actual);fixture[key]=value;caught=False
        try:check(fixture,baseline)
        except AssertionError:caught=True
        assert caught
    print(json.dumps({'case':'CHR-A01','actualCheckExit':0,'source':'e01612fcd7f2752df5ae0836b78538fd5e87f120','artifactSha256':hashlib.sha256(a.read_bytes()).hexdigest(),'baselineUnchanged':True,'DIF001TitleOnly':True,'secretScan0':True,'formalAccepted':False}))
