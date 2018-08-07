from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.devices import XBeeDevice
from digi.xbee.models.address import XBee64BitAddress
from threading import Thread
import time

root = Builder.load_file("packagetracking.kv")


class Package(BoxLayout):
    # def update(self, dt):
    #     self.node = Button(text='XBee Device', size_hint=(.5, .2), background_color=(0, 0, 1, 1))
    #     self.node.id = 'device'
    #     self.ids.package_pool.add_widget(self.node)
    #     self.node_name = Button(text='XBee Device', size_hint=(1, .1))
    #     self.ids.transmitters_list.add_widget(self.node_name)

    def show_message(self, transmitter, message, time):
        node = Button()
        node.id = transmitter

        node_id = node.id
        self.ids.node_id.text = "hey"
        #for x in self.ids:
            # if x == transmitter:
            #     x.text = transmitter + "\nData: " + message + "\n Time: " + str(time)

        x = node_id
        print("hey")


class PackageTrackingApp(App):
    def build(self):
        root.ids.gateway.text = "Gateway: '" + GATEWAY + "' (" + PORT + ")"
        # Clock.schedule_interval(root.update, 1)
        # root.update(1)
        return root


def package_receiving():
    counter = 5
    while counter >= 0:
        print("Message")
        if counter%2 == 0:
            remote_device = 'device1'
        else:
            remote_device = 'device2'
        data = 'hey'
        timestamp = counter
        transmitters.append(remote_device)
        root.show_message(remote_device, data, timestamp)
        counter = counter - 1
        time.sleep(1)


if __name__ == '__main__':
    # print(" +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    # print(" | Establish a communication between a local and remote XBee devices | ")
    # print(" +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")

    PORT = 'COM4'
    GATEWAY = '1522'
    BAUD_RATE = 115200
    REMOTE_ADDRESS = ''
    root = Package()
    transmitters = []

    # # Instantiate a local XBee device object #
    # local_xbee = XBeeDevice(PORT, BAUD_RATE)
    # local_xbee.open()
    #
    # # Get the node identifier of the device.
    # node_id = local_xbee.get_node_id()

    Thread(target=package_receiving).start()
    Thread(target=PackageTrackingApp().run()).start()
    #PackageTrackingApp().run()

    # counter = 5
    # while(counter >= 0):
    #     print("Message")
    #     remote_device = 'device'
    #     data = 'hey'
    #     timestamp = counter
    #     transmitters.append(remote_device)
    #     root.show_message(remote_device, data, timestamp)
    #     counter = counter - 1
        # # Read data from transmitters #
        # xbee_message = local_xbee.read_data()
        # if xbee_message is not None:
        #     print("Message Received")
        #     remote_device = xbee_message.remote_device
        #     transmitters.append(remote_device)
        #     data = xbee_message.data
        #     timestamp = xbee_message.timestamp
        #     counter = counter - 1

    # # Close the XBee device connection #
    # if local_xbee is not None and local_xbee.is_open():
    #     local_xbee.close()





