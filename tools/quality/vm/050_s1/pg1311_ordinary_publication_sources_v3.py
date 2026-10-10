"""BUG1075 new-only tool: canonical epoch update is not a read-only operation."""
import ast
from pg1308_ordinary_publication_sources_v2 import sources as previous


def sources():
    result={}
    for name,text in previous().items():
        if name.startswith(('Pg1308','pg1308')):
            name=name.replace('Pg1308','Pg1311').replace('pg1308','pg1311')
            text=text.replace('Pg1308','Pg1311').replace('pg1308','pg1311').replace('PG1308','PG1311')
        if name=='Pg1311OrdinaryPublication.java':
            if text.count('startsStopsReloadsEpochWrites0=true')!=2:
                raise ValueError('fixed terminal claims required')
            text=text.replace('startsStopsReloadsEpochWrites0=true','startsStopsReloads0=true canonicalEpochWrites=1')
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    return result
