# This list of frozen files doesn't include task.py because that's provided by the C module.

freeze(
    "..",
    (
        "gsm/__init__.py",
        "gsm/at_base.py"
        "gsm/gprs.py",
        "gsm/gps.py",
        "gsm/modem.py",
        "gsm/sim7000.py",
    ),
    opt=3,
)
