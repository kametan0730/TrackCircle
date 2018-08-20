import cv2
import numpy as np
import time

class Circle:
	x = 0
	y = 0
	radius = 0
	objectId = 0
	lastUpdate = 0;
	lastDistance = 0;
	def __init__(self, x, y, r): 
		self.x = x
		self.y = y
		self.radius = r
		
	def distance(self, circle2):
		dx = int(self.x) - int(circle2.getX())
		dy = int(self.y) - int(circle2.getY())
		dis = np.sqrt(dx*dx + dy*dy)
		return dis

	def getInfo(self):
		return (self.radius,self.x, self.y)
		
	def getCenter(self):
		return (self.x, self.y)
		
	def getLastUpdate(self):
		return self.lastUpdate
	def setUpdate(self, count):
		self.lastUpdate = count
		
	def getX(self):
		return self.x
	def getY(self):
		return self.y
	def getRadius(self):
		return self.radius
		
	def getObjectId(self):
		return self.objectId
	def setObjectId(self, objectId):
		self.objectId = objectId
		
	def syncObject(self, circle2):
		self.x = circle2.getX()
		self.y = circle2.getY()
		self.radius = circle2.getRadius()
	
	def setLastDistance(self, distance):
		self.lastDistance = distance
	def getLastDistance(self):
		return self.lastDistance
	
	def equals(self, circle2):
		return ((self.x == circle2.getX()) and  (self.y == circle2.getY()) and (self.radius == circle2.getRadius()))
		
def searchMinDistancePair(pairObjects):
	minDistance = 100
	minPair = None
	for pair in pairObjects:
		if(pair[0] <= minDistance):
			minDistance = pair[0]
			minPair = pair
	return minPair
	
cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280*1.5);
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720*1.5); 

green = (0,255,0)
red = (0,0,255)
gray = (160,160,160)
white = (255, 255, 255)
updateCount = 0
circleId = 0;
discoveredCircleList = [];

while(cap.isOpened()):
	startTime = time.time()
	updateCount+=1
	resultCircleList = []
	originalImage = cap.read()[1]
	noColorImage = cv2.cvtColor(originalImage,cv2.COLOR_RGB2GRAY)
	noColorImage = cv2.medianBlur(noColorImage,5)
	circles = cv2.HoughCircles(noColorImage,cv2.HOUGH_GRADIENT,1,50, param1=30,param2=90,minRadius=15,maxRadius=80)
	#print(str(time.time() - startTime));
	if(circles is not None):
		circles = np.uint16(np.around(circles))[0]
		
		for i in circles:
			resultCircleList.append(Circle(i[0], i[1], i[2]))
			
	pairObjects = []
	for discoveredCircle in discoveredCircleList:

		if(discoveredCircle.getLastUpdate() < updateCount - 10):
			#オブジェクトを削除
			discoveredCircleList.remove(discoveredCircle)
			continue
			
		for resultCircle in resultCircleList:
			distance = discoveredCircle.distance(resultCircle)
			if(distance < 99):
				pairObjects.append([distance,discoveredCircle,resultCircle])
		
	while(not len(pairObjects) == 0):
		
		discovered = searchMinDistancePair(pairObjects)
		deletePairList = [];
		
		for pair in pairObjects:
			if((discovered[1].equals(pair[1])) or (discovered[2].equals(pair[2]))):
				deletePairList.append(pair)
		
		resultCircleList.remove(discovered[2])
		key = discoveredCircleList.index(discovered[1])
		discoveredCircleList[key].syncObject(discovered[2])
		discoveredCircleList[key].setUpdate(updateCount)
		discoveredCircleList[key].setLastDistance(discovered[0])

		for pair in deletePairList:
			pairObjects.remove(pair)
				
	for resultCircle in resultCircleList:
		#オブジェクトを新規登録
		resultCircle.setUpdate(updateCount)
		circleId+=1
		resultCircle.setObjectId(circleId)
		discoveredCircleList.append(resultCircle)
		
	for discoveredCircle in discoveredCircleList:
		#円と文字を描画
		fontScale = np.ceil(discoveredCircle.getRadius()/15)
		thickness = discoveredCircle.getRadius()/10
		if(discoveredCircle.getLastUpdate() == updateCount):
			cv2.circle(originalImage ,discoveredCircle.getCenter(), discoveredCircle.getRadius(), green, 5)
			cv2.circle(originalImage ,discoveredCircle.getCenter(), 2, red, discoveredCircle.getRadius()/10)
			cv2.putText(originalImage, str(discoveredCircle.getObjectId()), discoveredCircle.getCenter(), cv2.FONT_HERSHEY_PLAIN, fontScale, white, thickness, 4)
		else:
			cv2.circle(originalImage ,discoveredCircle.getCenter(), discoveredCircle.getRadius(), gray, 5)
			cv2.putText(originalImage, str(discoveredCircle.getObjectId()), discoveredCircle.getCenter(), cv2.FONT_HERSHEY_PLAIN, fontScale, white, thickness, 4)
		
	originalImage = cv2.resize(originalImage, (1280, 720))
	cv2.imshow('CV2', originalImage)

	if cv2.waitKey(1) & 0xFF == ord("q"):
		break
