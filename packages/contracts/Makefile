build:
	poetry run python ./scripts/compile_all.py

deploy: build
	poetry run python ./scripts/deploy_pragma.py

publish: build deploy
	poetry run python ./scripts/publish_data.py
