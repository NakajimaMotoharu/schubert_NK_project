"""Qualified current769 Root eight + actual ADMIN two, frozen1279 host; no old source."""
from pathlib import Path
import pg992_current_bootstrap_native_counter as previous
R=Path(__file__).resolve().parent

def source():
    raw=previous.source()
    changes=(
        ('40ef6e894573d2ffab1d1732124960f9c98d5f97','769ddb15cd735c25fef581b5f9850ef9d0053c0f'),
        ('pg983','pg1396'),('pg989-bootstrap-post-v4','pg1400-existing-admin-independent-post-v1'),('PG989-bootstrap-post-v4','PG1400-existing-admin-independent-post-v1'),
        ('pg972-current-eight-native-v2','pg1341-published-eight-native-v1'),
        ('043e7c88400840fd945512548c70a2d8dda2e53a6d9e2f6b5b5855bd0bab3d8b','99ace9ae4497d33c331700ec656502e543de2e64192ba5350b4f1dfa456f4d71'),
        ('pg992-current-ten-native-v1','pg1401-current-bootstrap-ten-native-v1'),('PG992-current-ten-native-v1','PG1401-current-bootstrap-ten-native-v1'),
        ('pg926-body-six-host-v1','pg1279-held-channel-six-host-v1'),("h['tests']==3560","h['tests']==3569"),
        ("'hostRun':'PG926'","'hostRun':'PG1279'"),('incrementalVsPG972','incrementalVsPG1341'))
    for old,new in changes:
        if old not in raw:raise ValueError('complete current same-source native binding required')
        raw=raw.replace(old,new)
    compile(raw,'<qualified current ADMIN ten native>','exec');return raw

if __name__=='__main__':exec(compile(source(),'<new current769 ten native only>','exec'),{'__file__':str(R/'pg1401_current_bootstrap_ten_native.py'),'__name__':'__main__'})
