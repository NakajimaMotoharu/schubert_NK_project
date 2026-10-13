"""Only after independent loaded-view post; immutable current finish six ABI."""
import inspect
import json
import pg2305_current_completed_resume_compile as previous
from pg2330_current_existing_runtime_finish_sources import sources,TOOLS,CLASS,SOURCE,BOM,BEFORE

TARGET=previous.W/TOOLS


def main():
    post=json.loads((previous.W/'pg2328-current-partial-loaded-view-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['guest']['afterSha256']!=BEFORE or not post['guest']['allClientAdvisoryFlock0']or not post['guest']['reloadNotReserved']:
        raise ValueError('exact partial loaded-view independent post required')
    raw=inspect.getsource(previous.main).replace('pg2305','pg2331').replace('Pg2304FreshResumePreparation',CLASS).replace('Pg2304','Pg2330')
    # Baseline is the new independent partial loaded-view envelope, not the old stop root.
    raw=raw.replace("post['proofHashes']['after.private.json']['sha256']!=BEFORE","post['proofHashes']['after.private.json']['sha256']!='e7456ef531cde4d5e09161f401861ad0f718febbe786e59038e46dc869298a1e'")
    ns={**previous.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'SOURCE':SOURCE,'BOM':BOM,'BEFORE':BEFORE,'TARGET':TARGET}
    exec(compile(inspect.getsource(previous.write),'<newonly samefile finish writer>','exec'),ns)
    exec(compile(raw,'<current existing file finish ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
