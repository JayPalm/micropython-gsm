"""Test PPP Connection
Establishing [PPP](https://en.wikipedia.org/wiki/Point-to-Point_Protocol) is useful on micropython, as it allows using built in sockets to access internet and the like.
For reference and documentation about AT commands used in this example or in the library, please see [AT CMD reference for SIM7000](https://cdn.geekfactory.mx/sim7000g/SIM7000%20Series_AT%20Command%20Manual_V1.06.pdf)

"""

# AT CMD reference for SIM7000:
# https://cdn.geekfactory.mx/sim7000g/SIM7000%20Series_AT%20Command%20Manual_V1.06.pdf


from time import sleep

from gsm import SIM7000

# You will likely need to change your APN based on the wireless provider of your SIM card
sim7000_config = {"power_pin": 4, "uart_rx": 26, "uart_tx": 27, "apn": "mobilenet"}


if __name__ == "__main__":
    gsm = SIM7000(**sim7000_config)
    gsm.power(True)
    gsm.connect()

    gsm = SIM7000(**sim7000_config)
    gsm.power(True)
    gsm.connect()
    gsm_initialized = False

    while not gsm_initialized:

        gsm_initialized = gsm.init()
        sleep(2)

    gsm.connect_ppp()

    ppp_test = gsm.test_ppp_connection()
    print(f'PPP Test result: {"Success" if ppp_test else "Fail"}')
