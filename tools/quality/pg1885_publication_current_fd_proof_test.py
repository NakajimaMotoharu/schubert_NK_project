"""Actual generated fd_relation and fixed current-role vectors."""
import ast
import unittest
from pg1885_publication_current_fd_proof import payload


class Fds(unittest.TestCase):
    def test_actual_current_fd_role_positive_and_foreign_rejection(self):
        tree=ast.parse(payload());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='fd_relation');namespace={}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual current role fd contract>','exec'),namespace)
        f=namespace['fd_relation']
        self.assertEqual(3,len(f('maintenance.lock',['88','91','92'],['92'],lambda a,b:1)))
        self.assertEqual([{'a':'101','b':'128','sameOfd':True}],f('startup-admission.lock',['101','128'],['101','128'],lambda a,b:0))
        for name,linked,locking,call in [('maintenance.lock',['30','33','34'],['34'],lambda a,b:1),('maintenance.lock',['88','91','92'],['91'],lambda a,b:1),('maintenance.lock',['88','91','92'],['92'],lambda a,b:0),('startup-admission.lock',['101','128'],['101','128'],lambda a,b:1),('startup-admission.lock',['101','128'],['101','128'],lambda a,b:-1)]:
            with self.assertRaises(ValueError):f(name,linked,locking,call)


if __name__=='__main__':unittest.main()
