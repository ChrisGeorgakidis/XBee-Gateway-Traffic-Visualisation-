from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder


root = Builder.load_string('''
BoxLayout:
    orientation: 'horizontal'
     
    BoxLayout:
        orientation: 'vertical'
        size_hint: 0.3, 1
    
        canvas:
            Color:
                rgb: .6, .6, .6
            
            Rectangle:
                pos: self.pos
                size: self.size
        
        BoxLayout:
            orientation: 'vertical'
                        
            Label:
                text: 'Node List'
                size_hint: 1, 0.05
            
            BoxLayout:
                orientation: 'vertical'
                padding: 10
                
                Button:
                    text: 'button1'
                
                Button:
                    text: 'button2'
                
    BoxLayout:
        canvas:
            Color:
                rgb: 1, 1, 1
            
            Rectangle:
                pos: self.pos
                size: self.size
        
    
        StackLayout:
            id: package_pool
            padding: 10
            spacing: 15
            orientation: 'lr-tb'
        
            Button:
                text: 'Device 1'
                background_color: (0, 0.5, 1, 1)
                size_hint: 0.5, 0.2
            
            Button:
                text: 'Device 2'
                background_color: (0, 0.5, 1, 1)
                size_hint: 0.5, 0.2
                
            Button:
                text: 'Device 3'
                background_color: (0, 0.5, 1, 1)
                size_hint: 0.5, 0.2

            
            Button:
                text: 'Device 4'
                background_color: (0, 0.5, 1, 1)
                size_hint: 0.5, 0.2

            
            Button:
                text: 'Device 5'
                background_color: (0, 0.5, 1, 1)
                size_hint: 0.5, 0.2

                
            Button:
                text: 'Device 6'
                background_color: (0, 0.5, 1, 1)
                size_hint: 0.5, 0.2
            
            Button:
                text: 'Device 7'
                background_color: (0, 0.5, 1, 1)
                size_hint: 0.5, 0.2   
''')


class PackageTrackingApp(App):
    def build(self):
        return root


if __name__ == '__main__':
    PackageTrackingApp().run()

