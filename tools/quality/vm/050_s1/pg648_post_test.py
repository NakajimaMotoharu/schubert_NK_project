"""Literal independent full19 retirement oracle and readonly bindings."""
import copy
import hashlib
import unittest
from pg647_retirement_contract_test import fixture
from pg648_post_contract import retired
from pg648_retirement_post import payload


def full_fixture():
    a,b,_=fixture()
    for key in 'backup bootstrapOldProofs bootstrapTools credentials dependencies oldProofs parentPid1 pid1Stop startup current approval'.split():
        a[key]=b[key]={'literal':'unchanged'}
    argv='/usr/bin/java fixed MorningProcessMain --resume e49243d5-de84-4714-8612-6912ddc17e9e'
    raw=('# SSC228: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv+'\n').encode()
    a['runtime']['sha256']=hashlib.sha256(raw).hexdigest()
    return a,b


class Oracle(unittest.TestCase):
    def test_literal_normal_nineteen_fields(self):
        a,b=full_fixture();self.assertEqual(len(a),19);self.assertTrue(retired(a,b))

    def test_each_immutable_field_and_runtime_source_oracle(self):
        a,b=full_fixture()
        for key in a.keys()-{'configuration','runtime','unitFiles','caddyPre'}:
            bad=copy.deepcopy(b);bad[key]=None
            with self.subTest(field=key),self.assertRaises(ValueError):retired(a,bad)
        for kind in ('runtime','hash','extra','argv','missing'):
            old,new=full_fixture()
            if kind=='runtime':new['runtime']=old['runtime']
            if kind=='hash':old['runtime']['sha256']='foreign'
            if kind=='extra':new['unitFiles']['foreign']={}
            if kind=='argv':new['configuration']['schubert-nk-morning-controller.service']['ExecStart']=old['configuration']['schubert-nk-morning-controller.service']['ExecStart']
            if kind=='missing':new.pop('rows')
            with self.subTest(kind=kind),self.assertRaises(ValueError):retired(old,new)

    def test_readonly_twice_current_parent_stop_source_resources(self):
        v=payload();compile(v,'<new post>','exec')
        for literal in ('==504', '==18', 'pg647-runtime-retirement-v1', 'pg642-native-stop-v1',
                        '293d218b06454bd1a8ff350bb93de2d5', 'retired(before,after)',
                        'stat.S_IFDIR|0o755,2', 'for repeat in range(2)', 'manager.UnrefUnit(u)', 'bus.close()',
                        'repeatable read read only', "lines[-2:]==[b'0',b'0']"):
            self.assertIn(literal,v)
        for forbidden in ('daemon-reload', '.unlink(', "['systemctl','start'", "['systemctl','stop'"):
            self.assertNotIn(forbidden,v)


if __name__=='__main__':unittest.main()
