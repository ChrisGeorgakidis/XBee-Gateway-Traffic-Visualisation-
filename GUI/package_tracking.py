from tkinter import *
from tkinter import messagebox

from digi.xbee.exception import TimeoutException
from digi.xbee.serial import XBeeSerialPort
from digi.xbee.devices import XBeeDevice
from serial.tools import list_ports
from digi.xbee.util import utils
import serial
import time
import sys
import functools
import math

# Gateway parameters
PARAM_NODE_ID = "NI"
PARAM_PAN_ID = "ID"
PARAM_SM = "SM"
PARAM_SO = "SO"
PARAM_SP = "SP"
PARAM_ST = "ST"
PARAM_OS = "OS"
PARAM_OW = "OW"
PARAM_VALUE_NODE_ID = "GATEWAY"

# Global Variables
PARAM_VALUE_PAN_ID = utils.hex_string_to_bytes("10")
PARAM_VALUE_SM = utils.int_to_bytes(7, 1)
PARAM_VALUE_SO = utils.int_to_bytes(1, 1)
PARAM_VALUE_SP = utils.int_to_bytes(2000, 2)
PARAM_VALUE_ST = utils.int_to_bytes(10000, 2)
prevSelectedIndex = -1
devices = []
counter = -1
grid_width = 0
grid_height = 0
node_list = None
node_frame = None
sleep_label = None
sleep_entry = None
awake_label = None
awake_entry = None
sleep_wake_label = None
prev_status = 0
status_timer = 0
sleep_time = 0
awake_time = 0
OS_time = 0
OW_time = 0
previously_changed = 0 # 0 = no change, 1 = changed sleep time, 2 = changed wake time, 3 = changed both

baudrates = {'1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600'}

# My colors
# BACKGROUND_COLOR = '#0a463c'
# NODELIST_COLOR = '#fceec7'
# PACKETPOOL_COLOR = '#b6d2dd'
# ASLEEP_DEVICE_COLOR = '#e45149'
# AWAKE_DEVICE_COLOR = '#259086'
# NEW_DEVICE_COLOR = '#e9cb31'

BACKGROUND_COLOR = '#dd9166'
NODELIST_COLOR = '#e2ddc7'
PACKETPOOL_COLOR = '#958f80'
ASLEEP_DEVICE_COLOR = '#54595a'
AWAKE_DEVICE_COLOR = '#cd9d8d'
NEW_DEVICE_COLOR = '#f2be54'
SCROLLBARS_COLOR = '#ded7d1'


def bitconv(n):
    return [int(digit) for digit in bin(n)[2:]]  # [2:] to chop off the "0b" part


# *** Application Class ***
# The class of the main app
class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.update_time()
        self.master.mainloop()

    # *** update_time ***
    def update_time(self):
        global status_timer, prev_status, devices, OS_time, OW_time, previously_changed

        status_timer = status_timer + 1

        try:
            ST = utils.bytes_to_int(gateway.get_parameter("OS")) * 10 / 1000
        except TimeoutException:
            ST = OS_time

        try:
            AT = utils.bytes_to_int(gateway.get_parameter("OW")) / 1000
        except TimeoutException:
            AT = OW_time

        try:
            ss = utils.bytes_to_int(gateway.get_parameter("SS"))
            sleep_status = bitconv(ss)
            print(sleep_status)

            status = sleep_status[len(sleep_status) - 1]
            pending_changes = sleep_status[len(sleep_status) - 5]
            print(status)

            # check if network is asleep or awake
            if status == 1:   # asleep
                if status != prev_status:
                    status_timer = 0
                    if len(devices) > 0:
                        for rect in devices:
                            rect.config(bg=AWAKE_DEVICE_COLOR)
                sleep_wake_time_txt = "Network Sleep in " + str(AT - status_timer) + " sec"
            else:
                if status != prev_status:
                    status_timer = 0
                    if len(devices) > 0:
                        for rect in devices:
                            rect.config(bg=ASLEEP_DEVICE_COLOR)
                sleep_wake_time_txt = "Network Awake in " + str(ST - status_timer) + " sec"

            sleep_wake_label.configure(text=sleep_wake_time_txt)
            prev_status = status

            txt = "Network Sleeping Time: " + str(ST) + " sec"
            if previously_changed == 1 or previously_changed == 3:
                txt = txt + " (*)"
            sleep_label.configure(text=txt)
            txt = "Network Awaking Time: " + str(AT) + " sec"
            if previously_changed == 2 or previously_changed == 3:
                txt = txt + " (*)"
            awake_label.configure(text=txt)

            if not pending_changes:
                previously_changed = 0

            OS_time = ST
            OW_time = AT
        except TimeoutException:
            print("Couldn't retrieve Sleep Status right now.")

        self.master.after(1000, self.update_time)

    def create_widgets(self):
        global node_list, node_frame, sleep_label, sleep_entry, awake_label, awake_entry, sleep_wake_label

        # Divide the root window vertically
        m1 = PanedWindow(width=500, height=500, orient=VERTICAL, bg=BACKGROUND_COLOR)
        m1.pack(fill=BOTH, expand=1)

        f0 = Frame(m1, bd=20, bg=BACKGROUND_COLOR)
        m1.add(f0)

        # Label for the gateway id and port
        gateway_text = "Gateway: " + GATEWAY + " (Port: " + PORT + ")"
        gateway_label = Label(f0, text=gateway_text, fg='black', font=("Verdana", 16, "underline"), bg=BACKGROUND_COLOR)
        gateway_label.pack(side=LEFT, fill=BOTH)

        sleep_wake_label = Label(f0, fg='black', font=("Verdana", 16, "bold"), bg=BACKGROUND_COLOR)
        sleep_wake_label.pack(side=RIGHT, fill=BOTH)

        f1 = Frame(m1, bd=10, bg=BACKGROUND_COLOR)
        m1.add(f1)

        sleep_label = Label(f1, fg='black', font=("Verdana", 16, "underline"), bg=BACKGROUND_COLOR)
        sleep_label.pack(side=LEFT, fill=Y)

        f11 = Frame(f1, bg=BACKGROUND_COLOR)
        f11.pack(side=RIGHT, fill=BOTH)

        sleep_entry = Entry(f11, bd=2, bg=SCROLLBARS_COLOR)
        sleep_entry.pack(side=LEFT, fill=BOTH)

        update_sleep_period_button = Button(f11, text="Update Sleep Time", font="Verdana", command=update_sleep_time, bg=SCROLLBARS_COLOR)
        update_sleep_period_button.pack(side=RIGHT, fill=BOTH)

        f2 = Frame(m1, bd=10, bg=BACKGROUND_COLOR)
        m1.add(f2)

        awake_label = Label(f2, fg='black', font=("Verdana", 16, "underline"), bg=BACKGROUND_COLOR)
        awake_label.pack(side=LEFT)

        f22 = Frame(f2, bg=BACKGROUND_COLOR)
        f22.pack(side=RIGHT, fill=BOTH)

        awake_entry = Entry(f22, bd=2, bg=SCROLLBARS_COLOR)
        awake_entry.pack(side=LEFT, fill=BOTH)

        update_awake_time_button = Button(f22, text="Update Wake Time", font="Verdana", command=update_wake_time, bg=SCROLLBARS_COLOR)
        update_awake_time_button.pack(side=RIGHT, fill=BOTH)

        # Now divide the remainder of m1 horizontally
        m2 = PanedWindow(m1, orient=HORIZONTAL, bg=BACKGROUND_COLOR)
        m1.add(m2)

        m3 = PanedWindow(m2, orient=VERTICAL, bg=BACKGROUND_COLOR)
        m2.add(m3)

        m4 = PanedWindow(m2, orient=VERTICAL, bg=BACKGROUND_COLOR)
        m2.add(m4)

        # Create the scrollable list of nodes
        node_list_label = Label(m3, text="Node List", fg='black', font=("Verdana", 14, "bold"), width=20, bg=BACKGROUND_COLOR)
        m3.add(node_list_label)

        node_list = Listbox(m3, selectbackground=NEW_DEVICE_COLOR, selectmode=SINGLE, font="Verdana", bg=NODELIST_COLOR)
        m3.add(node_list)

        node_list_scrollbar = Scrollbar(node_list, orient=VERTICAL, command=node_list.yview, bg=SCROLLBARS_COLOR)
        # node_list_scrollbar.config(command=node_list.yview)
        node_list_scrollbar.pack(side=RIGHT, fill=Y)

        node_list.config(yscrollcommand=node_list_scrollbar.set)

        for x in transmitters:
            node_list.insert(END, x)

        # Create the scrollable pool of packets
        node_list_label = Label(m4, text="Packet Pool", fg='black', font=("Verdana", 14, "bold"), bg=BACKGROUND_COLOR)
        m4.add(node_list_label)

        pool_frame = Frame(m4, bg=PACKETPOOL_COLOR)
        m4.add(pool_frame)

        # Add a canvas to the frame
        canvas = Canvas(pool_frame, bg=PACKETPOOL_COLOR)
        canvas.grid(column=0, row=0, sticky=NE + SW)

        # Allow the canvas (in row/column 0,0) to grow to fill the
        # entire frame
        pool_frame.grid_rowconfigure(0, weight=1)
        pool_frame.grid_columnconfigure(0, weight=1)

        # Add a scrollbar that will scroll the canvas vertically
        vscrollbar = Scrollbar(pool_frame, bg=SCROLLBARS_COLOR)
        vscrollbar.grid(column=1, row=0, sticky=N+S)

        # Link the scrollbar to the canvas
        canvas.config(yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=canvas.yview)

        # This frame must be defined as a child of the canvas,
        # even though we later add it as a window to the canvas
        node_frame = Frame(canvas, bg=PACKETPOOL_COLOR)

        node_frame.update_idletasks()  # REQUIRED: For f.bbox() below to work!

        # Initialise the grid with the existing transmitters'
        # data, if there are any.
        dim = int(math.ceil(math.sqrt(nOfTransmitters)))

        for x in range(dim):
            for y in range(dim):
                if (x * dim + y) < nOfTransmitters:
                    txt = transmitters[x * dim + y]
                    devices.append(Label(node_frame, text=txt, relief=RAISED, height=5, bg='gold'))

        pool_frame.bind("<Configure>", functools.partial(resize_grid, canvas=canvas, node_frame=node_frame))

        node_list.bind("<<ListboxSelect>>", functools.partial(on_select))
        for i in range(nOfTransmitters):
            devices[i].bind("<Button-1>", functools.partial(show_data_history, index=i))


def update_sleep_time():
    global sleep_label, sleep_entry, sleep_time, status_timer, previously_changed

    if len(sleep_entry.get()) > 0:
        new_sleep_time = float(sleep_entry.get())
        sleep_entry.delete(0, END)

        print(new_sleep_time)

        ms_time = int((new_sleep_time / 10) * 1000)

        gateway.set_parameter("SP", utils.hex_string_to_bytes(hex(ms_time)))

        if previously_changed == 0:
            previously_changed = 1
        elif previously_changed == 2:
            previously_changed = 3

        print(utils.bytes_to_int(gateway.get_parameter("OS")))

        sleep_time = new_sleep_time


def update_wake_time():
    global awake_label, awake_entry, awake_time, previously_changed

    if len(awake_entry.get()) > 0:
        new_awake_time = float(awake_entry.get())
        awake_entry.delete(0, END)

        ms_time = int(new_awake_time * 1000)

        gateway.set_parameter("ST", utils.hex_string_to_bytes(hex(ms_time)))
        if previously_changed == 0:
            previously_changed = 2
        elif previously_changed == 1:
            previously_changed = 3
        awake_time = new_awake_time


# *** insert_devices ***
# This function inserts the information of each transmitter
# that have sent data and also updates the corresponding data
# structures and the GUI.
def insert_devices(remote_device, data):
    global nOfTransmitters, devices, counter, node_list
    double = -1

    # Check if the transmitter is already in the node list
    if nOfTransmitters is not 0:
        for i in range(nOfTransmitters):
            if remote_device == transmitters[i]:
                double = i

    # Store device's name if it is not already in the node list.
    # If it is already in the list, then just append the new data
    # that it sent.
    if double is -1:

        nOfTransmitters = nOfTransmitters + 1
        transmitters.append(remote_device)

        data_log.append(data)
        transmitters_data[remote_device] = [data]

        node_list.insert(END, remote_device)
        txt = remote_device + "\n" + data
        label = Label(node_frame, text=txt, relief=RAISED, height=5, bg=NEW_DEVICE_COLOR)
        devices.append(label)
        devices[nOfTransmitters-1].grid(padx=10, pady=10)
        devices[nOfTransmitters-1].bind("<Button-1>", functools.partial(show_data_history, index=nOfTransmitters-1))
    else:
        txt = remote_device + "\n" + data
        devices[double].configure(text=txt)
        transmitters_data[remote_device].append(data)
        devices[double].bind("<Button-1>", functools.partial(show_data_history, index=double))


# *** quit_transmitter_window ***
# This function does the appropriate actions in order to close the
# transmitter info window
def quit_transmitter_window():
    # Destroy the transmitter info window
    global transmitter_info_window

    transmitter_info_window.destroy()


# *** show_data_history ***
# When the user clicks on a transmitter's rectangle, then
# a message box is created and shows the log of the data that
# the corresponding transmitter has sent.
def show_data_history(event, index):
    transmitters_history = transmitters_data.get(transmitters[index])
    data = "\n".join(str(x) for x in transmitters_history)
    messagebox.showinfo(transmitters[index], "Data Log:\n" + data)


# *** resize_grid ***
# This is the handler which resizes the grid when the user
# resizes the app's window.
def resize_grid(event, canvas, node_frame):
    global devices, grid_width, grid_height

    # Add the frame to the canvas
    if event.width > 348:
        x0 = event.width/2
    else:
        x0 = 0

    grid_width = event.width
    grid_height = event.height

    dim = int(math.ceil(math.sqrt(nOfTransmitters)))

    for x in range(dim):
        for y in range(dim):
            if (x * dim + y) < nOfTransmitters:
                devices[x*dim+y].grid(row=x, column=y, padx=10, pady=10)

    canvas.create_window((event.width/2, event.height/2), window=node_frame)

    # Tell the canvas how big of a region it should scroll
    canvas.config(scrollregion=node_frame.bbox("all"))


# *** on_select ***
# This is the handler that is triggered when the user is
# selecting an element of the listbox. This listbox contains
# the unique 64-bit addresses of the transmitters that have
# already sent data. When the users selects one of these
# addresses then the corresponding rectangle of the grid
# is highlighted.
def on_select(event):
    global prevSelectedIndex, devices
    w = event.widget
    selected_text = w.curselection()

    if prevSelectedIndex is not -1:
        devices[prevSelectedIndex].config(bg='gold')

    if selected_text != ():
        index = int(list(selected_text)[0])
        devices[index].config(bg=NEW_DEVICE_COLOR)
        prevSelectedIndex = index


# *** packages_received_callback ***
# This is the handler that is triggered each time the
# gateway is receiving a new data from a transmitter.
# When the gateway is receiving new data from a transmitter,
# it gets the information of the message that was sent and
# inserts them into the current data structures.
def packages_received_callback(xbee_message):
    remote_device = "0x" + str(xbee_message.remote_device.get_64bit_addr())
    data = xbee_message.data.decode("utf8")
    timestamp = time.ctime(xbee_message.timestamp)
    print("Received data from " + str(remote_device) + ": " + data + "  [" + str(timestamp) + "]")
    message = data + " [" + str(timestamp) + "]"
    insert_devices(remote_device=remote_device, data=message)


# *** ask_quit ***
# Verifies that the user is sure he wants to quit the app.
# This is needed in order to close the connection with the
# gateway xbee device.
def ask_quit():
    # Ask user if he is sure he wants to quit
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        if gateway is not None and gateway.is_open():
            gateway.close()
        root.destroy()


if __name__ == '__main__':
    PORT = ''
    GATEWAY = ''

    BAUD_RATE = 115200
    nOfTransmitters = 0

    transmitters = []
    data_log =[]
    transmitters_data = {}

    # Look for COM port that might have an XBee connected
    portfound = FALSE
    ports = list(list_ports.comports())

    for p in ports:
        print(p)

    if len(ports) > 1:
        print("Found more than one XBee devices. Which one do you want to use as your gateway?")
        while portfound == FALSE:
            user_port = input("Enter the port code (COMx, where x the corresponding number of the port): ")
            if user_port == "quit" or user_port == "exit":
                sys.exit("Exit the Program")
            for p in ports:
                if user_port in p:
                    if not portfound:
                        portfound = TRUE
                        PORT = p[0]
                        print("Using " + p[0] + " as XBee COM port.")

            if portfound == FALSE:
                print("No serial port seems to have an XBee connected.")
    elif len(ports) == 1:
        for p in ports:
            print("Found possible XBee on " + p[0])
            if not portfound:
                portfound = TRUE
                PORT = p[0]
                print("Using " + p[0] + " as XBee COM port.")

    # If a port found then initialise and run the app
    if portfound:
        # Asks the user to enter the baudrate
        while TRUE:
            print("Supported baudrates: " + str(baudrates))
            if input("Enter the baudrate of the device: ") not in baudrates:
                print("Not supported baudrate. Please try again")
            else:
                break
        root = Tk()
        root.geometry("1000x1000")
        root.resizable(1, 1)
        root.title("Packet Traffic Visualisation")
        root.protocol("WM_DELETE_WINDOW", ask_quit)
        root.config(bg=BACKGROUND_COLOR)
        root.iconbitmap(r'C:\Users\xbee.ico')

        gateway = XBeeDevice(PORT, BAUD_RATE)

        if gateway.is_open():
            gateway.close()
        gateway.open()

        ser = gateway.serial_port

        # Get the 64-bit address of the device.
        GATEWAY = "0x" + str(gateway.get_64bit_addr())

        # Set the ID & NI Parameter
        gateway.set_parameter("NI", bytearray(PARAM_VALUE_NODE_ID, 'utf8'))
        gateway.set_parameter("ID", PARAM_VALUE_PAN_ID)
        gateway.set_parameter("SM", utils.hex_string_to_bytes(hex(7)))
        gateway.set_parameter("SO", utils.hex_string_to_bytes(hex(1)))
        gateway.set_parameter("SP", utils.hex_string_to_bytes(hex(2000)))
        gateway.set_parameter("ST", utils.hex_string_to_bytes(hex(10000)))

        sleep_time = utils.bytes_to_int(gateway.get_parameter("OS")) * 10 / 1000
        awake_time = utils.bytes_to_int(gateway.get_parameter("OW")) / 1000

        # Get parameters.
        print("---------GATEWAY INFO---------")
        print("Node ID (NI):\t%s" % gateway.get_parameter("NI").decode())
        print("PAN ID (ID):\t%s" % utils.hex_to_string(gateway.get_parameter("ID")))
        print("---------SLEEP PARAMETERS---------")
        print("Sleep Mode(SM):\t%s" % utils.bytes_to_int(gateway.get_parameter("SM")))
        print("Sleep Options(SO):\t%s" % utils.bytes_to_int(gateway.get_parameter("SO")))
        print("Sleep Time(SP):\t%s" % utils.bytes_to_int(gateway.get_parameter("SP")))
        print("Wake Time(ST):\t%s" % utils.bytes_to_int(gateway.get_parameter("ST")))
        print("---------CURRENT SLEEP PARAMETERS---------")
        print("Operating Sleep Time(OS):\t%s" % utils.bytes_to_int(gateway.get_parameter("OS")))
        print("Operating Wake Time(OW):\t%s" % utils.bytes_to_int(gateway.get_parameter("OW")))

        # Assign the data received callback to the gateway
        gateway.add_data_received_callback(packages_received_callback)

        app = Application(master=root)
    else:
        sys.exit("No serial port seems to have an XBee connected.")

