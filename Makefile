build:
	docker build -t utsav2307/k8-aws-autoscaler:v1.0 .

push:
	docker push utsav2307/k8-aws-autoscaler:v1.0

run:
	docker run -d --rm --name utsav2307/k8-aws-autoscaler -p 5000:5000 k8-aws-autoscaler:v1.0

kill:
	docker kill k8-aws-autoscaler
