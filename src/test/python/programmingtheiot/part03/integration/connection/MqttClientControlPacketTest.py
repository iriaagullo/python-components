import logging
import unittest

from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.data.DataUtil import DataUtil

class MqttClientControlPacketTest(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		logging.basicConfig(
			format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', 
			level = logging.DEBUG
		)
		logging.info("Executing MqttClientControlPacketTest...")

		cls.cfg = ConfigUtil()
		cls.mcc = MqttClientConnector(clientID = "MqttClientControlPacketTestClient")
		cls.dataUtil = DataUtil()

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testConnectAndDisconnect(self):
		# CONNECT + CONNACK + DISCONNECT
		logging.info("Testing connect and disconnect...")
		self.assertTrue(self.mcc.connectClient(), "MQTT client failed to connect.")
		sleep(1)
		self.assertTrue(self.mcc.disconnectClient(), "MQTT client failed to disconnect.")
		sleep(1)

	def testServerPing(self):
		# PINGREQ + PINGRESP
		logging.info("Testing keep-alive ping...")
		self.assertTrue(self.mcc.connectClient())
		sleep(65)  # default keep alive is 60s; wait to trigger PINGREQ
		self.mcc.disconnectClient()

	def testPubSubQoS1And2(self):
		# PUBLISH, PUBACK (QoS 1), PUBREC, PUBREL, PUBCOMP (QoS 2)
		logging.info("Testing publish and subscribe with QoS 1 and 2...")

		self.assertTrue(self.mcc.connectClient())

		topic = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE
		self.mcc.subscribeToTopic(topic, qos=1)
		self.mcc.subscribeToTopic(topic, qos=2)

		sd = SensorData()
		sd.setValue(22.5)
		payload = self.dataUtil.sensorDataToJson(sd)

		# QoS 1
		self.mcc.publishMessage(topic, payload, qos=1)
		sleep(2)

		# QoS 2
		self.mcc.publishMessage(topic, payload, qos=2)
		sleep(2)

		self.mcc.unsubscribeFromTopic(topic)
		self.mcc.disconnectClient()

	def testSubscribeUnsubscribe(self):
		# SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK
		logging.info("Testing subscribe and unsubscribe...")

		self.assertTrue(self.mcc.connectClient())

		topic = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE
		self.mcc.subscribeToTopic(topic, qos=1)
		sleep(1)

		self.mcc.unsubscribeFromTopic(topic)
		sleep(1)

		self.mcc.disconnectClient()

if __name__ == '__main__':
	unittest.main()
