#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.data.BaseIotData import BaseIotData

class ActuatorData(BaseIotData):
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, typeID: int = ConfigConst.DEFAULT_ACTUATOR_TYPE, name = ConfigConst.NOT_SET, d = None):
		super(ActuatorData, self).__init__(name = name, typeID = typeID, d = d)
		
		self.value = ConfigConst.DEFAULT_VAL
		self.command = ConfigConst.DEFAULT_COMMAND
		self.stateData = ""
		self.isResponse = False
		pass
	
	def getCommand(self) -> int:
		return self.command
		pass
	
	def getStateData(self) -> str:
		return self.stateData
		pass
	
	def getValue(self) -> float:
		return self.value
		pass
	
	def isResponseFlagEnabled(self) -> bool:
		return self.isResponse
	
	def setCommand(self, command: int):
		self.command = command
		self.updateTimeStamp()
		pass
	
	def setAsResponse(self):
		self.isResponse = True
		self.updateTimeStamp()
		pass
		
	def setStateData(self, stateData: str):
		if stateData:
			self.stateData = stateData
			self.updateTimeStamp()
		pass
	
	def setValue(self, val: float):
		self.value = val
		self.updateTimeStamp()
		pass
		
	def _handleUpdateData(self, data):
		if data and isinstance(data, ActuatorData):
			self.command = data.getCommand()
			self.stateData = data.getStateData()
			self.value = data.getValue()
			self.isResponse = data.isResponseFlagEnabled()
		
		pass
		