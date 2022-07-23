from PIL import Image
import numpy as np

from tkinter import Tk, Label, filedialog
from tkinter.ttk import Progressbar, Scale, Button, Combobox
from tkinter import HORIZONTAL, DISABLED, NORMAL

import threading
import os


img = None
imagepath = None
width, height = None, None

FONT_SCALE = 0.505

ASCII2 = ' @'
ASCII10 = ' .:-=+*#%@'
ASCII70 = ' .\'`^",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'


def write(ascii_list: list, path=os.path.expanduser("~/Desktop"), filename='result'):
    '''
    Write rows of ASCII list from image to txt file and try opening the file when done.

    Parameters
    ----------
    ascii_list : list
        The list of ASCII values.
    path : str, default Desktop
        The path where the file will be saved.
    filename : str, default 'result'
    '''

    with open(f'{path}/{filename}.txt', 'w') as file:
        for r in ascii_list:
            file.write(r)
            file.write('\n')

    os.system(f'open {path}/{filename}.txt')


def ascii(img: Image, ascii: str, columns: int):
    '''
    Generate ASCII image and create the file.

    Parameters
    ----------
    img: Image
        The image to convert.
    ascii: str
        The ASCII characters to use (luminance).
    columns: int
        The number of columns to have in the output.
    '''

    def average_luminance(tile):
        ''' Get the average luminance of a tile. '''

        tile = np.array(tile)
        average = int(np.average([sum(c) for r in tile for c in r]))
        return average

    def divisor(ascii):
        ''' Get the divisor to index from ASCII list. '''

        high = 255*3
        asciilen = len(ascii)
        div = None

        d = 1
        while not div:
            if high//d == asciilen-1:
                div = d
            d += 0.1

        return round(d, 1)

    asciidiv = divisor(ascii)

    tile_width = width/columns
    tile_height = tile_width/FONT_SCALE
    rows = int(height/tile_height)

    create_progressbar()
    widgets(False)

    ascii_list = []
    for irow in range(rows):
        upper = int(irow*tile_height)
        lower = int(upper+tile_height) if irow != rows-1 else height
        ascii_list.append("")
        for icol in range(columns):
            left = int(icol*tile_width)
            right = int(left+tile_width) if icol != columns-1 else width

            tile = img.crop((left, upper, right, lower))
            try:
                ascii_list[irow] += ascii[int(average_luminance(tile)//asciidiv)]
            except IndexError:
                ascii_list[irow] += ascii[-1]

        tk_progressbar['value'] = (irow/rows)*100

    write(ascii_list, filename=imagepath.split('/')[-1].split('.')[0])

    destroy_progressbar()
    widgets(True)


def select():
    ''' Select a file in GUI. '''

    global width, height, img, imagepath

    filetypes = (
        ('text files', '*.png'),
        ('text files', '*.jpeg'),
        ('text files', '*.jpg'),
        ('text files', '*.webp')
    )

    imagepath = filedialog.askopenfilename(
        title='Open a file',
        initialdir=os.path.expanduser("~/Desktop"),
        filetypes=filetypes)

    img = Image.open(imagepath)
    width, height = img.size

    if width > 1200:
        width, height = 1200, int(height/(width/1200))
        img = img.resize((width, height))

    tk_current.config(text=imagepath.split('/')[-1])
    tk_scale.config(to=width)

    tk_create.config(state=NORMAL)
    tk_scale.config(state=NORMAL)
    tk_scale.set(np.random.randint(10, width))
    tk_columns.config(text=f'Columns: {int(tk_scale.get())}')

    win.focus()


def create():
    ''' Create ASCII image/file. '''

    threading.Thread(target=ascii, kwargs={'img': img, 'ascii': eval(
        f'ASCII{tk_combobox.get().split(" ")[0]}'), 'columns': int(tk_scale.get())}).start()



win = Tk()
win.title('Image to ASCII')
win.geometry('400x210')
win.resizable(False, False)

def widgets(state: bool = True):
    state = NORMAL if state else DISABLED

    tk_choose.config(state=state)
    tk_create.config(state=state)

    if tk_scale:
        tk_scale.config(state=state)

    state = 'readonly' if state == NORMAL else 'disabled'
    tk_combobox.config(state=state)


''' Buttons '''
tk_choose = Button(
    text='Choose file',
    command=select,
    style='Fun.TButton'
)
tk_choose.place(x=150, y=20)

tk_create = Button(
    text='Create ASCII',
    command=create,
    state=DISABLED,
    style='Fun.TButton'
)
tk_create.place(x=150, y=150)


''' Label '''
tk_current = Label(text='',
                   anchor='center', width=44)
tk_current.place(x=0, y=45)

tk_characters = Label(text='Characters: ')
tk_characters.place(x=50, y=75)

tk_columns = Label(text='Columns: X')
tk_columns.place(x=50, y=100)


''' Combobox '''
tk_combobox = Combobox(state='readonly', values=('2 ( @)', '10 ( .:-=+*#%@)',
                       '70 ( .\'`^",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$)'), width=22, )
tk_combobox.bind("<<ComboboxSelected>>", lambda x: win.focus())
tk_combobox.current(newindex=1)
tk_combobox.place(x=130, y=75)


''' Scale '''
tk_scale = Scale(from_=10, to=1000, value=np.random.randint(10, 1000), orient=HORIZONTAL, length=300, state=DISABLED,
                 command=lambda x: tk_columns.config(text=f'Columns: {int(tk_scale.get())}'))
tk_scale.place(x=50, y=120)


''' Progress Bar '''
tk_progressbar = None

def create_progressbar():
    global tk_progressbar
    tk_progressbar = Progressbar(orient='horizontal', mode='determinate', length=300)
    tk_progressbar.place(x=50, y=190)


def destroy_progressbar():
    global tk_progressbar
    tk_progressbar.destroy()
    tk_progressbar = None


win.mainloop()
