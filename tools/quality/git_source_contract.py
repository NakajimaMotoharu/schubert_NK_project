"""Explicit Git file scopes; filesystem glob syntax is not a Git pathspec contract."""
import re
import subprocess

MAIN_PATHSPEC=':(glob)src/*/src/main/**'
POM_PATHSPEC=':(glob)src/*/pom.xml'


def last_main_source(root):
    if not subprocess.check_output(['git','ls-files','--',MAIN_PATHSPEC],cwd=root):raise ValueError('nonempty Main file scope required')
    value=subprocess.check_output(['git','log','-1','--format=%H','--',MAIN_PATHSPEC],cwd=root,text=True).strip()
    if re.fullmatch('[0-9a-f]{40}',value)is None:raise ValueError('nonempty exact Main commit required')
    subprocess.run(['git','cat-file','-e',value+'^{commit}'],cwd=root,check=True)
    return value
