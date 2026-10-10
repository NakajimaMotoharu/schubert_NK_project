"""SSC249/253 fixed full held-current inventory, never direct-tree expansion.

BUG1033/YKT802; PT-DEP-1125001..003. All nine metadata, ACL and byte hashes
remain strict. No current bytes generate a historical expected hash.
"""
from pathlib import PurePosixPath


def require(ok):
    if not ok:raise ValueError('fixed held-current projection refused')


def project(group,now,ancestors,root_name):
    require(type(group)is list and type(now)is dict and type(ancestors)is list and len(ancestors)==4)
    require(''in now and len(group)==len(now)+4)
    require(type(root_name)is str and root_name.startswith('0.1.0-PG'))
    paths=['',*sorted(k for k in now if k!='')]
    require(len(group)==len(paths)+4)
    result={}
    for index,(row,path)in enumerate(zip(group,[None]*4+paths)):
        require(type(row)is list and len(row)==4 and type(row[0])is str and
                type(row[1])is list and len(row[1])==9 and
                all(type(v)is int for v in row[1])and row[2]==[])
        if index<4:
            require(type(ancestors[index])is dict and set(ancestors[index])=={'name','value'})
            require(row[0]==['/','opt','schubert-nk','releases'][index]and
                    ancestors[index]['name']==row[0]and
                    ancestors[index]['value']=={'metadata':row[1],'sha256':row[3]})
        else:
            require(row[0]==(root_name if path==''else PurePosixPath(path).name))
            require(now[path]=={'metadata':row[1],'sha256':row[3]})
            result[path]={'metadata':row[1],'sha256':row[3],'acl':row[2],'target':None}
    require(set(result)==set(now))
    return result
