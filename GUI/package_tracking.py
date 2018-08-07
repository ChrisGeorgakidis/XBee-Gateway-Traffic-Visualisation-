from tkinter import *


class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        m1 = PanedWindow(width=500, height=500, orient=VERTICAL)
        m1.pack(fill=BOTH, expand=1)

        gateway_label = Label(m1, text="Gateway: " + GATEWAY + " (" + PORT + ")")
        m1.add(gateway_label)

        m2 = PanedWindow(m1, orient=HORIZONTAL)
        m1.add(m2)

        node_list = Listbox(m2)
        counter = 0
        for device in transmitters:
            node_list.insert(counter, device)
            counter = counter + 1
        m2.add(node_list)

        frame = Frame(m2)
        m2.add(frame)

        for r in range(3):
            for c in range(4):
                Button(frame, text='R%s/C%s' % (r, c),
                              borderwidth=10).grid(row=r, column=c)


if __name__ == '__main__':
    PORT = 'COM4'
    GATEWAY = '1522'
    BAUD_RATE = 115200
    REMOTE_ADDRESS = ''
    transmitters = ['device1', 'device2', 'device3', 'device4']

    root = Tk()
    app = Application(master=root)
    app.mainloop()