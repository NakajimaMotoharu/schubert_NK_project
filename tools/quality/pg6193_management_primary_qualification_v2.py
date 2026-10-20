"""Qualify original new-only60 v2, never the format-rejected v1."""
import inspect
from types import FunctionType
import pg6192_management_primary_qualification as prior

RUN=prior.W/'pg6191-management-primary-selected-v2'


def original_source():
    return FunctionType(prior.original_source.__code__,{**vars(prior),'RUN':RUN})()


def main():
    raw=inspect.getsource(prior.main)
    for before,after in (
        ('pg6192-management-primary-qualification-v1','pg6193-management-primary-qualification-v2'),
        ('PG6192-management-primary-qualification-v1','PG6193-management-primary-qualification-v2')):
        if raw.count(before)!=1:raise ValueError('one new-only original60 reader namespace')
        raw=raw.replace(before,after,1)
    scope={**vars(prior),'RUN':RUN,'original_source':original_source}
    exec(compile(raw,'<genuine original60 v2 reader>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
