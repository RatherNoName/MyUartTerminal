
import wx
import serial
import sys
import threading
import glob
import time

class guiforUARTCOM(wx.Frame):

    def __init__(self,parent,id,port_list):
        wx.Frame.__init__(self,parent,id,'Uart Terminal',size = (300,300))
        self.panel = wx.Panel(self)
        self.buttonSend = wx.Button(self.panel,label = "Send",pos=(235,265),size = (60,30))
        self.textbox = wx.TextCtrl(self.panel,pos=(5,265),size = (225,30))
        self.textshow = wx.TextCtrl (self.panel, pos = (5,40), size = (290,220),style = wx.TE_MULTILINE)
        self.portlist = wx.ComboBox (self.panel, pos = (5,5),size = (100,30), choices = port_list)
        self.buttonConnect = wx.Button(self.panel,pos = (205,5),size = (90,30),label = "Connect")
        self.comboBaudRate = wx.ComboBox (self.panel,pos= (110,5),size = (90,30), choices = ["9600","19200"])
        self.buttonDisconnect = wx.Button(self.panel,pos = (205,5),size = (90,30),label = "Disconnect")
        self.buttonDisconnect.Hide()


#Tato classsa je vytvorena cez multithreading aby mohol bezat jeden proces na pozadi a zaroven
#aby fungovali ostatne procesy normalne.

class Recieve_message(threading.Thread):
    def __init__(self,port,text_list):
        threading.Thread.__init__(self)
        self.port = port
        self.text_list = text_list
        self.shouldirun = True

 # Tato funkcia sa spusta automaticky a je v nej vyobrazene co sa bude diat pocas threadingu
    def run(self):
        while self.shouldirun:
            obsah = self.port.readline()
            self.text_list.SetForegroundColour((255, 0, 0))
            self.text_list.WriteText(obsah)
            time.sleep(0.2)

class UARTcommunication:

    def init_port(self,selected_port,selected_baudrate):
        port = serial.Serial(
            port = selected_port, #tak sme zadefinujeme zariadenie s ktorym chceme komunikovat
            baudrate =  selected_baudrate   ,
            bytesize =  serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            timeout = 0,
            xonxoff = bool(0),
            rtscts = bool(0),
            dsrdtr = bool(0),
            write_timeout = 0
        )
        return port

    def port_status(self,port):  # Uz nieje az taka zbytocna
        status = port.isOpen()
        print "Port je %d" %status
        return

    def write_to_port(self,port,text): #zapis do portu
        port.write(text)
        return
 #Viacmenej zbytocna
    def read_from_port(self,port):#citanie z portu
        obsah = port.readline()
        print "precital som %s " %obsah
        return obsah
#Funkcia na zistovanie pouzitych portov. Moc neviem ako funguje nakolko som ju skopirova
    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(str(port))
            except (OSError, serial.SerialException):
                pass
        return result

class view:

    def __init__(self):  #zakladna inicializacia
        self.portsofuart = UARTcommunication()
        connected_ports  = self.portsofuart.serial_ports()
        self.uart_in = guiforUARTCOM(parent=None,id=-1,port_list= connected_ports)
        self.uart_in.buttonConnect.Bind(wx.EVT_BUTTON, self.connect_device)
        self.uart_in.buttonSend.Bind(wx.EVT_BUTTON, self.send_message) #Event pre button Send
        self.uart_in.buttonDisconnect.Bind(wx.EVT_BUTTON, self.disconnect_port) # Odpojenie portu
        self.port = None

    def runapp(self):  #tymto spustame appku
        self.uart_in.Show()
        return

#Funkcia na ovladanie buttonu connect :) Pol dna mi trvalo pokym som na to dosiel !
    def connect_device(self, event):
        port = self.uart_in.portlist.GetValue()
        baudrate = self.uart_in.comboBaudRate.GetValue()
        if (port  != "") and (baudrate != "") :
            self.port = self.portsofuart.init_port(port,baudrate) #Inicializovanie portu
            print self.portsofuart.port_status(self.port) #Vypisem port
            self.uart_in.buttonConnect.Hide() #Skrytie a zobrazenie buttonow connect a disconnect
            self.uart_in.buttonDisconnect.Show()
            self.reading = Recieve_message(self.port,self.uart_in.textshow) #Inicializujeme triedu na citanie z portu
            self.reading.start() #jej nasledne spustenie
        else: #Chybova hlaska v pripade chybajucich input paramterov
            error_message = wx.MessageDialog (None, "Zadajte input parametry","Connection Failed",wx.OK)
            error_message.ShowModal()
            error_message.Destroy()
        return


    def send_message(self,event):
        if (self.port) and (self.port.isOpen() == 1):
            text = self.uart_in.textbox.GetValue()  # nacita hodnotu z textoveho pola
            self.uart_in.textshow.SetForegroundColour((0, 0, 255)) #Nastavenie farby
            self.uart_in.textshow.WriteText(text) #Vycitanie textu z riadku
            text = text.encode()
            self.portsofuart.write_to_port(self.port,text) #Jeho nasledne odoslanie
        else: #ak nieje zapojeny port
            error_message = wx.MessageDialog(None, "Port nie je zapojeny", "Message send failed", wx.OK)
            error_message.ShowModal()
            error_message.Destroy()
        return

# Funkcia tlacidka dissconect
    def disconnect_port(self,event):
        self.reading.shouldirun = False #Priznak pre threading aby sa zastavil
        self.port.close() #Zavrenie portu
        self.uart_in.buttonConnect.Show()
        self.uart_in.buttonDisconnect.Hide()



if __name__ == '__main__':
    app = wx.PySimpleApp()
    #uart.view()
    uart = view()
    uart.runapp()
    app.MainLoop()
