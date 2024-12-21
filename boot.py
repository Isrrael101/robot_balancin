import network
import esp
import gc

def init_wifi():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='RobotAP',
              authmode=network.AUTH_WPA_WPA2_PSK,
              password='12345678',
              channel=1,
              max_clients=1)
    
    print('Red WiFi: RobotAP')
    print('Password: 12345678')
    print('IP:', ap.ifconfig()[0])
    
    return ap

esp.osdebug(None)
ap = init_wifi()
gc.collect()
