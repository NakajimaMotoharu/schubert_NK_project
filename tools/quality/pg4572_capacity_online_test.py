"""Independent geometry vectors, rejection mutations and exact one-shot programs."""
import ast
import copy
import json
import types
import unittest
from unittest.mock import Mock
from pyflakes.api import check
import pg4570_capacity_current_post as post
import pg4572_capacity_online_grow as grow


class Capacity(unittest.TestCase):
    def vector(self):
        return {'label':'gpt','id':'D1D80BB0-6CC8-4F75-96D7-429EFFC6A7E7','device':'/dev/vda','unit':'sectors','firstlba':34,'lastlba':117440478,'sectorsize':512,
          'partitions':[{'node':'/dev/vda1','start':2324480,'size':115115999,'uuid':'F8A5DEDF-C7D3-42EA-96AA-30C2DB90705C','type':'root'},
            {'node':'/dev/vda13','start':227328,'size':2095104,'uuid':'boot','type':'boot'},
            {'node':'/dev/vda14','start':2048,'size':8192,'uuid':'bios','type':'bios'},
            {'node':'/dev/vda15','start':10240,'size':217088,'uuid':'efi','type':'efi'}]}

    def run_geometry(self,after,mutation=None):
        before=self.vector();actual=copy.deepcopy(before)
        if after:actual['lastlba']+=33554432;actual['partitions'][0]['size']+=33554432
        if mutation:mutation(actual)
        class Private:
            def __truediv__(self,name):return self
            def read_bytes(self):return json.dumps(actual if self.which=='after'else before).encode()
        class Base:
            def __truediv__(self,name):
                v=Private();v.which='after'if '4572'in name else 'before';return v
        def command(args,bound):
            if args[0].endswith('sfdisk'):return json.dumps({'partitiontable':actual}).encode()
            if args[0].endswith('blockdev'):return b'77309411328'if after else b'60129542144'
            return b'92978eec-7925-481e-8629-5b963d59ced1\n'
        def require(value):
            if value is not True:raise ValueError('independent geometry refused')
        raw=post.geometry(after)
        # Real block is inside a retained scope; remove exactly its one outer indent.
        raw='\n'.join(line[1:]for line in raw.splitlines())
        ns={'json':json,'command':command,'require':require,'save_private':Mock(),'base':Base(),
            'os':types.SimpleNamespace(statvfs=lambda path:types.SimpleNamespace(f_bavail=50_000_000 if after else 2_000_000,f_frsize=4096))}
        exec(compile(raw,'<actual independent capacity geometry>','exec'),ns)
        self.assertEqual(2,ns['save_private'].call_count)

    def test_before_literal(self):self.run_geometry(False)
    def test_after_exact_sixteen_gib(self):self.run_geometry(True)
    def test_reject_root_start(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'][0].update(start=2324481))
    def test_reject_root_uuid(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'][0].update(uuid='foreign'))
    def test_reject_other_partition(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'][1].update(size=2095105))
    def test_reject_wrong_delta(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'][0].update(size=148670430))
    def test_reject_table_id(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v.update(id=None))
    def test_reject_missing_partition(self):
        with self.assertRaises(ValueError):self.run_geometry(True,lambda v:v['partitions'].pop())
    def test_actual_payloads_static_and_mutations(self):
        host=grow.lan_payload();guest=grow.guest_payload()
        for name,raw in [('host',host),('guest',guest),('pre',post.payload()),('post',post.payload(True))]:
            self.assertEqual(0,check(raw,name));compile(raw,name,'exec')
        calls=[n for n in ast.walk(ast.parse(host))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='rpc'and n.args and isinstance(n.args[0],ast.Constant)and n.args[0].value=='block_resize']
        self.assertEqual(1,len(calls));self.assertEqual(77309411328,ast.literal_eval(calls[0].args[1].values[1]))
        self.assertIn("old['node-name']=='#block113'",host)
        self.assertIn("old['image']['backing-image']['virtual-size']==51539607552",host)
        self.assertIn('oldThreeBackingMetadataUnchanged',host)
        commands=[ast.literal_eval(n.args[0])for n in ast.walk(ast.parse(guest))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='command']
        self.assertEqual([['/usr/bin/growpart','/dev/vda','1'],['/usr/sbin/resize2fs','/dev/vda1']],commands)
        self.assertGreater(guest.index('print(json.dumps(result))'),guest.index('for fd in reversed(held):os.close(fd)'))
        for forbidden in ['qemu-img','--force','reboot(', 'poweroff(', 'unlink(']:self.assertNotIn(forbidden,host+guest)


if __name__=='__main__':unittest.main()
