from micInput import micController
from webcamInput import webcamController
import threading
import time

# mic = micController()
# try:
mic = micController()
webcam = webcamController()
# threading.Thread( target=mic.run())
threading.Thread( target=webcam.run())
# _thread.start_new_thread( webcam.run())
# except:
#     print("Something went wrong")

while(1):
    pass