import pg5366_ffm_outputs_bytecode as original

SOURCE='fceffefd6639ae0b217565dc0acdf0d2e0a2a6fe'
RUN='pg5372-ffm-progress-green-v1'
OUT='PG5374-ffm-progress-bytecode-v1'


if __name__=='__main__':
    original.main(source=SOURCE,run_name=RUN,tests=1100,new_cases=8,out_name=OUT)
