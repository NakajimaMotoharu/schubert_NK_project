"""BUG671: two authority/argv/kernel samples and manager sandwich, no runtime authority."""
import pathlib

AUTHORITY={'Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}
ENTRIES={'dev.codex.schubert.nk.batch.file.RootServiceLauncher','dev.codex.schubert.nk.api.bootstrap.ApiProcessMain','dev.codex.schubert.nk.web.bootstrap.WebProcessMain','dev.codex.schubert.nk.batch.file.MorningProcessMain'}

def process_sample(pid):
    proc=pathlib.Path('/proc')/str(pid)
    ticks=int((proc/'stat').read_text().rpartition(')')[2].split()[19])
    values={}
    for line in (proc/'status').read_text().splitlines():
        if ':' in line:
            key,value=line.split(':',1)
            if key in AUTHORITY:
                if key in values:raise ValueError('duplicate authority field')
                values[key]=value.strip()
    if set(values)!=AUTHORITY:raise ValueError('authority field missing')
    argv=(proc/'cmdline').read_bytes()
    entries=[word.decode('ascii') for word in argv.split(b'\0') if word.decode('ascii',errors='replace') in ENTRIES]
    if len(entries)>1:raise ValueError('entry identity ambiguous')
    return {'startTicks':ticks,'process':values,'entry':entries[0] if entries else 'other',
            '_argv':argv,'_cgroup':(proc/'cgroup').read_bytes()}

def stable_actor(role,manager,sample=process_sample):
    last=None
    for _ in range(3):
        before=manager(role);last=before
        if int(before['MainPID'])==0:
            if before==manager(role):return before
            continue
        try:
            first=sample(before['MainPID']);second=sample(before['MainPID']);after=manager(role)
        except (FileNotFoundError,ProcessLookupError):continue
        if before!=after or first!=second:continue
        return {**before,**{k:v for k,v in first.items() if not k.startswith('_')}}
    return {**last,'race':True}
