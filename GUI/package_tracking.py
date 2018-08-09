from tkinter import *
from tkinter import messagebox
from threading import Thread
import time
import functools, math


# Global Variables
prevSelectedIndex = -1
devices = []
counter = -1
grid_width = 0
grid_height = 0
node_list = None
node_frame = None


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
        gateway_text = "Gateway: " + GATEWAY + " (" + PORT + ")"
        gateway_label = Label(m1, text=gateway_text, fg='black', font=("Helvetica", 16, "underline"))
        m1.add(gateway_label)

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

        # IMPORTANT:
        node_frame.update_idletasks()  # REQUIRED: For f.bbox() below to work!

        # Add a large grid of sample label widgets to fill the space
        dim = int(math.ceil(math.sqrt(nOfTransmitters)))
        # devices = []
        for x in range(dim):
            for y in range(dim):
                if (x * dim + y) < nOfTransmitters:
                    txt = transmitters[x * dim + y]
                    devices.append(Label(node_frame, text=txt, relief=RAISED, height=5, bg='gold'))

        pool_frame.bind("<Configure>", functools.partial(resize_grid, canvas=canvas, node_frame=node_frame))

        node_list.bind("<<ListboxSelect>>", functools.partial(on_select))
        for i in range(nOfTransmitters):
            devices[i].bind("<Button-1>", functools.partial(show_data_history, index=i))


def insert_devices(event, canvas):
    global nOfTransmitters, devices, counter, node_list
    double = -1

    counter = counter + 1
    print(nOfTransmitters)
    print(serial[counter])

    # Check if the transmitter is already in the node list
    if nOfTransmitters is not 0:
        for i in range(nOfTransmitters):
            # print(transmitters[i])
            if serial[counter] == transmitters[i]:
                print("Already in node list")
                double = i

    # Store device's name if it is not already in the node list

    device_name = serial[counter]
    data = data_serial[counter]
    if double is -1:
        nOfTransmitters = nOfTransmitters + 1
        transmitters.append(device_name)
        data_log.append(data)
        transmitters_data[device_name] = [data]

        node_list.insert(END, device_name)
        txt = device_name + "\n" + data
        label = Label(node_frame, text=txt, relief=RAISED, height=5, bg='gold')
        devices.append(label)
        devices[nOfTransmitters-1].grid(padx=10, pady=10)
        devices[nOfTransmitters-1].bind("<Button-1>", functools.partial(show_data_history, index=nOfTransmitters-1))
    else:
        txt = device_name + "\n" + data
        devices[double].configure(text=txt)
        transmitters_data[device_name].append(data)
        devices[double].bind("<Button-1>", functools.partial(show_data_history, index=double))

    print(transmitters)
    print(transmitters_data)
    print(devices)


def show_data_history(event, index):
    transmitters_history = transmitters_data.get(transmitters[index])
    data = "\n".join(str(x) for x in transmitters_history)
    messagebox.showinfo(transmitters[index], "Data Log:\n" + data)


def resize_grid(event, canvas, node_frame):
    global devices, grid_width, grid_height
    print(event.width, event.height)

    # Add the frame to the canvas
    if event.width > 348:
        x0 = event.width/2
    else:
        x0 = 0
    print(x0)

    grid_width = event.width
    grid_height = event.height

    dim = int(math.ceil(math.sqrt(nOfTransmitters)))

    for x in range(dim):
        for y in range(dim):
            if (x * dim + y) < nOfTransmitters:
                devices[x*dim+y].grid(row=x, column=y, padx=10, pady=10)

    canvas.bind("<Button-3>", functools.partial(insert_devices, canvas=canvas))
    canvas.create_window((event.width/2, event.height/2), window=node_frame)

    # Tell the canvas how big of a region it should scroll
    canvas.config(scrollregion=node_frame.bbox("all"))



def on_select(event):
    global prevSelectedIndex, devices
    w = event.widget
    selected_text = w.curselection()

    if prevSelectedIndex is not -1:
        devices[prevSelectedIndex].config(bg='gold')

    index = int(list(selected_text)[0])
    devices[index].config(bg='salmon2')
    prevSelectedIndex = index


if __name__ == '__main__':
    PORT = 'COM4'
    GATEWAY = '1522'
    BAUD_RATE = 115200
    REMOTE_ADDRESS = ''
    nOfTransmitters = 0

    serial = ['device 1', 'device 2', 'device 3', 'device 1', 'device 2', 'device 3', 'device 4', 'device 5']
    data_serial = ['Humidity: 16%, Temperature: 32oC', 'Humidity: 26%, Temperature: 32oC',
                   'Humidity: 36%, Temperature: 32oC', 'Humidity: 20%, Temperature: 32oC',
                   'Humidity: 30%, Temperature: 32oC', 'Humidity: 40%, Temperature: 32oC',
                   'Humidity: 46%, Temperature: 32oC', 'Humidity: 56%, Temperature: 32oC']

    transmitters = []
    data_log =[]
    transmitters_data = {}

    root = Tk()
    root.geometry("800x800")
    root.resizable(1, 1)
    root.title("Packet Traffic Visualisation")
    app = Application(master=root)

    app.mainloop()

