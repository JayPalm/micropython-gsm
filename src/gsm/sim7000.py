from time import sleep

from machine import UART, Pin

from gsm.gprs import GPRS
from gsm.gps import GPS
from gsm.modem import MODEM


class SIM7000(GPS, GPRS, MODEM):
    def __init__(
        self,
        power_pin: int,
        uart_rx: int,
        uart_tx: int,
        uart_baud: int = 115200,
        uart_id: int = 1,
        apn: str = "",
        gsm_username: str = "",
        gsm_password: str = "",
    ):
        self.power_pin = Pin(power_pin, Pin.OUT)
        self.uart_rx = uart_rx
        self.uart_tx = uart_tx
        self.uart_baud = uart_baud
        self.uart_id = uart_id
        self.apn = apn
        self.gsm_username = gsm_username
        self.gsm_password = gsm_password

        self.stream = self.__make_uart__()
        super().__init__(stream=self.stream, apn=self.apn)

    def __make_uart__(self):
        return UART(
            self.uart_id, baudrate=self.uart_baud, rx=self.uart_rx, tx=self.uart_tx
        )

    def power(self, active: bool):
        """Power up module"""
        if active:
            self.power_pin.value(1)
            sleep(0.5)
            self.power_pin.value(0)
            sleep(0.5)
            self.power_pin.value(1)
            sleep(10)
        else:
            self.power_pin.value(0)
            sleep(1)

    def getNetworkMode(self):
        """Get Network Mode using AT+CNMP?
        Responses:
            2  - Automatic
            13 - GSM only
            38 - LTE only
            51 - GSM and LTE only
        """
        cmd = "AT+CNMP?"
        return self.sendAndGet(cmd).replace("+CNMP: ", "")

    def setNetworkMode(self, mode) -> bool:
        """
        2  - Automatic
        13 - GSM only
        38 - LTE only
        51 - GSM and LTE only
        """
        self.sendCmd(f"AT+CNMP={mode}")
        res, data = self.waitResponse()
        if res:
            return True

        return False

    def isNetworkConnected(self):
        status = self.getRegistrationStatus()
        return status == 1 or status == 5

    def getFirmwareVersion(self) -> str:
        cmd = "AT+CGMR"
        self.sendCmd(cmd)
        return self.sendAndGet(cmd)
