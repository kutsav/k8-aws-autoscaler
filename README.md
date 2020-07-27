# k8-aws-autoscaler


Flask app that scales up kuberenetes worker nodes(AWS autoscaling group) when cluster's collective CPU and Memory reaches a threshold value.


USAGE:

Use the manifests/deploy.yaml file to deploy the app in you cluster. Replace the env variables with the desired values.
Make sure the pod has permission to change the ASG capacity settings.
