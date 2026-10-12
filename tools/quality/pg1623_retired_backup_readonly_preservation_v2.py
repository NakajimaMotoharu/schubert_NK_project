"""New-only private preservation slot after source Path argv boundary correction."""
import inspect
import pg1622_retired_backup_readonly_preservation as prior

def main():
    raw=inspect.getsource(prior.main)
    ns={**prior.__dict__,'SLOT':'pg1623-retired-backup-readonly-v2','REMOTE':'/home/mini/schubert-nk-pgpt/runs/PG1623-retired-backup-v2','SERVER':prior.SERVER.replace('PG1622-retired-backup-v1','PG1623-retired-backup-v2')}
    exec(compile(raw,'<new readonly original preservation slot>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
