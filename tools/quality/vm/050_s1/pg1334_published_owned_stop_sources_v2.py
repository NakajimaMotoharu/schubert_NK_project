"""New-only namespace after old release guard stage failure; preserve all old slots."""
from pg1328_published_owned_stop_sources import sources as previous,SOURCE,BEFORE,W,CHANGES,OWNED


def sources():
    values={}
    for name,text in previous().items():
        name=name.replace('1328','1334')
        text=text.replace('Pg1328','Pg1334').replace('pg1328','pg1334').replace('PG1328','PG1334')
        if name.endswith('.py'):compile(text,'<new-only current owned stop>','exec')
        values[name]=text
    return values
