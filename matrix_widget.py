#!/usr/bin/env python3
from kivy.base import EventLoop
from kivy.uix.label import Label
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.widget import MDWidget
from kivy.lang import Builder
from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup
from kivymd.app import MDApp
from kivy.core.window import Window
from  kivy.clock import Clock
KV='''
<MatrixWidget>:
    id: matrix
    canvas:
    MDTextField:
        id: input
        text: "0"
        mode: "round"
        size_hint: None, None
        pose_hint: {None, None}
        multiline: False
        on_text: root.on_text(self.text)
        on_text_validate: root.on_enter(self, self.text)
'''

#class MatrixWidget(MDFloatLayout) :
class MatrixWidget(MDWidget) :
    cols = 2
    rows = 2
    pts = []
    mtype = "bmatrix"
    def __init__(self, **kwargs):
        Builder.load_string(KV)
        _cols = kwargs.get('cols')
        if _cols != None :
            _cols = kwargs.pop('cols')
        else:
            _cols = self.cols
        _rows = kwargs.get('rows')
        if _rows != None :
            _rows = kwargs.pop('rows')
        else:
            _rows = self.rows
        self.pad = 5
        self.result = ''
        self.kivy_instructions = InstructionGroup()
        super(MatrixWidget, self).__init__(**kwargs)
        EventLoop.ensure_window()
        self.bind(pos=self.resize)
        self.bind(size=self.resize)
        self.ids.input.bind(focus=self._focus_input)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, "text")
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.set_col_row(_cols, _rows)
    def set_col_row(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.input_pos = 0
        self.pts = [0]*4*(self.cols+self.rows - 2)
        self.canvas_size = [60*self.cols, 60*self.rows]
        self.create_cell_label()
        self.size = [60*self.cols+2*self.pad, 60*self.rows + 2*self.pad]
        #self.ids.input.focus = True
    def create_cell_label(self):
        total = self.cols * self.rows
        self.label_list = [None]*total
        for i in range(0, total):
            self.label_list[i] = Label(
                                    text="0",
                                    size_hint = (None, None),
                                    pos_hint = {None, None},
                                    color = [0, 0, 0, 1]
                                )
    def on_time(self, dt):
        self.ids.input.focus = True
        pass
    def on_text(self, value):
        c = ''
        if len(value) > 0:
            c = value[len(value) - 1]
        if c != '\t':
            self.label_list[self.input_pos].text = value
            return
        pos = self.input_pos + 1
        pos = pos%(self.cols * self.rows)
        self.ids.input.text = value.rstrip('\t')
        self.moveTextfield(pos)
    def on_enter(self, instance, value):
        self.input_pos += 1
        self.input_pos = self.input_pos%(self.cols * self.rows)
        self.moveTextfield(self.input_pos)
        Clock.schedule_once(self.on_time)
    def _focus_input(self, instance, value):
        #print('_focus_input', value)
        if value == True :
            self.ids.input.select_all()
            return
        #print('register keboard')
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, "text")
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    def _keyboard_closed(self):
        #print('_keyboard_closed')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        pass
    def create_matrix_text(self):
        ret = '\\['
        ret += '\\begin{'+self.mtype+'}\n'
        for i in range(0, self.rows):
            for j in range(0, self.cols):
                ret += self.label_list[i*self.cols + j].text + ' & '
            ret = ret[:len(ret)-2]
            ret += '\\\\\n'
        ret += '\end{'+self.mtype+'}'
        ret += '\\]'
        self.result = ret
    def _on_keyboard_down(self,  keyboard, keycode, text, modifiers):
        old = self.input_pos
        if modifiers == ['ctrl'] and keycode[0] == 115:
            self.create_matrix_text()
            return True
        if keycode[0] == 13:
            #print("enter")
            self.ids.input.focus = True
            return True
        if keycode[0] == 273 :
            self.input_pos = self.input_pos - self.cols
        if keycode[0] == 274 :
            self.input_pos = self.input_pos + self.cols
        if keycode[0] == 276 : # left
            self.input_pos -= 1
        if keycode[0] == 275 : # right
            self.input_pos += 1
        if keycode[0] == ord('j'): # down
            self.input_pos = self.input_pos + self.cols
        if keycode[0] == ord('k'): # up
            self.input_pos = self.input_pos - self.cols
        if keycode[0] == ord('l'): # right
            self.input_pos += 1
        if keycode[0] == ord('h'): # left
            self.input_pos -= 1
        self.input_pos = self.input_pos%(self.cols * self.rows)
        if old != self.input_pos :
            self.moveTextfield(self.input_pos)
            return True
        return False
    def drawBackground(self):
        self.kivy_instructions.add(
            Color(0.85,0.85,0.85,1)
        )
        self.kivy_instructions.add(
            Rectangle(pos=(self.pos[0],self.pos[1]), size=(self.width, self.height))
        )
        pass
    def drawOutline(self):
        self.kivy_instructions.add(
            Line(
                points=
                 [
                   self.base_x, self.base_y,
                   self.base_x+self.canvas_size[0], self.base_y,
                   self.base_x + self.canvas_size[0], self.base_y + self.canvas_size[1],
                   self.base_x, self.base_y + self.canvas_size[1],
                   self.base_x, self.base_y
                 ]
                 , width=1
                 )
        )
        pass
    def drawCell(self):
        for i in range(0, 4*(self.cols + self.rows - 2), 4):
            self.kivy_instructions.add(
                Line(
                    points=[
                    self.pts[i], self.pts[i+1],
                    self.pts[i+2], self.pts[i+3]
                    ],
                    width=1
                )
            )
        pass
    def drawCellContent(self):
        for pos in range(self.cols * self.rows):
            x =self.base_x + ( (pos % self.cols) * self.unit_width
                + ((self.unit_width - self.label_list[pos].size[0])/2  )
                )
            y = (
                self.base_y+self.canvas_size[1]
                - (pos // self.cols) * self.unit_height - (self.unit_height + self.label_list[pos].size[1])/2
                )
            x = int(x)
            y = int(y)
            self.label_list[pos].pos =(x, y)
            self.remove_widget(self.label_list[pos])
            self.add_widget(self.label_list[pos])
    def repositionTextfield(self):
        self.ids.input.size[0] = self.unit_width*0.9 - 2*self.pad
        self.ids.input.size[1] = self.unit_height*0.8 - 2*self.pad
        x =self.base_x + ( (self.input_pos % self.cols) * self.unit_width
             + ((self.unit_width - self.ids.input.size[0])/2  )
             )
        y = (
            self.base_y+self.canvas_size[1]
            - (self.input_pos // self.cols) * self.unit_height - (self.unit_height + self.ids.input.size[1])/2
             )
        x = int(x)
        y = int(y)
        self.ids.input.pos =(x, y)
        self.remove_widget(self.ids.input)
        self.add_widget(self.ids.input)
        pass
    def moveTextfield(self, pos):
        self.input_pos = pos
        self.ids.input.text = self.label_list[pos].text
        self.invalidate()
    def invalidate(self):
        # initialize graphic
        self.kivy_instructions.clear()
        # back ground
        self.drawBackground()
        #back ground
        self.kivy_instructions.add(Color(1.,1.,1.,1.))
        # Out line
        self.drawOutline()
        # Cell
        self.drawCell()
        # update canvas
        self.canvas.clear()
        self.canvas.add(self.kivy_instructions)
        self.drawCellContent()
        # text field resize and resposition
        self.repositionTextfield()
        #
    def resize(self, *args):
        # recalculate position
        self.unit_width = self.canvas_size[0]/(self.cols)
        self.unit_height = self.canvas_size[1]/(self.rows)
        self.center_x = self.width/2 + self.pos[0]
        self.center_y = self.height/2 + self.pos[1]
        self.base_x = self.center_x - self.canvas_size[0]/2
        self.base_y = self.center_y - self.canvas_size[1]/2
        for i in range(0, 4*self.cols - 4 , 4):
            self.pts[i] = self.base_x + self.unit_width * (1+i/4)
            self.pts[i+1 ] = self.base_y
            self.pts[i+2 ] = self.base_x + self.unit_width * (1+i/4)
            self.pts[i+3 ] = self.base_y + self.canvas_size[1]
        base = 4 * self.cols  - 4
        for i in range(0, 4*self.rows - 4, 4):
            self.pts[base+i] = self.base_x
            self.pts[base+i+1] = self.base_y + self.unit_height * (1+i/4)
            self.pts[base+i+2] = self.base_x + self.canvas_size[0]
            self.pts[base+i+3] = self.base_y + self.unit_height * (1+i/4)
        self.invalidate()


if __name__ == "__main__":
    matrix_kv = '''
<Matrix>:
    orientation: "vertical"
    '''
    from kivy.uix.boxlayout import BoxLayout
    class Matrix(BoxLayout):
        def __init__(self, **kwargs):
            super(Matrix, self).__init__(**kwargs)
            self.editor = MatrixWidget(cols=3, rows=3)
            self.add_widget(self.editor)

    Builder.load_string(matrix_kv)
    class TestApp(MDApp):
        def build(self):
            #return MatrixWidget(cols=5, rows=5)
            return Matrix()
    TestApp().run()
