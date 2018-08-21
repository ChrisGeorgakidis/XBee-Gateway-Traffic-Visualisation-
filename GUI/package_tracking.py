from tkinter import *
from tkinter import messagebox
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress
from serial.tools import list_ports
from digi.xbee.util import utils
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


# *** Application Class ***
# The class of the main app
class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        global node_list, node_frame
        # Divide the root window vertically
        m1 = PanedWindow(width=500, height=500, orient=VERTICAL)
        m1.pack(fill=BOTH, expand=1)

        # Label for the gateway id and port
        gateway_text = "Gateway: " + GATEWAY + " (Port: " + PORT + ")"
        gateway_label = Label(m1, text=gateway_text, fg='black', font=("Helvetica", 16, "underline"))
        m1.add(gateway_label)

        f1 = Frame(m1)
        m1.add(f1)

        txt = "Network Sleeping Time: "
        sleep_label = Label(f1, text=txt, fg='black', font=("Helvetica", 16, "underline"))
        sleep_label.pack(side=LEFT, fill=Y)

        e1 = Entry(f1, bd=2)
        e1.pack(side=RIGHT, fill=BOTH)

        f2 = Frame(m1)
        m1.add(f2)

        txt = "Network Awake Time: "
        awake_label = Label(f2, text=txt, fg='black', font=("Helvetica", 16, "underline"))
        awake_label.pack(side=LEFT)

        e2 = Entry(f2, bd=2)
        e2.pack(side=RIGHT, fill=BOTH)

        # Now divide the remainder of m1 horizontally
        m2 = PanedWindow(m1, orient=HORIZONTAL)
        m1.add(m2)

        m3 = PanedWindow(m2, orient=VERTICAL)
        m2.add(m3)

        m4 = PanedWindow(m2, orient=VERTICAL)
        m2.add(m4)

        # Create the scrollable list of nodes
        node_list_label = Label(m3, text="Node List", fg='black', font=("Helvetica", 14, "bold"))
        m3.add(node_list_label)

        list_frame = Frame(m3)
        m3.add(list_frame)

        node_list = Listbox(list_frame, selectbackground='gold', selectmode=SINGLE)
        node_list.pack(side=LEFT, fill=Y)

        node_list_scrollbar = Scrollbar(list_frame, orient=VERTICAL)
        node_list_scrollbar.config(command=node_list.yview)
        node_list_scrollbar.pack(side=RIGHT, fill=Y)

        node_list.config(yscrollcommand=node_list_scrollbar.set)

        for x in transmitters:
            node_list.insert(END, x)

        # Create the scrollable pool of packets
        node_list_label = Label(m4, text="Packet Pool", fg='black', font=("Helvetica", 14, "bold"))
        m4.add(node_list_label)

        pool_frame = Frame(m4)
        m4.add(pool_frame)

        # Add a canvas to the frame
        canvas = Canvas(pool_frame, bg='light yellow')
        canvas.grid(column=0, row=0, sticky=NE + SW)

        # Allow the canvas (in row/column 0,0) to grow to fill the
        # entire frame
        pool_frame.grid_rowconfigure(0, weight=1)
        pool_frame.grid_columnconfigure(0, weight=1)

        # Add a scrollbar that will scroll the canvas vertically
        vscrollbar = Scrollbar(pool_frame)
        vscrollbar.grid(column=1, row=0, sticky=N+S)

        # Link the scrollbar to the canvas
        canvas.config(yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=canvas.yview)

        # This frame must be defined as a child of the canvas,
        # even though we later add it as a window to the canvas
        node_frame = Frame(canvas, bg='light yellow')

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
        label = Label(node_frame, text=txt, relief=RAISED, height=5, bg='gold')
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

    index = int(list(selected_text)[0])
    devices[index].config(bg='salmon2')
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
        root = Tk()
        root.geometry("800x800")
        root.resizable(1, 1)
        root.title("Packet Traffic Visualisation")
        root.protocol("WM_DELETE_WINDOW", ask_quit)

        # Asks the user to enter the baudrate
        BAUD_RATE = input("Enter the baudrate of the device: ")

        gateway = XBeeDevice(PORT, BAUD_RATE)
        if gateway.is_open():
            gateway.close()
        gateway.open()
        # Get the 64-bit address of the device.
        GATEWAY = "0x" + str(gateway.get_64bit_addr())

        # Set the ID & NI Parameter
        gateway.set_parameter(PARAM_NODE_ID, bytearray(PARAM_VALUE_NODE_ID, 'utf8'))
        gateway.set_parameter(PARAM_PAN_ID, PARAM_VALUE_PAN_ID)
        gateway.set_parameter(PARAM_SM, PARAM_VALUE_SM)
        gateway.set_parameter(PARAM_SO, PARAM_VALUE_SO)
        gateway.set_parameter(PARAM_SP, PARAM_VALUE_SP)
        gateway.set_parameter(PARAM_ST, PARAM_VALUE_ST)

        # Get parameters.
        print("Node ID:\t%s" % gateway.get_parameter(PARAM_NODE_ID).decode())
        print("Power management mode(SM):\t%s" % utils.bytes_to_int(gateway.get_parameter(PARAM_SM)))
        print("Sleep Options(SO):\t%s" % utils.bytes_to_int(gateway.get_parameter(PARAM_SO)))
        print("Sleep Time(SP):\t%s" % utils.bytes_to_int(gateway.get_parameter(PARAM_SP)))
        print("Wake Time(ST):\t%s" % utils.bytes_to_int(gateway.get_parameter(PARAM_ST)))
        print("PAN ID:\t%s" % utils.hex_to_string(gateway.get_parameter(PARAM_PAN_ID)))

        # Assign the data received callback to the gateway
        gateway.add_data_received_callback(packages_received_callback)

        app = Application(master=root)
        app.mainloop()
    else:
        sys.exit("No serial port seems to have an XBee connected.")

