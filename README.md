# k8-aws-autoscaler


Flask app that scales up kuberenetes worker nodes(AWS autoscaling group) when cluster's collective CPU and Memory reaches a threshold value.


# Usage:

- Use the manifests/deploy.yaml file to deploy the app in you cluster. 
- Replace the env variables with the desired values.
- Make sure the pod has permission to change the ASG capacity settings.


# Environment variables:
- REGION: This is to define the region of your ASG
- PROMETHEUS_URL: The prometheus url to use to get cluster nodes resource usage
- ASG_NAME: The name of worker nodes autoscaling group
- THRESHOLD_CPU: The combined CPU usage value of cluster at which nodes should be increased
- THRESHOLD_MEMORY: The combined Memory usage value of cluster at which nodes should be increased


# NOTE: 
- Right now the app does not have support for handling multiple ASGs
