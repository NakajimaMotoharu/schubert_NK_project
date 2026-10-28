"""Fixed-source complete six-artifact static analysis, never application execution."""
import pg13590_lgs_remaining_config as cfg
from f03_spotbugs_fresh import stage

if __name__ == '__main__':
    stage(cfg, '17ab52b253282ce45016f0586c0167a22029fd8c',
          '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12',
          ('PG13594-lgs-remaining-two-branches-v1', 'f1dc83806c95332d3095bf117d11b725998aa68ff9674371d1fd866eb1fadf12'))
