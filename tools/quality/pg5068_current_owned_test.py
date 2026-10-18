"""Same independent owned-stop matrix against actual newday/current composed roles."""
import inspect
import unittest
import pg4916_current_owned_test as previous
import pg5060_current_owned_sources as role
import pg5064_current_owned_dispatch as dispatch
import pg5066_current_owned_post as post


def matrix():
    # Translate assertion/fixture role labels only, not any runtime oracle or
    # receipt. The synthetic emission fixture never grants a stop permission.
    raw = inspect.getsource(previous.Owned)
    for a, b in [('pg4916', 'pg5060'), ('Pg4916', 'Pg5060'), ('pg4918', 'pg5062'),
                 ('pg4920', 'pg5064'), ('pg4923', 'pg5065'),
                 ('04bbdb73b532537e3546191d72dee913b17629a0', role.SOURCE)]:
        raw = raw.replace(a, b)
    ns = {**vars(previous), '__file__': __file__, 'role': role, 'dispatch': dispatch, 'post': post}
    exec(compile(raw, '<new current owned independent matrix>', 'exec'), ns)
    return ns['Owned']


Owned = matrix()


class CompleteTransport(unittest.TestCase):
    def test_actual_emitted_stage_binds_every_current_identity_and_archive_path(self):
        raw = dispatch.namespace()['stage']()
        for marker in ('/opt/schubert-nk/releases/0.1.0-PG4980', role.SOURCE, role.BOM,
                       dispatch.ARCHIVE, dispatch.REMOTE, dispatch.GUEST):
            self.assertIn(marker, raw)
        self.assertNotIn('/opt/schubert-nk/releases/0.1.0-PG4860', raw)


if __name__ == '__main__':
    unittest.main()
