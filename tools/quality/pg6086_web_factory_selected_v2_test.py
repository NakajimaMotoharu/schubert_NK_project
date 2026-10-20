import unittest
import pg6086_web_factory_selected_v2 as p


class FixedSourceTest(unittest.TestCase):
    def test_inner_generated_head_requires_no_implicit_outer_scope(self):
        raw = p.runner_source()
        head = next(s.strip() for s in raw.splitlines() if s.strip().startswith('head='))
        scope = {}
        exec(compile(head, '<inner source binding>', 'exec'), scope)
        self.assertEqual(p.SOURCE, scope['head'])
        self.assertIn('done=done and target100', raw)
        self.assertIn('os.pathsep+NODE_PATH,MAVEN_OPTS', raw)
        self.assertIn("'expectedTests':925", raw)


if __name__ == '__main__':
    unittest.main()
