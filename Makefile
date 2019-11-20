build:
	docker build -t k8-aws-autoscaler:v1 .

run:
	docker run -d --rm --name k8-aws-autoscaler -p 5000:5000 k8-aws-autoscaler:v1

kill:
	docker kill k8-aws-autoscaler
