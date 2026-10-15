"""New immutable observer bound to actual current prepared full11 post."""
import pg3462_outbox_current_observer as template
from pg3564_current_browser_resume_sources import SOURCE, BOM
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate


def source():
    raw=template.source().replace('pg3462','pg3572').replace('PG3462','PG3572')
    raw=raw.replace('pg3458-current-outbox-publication-independent-post-v1','pg3570-current-browser-resume-independent-post-v1')
    marker=" assert json.loads((W/'pg3570-current-browser-resume-independent-post-v1/manifest.safe.json').read_bytes())['actualExit']==0"
    if raw.count(marker)!=1:raise ValueError('one current independent admission required')
    raw=raw.replace(marker,marker+"\n post=json.loads((W/'pg3570-current-browser-resume-independent-post-v1/manifest.safe.json').read_bytes());assert post['productionSource']==SOURCE and post['guest']['independentResumeOnlyDeltaVerified']and post['guest']['dbClientsAdvisoryMA0']")
    if SOURCE not in raw or BOM not in raw:raise ValueError('same current observer identity required')
    compile(raw,'<new immutable prepared current observer>','exec');return raw


def namespace():
    ns={'__file__':str(template.old.previous.previous.R/'pg3572_current_browser_observer.py'),'__name__':'current_prepared_browser_observer'}
    exec(compile(source(),'<immutable prepared current observer>','exec'),ns);return ns


def main():
    import sys
    ns=namespace()
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return ns['main']()
    return ns['main']()


if __name__=='__main__':main()
