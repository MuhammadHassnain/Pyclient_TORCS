'''
Created on Apr 4, 2012

@author: lanquarden
'''

import msgParser
import carState
import carControl

class Driver(object):
    '''
    A driver object for the SCRC
    '''

    def __init__(self, stage):
        '''Constructor'''
        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage

        self.parser = msgParser.MsgParser()

        self.state = carState.CarState()

        self.control = carControl.CarControl()

        self.steer_lock =0.805398 #0.785398
        self.max_speed = 400
        self.prev_rpm = None

        self.prev_accel = 0
        self.prev_gear = 0

    def init(self):
        '''Return init string with rangefinder angles'''
        self.angles = [0 for x in range(19)]

        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15

        for i in range(5, 9):
            self.angles[i] = -20 + (i-5) * 5
            self.angles[18 - i] = 20 - (i-5) * 5

        return self.parser.stringify({'init': self.angles})

    def drive(self, msg):
        self.state.setFromMsg(msg)

        print self.state.getTrack()[9]

        self.steer()

        self.gear()

        self.speed1()

        self.brake()
        

        return self.control.toMsg()

    def brake(self):
        track = self.state.getTrack()
        speed = self.state.getSpeedX()

        front_edge = track[9]
        brake = self.control.getBrake()

        if(front_edge>100):
            brake = 0
        
        elif(front_edge<=100 and speed > 100):
            brake = (1/front_edge+0.5)*100
        else:
            brake = 0
        if (brake > 1.0):
            brake = 1
        
        print brake

        self.control.setBrake(brake)
                
    def steer(self):
        angle = self.state.angle
        dist = self.state.trackPos

        steer = (angle - dist* 0.8)/self.steer_lock

        if steer < -1.0:
            steer = -1.0
        elif steer > 1.0:
            steer = 1.0
        self.control.setSteer(steer)

    def gear(self):
        speedX = self.state.getSpeedX()
        gear = 1
        rpm = self.state.getRpm()
        prev_gear = self.control.getGear()
        if (prev_gear == 5 and rpm>5000 and rpm < 7000 and speedX > 150):
            gear = 5
        elif (prev_gear == 5 and rpm > 7000 and speedX > 210):
            gear = 6
        elif (prev_gear == 6 and rpm > 5000 and speedX > 200):
            gear = 6
        else:
            if speedX > 30:
                gear = 2
            if speedX > 50:
                gear = 3
            if speedX > 80:
                gear = 4
            if speedX > 160:
                gear = 5
            if speedX > 220:
                gear = 6
        self.control.setGear(gear)
    
    

    def speed(self):
        speed = self.state.getSpeedX()
        accel = self.control.getAccel()

        if speed < self.max_speed:
            accel += 0.1
            if accel > 1:
                accel = 1.0
        else:
            accel -= 0.1
            if accel < 0:
                accel = 0.0

        self.control.setAccel(accel)

    def speed1(self):
        speedX = self.state.getSpeedX()
        steer = self.control.getSteer()
        accel = self.prev_accel
        wheelSpinVal = self.state.getWheelSpinVel()

        if speedX < self.max_speed - steer*50:
            accel +=0.1
        else:
            accel -= 0.1
        
        if accel > 1.0:
            accel = 1.0
        
        if speedX < 10:
            accel += 1/ (speedX + 0.1)
        
        
        if (wheelSpinVal[2]+wheelSpinVal[3]) - (wheelSpinVal[1]+wheelSpinVal[0]) > 6:
            accel -= 0.2
        if accel < 0:
            accel = 0.0
        self.prev_accel = accel
        
        self.control.setAccel(accel)


    def onShutDown(self):
        pass

    def onRestart(self):
        pass
