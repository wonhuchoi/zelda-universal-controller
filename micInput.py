import pyaudio
import sys
import numpy as np
import aubio
from pynput.keyboard import Key, Controller
import pyautogui


class micController:
  def __init__(self):
      # pass
    # initialise pyaudio
    self.keyboard = Controller()
    self.p = pyaudio.PyAudio()

  slidingWindow = [None, None, None]

  keyMap = {
    0.0 : '',
    68.0 : 'A',
    71.0 : 'B',
    73.0 : 'D',
    75.0 : 'E',
    76.0 : 'F',
    78.0 : 'G',
    80.0 : 'A',
    83.0 : 'B',
    84.0 : 'C',
    86.0 : 'D',
    87.0 : 'E',
    88.0 : 'F'
  }

  keyboardMap = {
    'right': 'h',
    'left': 'f',
    'up': 't',
    'down': 'g',
    'A': 'a',
    '': '',
    'aright': Key.right,
    'aleft': Key.left,
    'aup': Key.up,
    'adown': Key.down,
  }


  controlMap = {
    0.0 : '',
    68.0 : '',
    71.0 : 'right',
    73.0 : '',
    75.0 : 'down',
    76.0 : 'up',
    78.0 : 'A',
    80.0 : '',
    83.0 : 'left',
    84.0 : 'aright',
    86.0 : 'aleft',
    87.0 : 'aup',
    88.0 : 'adown'
  }

  possibleVals = list(keyMap.keys())

  def moveSlidingWindow(self,key):
        self.slidingWindow[0] = self.slidingWindow[1]
        self.slidingWindow[1] = self.slidingWindow[2]
        self.slidingWindow[2] = key
        # print(slidingWindow)

  def pressKey(self, input, releaseKey = None):
      # print("pressing key", input)
      if input == None:
        return
      keyToPress = self.keyboardMap[input]
      if releaseKey != input and releaseKey != None:
        keyToRelease = self.keyboardMap[releaseKey]
        self.keyboard.release(keyToRelease)
      if keyToPress == '' and releaseKey != None:
        print("I'm doin gthis")
        keyToRelease = self.keyboardMap[releaseKey]
        self.keyboard.release(keyToRelease)
      elif keyToPress == '' and releaseKey == None:
        return
      else:  
        print("I'm doin gthis111", keyToPress)
        self.keyboard.press(keyToPress)
        return input

  def getClosest(self, val1, val2, target): 
    
      if (target - val1 >= val2 - target): 
          return val2 
      else: 
          return val1 

  def findClosest(self, arr, n, target): 
    
      # Corner cases 
      if (target <= arr[0]): 
          return arr[0] 
      if (target >= arr[n - 1]): 
          return arr[n - 1] 
    
      # Doing binary search 
      i = 0; j = n; mid = 0
      while (i < j):  
          mid = int((i + j) / 2)
    
          if (arr[mid] == target): 
              return arr[mid] 
    
          # If target is less than array  
          # element, then search in left 
          if (target < arr[mid]) : 
    
              # If target is greater than previous 
              # to mid, return closest of two 
              if (mid > 0 and target > arr[mid - 1]): 
                  return self.getClosest(arr[mid - 1], arr[mid], target) 
    
              # Repeat for left half  
              j = mid 
            
          # If target is greater than mid 
          else : 
              if (mid < n - 1 and target < arr[mid + 1]): 
                  return self.getClosest(arr[mid], arr[mid + 1], target) 
                    
              # update i 
              i = mid + 1
            
      # Only single element left after search 
      return arr[mid]
  # open stream
  def run(self):
      buffer_size = 1024
      pyaudio_format = pyaudio.paFloat32
      n_channels = 1
      samplerate = 44100
      stream = self.p.open(format=pyaudio_format,
                      channels=n_channels,
                      rate=samplerate,
                      input=True,
                      frames_per_buffer=buffer_size)

      if len(sys.argv) > 1:
          # record 5 seconds
          output_filename = sys.argv[1]
          record_duration = 5 # exit 1
          outputsink = aubio.sink(sys.argv[1], samplerate)
          total_frames = 0
      else:
          # run forever
          outputsink = None
          record_duration = None

      # setup pitch
      tolerance = 0.8
      win_s = 4096 # fft size
      hop_s = buffer_size # hop size
      pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
      pitch_o.set_unit("midi")
      pitch_o.set_tolerance(tolerance)
      currentKey = None
      print("*** starting recording")
      while True:
          try:
              audiobuffer = stream.read(buffer_size)
              signal = np.fromstring(audiobuffer, dtype=np.float32)

              pitch = pitch_o(signal)[0]
              confidence = pitch_o.get_confidence()
              # if pitch == 0.0:
              #       continue
              # if(pitch != 0):
              
              #   print("{} / {}".format(pitch,confidence))
              keyPressed = self.controlMap[self.findClosest(self.possibleVals, len(self.possibleVals), pitch)]
              # if val != 'A':
              #   print(keyMap[findClosest(possibleVals, len(possibleVals), pitch)])

              self.moveSlidingWindow(keyPressed)

              if self.slidingWindow[0] == self.slidingWindow[1] and self.slidingWindow[1] == self.slidingWindow[2] and self.slidingWindow[0] != None:
                # print(slidingWindow)
                pressedKey = self.pressKey(keyPressed, currentKey)
                currentKey = pressedKey

              if outputsink:
                  outputsink(signal, len(signal))

              if record_duration:
                  total_frames += len(signal)
                  if record_duration * samplerate < total_frames:
                      break
          except KeyboardInterrupt:
              print("*** Ctrl+C pressed, exiting")
              break

      print("*** done recording")
      stream.stop_stream()
      stream.close()
      self.p.terminate()


  # import numpy as np

  # pitches=[69]
  # dur=0.5
  # Fs=4000
  # amp=1

  # N = int(dur * Fs)
  # t = np.arange(N) / Fs
  # x = []

  # for p in pitches:
  #     freq = 2 ** ((p - 69) / 12) * 440
  #     x = np.append(x, np.sin(2 * np.pi * freq * t))

  # print(x)