from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import boto3,inspect,logging,json,requests
app = Flask(__name__)

global region, prom_url, THRESHOLD_CPU, THRESHOLD_MEMORY
THRESHOLD_CPU=70
THRESHOLD_MEMORY=80
prom_url="http://localhost:8080"
region='ap-south-1'

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
	

def check_metrics():
	try:
		client = boto3.client('autoscaling',region_name=region)
		metrics=get_metrics()
		cpu=metrics['cpu']
		memory=metrics['memory']
		if cpu > int(THRESHOLD_CPU) or memory > int(THRESHOLD_MEMORY): 
			logging.info("Current resource utilization has crossed the threshold, Scale up is required.")
		else:
			logging.info("All metrics are below threshold. No action required.")
		
				
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))	



def scale_asg():
	try:
		client = boto3.client('autoscaling',region_name=region)
				
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))	


if __name__ == '__main__':
  try:
    logging.basicConfig(level=logging.INFO,format='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%Y %H:%M:%S')

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_metrics, trigger="interval", seconds=10)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())

    app.run(host='0.0.0.0',port='5000', debug = False)
  except Exception as e:
    logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))
    atexit.register(lambda: scheduler.shutdown())
