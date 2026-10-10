"""Explicit selection permits zero dependency-selected tests, never counts them passed.
Mandatory four batch suites and new Test IDs are qualified by the separate collector.
No formal/full-run POM/quality/coverage configuration change.
"""
import pg1009_stream_selected_v3 as previous
selected=previous.selected
selected.D=selected.W/'pg1010-stream-selected-v4'

def source():
    code=previous.source().replace('PG1009-stream-selected-v3','PG1010-stream-selected-v4')
    marker="'-Dsurefire.failIfNoSpecifiedTests=false'";assert code.count(marker)==1
    return code.replace(marker,"'-Dsurefire.failIfNoSpecifiedTests=false', '-DfailIfNoTests=false'")

if __name__=='__main__':
    env=dict(selected.__dict__);exec(compile(source(),'<PG1010 explicit selected scope>','exec'),env);env['main']()
