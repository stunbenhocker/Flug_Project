import RPi.GPIO as GPIO
import time

#BCM 번호 체계를 사용
GPIO.setmode(GPIO.BCM)
#BCM21에 시그널 핀을 연결함
sensor = 21
GPIO.setup(sensor, GPIO.IN)
time.sleep(2)

delay = 0

def moving():	
	#감지되면 출력
	while True:
		if GPIO.input(sensor):
			delay = 1
			return delay
		else:
		 	return None