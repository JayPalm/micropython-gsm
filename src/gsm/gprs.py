from time import sleep, ticks_ms

from network import PPP

from gsm.at_base import ATBase


class GPRS(ATBase):
    """
    SIM card functions
    """

    def __init__(
        self, stream, apn: str = "", gsm_username: str = "", gsm_password: str = ""
    ):
        super().__init__(stream)
        self.apn = apn
        self.gsm_username = gsm_username
        self.gsm_password = gsm_password
        self.ppp = PPP(stream)

    def simUnlock(self):
        """
        Unlocks the SIM

        TODO: to be realized
        """

    def getSimCCID(self):
        """
        Gets the CCID of a sim card via AT+CCID
        """
        cmd = "AT+CCID"
        return self.sendAndGet(cmd)

    def getIMEI(self):
        """
        Asks for TA Serial Number Identification (IMEI)
        """
        cmd = "AT+CGSN"
        return self.sendAndGet(cmd)

    def getIMSI(self):
        """
        Asks for International Mobile Subscriber Identity IMSI
        """
        cmd = "AT+CIMI"
        return self.sendAndGet(cmd)

    def getSimStatus(self, timeout=10000):
        """
        TODO: Not Tested
        """
        startMillis = ticks_ms()
        while (ticks_ms() - startMillis) < timeout:
            self.sendCmd("AT+CPIN?")
            res, data = self.waitResponse()
            if not res:
                sleep(1)
                continue
            s = self.parseResponse(data, "+CPIN:")
            if s == "READY":
                return (1, "READY")
            elif s == "SIM PIN":
                return (2, "SIM PIN")
            elif s == "SIM PUK":
                return (3, "SIM PUK")
            elif s == "PH_SIM PIN":
                return (4, "PH_SIM PIN")
            elif s == "PH_SIM PUK":
                return (5, "PH_SIM PUK")
            elif s == "SIM PIN2":
                return (5, "SIM PIN2")
            elif s == "SIM PUK2":
                return (5, "SIM PUK2")
        return (0, "")

    # GPRS functions

    def gprsConnect(self):
        """
        TODO: to be realized
        """

    def gprsDisconnect(self):
        """
        TODO: to be realized
        """
        pass

    def isGprsConnected(self):
        """
        Checks if current attached to GPRS/EPS service

        TODO: to be realized
        """

    def setOperatorFormat(self):
        """Set Operator format. This needs to be called before checking for operator"""
        self.sendCmd("AT+COPS=3,0")
        res, data = self.waitResponse()

    def getOperator(self):
        """Get Operator"""
        self.sendCmd("AT+COPS?")
        res, data = self.waitResponse()
        return (res, data.decode())

    def getRegistrationStatus(self):
        cmd = "AT+CEREG?"
        data = self.sendAndGet(cmd)
        if data:
            data = data.replace("+CEREG: ", "").split(",")
            return data[1]
        return -1

    def connect_ppp(self):
        # Connect to network and establish PPP

        self.sendCmd(f'AT+CGDCONT=1,"IP","{self.apn}"')
        self.waitResponse()
        self.sendCmd('AT+CGDATA="PPP",1')
        self.waitResponse()
        sleep(2)
        # Hand modem object off to system PPP module
        self.ppp = PPP(self.stream)
        self.ppp.active(True)
        self.ppp.connect(
            authmode=self.ppp.AUTH_PAP,
            username=self.gsm_username,
            password=self.gsm_password,
        )
        attempts = 10
        while attempts:
            if self.ppp.ifconfig()[0] != "0.0.0.0":
                return True
            attempts -= 1
            sleep(2)
        print("Failed to establish PPP. Please check config")
        return False

    def test_ppp_connection(self) -> bool:
        try:
            import socket

            addr = socket.getaddrinfo("micropython.org", 80)[0][-1]
            if addr:
                return True
        except Exception:
            ...

        return False

    def ifconfig(self) -> tuple:
        return self.ppp.ifconfig()
