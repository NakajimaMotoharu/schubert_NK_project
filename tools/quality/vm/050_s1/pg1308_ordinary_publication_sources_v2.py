"""New-only namespace after initial unqualified fixture compiler; no old tool resume."""
import ast
from pg1306_ordinary_publication_sources import sources as previous


def sources():
    result={}
    for name,text in previous().items():
        if name.startswith(('Pg1306','pg1306')):
            name=name.replace('Pg1306','Pg1308').replace('pg1306','pg1308')
            text=text.replace('Pg1306','Pg1308').replace('pg1306','pg1308').replace('PG1306','PG1308')
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    return result
