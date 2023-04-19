container_registry := 124596083913.dkr.ecr.ca-central-1.amazonaws.com
image_name         := goal-bot
image_tag          := latest

.PHONY: lint
lint:
	python -m pylint main.py src/

.PHONY: analyze
analyze:
	python -m mypy --ignore-missing-imports main.py src/

.PHONY: build
build:
	docker build . -t $(image_name)
	docker tag $(image_name) $(container_registry)/$(image_name):$(image_tag)

.PHONY: deploy
deploy: build
	docker push $(container_registry)/$(image_name):$(image_tag)

.PHONY: run
run: build
	docker run $(container_registry)/$(image_name):$(image_tag)

.PHONY: clean
clean:
	python -m pyclean .
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -f data.json
	rm -f results.xml
	rm -f bot.log*
