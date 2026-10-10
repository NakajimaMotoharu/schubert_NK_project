"""SSC252 explicit cross-scope ancestral effects; live FD nine-fields stay strict.

Only the three proven fixed private siblings and shared /run timestamps differ.
This does not grant mutation, old FD rebasing, signed-content or namespace bypass.
"""
import copy
import stat

POSITIONS={(3,3):'pgpt-s1-preservation',(4,3):'pgpt-s1-preservation',(6,1):'run'}


def compare(before,actual,begin_ns,end_ns,private_sibling_proven):
    if (type(before)is not dict or type(actual)is not dict or type(begin_ns)is not int
        or type(end_ns)is not int or not 0<=begin_ns<=end_ns or private_sibling_proven is not True):
        raise ValueError('cross scope proof refused')
    normalized=copy.deepcopy(actual)
    left=before.get('heldWholeMetadata');right=normalized.get('heldWholeMetadata')
    if type(left)is not list or type(right)is not list or len(left)!=7 or len(left)!=len(right):raise ValueError('whole held scopes refused')
    for inventory_index,(old_inventory,new_inventory) in enumerate(zip(left,right)):
        if type(old_inventory)is not list or type(new_inventory)is not list or len(old_inventory)!=len(new_inventory):raise ValueError('whole held entries refused')
        for row_index,(old,new) in enumerate(zip(old_inventory,new_inventory)):
            if type(old)is not list or type(new)is not list or len(old)!=4 or len(new)!=4:raise ValueError('held row refused')
            if old[0]!=new[0]or old[2:]!=new[2:]:raise ValueError('held name ACL content refused')
            a=old[1];b=new[1]
            if (type(a)is not list or type(b)is not list or len(a)!=9 or len(b)!=9
                or any(type(x)is not int or x<0 for x in (*a,*b))):raise ValueError('held nine fields refused')
            if a==b:continue
            if POSITIONS.get((inventory_index,row_index))!=old[0]:raise ValueError('unrelated held mutation refused')
            mode=stat.S_IFDIR|(0o755 if old[0]=='run'else 0o700)
            if a[2:5]!=[0,0,mode]:raise ValueError('fixed ancestor type authority refused')
            # Exact immutable identity/security/size; no inode/type/ACL allowance.
            links=a[5]+3 if old[0]=='pgpt-s1-preservation'else a[5]
            if b[:5]!=a[:5]or b[5]!=links or b[6]!=a[6]:raise ValueError('shared ancestor identity refused')
            if not all(begin_ns<=x<=end_ns for x in b[7:]):raise ValueError('shared ancestor time refused')
            new[1]=list(a)
    if normalized!=before:raise ValueError('ordinary before differs outside explicit ancestors')
    return True
