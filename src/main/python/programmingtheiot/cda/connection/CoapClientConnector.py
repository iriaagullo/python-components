#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import socket
import traceback

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.IRequestResponseClient import IRequestResponseClient

from programmingtheiot.data.DataUtil import DataUtil


import asyncio
from aiocoap import *

from coapthon import defines
from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
from coapthon.utils import generate_random_token

class CoapClientConnector(IRequestResponseClient):
	"""
	Shell representation of class for student implementation.
	
	"""
	
	def __init__(self, dataMsgListener: IDataMessageListener = None):
		self.config = ConfigUtil()
		self.dataMsgListener = dataMsgListener
		self.enableConfirmedMsgs = False
		self.coapClient = None

		self.observeRequests = {}

		self.host = self.config.getProperty(
			ConfigConst.COAP_GATEWAY_SERVICE,
			ConfigConst.HOST_KEY,
			ConfigConst.DEFAULT_HOST
		)
		self.port = self.config.getInteger(
			ConfigConst.COAP_GATEWAY_SERVICE,
			ConfigConst.PORT_KEY,
			ConfigConst.DEFAULT_COAP_PORT
		)
		self.uriPath = "coap://" + self.host + ":" + str(self.port) + "/"

		logging.info('\tHost:Port: %s:%s', self.host, str(self.port))

		self.includeDebugLogDetail = True

		try:
			tmpHost = socket.gethostbyname(self.host)

			if tmpHost:
				self.host = tmpHost
				self._initClient()
			else:
				logging.error("Can't resolve host: " + self.host)

		except socket.gaierror:
			logging.info("Failed to resolve host: " + self.host)
			
		pass
	
	def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		
		logging.info("Discovering remote resources...")

		return self.sendGetRequest(
			resource=None,
			name='.well-known/core',
			enableCON=False,
			timeout=timeout
		)

	def sendDeleteRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing Async DELETE to path: " + resourcePath)

			asyncio.get_event_loop().run_until_complete(
				self._handleDeleteRequest(
					resourcePath=resourcePath,
					enableCON=enableCON
				)
			)
		else:
			logging.warning("Can't issue Async DELETE - no path or path list provided.")
			

		'''
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing DELETE with path: " + resourcePath)

			request = self.coapClient.mk_request(defines.Codes.DELETE, path=resourcePath)
			request.token = generate_random_token(2)

			if not enableCON:
				request.type = defines.Types["NON"]

			self.coapClient.send_request(
				request=request,
				callback=self._onDeleteResponse,
				timeout=timeout
			)
		else:
			logging.warning("Can't test DELETE - no path or path list provided.")

		'''

	async def _handleDeleteRequest(self, resourcePath: str = None, enableCON: bool = False):
		try:
			msgType = NON

			if enableCON:
				msgType = CON

			fullUri = self.uriPath + resourcePath if resourcePath else self.uriPath
			msg = Message(mtype=msgType, code=Code.DELETE, uri=fullUri)
			req = self.coapClient.request(msg)
			responseData = await req.response

			self._onDeleteResponse(responseData)

		except Exception as e:
			# TODO: for debugging, you may want to optionally include the stack trace, as shown
			logging.warning("Failed to process DELETE request for path: " + resourcePath)
			traceback.print_exception(type(e), e, e.__traceback__)


	def _onDeleteResponse(self, response):
		if not response:
			logging.warning('DELETE response invalid. Ignoring.')
			return

		logging.info('DELETE response received: %s', response.payload)

		

	def sendGetRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing Async GET to path: " + resourcePath)

			asyncio.get_event_loop().run_until_complete(
				self._handleGetRequest(resourcePath=resourcePath, enableCON=enableCON)
			)
		else:
			logging.warning("Can't issue Async GET - no path or path list provided.")
		'''
	
		if resource or name:
				resourcePath = self._createResourcePath(resource, name)

				logging.info("Issuing GET with path: " + resourcePath)

				request = self.coapClient.mk_request(defines.Codes.GET, path=resourcePath)
				request.token = generate_random_token(2)

				if not enableCON:
					request.type = defines.Types["NON"]

				response = self.coapClient.send_request(request=request, timeout=timeout)

				self._onGetResponse(response=response, resourcePath=resourcePath)
		else:
				logging.warning("Can't test GET - no path or path list provided.")


	'''

	async def _handleGetRequest(self, resourcePath: str = None, enableCON: bool = False):
		try:
			msgType = NON

			if enableCON:
				msgType = CON

			fullUri = self.uriPath + resourcePath if resourcePath else self.uriPath
			msg = Message(mtype=msgType, code=Code.GET, uri=fullUri)
			req = self.coapClient.request(msg)
			responseData = await req.response

			self._onGetResponse(responseData)

		except Exception as e:
			# TODO: for debugging, you may want to optionally include the stack trace, as shown
			logging.warning("Failed to process GET request for path: " + resourcePath)
			traceback.print_exception(type(e), e, e.__traceback__)
	
	'''
	def _onGetResponse(self, response):
		if not response:
			logging.warning('Async GET response invalid. Ignoring.')
			return

		logging.info('Async GET response received.')

		jsonData = response.payload.decode("utf-8")

		if len(response.requested_path) >= 2:
			dataType = response.requested_path[2]

			if dataType == ConfigConst.ACTUATOR_CMD:
				# TODO: convert payload to ActuatorData and verify!
				logging.info("ActuatorData received: %s", jsonData)

				try:
					ad = DataUtil().jsonToActuatorData(jsonData)

					if self.dataMsgListener:
						self.dataMsgListener.handleActuatorCommandMessage(ad)
				except:
					logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
					return
			else:
				logging.info("Response data received. Payload: %s", jsonData)
		else:
			logging.info("Response data received. Payload: %s", jsonData)

	'''
	def _onGetResponse(self, response, resourcePath: str = None):
		if not response:
			logging.warning('GET response invalid. Ignoring.')
			return

		logging.info('GET response received.')

		jsonData = response.payload
		locationPath = resourcePath.split('/') if resourcePath else []

		if len(locationPath) > 2:
			dataType = locationPath[2]

			if dataType == ConfigConst.ACTUATOR_CMD:
				# TODO: convert payload to ActuatorData and verify!
				logging.info("ActuatorData received: %s", jsonData)

				try:
					ad = DataUtil().jsonToActuatorData(jsonData)

					if self.dataMsgListener:
						self.dataMsgListener.handleActuatorCommandMessage(ad)
				except:
					logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
					return
			else:
				logging.info("Response data received. Payload: %s", jsonData)
		else:
			logging.info("Response data received. Payload: %s", jsonData)
	
	def sendPostRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing Async POST to path: " + resourcePath)

			asyncio.get_event_loop().run_until_complete(
				self._handlePostRequest(
					resourcePath=resourcePath,
					payload=payload,
					enableCON=enableCON
				)
			)
		else:
			logging.warning("Can't issue Async POST - no path or path list provided.")
		
	'''
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing POST with path: " + resourcePath)

			request = self.coapClient.mk_request(defines.Codes.POST, path=resourcePath)
			request.token = generate_random_token(2)
			request.payload = payload

			if not enableCON:
				request.type = defines.Types["NON"]

			self.coapClient.send_request(
				request=request,
				callback=self._onPostResponse,
				timeout=timeout
			)
		else:
			logging.warning("Can't test POST - no path or path list provided.")
	'''

	async def _handlePostRequest(self, resourcePath: str = None, payload: str = None, enableCON: bool = False):
		try:
			msgType = NON

			if enableCON:
				msgType = CON

			payloadBytes = b''

			# Decide which encoding to use - can also load from config
			if payload:
				payloadBytes = payload.encode('utf-8')

			fullUri = self.uriPath + resourcePath if resourcePath else self.uriPath
			msg = Message(mtype=msgType, code=Code.POST, uri=fullUri)
			req = self.coapClient.request(msg)
			responseData = await req.response

			self._onPostResponse(responseData)

		except Exception as e:
			# TODO: for debugging, you may want to optionally include the stack trace, as shown
			logging.warning("Failed to process POST request for path: " + resourcePath)
			traceback.print_exception(type(e), e, e.__traceback__)


	def _onPostResponse(self, response):
		if not response:
			logging.warning('POST response invalid. Ignoring.')
			return

		logging.info('POST response received: %s', response.payload)
	


	def sendPutRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing Async PUT to path: " + resourcePath)

			asyncio.get_event_loop().run_until_complete(
				self._handlePutRequest(
					resourcePath=resourcePath,
					payload=payload,
					enableCON=enableCON
				)
			)
		else:
			logging.warning("Can't issue Async PUT - no path or path list provided.")

	'''
	if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing PUT with path: " + resourcePath)

			request = self.coapClient.mk_request(defines.Codes.PUT, path=resourcePath)
			request.token = generate_random_token(2)
			request.payload = payload

			if not enableCON:
				request.type = defines.Types["NON"]

			self.coapClient.send_request(
				request=request,
				callback=self._onPutResponse,
				timeout=timeout
			)
		else:
			logging.warning("Can't test PUT - no path or path list provided.")
	'''


	async def _handlePutRequest(self, resourcePath: str = None, payload: str = None, enableCON: bool = False):
		try:
			msgType = NON

			if enableCON:
				msgType = CON

			payloadBytes = b''

			# Decide which encoding to use - can also load from config
			if payload:
				payloadBytes = payload.encode('utf-8')

			fullUri = self.uriPath + resourcePath if resourcePath else self.uriPath
			msg = Message(mtype=msgType, code=Code.PUT, uri=fullUri)
			req = self.coapClient.request(msg)
			responseData = await req.response

			self._onPutResponse(responseData)

		except Exception as e:
			# TODO: for debugging, you may want to optionally include the stack trace, as shown
			logging.warning("Failed to process PUT request for path: " + resourcePath)
			traceback.print_exception(type(e), e, e.__traceback__)


	def _onPutResponse(self, response):
		if not response:
			logging.warning('PUT response invalid. Ignoring.')
			return

		logging.info('PUT response received: %s', response.payload)


	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		self.dataMsgListener = listener
		pass

	def startObserver(self, resource: ResourceNameEnum = None, name: str = None, ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
		
		logging.info("startObserver llamado.")
        
		return False

	def stopObserver(self, resource: ResourceNameEnum = None, name: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		
		logging.info("stopObserver llamado.")
        
		return False
	
	
	def _initClient(self):
		asyncio.get_event_loop().run_until_complete(self._initClientContext())
		'''
		try:
			self.coapClient = HelperClient(server=(self.host, self.port))
			logging.info('Client created. Will invoke resources at: ' + self.uriPath)
		except Exception as e:
			# obviously, this is a critical failure - you may want to handle this differently
			logging.error("Failed to create CoAP client to URI path: " + self.uriPath)
			traceback.print_exception(type(e), e, e.__traceback__)
		'''
	async def _initClientContext(self):
			try:
				logging.info("Creating CoAP client for URI path: " + self.uriPath)

				self.coapClient = await Context.create_client_context()

				logging.info('Client context created. Will invoke resources at: ' + self.uriPath)

			except Exception as e:
				# obviously, this is a critical failure - you may want to handle this differently
				logging.error("Failed to create CoAP client to URI path: " + self.uriPath)
				traceback.print_exception(type(e), e, e.__traceback__)

		
	def _createResourcePath(self, resource: ResourceNameEnum = None, name: str = None):
			resourcePath = ""
			hasResource = False

			if resource:
				resourcePath = resourcePath + resource.value
				hasResource = True

			if name:
				if hasResource:
					resourcePath = resourcePath + '/'
				resourcePath = resourcePath + name

			return resourcePath
	


