"""Handwritten72→80 geometry vectors and exact one-shot protocol; no actual VM mutation."""
import ast
import copy
import json
from pathlib import Path
import types
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg5654_capacity_preflight_read as preflight
import pg5656_capacity_current_post as post
import pg5658_capacity_online_grow as grow


def vector():
    return {'label':'gpt','id':'D1D80BB0-6CC8-4F75-96D7-429EFFC6A7E7','device':'/dev/vda','unit':'sectors','firstlba':34,'lastlba':150994910,'sectorsize':512,
      'partitions':[{'node':'/dev/vda1','start':2324480,'size':148670431,'uuid':'F8A5DEDF-C7D3-42EA-96AA-30C2DB90705C','type':'root'},
        {'node':'/dev/vda13','start':227328,'size':2095104,'uuid':'boot','type':'boot'},
        {'node':'/dev/vda14','start':2048,'size':8192,'uuid':'bios','type':'bios'},
        {'node':'/dev/vda15','start':10240,'size':217088,'uuid':'efi','type':'efi'}]}


class Capacity(unittest.TestCase):
    def test_prompt_frame_is_strict_and_does_not_replay_host(self):
        for raw in('{"actualExit":0}\n',' \n[sudo: ] Password: \r\n{"actualExit":0}\n'):
            self.assertEqual({'actualExit':0},preflight.decode_host_frame(raw))
        for raw in('banner\n{"actualExit":0}', '{"actualExit":0}\n{"actualExit":0}', 'null', '{"actualExit":false}', '{"actualExit":1}', '[sudo: ] Password:'):
            with self.assertRaises(ValueError):preflight.decode_host_frame(raw)
        source=Path(preflight.__file__).read_text();tree=ast.parse(source)
        recovery=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='recover_v2')
        self.assertNotIn('previous.run(',ast.get_source_segment(source,recovery))

    def test_actual_chain_active_plus_three_backings_not_count_only(self):
        rows=[{'filename':p,'virtualSize':s}for p,s in[
          ('/home/mini/schubert-nk-pgpt/vm/pg2810-network-resume-cold-v1/active.qcow2',77309411328),
          ('/home/mini/schubert-nk-pgpt/vm/pg2200-outage-cold-v1/active.qcow2',51539607552),
          ('/home/mini/schubert-nk-pgpt/vm/pg1435-cold-v1/active.qcow2',51539607552),
          ('/home/mini/schubert-nk-pgpt/vm/pg1431/guest.qcow2',42949672960)]]
        preflight.qualify_layers(rows)
        for value in(None,rows[1:],rows+[rows[-1]],list(reversed(rows)),[{**rows[0],'virtualSize':85899345920},*rows[1:]],
          [rows[0],{**rows[1],'filename':'/foreign'},*rows[2:]]):
            with self.assertRaises(ValueError):preflight.qualify_layers(value)
        self.assertIn('qualify_layers(layers)',preflight.HOST)
        self.assertIn('os.O_ACCMODE==os.O_RDONLY',preflight.HOST)

    def run_geometry(self,after,mutation=None):
        before=vector();actual=copy.deepcopy(before)
        if after:actual['lastlba']+=16777216;actual['partitions'][0]['size']+=16777216
        if mutation:mutation(actual)
        class Private:
            def __truediv__(self,name):return self
            def read_bytes(self):return json.dumps(actual if self.after else before).encode()
        class Base:
            def __truediv__(self,name):
                p=Private();p.after='5658'in name;return p
        def command(args,timeout):
            if args[0].endswith('sfdisk'):return json.dumps({'partitiontable':actual}).encode()
            if args[0].endswith('blockdev'):return b'85899345920'if after else b'77309411328'
            return b'92978eec-7925-481e-8629-5b963d59ced1\n'
        def require(value):
            if value is not True:raise ValueError('independent geometry refused')
        exec(compile(post.geometry(after),'<independent literal geometry>','exec'),{'json':json,'subprocess':types.SimpleNamespace(check_output=command),
          'base':Base(),'free':20*1024**3 if after else 11*1024**3,'require':require})

    def test_before_literal(self):self.run_geometry(False)
    def test_after_exact_eight_gib(self):self.run_geometry(True)
    def test_root_start_rejected(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'][0].update(start=2324481))
    def test_root_uuid_rejected(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'][0].update(uuid='foreign'))
    def test_other_partition_rejected(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'][1].update(size=2095105))
    def test_wrong_delta_rejected(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'][0].update(size=165447646))
    def test_missing_partition_rejected(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'].pop())
    def test_table_id_rejected(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v.update(id=None))
    def test_emitted_programs_static_exact_commands_and_no_cleanup(self):
        host,guest=grow.lan_payload(),grow.guest_payload()
        for name,raw in(('host',host),('guest',guest),('before',post.payload()),('after',post.payload(True)),('hostRO',preflight.HOST),('guestRO',preflight.GUEST)):
            self.assertEqual(check(raw,name),0);compile(raw,name,'exec')
        calls=[n for n in ast.walk(ast.parse(host))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='rpc'and n.args and isinstance(n.args[0],ast.Constant)and n.args[0].value=='block_resize']
        self.assertEqual(1,len(calls));self.assertEqual({'node-name':None,'size':85899345920},{k.value:(None if isinstance(v,ast.Subscript)else ast.literal_eval(v))for k,v in zip(calls[0].args[1].keys,calls[0].args[1].values)})
        self.assertIn("old['node-name']=='#block113'",host);self.assertIn('oldThreeBackingMetadataUnchanged',host)
        self.assertIn("old['image']['virtual-size']==77309411328",host);self.assertIn("old['image']['backing-image']['virtual-size']==51539607552",host)
        commands=[ast.literal_eval(n.args[0])for n in ast.walk(ast.parse(guest))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='command']
        self.assertEqual([['/usr/bin/growpart','/dev/vda','1'],['/usr/sbin/resize2fs','/dev/vda1']],commands)
        self.assertGreater(guest.index('print(json.dumps(result))'),guest.index('for fd in reversed(held):os.close(fd)'))
        for forbidden in('qemu-img','--force','reboot(', 'poweroff(', 'unlink(', 'rmtree(', 'remove('):self.assertNotIn(forbidden,host+guest)
        for p in(preflight.__file__,post.__file__,grow.__file__,__file__):self.assertEqual(checkPath(p),0)
    def test_incomplete_or_bool_grow_refuses_post_before_connection(self):
        path=post.current.post.role.W/(post.GROW+'/manifest.safe.json')
        for result in(False,1,None):
            with patch.object(Path,'read_bytes',return_value=json.dumps({'actualExit':result}).encode()),patch.object(post.current,'authenticate_host')as connection:
                with self.assertRaises(ValueError):post.main(True)
                connection.assert_not_called()
        self.assertTrue(path.name.endswith('.json'))


if __name__=='__main__':unittest.main()
