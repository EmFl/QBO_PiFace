#!/usr/bin/env python2.7

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr
import subprocess
import pipes
import json
import apiai
import time
import yaml

class QBOtalk:
    def __init__(self):
	config = yaml.safe_load(open("/home/pi/Documents/config.yml"))

        CLIENT_ACCESS_TOKEN = config["tokenAPIai"]
	print "TOKEN: " + CLIENT_ACCESS_TOKEN
#	You can enter your token in the next line
#        CLIENT_ACCESS_TOKEN = 'YOUR_TOKEN'
        # obtain audio from the microphone
        self.r = sr.Recognizer()
        self.ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
        self.Response = "hello"
        self.GetResponse = False
        self.GetAudio = False
        self.strAudio = ""
        
        for i, mic_name in enumerate (sr.Microphone.list_microphone_names()):
            if(mic_name == "dmicQBO_sv"):
                self.m = sr.Microphone(i)
        with self.m as source:        
            self.r.adjust_for_ambient_noise(source)

    def Decode(self, audio):
        try:
            # print(r.recognize_google(audio,language="es-ES"))

#            str = self.r.recognize_google(audio, language="es-ES")
            str = self.r.recognize_google(audio)
	    print "LISTEN: " + str
            request = self.ai.text_request()
#	    request.lang = 'es'
            request.query = str
            response = request.getresponse()
            jsonresp = response.read()
            data = json.loads(jsonresp)
            str_resp = data["result"]["fulfillment"]["speech"]

        except sr.UnknownValueError:
            str_resp = ""
        except sr.RequestError as e:
            str_resp = "Could not request results from Speech Recognition service"
        return str_resp
    
    def SpeechText(self, text):
        speak = "espeak -ven+f3 \"" + text + "\" --stdout  | aplay -D convertQBO"
        print "QBOtalk: " + speak
	result = subprocess.call(speak, shell = True)
        print text
    
    def callback(self, recognizer, audio):
        try:
            self.Response = self.Decode(audio)
            self.GetResponse = True
            print("Google say ")
            #self.SpeechText(self.Response)
        except:
            return
        
    def callback_listen(self, recognizer, audio):
        print("callback listen")
        try:
            #strSpanish = self.r.recognize_google(audio,language="es-ES")
	    with open("microphone-results.wav", "wb") as f:
    		f.write(audio.get_wav_data())
            self.strAudio = self.r.recognize_google(audio)
	    self.GetAudio = True
            print("listen: " + self.strAudio)
            #print("listenSpanish: ", strSpanish)
            #self.SpeechText(self.Response)
        except:
            print("callback listen exception")
            self.strAudio = ""
            return

    def Start(self):
        print("Say something!")
        self.r.operation_timeout = 10
        with self.m as source:
            audio = self.r.listen(source = source, timeout = 2)

        # recognize speech using Google Speech Recognition

        Response = self.Decode(audio)
        self.SpeechText(Response)
        
    def StartBack(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

        print("start background listening")

        return self.r.listen_in_background(self.m, self.callback)

    def StartBackListen(self):
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

        print("start background only listening")

        return self.r.listen_in_background(self.m, self.callback_listen)

 
#qbo = QBOtalk()
#qbo.Start()

#while True:
#    print("start background listening")

#    listen_thd = qbo.StartBack()

#    for _ in range(100):
#        if qbo.GetResponse:
#            listen_thd(wait_for_stop = True)
#            qbo.SpeechText(qbo.Response)
#            qbo.GetResponse = False
#            break
#        time.sleep(0.1)
#    print("End listening")

