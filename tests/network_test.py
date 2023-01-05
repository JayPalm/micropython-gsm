"""
Network Test

Cycle through network modes and attempt to connect via each.

Network Modes
  - 2,  # Automatic
  - 13, # GSM only
  - 38, # LTE only
  - 51  # GSM and LTE only

"""
from time import sleep


from gsm import SIM7000

# You will likely need to change your APN based on the wireless provider of your SIM card
sim7000_config = {"power_pin": 4, "uart_rx": 26, "uart_tx": 27, "apn": "mobilenet"}

if __name__ == "__main__":

    gsm = SIM7000(**sim7000_config)
    gsm.power(True)
    gsm.connect()

    while True:
        gsm.init()
        isConnected = False
        for i in [2, 13, 38, 51]:

            gsm.setNetworkMode(i)
            sleep(3)
            tryCount = 60
            while tryCount:
                print(gsm.getSignalQuality())
                isConnected = gsm.isNetworkConnected()
                print("CONNECT" if isConnected else "NO CONNECT")
                if isConnected:
                    break
                tryCount -= 1
            if isConnected:
                break

        print("Device is connected .")
        print("=====Inquiring UE system information=====")
        gsm.sendCmd("AT+CPSI?")
        res, data = gsm.waitResponse()
        print(data)
        break
