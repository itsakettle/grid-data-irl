from electricity_bidding_data import extract_semo

def handler(event, context):
    run_time = event["run_time"]
    s3_path = event["s3_path"]
    extract_semo.main(run_time=run_time, semo_df_path=s3_path)