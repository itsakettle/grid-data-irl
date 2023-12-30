# electricity_bidding

`terraform plan`
`terraform apply`
`docker-compose up`
`docker-compose up --build`
`docker build . --progress=plain --no-cache`
`docker run --rm -it --entrypoint bash <image>`

# Modules

## electricity_bidding_data
Module resonsible for extacting semo data, transforming it into features. Currently it uses a single parquet file as databases which seems reasonable given the data is small.

Run tests using`run_tests.sh`.