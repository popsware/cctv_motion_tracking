
import requests
ifttt_key = 'pzZ8_g2o-Kyo3Xcyk5fMx'
ifttt_event = 'globalmotion_deepsleep'

response = requests.post('https://maker.ifttt.com/trigger/'+ifttt_event+'/with/key/'+ifttt_key,
                         params={"value1": "Test Title", "value2": "Test Message", "value3": "Test Value 3"})
