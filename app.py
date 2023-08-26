from functools import partial
import json
import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk,Gdk,Gio,GLib

class MorseConvert:
    def __init__(self,MORSE_FILE:str='./assets/morse.json'):
        self.ascii_to_morse={}
        self.morse_to_ascii={}
        with open(MORSE_FILE,'r') as f:
            self.ascii_to_morse=json.load(fp=f)
            _=self.ascii_to_morse.pop('__source__')
        self.morse_to_ascii={f'{value}':key for key,value
                                in self.ascii_to_morse.items()}
    def to_morse(self,text:str)->str:
         new_text=[]
         for c in text.upper():
             convert=self.ascii_to_morse.get(c,None)
             if convert is None:
                 new_text.append(c)
             else:
                 new_text.append(convert)
         return " ".join(new_text)
    def to_ascii(self,text:str)->str:
         text=text.split(" ")
         new_text=[]
         for c in text:
             convert=self.morse_to_ascii.get(c,None)
             if convert is None:
                 new_text.append(c)
             else:
                 new_text.append(convert)
         return "".join(new_text)

class MainApp(Gtk.Window):
    def __init__(self):
        self.mc=MorseConvert()
        super().__init__(title="MorseCII")
        self.set_default_size(500, 500)
        self.set_border_width(10)
        self.set_decorated(True)
        self.set_resizable(True)
        self.set_size_request(400, 300)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_default_icon_from_file('./assets/icon.png')


        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        box.set_name("container")
        box.set_size_request(-1,500)
        self.add(box)
        button:Gtk.Button=Gtk.Button(label='Clear Text Views')
        button.set_name("foo")
        button.connect("clicked",self.on_clear_text_views)
        box.pack_start(button,False,True,0)
        self.textview=Gtk.TextView()

        self.textview.set_name("mytextview")
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        buffer=self.textview.get_buffer()
        # buffer.connect("insert-text",self.on_textview_changes)
        self.insert_text_id = buffer.connect("insert-text",self.on_textview_insert_text)
        self.delete_text_id = buffer.connect("delete-range",self.on_textview_delete_text)

        # used the css since it is deprecated
        # self.textview.override_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(255,0,0,1))
        # self.textview.override_background_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(0,0,0,1))
        scrolledwindow=Gtk.ScrolledWindow()
        scrolledwindow.add(self.textview)
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                  Gtk.PolicyType.AUTOMATIC)
        box.pack_start(scrolledwindow,True,True,0)

        self.textview2=Gtk.TextView()
        self.textview2.set_name("mytextview2")
        self.textview2.set_wrap_mode(Gtk.WrapMode.WORD)

        buffer2=self.textview2.get_buffer()
        self.insert_text2_id = buffer2.connect("insert-text",self.on_textview2_insert_text)
        self.delete_text2_id = buffer2.connect("delete-range",self.on_textview2_delete_text)



        scrolledwindow2=Gtk.ScrolledWindow()
        scrolledwindow2.add(self.textview2)
        scrolledwindow2.set_policy(Gtk.PolicyType.AUTOMATIC,
                                  Gtk.PolicyType.AUTOMATIC)
        box.pack_start(scrolledwindow2,True,True,0)

        self.connect("key-press-event", self.on_key_press)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(Gio.File.new_for_path('./assets/style.css'))
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, css_provider,
                                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def on_textview_insert_text(self,buffer,location,text,length):
        # there is 1 key press lag so need to have a buffer wait
        if not self.textview2.has_focus():
            # TODO: MAKE THIS BUFFER text upper case ???
            GLib.idle_add(partial(self.fetch_buffer_text_and_write,
                                  buffer,
                                  self.textview2,
                                  self.mc.to_morse))

    def fetch_buffer_text_and_write(self,buffer:Gtk.TextBuffer,
                                         textview:Gtk.TextView,
                                         method)->bool:
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text_buffer=buffer.get_text(start_iter, end_iter, True)
        textview.get_buffer().set_text(method(text_buffer))
        return False

    def on_textview_delete_text(self,buffer,start,end):
        if not self.textview2.has_focus():
            GLib.idle_add(partial(self.fetch_buffer_text_and_remove,
                                 buffer,
                                 self.textview2,
                                 self.mc.to_morse))

    def fetch_buffer_text_and_remove(self,buffer:Gtk.TextBuffer,
                                          textview:Gtk.TextView,
                                          method)->bool:
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text_buffer=buffer.get_text(start_iter, end_iter, True)
        textview.get_buffer().set_text(method(text_buffer))
        self.buffer_one=True
        return False

    def on_textview2_insert_text(self,buffer,location,text,length):
        if not self.textview.has_focus():
            GLib.idle_add(partial(self.fetch_buffer_text_and_write,
                                 buffer,
                                 self.textview,
                                 self.mc.to_ascii))

    def on_textview2_delete_text(self,buffer,start,end):
        if not self.textview.has_focus():
            GLib.idle_add(partial(self.fetch_buffer_text_and_remove,
                                  buffer,
                                  self.textview,
                                  self.mc.to_ascii))
    def on_clear_text_views(self,widget):
        self.textview.get_buffer().handler_block(self.insert_text_id)
        self.textview.get_buffer().handler_block(self.delete_text_id)
        self.textview2.get_buffer().handler_block(self.insert_text2_id)
        self.textview2.get_buffer().handler_block(self.delete_text2_id)

        self.textview.get_buffer().set_text("")
        self.textview2.get_buffer().set_text("")

        self.textview.get_buffer().handler_unblock(self.insert_text_id)
        self.textview.get_buffer().handler_unblock(self.delete_text_id)
        self.textview2.get_buffer().handler_unblock(self.insert_text2_id)
        self.textview2.get_buffer().handler_unblock(self.delete_text2_id)

    def on_key_press(self, widget, event):
            # Check if the Ctrl key is pressed
            ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
            # Check if the key pressed is 'e'
            if ctrl and event.keyval == Gdk.KEY_e:
                if self.textview.is_focus():
                    self.textview2.grab_focus()
                else:
                    self.textview.grab_focus()
                return True # Return True to stop other handlers from being invoked for the event
            return False

def main():
    win=MainApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__=='__main__':
    main()
    pass
