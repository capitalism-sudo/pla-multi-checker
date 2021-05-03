from time import sleep
from abc import ABC, abstractmethod 

class Controller(ABC):
    # Botton
    def A(self,duration = 0.1):
        pass
    def B(self,duration = 0.1):
        pass
    def X(self,duration = 0.1):
        pass
    def Y(self,duration = 0.1):
        pass
    def L(self,duration = 0.1):
        pass
    def R(self,duration = 0.1):
        pass
    def ZL(self,duration = 0.1):
        pass
    def ZR(self,duration = 0.1):
        pass
    # Press down left stick
    def LS(self,duration = 0.1):
        pass
    # Press down right stick
    def RS(self,duration = 0.1):
        pass
    # Plus
    def p(self,duration = 0.1):
        pass
    # Minus
    def m(self,duration = 0.1):
        pass
    # Home
    def h(self,duration = 0.1):
        pass
    # Capture
    def c(self,duration = 0.1):
        pass
    # DPAD
    def l(self,duration = 0.1):
        pass
    def u(self,duration = 0.1):
        pass
    def r(self,duration = 0.1):
        pass
    def d(self,duration = 0.1):
        pass

    # LEFT STICK
    def ls_l(self,duration = 0.1):
        pass
    def ls_r(self,duration = 0.1):
        pass
    def ls_d(self,duration = 0.1):
        pass
    def ls_u(self,duration = 0.1):
        pass

    # RIGHT STICK
    def rs_l(self,duration = 0.1):
        pass
    def rs_r(self,duration = 0.1):
        pass
    def rs_d(self,duration = 0.1):
        pass
    def rs_u(self,duration = 0.1):
        pass

    def pause(self,duration):
        sleep(duration)

    def quit_app(self):
        self.h()
        sleep(0.5)
        self.X()
        self.A()

    def enter_app(self):
        self.A()
        sleep(1)
        self.A()

    def unlock(self):
        self.A()
        sleep(2)
        self.A()
        self.A()
        self.A()

    def sleepmode(self):
        self.h()
        sleep(0.5)
        self.d()
        self.r(0.7)
        self.A()
        sleep(0.5)
        self.A()
        print('Switch entering sleep mode')

    def attach(self):
        self.LS()
        self.A()
        self.h()
        sleep(1)
        self.A()
        sleep(2)

    def detach(self):
        self.h()
        self.pause(1)
        self.d()
        for jj in range(3):
            self.r()
        self.A()
        self.pause(1)
        self.A()
