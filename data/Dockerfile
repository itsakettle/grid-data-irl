FROM python:3.11-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY electricity_bidding_data/ ./electricity_bidding_data/
COPY tests/ ./tests/

CMD [ "python", "-m", "pytest", "-s", "tests/"]