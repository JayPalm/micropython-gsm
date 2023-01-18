import re
from time import sleep, ticks_ms

from gsm.gprs import GPRS
from gsm.gps import GPS
from gsm.modem import MODEM
from machine import UART, Pin


class SIM7000(GPS, GPRS, MODEM):
    def __init__(
        self,
        power_pin: int = 0,
        rst_pin: int = 0,
        dtr_pin: int = 0,
        uart_rx: int = 0,
        uart_tx: int = 0,
        uart_baud: int = 115200,
        uart_id: int = 1,
        apn: str = "",
        gsm_username: str = "",
        gsm_password: str = "",
        **kwargs,
    ):
        self.power_pin = Pin(power_pin, Pin.OUT)
        self.rst_pin = Pin(rst_pin, Pin.OUT)
        self.dtr_pin = Pin(dtr_pin, Pin.OUT)
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

    def getBatteryLevel(self) -> str:
        cmd = "AT+CBC"

        return self.sendAndGet(cmd)

    def enter_command_mode_dtr(self):
        self.dtr_pin.value(0)
        sleep(1)
        self.dtr_pin.value(1)
        return True

    def get_gsm_info(self, timeout=30, param_timeout=1000):
        self.enter_command_mode_dtr()
        counter = 0
        data = {}
        data_points = [
            {"key": "sig", "cmd": "AT+CSQ", "re": r".*(\+CSQ\: \d+,\d+)\.*"},
            {
                "key": "car",
                "cmd": "AT+COPS?",
                "re": r'.*(\+COPS: \d,\d,"[a-zA-Z \-]*",\d+)\.*',
            },
            {"key": "bat", "cmd": "AT+CBC", "re": r".*(\+CBC: \d+,\d+,\d+).*"},
        ]
        # data_keys = {"sig": "AT+CSQ", "car": "AT+COPS?", "bat": "AT+CBC"}

        for dp in data_points:
            key = dp["key"]
            cmd = dp["cmd"]
            re_pat = dp["re"]
            start_millis = ticks_ms()
            while True:
                counter += 1
                if (ticks_ms() - start_millis) > param_timeout:
                    data[key] = ""
                    break
                _ = self.stream.read()
                self.sendCmd(cmd)
                r, d = self.waitResponse(timeout=timeout)
                try:
                    d_str = d.decode()
                    print(d_str)
                    match = re.match(re_pat, d_str)
                    if match:
                        data[key] = match.group(1)
                        break
                except Exception:
                    ...
        self.enter_data_mode()
        self.enter_data_mode()
        self.enter_data_mode()
        data["attempts"] = counter

        return data


# Break PPP Mode?
# time.sleep(1); gsm.stream.write("+++"); time.sleep(1)


# z = {
#     "sig": "AT+CSQ\r\r\n+CSQ: 20,99\r\n\r\nOK\r\n",
#     "car": 'AT+COPS?\r\r\n+COPS: 0,0,"Boost Mobile",7\r\n\r\nOK\r\n',
#     "bat": "AT+CBC\r\r\n+CBC: 0,66,3863\r\n\r\nOK\r\n",
#     "attempts": 36,
# }

# r = {
#     "sig": r"AT\+CSQ\s+(\+CSQ\: \d+,\d+)\s+OK\s*",
#     "car": r'AT\+COPS\?\s*(\+COPS: \d,\d,"[a-zA-Z ]*",\d+)\s*OK\s*',
#     "bat": r"AT\+CBC\s+(\+CBC: \d+,\d+,\d+)\s+OK\s*",
#     "attempts": 36,
# }
##### OLD
# data_points = [
#     {
#         "key": "sig",
#         "cmd": "AT+CSQ",
#         "re": r"\s*AT\+CSQ\s+(\+CSQ\: \d+,\d+)\s+OK\s*",
#     },
#     {
#         "key": "car",
#         "cmd": "AT+COPS?",
#         "re": r'\s*AT\+COPS\?\s*(\+COPS: \d,\d,"[a-zA-Z ]*",\d+)\s*OK\s*',
#     },
#     {
#         "key": "bat",
#         "cmd": "AT+CBC",
#         "re": r"\s*AT\+CBC\s+(\+CBC: \d+,\d+,\d+)\s+OK\s*",
#     },
# ]
