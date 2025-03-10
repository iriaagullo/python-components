#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import programmingtheiot.common.ConfigConst as ConfigConst

class BaseSystemUtilTask():
	"""
	Shell implementation representation of class for student implementation.
	
	"""
	
	def __init__(self, name: str = ConfigConst.NOT_SET, typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE):
		
		self.name = name
		self.typeID = typeID
		
		pass
	
	def getName(self) -> str:
		return self.name
		pass
	
	def getTypeID(self) -> int:
		return self.typeID
		pass
	
	def getTelemetryValue(self) -> float:
		pass
	