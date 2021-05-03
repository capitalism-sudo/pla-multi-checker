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
