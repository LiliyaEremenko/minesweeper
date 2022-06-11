import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror

colors = {
    1: '#9ACD32',
    2: '#9ACD32',
    3: '#FFD700',
    4: '#FFD700',
    5: '#FFA500',
    6: '#FFA500',
    7: '#8B0000',
    8: '#8B0000'
}


class MyButton(tk.Button):
    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_mines = 0
        self.is_open = False

    def __repr__(self):
        return f'MyButton{self.x} {self.y} {self.number} {self.is_mine}'


class MineSweeper:
    window = tk.Tk()
    window.wm_title('MineSweeper')
    rows = 8
    columns = 8
    mines = 10
    indexes = []
    flags = []
    is_game_over = False
    is_first_click = True
    is_win = False

    def __init__(self):
        self.buttons = []
        for i in range(MineSweeper.rows + 2):
            temp = []
            for j in range(MineSweeper.columns + 2):
                btn = MyButton(MineSweeper.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind("<Button-3>", self.right_click)
                temp.append(btn)
            self.buttons.append(temp)
    
    def right_click(self, event):
        if MineSweeper.is_game_over or MineSweeper.is_win:
            return
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            MineSweeper.flags.append(cur_btn.number)
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '🚩'
            cur_btn['disabledforeground'] = '#8B0000'
        elif cur_btn['text'] == '🚩':
            MineSweeper.flags.remove(cur_btn.number)
            cur_btn['text'] = ''
            cur_btn['state'] = 'normal'
        if sorted(MineSweeper.flags) == sorted(MineSweeper.indexes[:MineSweeper.mines]):
            showinfo('Win', 'Поздравляю, вы победили!')
            MineSweeper.is_win = True

    def click(self, clicked_button: MyButton):
        if MineSweeper.is_game_over or MineSweeper.is_win:
            return

        if MineSweeper.is_first_click:
            self.insert_mines(clicked_button.number)
            self.count_mines_around()
            self.print_buttons()
            MineSweeper.is_first_click = False   
    
        if clicked_button.is_mine:
            clicked_button.config(text='✪', background='#8B0000', disabledforeground='black')
            clicked_button.is_open = True
            MineSweeper.is_game_over = True
            showinfo('Game over', 'Вы проиграли :( В следующий раз у вас обязательно все получится!')
            for i in range(1, MineSweeper.rows + 1):
                for j in range(1, MineSweeper.columns + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '✪'
        else:
            color = colors.get(clicked_button.count_mines, 'black')
            if clicked_button.count_mines:
                clicked_button.config(text=clicked_button.count_mines, disabledforeground=color)
                clicked_button.is_open = True
            else:
                self.breadth_first_search(clicked_button)
        clicked_button.config(state='disabled', relief=tk.SUNKEN)

    def breadth_first_search(self, btn: MyButton):
        queue = [btn]
        while queue:
            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_mines, 'black')
            if cur_btn.count_mines:
                cur_btn.config(text=cur_btn.count_mines, disabledforeground=color)
            else:
                cur_btn.config(text='', disabledforeground=color)
            cur_btn.config(state='disabled', relief=tk.SUNKEN)
            cur_btn.is_open = True
            if cur_btn.count_mines == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        # if not abs(dx - dy) == 1:
                        #    continue
                        next_btn = self.buttons[x + dx][y + dy]
                        if not next_btn.is_open and 1 <= next_btn.x <= MineSweeper.rows and \
                        1 <= next_btn.y <= MineSweeper.columns and next_btn not in queue:
                            queue.append(next_btn)
    
    def reload(self):
        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.create_buttons()
        MineSweeper.is_first_click = True
        MineSweeper.is_game_over = False
        MineSweeper.is_win = False
        MineSweeper.flags = []

    def create_settings_window(self):
        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Настройки')
        tk.Label(win_settings, text='Кол-во строк:').grid(row=0, column=0)
        tk.Label(win_settings, text='Кол-во колонок:').grid(row=1, column=0)
        tk.Label(win_settings, text='Кол-во мин:').grid(row=2, column=0)

        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, MineSweeper.rows)
        row_entry.grid(row=0, column=1, padx=20, pady=20)

        column_entry = tk.Entry(win_settings)
        column_entry.insert(0, MineSweeper.columns)
        column_entry.grid(row=1, column=1, padx=20, pady=20)

        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, MineSweeper.mines)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)

        save_btn = tk.Button(win_settings, text='Применить',
        command=lambda: self.change_settings(row_entry, column_entry, mines_entry))
        save_btn.grid(row=3, column=0, columnspan=2, pady=20)

    def change_settings(self, row: tk.Entry, column: tk.Entry, mines: tk.Entry):
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Ошибка', 'Пожалуйста, введите правильные значения')
            return

        MineSweeper.rows = int(row.get())
        MineSweeper.columns = int(column.get())
        MineSweeper.mines = int(mines.get())
        self.reload()

    def create_buttons(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Играть', command=self.reload)
        settings_menu.add_command(label='Настройки', command=self.create_settings_window)
        settings_menu.add_command(label='Выход', command=self.window.destroy)
        menubar.add_cascade(label='Игра', menu=settings_menu)

        count = 1
        for i in range(1, MineSweeper.rows + 1):
            for j in range(1, MineSweeper.columns + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick='NWES')
                count += 1

        for i in range(1, MineSweeper.rows + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)
        
        for i in range(1, MineSweeper.columns + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)

    def print_buttons(self):
        for i in range(1, MineSweeper.rows + 1):
            for j in range(1, MineSweeper.columns + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print('M', end='')
                else:
                    print(btn.count_mines, end='')
            print()

    def start(self):
        self.create_buttons()
        MineSweeper.window.mainloop()

    def insert_mines(self, number: int):
        index_mines = self.set_mines_places(number)
        print(index_mines)
        for i in range(1, MineSweeper.rows + 1):
            for j in range(1, MineSweeper.columns + 1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_around(self):
        for i in range(1, MineSweeper.rows + 1):
            for j in range(1, MineSweeper.columns + 1):
                btn = self.buttons[i][j]
                count_mines = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i + row_dx][j + col_dx]
                            if neighbour.is_mine:
                                count_mines += 1
                btn.count_mines = count_mines

    @staticmethod
    def set_mines_places(exclude_number: int):
        MineSweeper.indexes = list(range(1, MineSweeper.rows * MineSweeper.columns + 1))
        MineSweeper.indexes.remove(exclude_number)
        shuffle(MineSweeper.indexes)
        return MineSweeper.indexes[:MineSweeper.mines]


game = MineSweeper()
game.start()