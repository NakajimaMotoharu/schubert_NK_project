"""Corrected SSC243/246 cold preparation, strictly new generated tool/save slots."""
import ast
from pg1037_cold_preparation_sources import files as previous


def files():
    result={}
    for name,text in previous().items():
        for old,new in [('Pg1037ColdOwnedPreparation','Pg1062ColdOwnedPreparation'),
                        ('pg1037_cold_refs.py','pg1062_cold_refs.py'),
                        ('pg1037-cold-tools-v1','pg1062-cold-tools-v1'),
                        ('pg1037-cold-prepared-v1','pg1062-cold-prepared-v1'),
                        ('PG1037_','PG1062_')]:
            name=name.replace(old,new);text=text.replace(old,new)
        if name.endswith('.java')and not name.endswith('Test.java'):
            old='original(session);refs.check("prepare");original(session);'
            if text.count(old)!=1:
                raise ValueError('fixed original/reference phases required')
            text=text.replace(old,'phase="ORIGINAL_BEFORE_REFERENCES";original(session);\n'
                              '              phase="REFERENCES_PREPARE";refs.check("prepare");\n'
                              '              phase="ORIGINAL_AFTER_REFERENCES";original(session);')
        if name.endswith('.py'):
            ast.parse(text)
        result[name]=text
    return result
