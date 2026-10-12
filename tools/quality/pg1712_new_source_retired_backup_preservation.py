"""Readonly certified base recovery of exact newly retired Backup, no VM replay."""
import inspect
import pg1622_retired_backup_readonly_preservation as prior

SLOT='pg1712-new-source-retired-backup-v1'
REMOTE='/home/mini/schubert-nk-pgpt/runs/PG1712-retired-backup-v1'


def selected_retired(before,after):
    raw=inspect.getsource(prior.selected_retired).replace('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a',
                                                        '02e941b9-1c52-4018-a193-63dd00b269af')
    ns={};exec(compile(raw,'<independent exact current retention delta>','exec'),ns)
    return ns['selected_retired'](before,after)


def guest():
    raw=prior.GUEST
    for old,new in [('pg1596-current-ordinary-before-v1','pg1699-new-current-ordinary-once-v1'),
                    ('6d144309d3294abb31440d523940bfd4275d3a99eab3e4ce8e0486f81a154bce','ef9ddffcf813c6e4f4b8bb6379c30e5e0d87503a4abaf46859976a32fa8bfecb'),
                    ('pg1609-native-stop-v1','pg1703-native-stop-v1')]:
        if old not in raw:raise ValueError('one actual current retention before/after join required')
        raw=raw.replace(old,new)
    compile(raw,'<current before-after Backup metadata readonly>','exec')
    return raw


def server():
    return prior.SERVER.replace('PG1622-retired-backup-v1','PG1712-retired-backup-v1')


def main():
    raw=inspect.getsource(prior.main).replace('pg1613-current-ordinary-terminal-post-v1.safe.json',
                                            'pg1707-new-source-terminal-post-v1.safe.json')
    ns={**prior.__dict__,'SLOT':SLOT,'REMOTE':REMOTE,'GUEST':guest(),'SERVER':server(),
        'selected_retired':selected_retired}
    exec(compile(raw,'<new Source readonly retiredOriginal preservation>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
