import pg5392_archive_pipeline_bytecode as original

SOURCE='60bc8f54b154e82c16ad3a32a71143d7ca80affe'
RUN='pg5390-archive-pipeline-green-v2'
OUT='PG5398-archive-complete-bytecode-v1'


if __name__=='__main__':original.main(source=SOURCE,run_name=RUN,out_name=OUT,require_all=True)
