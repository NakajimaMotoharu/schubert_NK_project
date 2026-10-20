"""Original current925 artifacts and unfiltered static; no additional PT or build."""
from pg5940_private_lock_compile import W,BASE
from pg6054_expiry_read_qualification import qualify
from pg6106_locked_flag_selected import inventory,MAIN

SOURCE='59960d19c226fd524bb608a34299d7616433ae50'


def main():
    definitions,_=inventory()
    return qualify(SOURCE,W/'pg6106-locked-flag-web925-v1',definitions,(925,150),{MAIN},
        BASE/'PG6082-web-factory-qualification-v1/manifest.json',
        '134e8181764a40b725fd0fa9365f5d18fa714b66221e4f46b992d3f84cd7e735',
        W/'pg6082-web-factory-qualification-v1/manifest.safe.json',
        W/'pg6082-web-factory-qualification-v1/findings.safe.json',
        'pg6108-locked-flag-qualification-v1','PG6108-locked-flag-qualification-v1')


if __name__=='__main__':main()
