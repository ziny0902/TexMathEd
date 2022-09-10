#!/usr/bin/env python3
from kivy.base import EventLoop
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivy.properties import BooleanProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivymd.color_definitions import colors
from kivymd.uix.list.list import MDList
from kivymd.uix.scrollview import ScrollView
from matrix_widget import MatrixWidget
from kivy.uix.boxlayout import BoxLayout
import os
meta_command={
"<cal": "cheatsheet/icon/calculus/",
'<acc': 'cheatsheet/icon/accents/',
'<bi' : 'cheatsheet/icon/binary/',
'<dot' : 'cheatsheet/icon/dots/',
'<gre' : 'cheatsheet/icon/greek/',
'<rel' : 'cheatsheet/icon/relation/',
'<set' : 'cheatsheet/icon/set_logic/',
'<c' : 'cheatsheet/picture/Calculus.png',
'<l' : 'cheatsheet/picture/linear algebra.png',
'<b': 'cheatsheet/picture/basic.png',
'<g': 'cheatsheet/picture/Greek and Hebrew.png',
'<gt': 'cheatsheet/picture/Geometry and trigonometry.png',
'<m': 'mat',
'<h' : 'help',
'<me' : 'menu'
}

info_str='''<cal: calculus
<acc: accents
<bi : binary
<dot: dots
<gre: greek
<rel: relation
<set: set_logic
---- cheatsheet -----------
<c  : calculus
<l  : linear algebra
<b  : basic
<g  : Greek and Hebrew
<gt : Geometry and trigonometry
<m  : Matrix
'''
#:import images_path kivymd.images_path
cheat_sheet_kv = '''
<SelectableOneLineIconListItem>
    IconLeftWidget:
        icon: root.icon
<Cheatsheet>:
    orientation: 'vertical'
    spacing: dp(10)
    padding: dp(20)
    height: "400dp"
    size_hint_y: None
    MDBoxLayout:
        adaptive_height: True

        MDIconButton:
            icon: 'magnify'

        MDTextField:
            id: search_field
            hint_text: 'Search icon'
            on_text: root.set_list_md_icons(self.text, True)

    RecycleView:
        id: rv
        viewclass: 'SelectableOneLineIconListItem'
        key_size: 'height'

        SelectableRecycleBoxLayout:
            padding: dp(10)
            default_size: None, dp(62)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            multiselect: False
    '''

def parse_meta(str):
    meta = ''
    for c in reversed(str):
        meta += c
        if c == '<':
            return  meta[::-1]
    return ''

shift_mode = {
    44:60, 48:41, 49:40, 50:64, 51:35, 52:36, 53:37, 54:94, 55:38, 56:42,
    57:40, 59:58, 61:43, 46:62, 47:63, 45:95, 39:126, 96:126
}
def convert_kecode2ascii(code, mode):
    if code >= 97 and 125 <= code and mode == ['shift']:
        return code - (97 - 65)
    if code > 32 and code < 127 and mode == ['shift']:
        ascii = shift_mode.get(code)
        if ascii != None :
            return ascii
    if code > 32 and code < 127 :
        return code
    return code

class SelectableRecycleBoxLayout(
    FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
    """ Adds selection and focus behaviour to the view. """

class SelectableOneLineIconListItem(OneLineIconListItem, RecycleDataViewBehavior):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    icon = StringProperty()
    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if self.selected:
            self.bg_color = colors['Light']['FlatButtonDown']
            #[0, 1, 1, 1]
        else:
            self.bg_color = [0, 0, 0, 0]
        return super(SelectableOneLineIconListItem, self).apply_selection(rv, index, is_selected)

class Cheatsheet(MDBoxLayout):
    path = './cheatsheet/icon/'
    def __init__(self, **kwargs):
        Builder.load_string(cheat_sheet_kv)
        super(Cheatsheet, self).__init__(**kwargs)
        self.ids.search_field.bind(focus=self._focus_text)
        self.selected = -1
    def set_list_md_icons(self, text="", search=False):
        '''Builds a list of icons for the screen MDIcons.'''
        file1 = open(self.path+'list.txt', 'r')
        Lines = file1.readlines()
        file1.close()
        def add_icon_item(name_icon):
            #print(self.path+name_icon+'.png')
            self.ids.rv.data.append(
                {
                    "viewclass": "SelectableOneLineIconListItem",
                    "icon": self.path+name_icon+'.png',
                    "text": name_icon,
                    "callback": lambda x: x,
                    "bg_color": [0, 0, 0, 0],
                }
            )

        self.ids.rv.data = []
        for name_icon in Lines:
            name_icon = name_icon.rsplit()[0]
            if search:
                if text in name_icon:
                    add_icon_item(name_icon)
            else:
                add_icon_item(name_icon)
    def _focus_text (self, instance, value):
        if value == False :
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            return
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def keyboard_selection(self, keycode):
        data_len = len (self.ids.rv.data)
        if self.selected >= 0 :
            self.ids.rv.layout_manager.deselect_node(self.selected)
        if keycode[0] == 274 :
            self.selected += 1
            if self.selected > data_len - 1 : self.selected = 0
        else:
            self.selected -= 1
            if self.selected < 0 : self.selected = data_len - 1
        self.scroll_to_index(self.selected)
        self.ids.rv.layout_manager.select_node(self.selected)

    def scroll_to_index(self, index):
        rv = self.ids.rv
        box = self.ids.rv.children[0]
        pos_index = (box.default_size[1] + box.spacing) * index
        total =rv.viewport_size[1] - rv.height
        view_distance = rv.height/total
        index_distance_s = 1 - pos_index/total
        index_distance_e = 1 - (pos_index+box.default_size[1])/total
        if index_distance_s > rv.scroll_y:
            scroll =(index_distance_s - rv.scroll_y )
            scroll = ( rv.scroll_y  + scroll )
        elif index_distance_e < (rv.scroll_y - view_distance) :
            scroll =(index_distance_e -rv.scroll_y + view_distance)
            scroll = ( rv.scroll_y + scroll )
        else:
            scroll = rv.scroll_y
        if scroll > 1 :
            scroll = 1
        if scroll <  0 :
            scroll = 0
        rv.scroll_y = scroll

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[0] == 274 or keycode[0] == 273:
            self.keyboard_selection(keycode)
            return True
        if keycode[0] >= 32 and keycode[0] <=127 :
            self.ids.search_field.text += keycode[1]
            self.ids.search_field.focus = True
            return True
        if keycode[0] == 13 :
            self.is_selected = True;
            self.selected_text = "\\" + self.ids.rv.data[self.selected]['text']
            self.dig.dismiss(force = True)
            pass
        return False

    def _on_open(self, instance):
        self.dig = instance
        self.is_selected = False;
        if self.selected >= 0 :
            self.ids.rv.layout_manager.deselect_node(self.selected)
        self.selected = -1
        self.set_list_md_icons()
result_kv = '''
<Result>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    size_hint_x: None
    height: "400dp"
    width: "400dp"
    MDTextField:
        id: result_view
        text: ""
        multiline: True
        font_name: 'NotoSansMono-Regular'
        readonly: True

'''

Builder.load_string(result_kv)
class Result(BoxLayout):
    pass

Builder.load_file('LatexMathEditor.kv')
class LatexEditor(Widget):
    info_text = StringProperty('')
    def __init__(self, **kwargs):
        super(LatexEditor, self).__init__(**kwargs)
        EventLoop.ensure_window()

        #register event handler
        Window.bind(focus=self.on_focus)
        Window.bind(on_key_down=self._on_keyboard_down)

        #
        # create cheatsheet popup dialog
        self.cheatsheet = Cheatsheet()
        self.popup = MDDialog(title="cheet sheet",
                         type="custom",
                         content_cls=self.cheatsheet,
                         )
        self.popup.bind(on_open=self.cheatsheet._on_open)
        self.popup.bind(on_dismiss=self._on_cheatsheet_dismiss)
        #
        self.ids.latex_field.bind(focus=self._focus_text)
        self.focus_text_field = self.ids.latex_field

        self.result_window = Result()
        self.result_popup = MDDialog(
            title = "Result",
            type = "custom",
            content_cls= self.result_window
        )
        self.result_popup.bind(on_dismiss=self._on_dismiss)

        self.matrix_window = MatrixWidget(
            cols=3, rows=3,
            size_hint=[0.9, None]
        )
        self.matrix_popup = MDDialog(
            title = "Matrix",
            type = "custom",
            content_cls = self.matrix_window
        )
        self.matrix_popup.bind(on_open=self.matrix_on_open)
        self.matrix_popup.bind(on_dismiss=self.matrix_on_dismiss)
        # create cheatsheet image
        self.img = Image(source = 'cheatsheet/picture/Calculus.png')
        self.img.allow_stretch = False
        self.img.keep_ratio = True
        self.img.size_hint = None, None
        self.img.size = self.img.texture.size
        self.img.mipmap = True
        self.img.pos_hint = {'center_x': 0.5}
        self.img_scrollview = ScrollView(
            #size_hint_x = 1,
            pos_hint = {'center_x': 0.5, 'bottom':1}
        )
        self.img_scrollview.add_widget(self.img)
        self.ids.display.add_widget(self.img_scrollview)
        self.info_text = info_str
        self.ids.display.bind(size=self.on_resize)
    def on_resize(self, *args):
        self.img_scrollview.size_hint_y = 0.9 - (self.ids.appbar.size[1]/self.ids.display.size[1])
        hint_x = self.img.texture.size[0]/self.size[0]
        if hint_x <= 1 :
            self.img_scrollview.size_hint_x = hint_x
        else:
            self.img_scrollview.size_hint_x = 1
    def matrix_on_open(self, instance):
        self.focus_text_field = self.matrix_window.ids.input
        self.matrix_window.moveTextfield(0)
        self.focus_text_field.focus = True
    def matrix_on_dismiss(self, instance):
        self.focus_text_field = self.ids.latex_field
        self.focus_text_field.focus = True
        self.ids.latex_field.text += self.matrix_window.result
    def _on_dismiss(self, *args):
        self.focus_text_field = self.ids.latex_field
        self.focus_text_field.focus = True
    def _on_cheatsheet_dismiss(self, *args):
        if self.popup.content_cls.is_selected :
            self.ids.latex_field.text += self.popup.content_cls.selected_text
        self.focus_text_field = self.ids.latex_field
        self.focus_text_field.focus = True
    def _focus_text (self, instance, value):
        if self.ids.latex_field.focus == False :
            #self.remove_widget(self.category_view)
            pass
    def callMatrixWindow(self):
        self.focus_text_field.focus = False
        self.focus_text_field = None
        self.matrix_popup.open()
        pass
    def callCheetSheet(self, path):
        self.cheatsheet.path = path
        self.popup.open()
        self.focus_text_field.focus = False
        self.focus_text_field = self.cheatsheet.ids.search_field
        self.focus_text_field.focus = True
        self.focus_text_field.text = ""
        pass

    def execute_convert(self):
        import subprocess
        self.result_popup.open()
        self.focus_text_field = self.result_window.ids.result_view
        subprocess.run(['rm', 'result.png'], capture_output=False)
        try:
            result = subprocess.run(['tex2png', self.ids.latex_field.text, 'result.png'],
                                    capture_output=True, check=True, text=True)
        except subprocess.CalledProcessError as e:
            self.result_window.ids.result_view.text = e.output
            return
        self.result_window.ids.result_view.text = result.stdout + result.stderr
        self.update_image("result.png")
        pass
    def _on_keyboard_down(self, window, keycode, codepoint, text, modifiers):
        #print('main window on keyboard down', keycode, text, modifiers, codepoint)
        if keycode == 27 :
            return False
        if keycode == 273 and self.focus_text_field == self.ids.latex_field: # up key
            if self.ids.nav_drawer.state == 'open' :
                self.menu_scroll_up()
                return True
            return False
        if self.focus_text_field == None :
            return False
        if keycode == 274 and self.focus_text_field == self.ids.latex_field: # down key
            if self.ids.nav_drawer.state == 'open' :
                self.menu_scroll_down()
                return True
            return False
        if (modifiers == ['ctrl'] and keycode == 115
            and self.focus_text_field == self.matrix_window.ids.input) :
            self.matrix_window.create_matrix_text()
            self.matrix_popup.dismiss()
            return True
        if self.focus_text_field.focus is False and self.focus_text_field == self.ids.latex_field:
            if keycode >= 32 and keycode < 127 and text != None:
                self.focus_text_field.focus = True
                self.focus_text_field.text += chr(convert_kecode2ascii(keycode, modifiers))
                return True
        if keycode == 9 and self.focus_text_field.focus is not True:
            self.focus_text_field.focus = True
            return True
        if keycode == 13 and modifiers == ['shift'] and  self.focus_text_field == self.ids.latex_field:
            self.execute_convert()
            return True
        return False

    def on_focus(self, instance, value):
        self.focus_text_field.focus = value

    def on_text(self, value):
        c = ''
        if len(value) > 0:
            c = value[len(value) - 1]
        if c == '\t':
            value = value.rstrip('\t')
            meta = parse_meta(value)
            category_str = meta_command.get(meta)
            if category_str is not None:
                self.ids.latex_field.text = value[0:-len(meta)]
                self.display_cheatsheet(category_str)
            else:
                self.ids.latex_field.text = value
    def display_cheatsheet(self, str):
        type_str = str[-3:]
        if type_str == 'png':
            self.update_image(str)
        elif type_str == 'mat':
            self.callMatrixWindow()
        elif str == 'menu':
            self.ids.nav_drawer.set_state("open")
            self.focus_text_field.focus = False
        elif str == 'help':
            self.result_popup.open()
            self.focus_text_field.focus = False
            self.focus_text_field = self.result_window.ids.result_view
            self.focus_text_field.text = info_str
        else:
            self.callCheetSheet(str)
        pass
    def update_image(self, source):
        self.img.source = source
        self.img.reload()
        self.img.size = self.img.texture.size
        self.on_resize()
    def menu_scroll_up(self):
        count = len(self.ids.nav_menu.children[0].children)
        inc = 1/count
        up = self.ids.nav_menu.scroll_y + inc
        if up > 1 :
            self.ids.nav_menu.scroll_y = 1
        else:
            self.ids.nav_menu.scroll_y = up
    def menu_scroll_down(self):
        count = len(self.ids.nav_menu.children[0].children)
        inc = 1/count
        up = self.ids.nav_menu.scroll_y - inc
        if up < 0 :
            self.ids.nav_menu.scroll_y = 0
        else:
            self.ids.nav_menu.scroll_y = up

if __name__ == "__main__":
    class LatexMathEditorApp(MDApp):
        title = 'LatexMathEditor'
        def __init__(self, **kwargs):
            os.chdir(os.path.dirname(__file__))
            super().__init__(**kwargs)
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palet = "BlueGrey"
            self.editor = LatexEditor()
        def build(self):
            return self.editor

    LatexMathEditorApp().run()
