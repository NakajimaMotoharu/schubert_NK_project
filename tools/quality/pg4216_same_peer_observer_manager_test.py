import unittest
from unittest.mock import patch
from types import SimpleNamespace
import pg4216_same_peer_observer_manager as p


class ManagerProjectionTest(unittest.TestCase):
    def fixture(self):
        return ({'Id':'schubert-nk-api.service','LoadState':'loaded','ActiveState':'active','SubState':'running','Job':(0,'/'),'InvocationID':bytes.fromhex('1234567890abcdef1234567890abcdef')},
                {'Type':'simple','Restart':'no','KillMode':'mixed','Result':'success','RemainAfterExit':False,'SendSIGKILL':False,
                 'MainPID':758821,'ControlPID':0,'ExecMainCode':0,'ExecMainStatus':0,'ExecMainStartTimestampMonotonic':130044470000,'ExecMainExitTimestampMonotonic':0})

    def test_literal_eighteen_fields_and_job_invocation_boundaries(self):
        u,s=self.fixture();value=p.projection('schubert-nk-api.service',u,s)
        expected={'Id':'schubert-nk-api.service','LoadState':'loaded','ActiveState':'active','SubState':'running','Job':'','InvocationID':'1234567890abcdef1234567890abcdef',
                  'Type':'simple','Restart':'no','KillMode':'mixed','Result':'success','RemainAfterExit':'no','SendSIGKILL':'no','MainPID':'758821','ControlPID':'0','ExecMainCode':'0','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'130044470000','ExecMainExitTimestampMonotonic':'0'}
        self.assertEqual(expected,value)
        self.assertEqual('255',p.projection('schubert-nk-api.service',{**u,'Job':(255,'/org/freedesktop/systemd1/job/255')},s)['Job'])
        for inv in [b'',bytes(16)]:self.assertEqual('',p.projection('schubert-nk-api.service',{**u,'InvocationID':inv},s)['InvocationID'])

    def test_every_required_member_missing_null_or_wrong_signature_rejected(self):
        u,s=self.fixture()
        for target,source in [('unit',u),('service',s)]:
            for key in source:
                for value in [None]:
                    wrong={**source,key:value}
                    with self.subTest(target=target,key=key),self.assertRaises(ValueError):p.projection('schubert-nk-api.service',wrong if target=='unit'else u,wrong if target=='service'else s)
                wrong={k:v for k,v in source.items()if k!=key}
                with self.subTest(missing=key),self.assertRaises(ValueError):p.projection('schubert-nk-api.service',wrong if target=='unit'else u,wrong if target=='service'else s)
        for key,value in [('Id','caddy.service'),('LoadState','not-found'),('Job',(True,'/')),('Job',(0,'/other')),('Job',(1,'/')),('InvocationID',b'x'),('ActiveState','active\n')]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):p.projection('schubert-nk-api.service',{**u,key:value},s)
        for key in p.SERVICE_INT:
            for value in [True,-1,18446744073709551616]:
                with self.subTest(key=key,value=value),self.assertRaises(ValueError):p.projection('schubert-nk-api.service',u,{**s,key:value})

    def native_fixture(self):
        types=SimpleNamespace(**{name:type(name,(base,),{})for name,base in {'Dictionary':dict,'String':str,'Struct':tuple,'UInt32':int,'Int32':int,'UInt64':int,'ObjectPath':str,'ByteArray':bytes,'Array':list,'Byte':int,'Boolean':int}.items()})
        u,s=self.fixture();nu=types.Dictionary({k:types.String(v)for k,v in u.items()if k not in {'Job','InvocationID'}})
        nu.update(Job=types.Struct((types.UInt32(0),types.ObjectPath('/'))),InvocationID=types.ByteArray(u['InvocationID']))
        ns=types.Dictionary({k:types.String(s[k])for k in p.SERVICE_TEXT})
        ns.update({k:types.Boolean(int(s[k]))for k in p.SERVICE_BOOL})
        ns.update({k:(types.UInt32 if k in {'MainPID','ControlPID'}else types.Int32 if k in {'ExecMainCode','ExecMainStatus'}else types.UInt64)(s[k])for k in p.SERVICE_INT})
        return types,nu,ns

    def test_native_signatures_are_checked_before_conversion(self):
        types,u,s=self.native_fixture();self.assertEqual(self.fixture()[1]['MainPID'],int(p.native_projection('schubert-nk-api.service',u,s,types)['MainPID']))
        for key,value in [('MainPID',types.Int32(758821)),('RemainAfterExit',types.String('false')),('ExecMainCode',types.UInt32(0))]:
            with self.subTest(key=key),self.assertRaises(ValueError):p.native_projection('schubert-nk-api.service',u,types.Dictionary({**s,key:value}),types)
        with self.assertRaises(ValueError):p.native_projection('schubert-nk-api.service',types.Dictionary({**u,'InvocationID':'not bytes'}),s,types)

    def reader(self,mode='normal'):
        types,u,s=self.native_fixture();calls=[]
        class Bus:
            def call_blocking(self,destination,path,interface,method,signature,args,timeout):
                calls.append((destination,path,method,args,timeout))
                if method=='GetNameOwner':return types.String(':1.2'if mode=='changed'and sum(c[2]=='GetNameOwner'for c in calls)>1 else':1.1')
                if method=='GetConnectionUnixProcessID':return types.UInt32(2 if mode=='foreign'else 1)
                if method=='GetConnectionUnixUser':return types.UInt32(0)
                if method=='GetUnit':return types.ObjectPath('/foreign'if mode=='path'else'/org/freedesktop/systemd1/unit/schubert_2dnk_2dapi_2eservice')
                if method=='GetAll':return u if args==('org.freedesktop.systemd1.Unit',)else s
                raise AssertionError('no unexpected or mutating RPC')
            def close(self):calls.append(('close',))
        reader=object.__new__(p.NativeReader);reader.bus=Bus();reader.closed=False
        return types,reader,calls

    def test_same_peer_full_projection_and_no_fallback_on_foreign_owner_or_path(self):
        for mode in ['normal','foreign','changed','path']:
            types,reader,calls=self.reader(mode)
            with self.subTest(mode=mode),patch.dict('sys.modules',{'dbus':types}):
                if mode=='normal':
                    self.assertEqual('758821',reader.read('schubert-nk-api.service')['MainPID'])
                    self.assertEqual(['GetNameOwner','GetConnectionUnixProcessID','GetConnectionUnixUser','GetUnit','GetAll','GetAll','GetNameOwner','GetConnectionUnixProcessID','GetConnectionUnixUser'],[c[2]for c in calls])
                    self.assertTrue(all(c[0]==':1.1'for c in calls if c[2]=='GetAll'))
                else:
                    with self.assertRaises(ValueError):reader.read('schubert-nk-api.service')
                self.assertTrue(all(0<c[4]<=5 for c in calls))
                reader.close()
                with self.assertRaises(ValueError):reader.close()

    def test_expired_or_closed_read_sends_no_rpc(self):
        unused,reader,calls=self.reader()
        with patch.object(p.time,'monotonic',return_value=10):
            with self.assertRaises(ValueError):reader.rpc('a','b','c','d','',(),10)
            reader.closed=True
            with self.assertRaises(ValueError):reader.rpc('a','b','c','d','',(),11)
        self.assertEqual([],calls)


if __name__=='__main__':unittest.main()
