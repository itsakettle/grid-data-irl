# electricity_bidding

`terraform plan`
`terraform apply`
`docker-compose up`
`docker-compose up --build`
`docker build . --progress=plain --no-cache`
`docker run --rm -it --entrypoint bash <image>`

# Module electricity_bidding_data
This module is responsible for extacting semo data, transforming it into features. Currently it uses a single parquet file as databases which seems reasonable given the data is small.

Run tests using`run_tests.sh`.

## AWS Deployment
The module is deployed using Lambda functions since the data is small and we expect it to run in seconds. See `tf/electricity_bidding_tf/extract_semo.tf` which contains the terraform for the lambda, step functions and the reqired roles, policies etc.