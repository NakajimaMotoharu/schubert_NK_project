"""Executable generated inventory helper against independent private file fixtures.

No VM, authority, publication or business data; the separate finite oracle tests
cover approved mutation phases. Here immutable FD/link/hash checks are exercised.
"""
import ast
import hashlib
import os
from pathlib import Path
import stat
import tempfile
import time
import types
import unittest
from pg1094_cold_activation_sources_v2 import files
import pg1090_cold_finite_capture as io
import pg1088_cold_exchange_io as exchange_io


class Observer(unittest.TestCase):
    def test_actual_signed_material_fd_link_and_directory_then_tamper_refused(self):
        tree=ast.parse(files()['pg1094_cold_refs.py'])
        helper=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory_check')
        with tempfile.TemporaryDirectory(prefix='pg1094-observer-fixture-') as tmp:
            root=Path(tmp);material=root/'signed';material.write_bytes(b'independent literal\n');material.chmod(0o400)
            current=root/'current-root';current.mkdir();(current/'current').symlink_to('/fixture/old-release')
            save=root/'private';save.mkdir()
            rows=[{'path':'signed','size':20,'sha256':hashlib.sha256(b'independent literal\n').hexdigest()}]
            # Fixture-only inventory shape: /tmp is deliberately NOT claimed
            # to satisfy the separate Root-owned trusted ancestor admission.
            material_fd=os.open(material,os.O_RDONLY|os.O_NOFOLLOW)
            root_fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            h=types.SimpleNamespace(root=root,records={row['path']:row for row in rows},
                held=[(material_fd,root_fd,'signed',tuple(io.metadata(os.fstat(material_fd))),())])
            directory=os.open(current,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            saved=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            link=os.open('current',os.O_PATH|os.O_NOFOLLOW,dir_fd=directory)
            calls=[]
            def verify(path,fixed,actual,phase,trees,begin,end):
                self.assertEqual('before',phase);self.assertEqual(fixed,actual);calls.append(path)
            pub=types.SimpleNamespace(CURRENT=str(current),APPROVAL=str(root/'approval'),verify_retained=verify)
            before={str(current):io.direct_tree(current)}
            namespace=dict(os=os,pathlib=__import__('pathlib'),hashlib=hashlib,stat=stat,io=io,pub=pub,
                           exchange_io=exchange_io,held=[h],directory_fds=[(save,saved,io.metadata(os.fstat(saved)))],
                           PHASE='before',BEGIN_NS=time.time_ns(),time=time,before_trees=before,
                           current_fd=directory,save_fd=saved,old_link_fd=link,require=lambda ok:self.assertTrue(ok))
            exec(compile(ast.Module(body=[helper],type_ignores=[]),'generated-inventory','exec'),namespace)
            try:
                namespace['inventory_check'](before)
                self.assertIn(str(material),calls)
                # Same inode/length and legal owner/mode are insufficient: bytes
                # and all nine metadata fields must remain the captured values.
                material.chmod(0o600);material.write_bytes(b'altered fixture xyz\n');material.chmod(0o400)
                with self.assertRaises(AssertionError):namespace['inventory_check'](before)
            finally:
                os.close(link);os.close(directory);os.close(saved);os.close(material_fd);os.close(root_fd)

    def test_v2_class_and_transport_slot_are_exact(self):
        value=files()
        self.assertEqual({'Pg1094ColdActivation.java','Pg1094ColdActivationTest.java','pg1094_cold_refs.py'},set(value))
        py=value['pg1094_cold_refs.py'];java=value['Pg1094ColdActivation.java']
        self.assertIn("[b'Pg1094ColdActivation',b'activate',b'']",py)
        self.assertIn('pg1094-cold-activate-v1',java)
        self.assertIn('pg1094-cold-activate-v1',py)
        self.assertNotIn('Pg1091ColdActivation',py)


if __name__=='__main__':unittest.main()
