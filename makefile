LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")

test:
	pytest
quality_check: test
	black .
	isort .
	pylint --recursive=y -sn -rn .
build: test quality_check
	./set_envs.sh
	echo ${LOCAL_TAG}
	cd web-service/ && ./docker-build.sh web-prediction-service:${LOCAL_TAG}
publish: test quality_check build
	echo $(PROJECT_ID)
	cd function/ && ./deploy.sh
