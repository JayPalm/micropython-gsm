from time import sleep


from gsm import SIM7000

sim7000_config = {"power_pin": 4, "uart_rx": 26, "uart_tx": 27}


if __name__ == "__main__":

    gsm = SIM7000(**sim7000_config)
    gsm.power(True)
    gsm.connect()
    gsm.sendCmd("AT+SGPIO=0,4,1,1")
    res, data = gsm.waitResponse(timeout=10000)
    if not res:
        print("error")
    gsm.enableGPS()

    while True:
        print(gsm.getGPS())
        print(gsm.getGPSTime())
        print(gsm.getGNSSMode())
        sleep(1)
