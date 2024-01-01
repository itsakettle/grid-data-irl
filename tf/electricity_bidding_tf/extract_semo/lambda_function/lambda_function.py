from electricity_bidding_data import extract_semo

def process_request_handler(event, context):
    run_time = event.run_time
    s3_path = event.run_time
    extract_semo.main(run_time=run_time, path=s3_path)