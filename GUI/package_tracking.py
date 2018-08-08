from tkinter import *
import functools
import math

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
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

        node_list = Listbox(list_frame)
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
        canvas = Canvas(pool_frame)
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
        node_frame = Frame(canvas)

        # IMPORTANT:
        node_frame.update_idletasks()  # REQUIRED: For f.bbox() below to work!

        # Add a large grid of sample label widgets to fill the space
        dim = int(math.ceil(math.sqrt(nOfTransmitters)))
        for x in range(dim):
            for y in range(dim):
                if (x * dim + y) < nOfTransmitters:
                    Label(node_frame, text=transmitters[x * dim + y], relief=RAISED) \
                        .grid(row=x, column=y, padx=10, pady=10)

        pool_frame.bind("<Configure>", functools.partial(d, canvas=canvas, node_frame=node_frame))

        # # creates a grid 50 x 50 in the pool frame
        # rows = 0
        # while rows < 10:
        #     pool_frame.rowconfigure(rows, weight=1)
        #     pool_frame.columnconfigure(rows, weight=1)
        #     rows += 1
        #
        # for r in range(10):
        #     for c in range(10):
        #         if (r%2 is 0) and (c%2 is 0):
        #             button = Button(pool_frame, text='XBee Device')
        #             button.grid(row=r, column=c)


def d(event, canvas, node_frame):
    print(event.width, event.height)

    # Add the frame to the canvas
    if event.width > 348:
        x0 = event.width/2
    else:
        x0 = 0
    print(x0)
    canvas.create_window((event.width/2, event.height/2), window=node_frame)

    # Tell the canvas how big of a region it should scroll
    canvas.config(scrollregion=node_frame.bbox("all"))

if __name__ == '__main__':
    PORT = 'COM4'
    GATEWAY = '1522'
    BAUD_RATE = 115200
    REMOTE_ADDRESS = ''
    nOfTransmitters = 34
    transmitters = ['device1', 'device2', 'device3', 'device4', 'device5',
                    'device6', 'device7', 'device8', 'device9', 'device10',
                    'device11', 'device12', 'device13', 'device14',
                    'device15', 'device16', 'device17', 'device18',
                    'device19', 'device20', 'device21', 'device22',
                    'device23', 'device24', 'device25', 'device26',
                    'device27', 'device28', 'device29', 'device30',
                    'device31', 'device32', 'device33', 'device34']

    root = Tk()
    root.geometry("600x600")
    root.resizable(1, 1) # don't allow to resize it horizontically
    root.title("Packet Traffic Visualisation")
    app = Application(master=root)
    app.mainloop()