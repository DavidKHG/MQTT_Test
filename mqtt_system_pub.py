import psutil
import paho.mqtt.client as mqtt

client = mqtt.Client()
# ret = client.connect('10.60.65.26')
# ret = client.connect('10.61.5.14')
ret = client.connect('localhost')
print(ret)

system_mem_topic = 'copilot/data/system/memory'
system_cpu_topic = 'copilot/data/system/cpu'


while 1:
	try:
		ram_usage = psutil.virtual_memory()[2]
		cpu_usage = psutil.cpu_percent(1)
		client.publish(system_mem_topic, ram_usage)
		client.publish(system_cpu_topic, cpu_usage)
	except KeyboardInterrupt:
		print("system data fetch failed")
		break