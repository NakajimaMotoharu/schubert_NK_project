"""Independent current0ea deferred owned-stop/post matrix; no mutation or fake receipt."""
import inspect
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import pg4916_current_owned_test as reference
import pg5670_current_owned_sources as role
import pg5674_current_owned_dispatch as dispatch
import pg5676_current_owned_post as post
from pg5520_guest_clock_contract_test import context as clock_context


def matrix():
    raw=inspect.getsource(reference.Owned)
    for old,new in(('pg4916','pg5670'),('Pg4916','Pg5670'),('pg4918','pg5672'),('pg4920','pg5674'),('pg4923','pg5675'),
      ('04bbdb73b532537e3546191d72dee913b17629a0',role.SOURCE)):
        raw=raw.replace(old,new)
    marker="'context':{'fixtureOnly':True}"
    if raw.count(marker)!=1:raise ValueError('one immutable pure Browser fixture')
    raw=raw.replace(marker,"'context':clock_context()",1)
    ns={**vars(reference),'__file__':__file__,'role':role,'dispatch':dispatch,'post':post,'clock_context':clock_context}
    exec(compile(raw,'<current0ea independent deferred owned matrix>','exec'),ns)
    return ns['Owned']


Owned=matrix()


class OutputPreservation(unittest.TestCase):
    def test_every_auxiliary_exists_or_symlink_refuses_before_auth(self):
        with tempfile.TemporaryDirectory()as name:
            root=Path(name);dispatch.ensure_outputs(root)
            for i,path in enumerate(dispatch.fresh_paths(root)):
                if i%2:path.symlink_to(root/'missing')
                else:path.write_bytes(b'independent original bytes')
                with self.assertRaises(ValueError):dispatch.ensure_outputs(root)
                if not path.is_symlink():self.assertEqual(b'independent original bytes',path.read_bytes())
                path.unlink()
        with patch.object(dispatch.sys,'argv',['tool','stop']),patch.object(dispatch,'ensure_outputs',side_effect=ValueError('collision')),patch.object(dispatch,'authenticate_host')as authenticate:
            with self.assertRaises(ValueError):dispatch.main()
            authenticate.assert_not_called()

    def test_original_stdout_and_stderr_create_new_and_bounded_transport(self):
        raw=dispatch.namespace()['run_source']()
        for slot in(dispatch.PARENT,dispatch.PRESTOP):
            self.assertNotIn("(W / '"+slot+".private.log').write_bytes(r.stderr)",raw)
            self.assertIn("(W / '"+slot+".private.log').open('xb')",raw)
        self.assertIn('capture_output=True, timeout=300',raw)
        self.assertIn("'pg5674-stage-v1.exit'",raw)


if __name__=='__main__':unittest.main()
