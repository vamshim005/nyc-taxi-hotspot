.PHONY: build run test clean

# Variables
IMAGE_NAME = nyc-taxi-hotspot
CONTAINER_NAME = nyc-taxi-hotspot-analysis

# Build Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run analysis in Docker container
run:
	docker run --name $(CONTAINER_NAME) \
		-v $(PWD)/results:/app/results \
		$(IMAGE_NAME)

# Run analysis on full dataset
run-prod:
	docker run --name $(CONTAINER_NAME)-prod \
		-v $(PWD)/results:/app/results \
		$(IMAGE_NAME) --scale prod

# Run tests
test:
	pytest tests/

# Clean up
clean:
	rm -rf results/*
	docker rm -f $(CONTAINER_NAME) $(CONTAINER_NAME)-prod 2>/dev/null || true

# Install dependencies
install:
	pip install -r requirements.txt

# Download sample data
download-data:
	mkdir -p data
	wget -O data/yellow_tripdata_2009-01.parquet \
		https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2009-01.parquet 