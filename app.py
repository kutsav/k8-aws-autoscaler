from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import boto3,inspect,logging,json,requests,os
app = Flask(__name__)

global region, prom_url, asg_name, threshold_cpu, threshold_memory

threshold_cpu=os.environ['THRESHOLD_CPU']
threshold_memory=os.environ['THRESHOLD_MEMORY']
prom_url=os.environ['PROMETHEUS_URL']
asg_name=os.environ['ASG_NAME']
region=os.environ['REGION']

def fetch_prometheus_metrics(query):
	try:
		api_path="/api/v1/query?query="
		response=requests.get(prom_url+api_path+query)
		prom_response=json.loads(response.text)
		metric=float(prom_response['data']['result'][0]['value'][1])
		metric=round(metric)
		return metric

	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))

def get_metrics():
	try:
		logging.info("Fetching metrics")
		cpu_query="sum(kube_pod_container_resource_requests_cpu_cores{node=~\".*\"}) / sum(kube_node_status_allocatable_cpu_cores{node=~\".*\"})*100"
		memory_query="sum(kube_pod_container_resource_requests_memory_bytes{node=~\".*\"}) / sum(kube_node_status_allocatable_memory_bytes{node=~\".*\"})*100"
		cpu=fetch_prometheus_metrics(cpu_query)
		memory=fetch_prometheus_metrics(memory_query)
		logging.info("Cluster CPU: %s" %(str(cpu)))
		logging.info("Cluster Memory: %s" %(str(memory)))
		metrics={}
		metrics['cpu']=cpu
		metrics['memory']=memory
		return metrics
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))
	

def get_asg_capacity(asg):
	try:
		client = boto3.client('autoscaling',region_name=region)
		response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[ asg, ])		
		response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[ asg, ])
		min_size=response['AutoScalingGroups'][0]['MinSize']
		max_size=response['AutoScalingGroups'][0]['MaxSize']
		desired=response['AutoScalingGroups'][0]['DesiredCapacity']
		logging.info("Current ASG capacity config ==>  Min: %s\t Max: %s\t Desired: %s" %(str(min_size),str(max_size),str(desired)))
		capacity={}
		capacity['min']=min_size
		capacity['max']=max_size
		capacity['desired']=desired
		return capacity
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))	

def scale_asg(asg):
	try:
		client = boto3.client('autoscaling',region_name=region)
		capacity=get_asg_capacity(asg)	
		new_desired=int(capacity['desired'])+1
		logging.info("New desired capacity: %s" %(str(new_desired)))
		if new_desired <= int(capacity['max']):
			logging.info("Scaling the ASG to new capacity.")
		else:
			logging.info("New desired count exceeds max instance count. Scaling stopped because of that.")
		
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))	


def autoscaler():
	try:
		client = boto3.client('autoscaling',region_name=region)
		metrics=get_metrics()
		cpu=metrics['cpu']
		memory=metrics['memory']
		if cpu > int(threshold_cpu) or memory > int(threshold_memory): 
			logging.info("Current resource utilization has crossed the threshold, Scale up is required.")
			## Call method to scale the asg group
			scale_asg(asg_name)
		else:
			logging.info("All metrics are below threshold. No action required.")
		
				
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))	


if __name__ == '__main__':
  try:
    logging.basicConfig(level=logging.INFO,format='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%Y %H:%M:%S')

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=autoscaler, trigger="interval", seconds=30)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0',port='5000', debug = False)
  except Exception as e:
    logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))
    atexit.register(lambda: scheduler.shutdown())
