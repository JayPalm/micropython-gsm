import sys
from time import ticks_ms, sleep
from micropython import const


class ATBase:
    DISCONNECT = const(0)
    CONNECT = const(1)
    BUSY = const(2)

    def __init__(self, stream, **kwargs):
        # check arg
        if not hasattr(stream, "write") or not hasattr(stream, "readline"):
            raise Exception("Invalid Argument", stream)

        self.stream = stream
        self.__status = ATBase.DISCONNECT

    def getStatus(self):
        return self.__status

    def connect(self, timeout=20000):
        res = False
        startMillis = ticks_ms()
        while not res:
            self.sendCmd("AT")
            res, data = self.waitResponse()
            if (ticks_ms() - startMillis) > timeout:
                raise Exception("Timeout")
        self.__status = ATBase.CONNECT
        return self.__status

    def sendCmd(self, cmd):
        # check arg
        if not isinstance("a", str):
            raise Exception("Invalid Argument", cmd)

        # check cmd
        if cmd.find("AT") == -1:
            raise Exception("String 'AT' not found ", cmd)
        if cmd.find("AT") != 0:
            raise Exception("Command must start with 'AT'", cmd)

        if cmd.find("\r") != (len(cmd) - 2) or cmd.find("\n") != (len(cmd) - 1):
            cmd = cmd + "\r\n"

        self.stream.write(cmd)

    def waitResponse(self, rsp1="OK\r\n", rsp2="ERROR\r\n", timeout=1000):
        rsp = bytearray()
        startMillis = ticks_ms()
        try:
            while (ticks_ms() - startMillis) < timeout:
                if self.stream.any():
                    rsp.extend(bytearray(self.stream.readline()))
                    if rsp.decode("utf-8").endswith(rsp1):
                        return True, rsp
                    if rsp.decode("utf-8").endswith(rsp2):
                        return False, rsp
        except Exception as err:
            print(f"waitResponse failed {err}")
        return False, rsp

    def sendAndGet(self, cmd: str) -> str:
        "Send AT command and return response"
        self.sendCmd(cmd)
        res, data = self.waitResponse()
        if res:
            data = data.decode().replace(cmd, "").replace("OK", "").strip()
            return data
        return ""

    def parseResponse(self, data, head):
        # check cmd
        if not (isinstance(data, str) or isinstance(data, bytearray)):
            raise Exception("Invalid Argument", data)
        if not isinstance(head, str):
            raise Exception("Invalid Argument", head)

        s = ""
        if isinstance(data, bytearray):
            s = data.decode("utf-8")
        s = s[s.find(head) + len(head) :]
        s = s[: s.find("\r\n")]
        return s.lstrip()

    def parseResp(self, data, head):
        if not (isinstance(data, str) or isinstance(data, bytearray)):
            raise Exception("Invalid Argument", data)
        if not isinstance(head, str):
            raise Exception("Invalid Argument", head)
        s = ""
        if isinstance(data, bytearray):
            data = data.decode()
        data = data.strip()

    def at_console(self):
        "Launch Interactive AT console. Note: This is currently blocking"
        while True:
            try:
                cmd = input("<- ")
                if cmd:
                    self.sendCmd(cmd)
                    r, d = self.waitResponse()
                    d_str = d.decode()
                    print(r)
                    print(f"-> {d_str}")
                    cmd = ""
            except KeyboardInterrupt:
                print("Exit by Keyboard Interupt")
                sys.exit()
            except Exception as err:
                print(f"Exception caught: {err}")
                print("To exit: ctrl+c")

    def enter_command_mode(self):
        sleep(1)
        self.stream.write("+++")
        sleep(1)
