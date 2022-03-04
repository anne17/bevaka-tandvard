# bevaka-tandvard
Monitor last-minute time slots at Folktandvården and send email upon change.


## How to run

1. Copy `config_default.py` to `config.py` and fill in the sender and receiver information (email adresses).

2. Add the following cron job (it will check for changes every 20 minutes):

```
*/20 * * * * cd [path to]/bevaka-tandvard && venv/bin/python3 bevakning.py
```
