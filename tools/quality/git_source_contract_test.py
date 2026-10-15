"""Actual isolated Git history: Main, later tests/docs, empty scope and changed Main."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from git_source_contract import MAIN_PATHSPEC,last_main_source


class Source(unittest.TestCase):
    def test_main_identity_is_not_latest_management_or_test_head_and_empty_is_refused(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-git-source-')as d:
            root=Path(d);env={**os.environ,'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_AUTHOR_NAME':'PGPT fixture','GIT_AUTHOR_EMAIL':'fixture@example.invalid','GIT_COMMITTER_NAME':'PGPT fixture','GIT_COMMITTER_EMAIL':'fixture@example.invalid'}
            def git(*args):return subprocess.check_output(['git',*args],cwd=root,env=env,stderr=subprocess.DEVNULL,text=True).strip()
            git('init','-q');(root/'note.md').write_text('independent management fixture\n');git('add','.');git('commit','-qm','management only')
            with self.assertRaises(ValueError):last_main_source(root)
            main=root/'src/schubert-nk-fixture/src/main/java/Subject.java';main.parent.mkdir(parents=True);main.write_text('class Subject {}\n');git('add','.');git('commit','-qm','actual Main');expected=git('rev-parse','HEAD')
            test=root/'src/schubert-nk-fixture/src/test/java/SubjectTest.java';test.parent.mkdir(parents=True);test.write_text('class SubjectTest {}\n');git('add','.');git('commit','-qm','later Test');(root/'note.md').write_text('later management\n');git('add','.');git('commit','-qm','later management')
            self.assertNotEqual(expected,git('rev-parse','HEAD'));self.assertEqual(expected,last_main_source(root));self.assertEqual('',git('log','-1','--format=%H','--','src/*/src/main'))
            main.write_text('class Subject {int value;}\n');self.assertNotEqual('',git('diff','--',MAIN_PATHSPEC));git('add','.');git('commit','-qm','changed Main');self.assertEqual(git('rev-parse','HEAD'),last_main_source(root))


if __name__=='__main__':unittest.main()
