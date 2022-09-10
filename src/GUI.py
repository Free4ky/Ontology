import tkinter as tk
import tkinter.ttk as ttk
from tree import *


class Menu(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        super(Menu, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.main_window = parent.parent
        self.main_window.config(menu=self)  # parent.parent == main window
        # DROP MENU
        file_menu = tk.Menu(self)
        file_menu.add_command(label="Exit", command=self.on_exit)

        mode_menu = tk.Menu(self)
        mode_menu.add_command(label="Classes", command=self.ontology_mode)
        mode_menu.add_command(label='Slots', command=self.slots_mode)
        mode_menu.add_command(label='Instances', command=self.instance_mode)
        mode_menu.add_command(label='Query', command=self.query_mode)
        # MAIN MENU
        self.add_cascade(label="File", menu=file_menu)
        self.add_cascade(label='Mode', menu=mode_menu)

    def forget_widgets(self):
        for name, widget in self.parent.widgets.items():
            widget.pack_forget()

    def query_mode(self):
        self.forget_widgets()
        self.parent.mode = 'query'
        self.parent.create_widgets()

    def ontology_mode(self):
        self.forget_widgets()
        self.parent.mode = 'ontology'
        self.parent.create_widgets()
        self.parent.widgets['tree_bar'].update_bar()

    def slots_mode(self):
        self.forget_widgets()
        self.parent.mode = 'slots'
        self.parent.create_widgets()

    def instance_mode(self):
        self.forget_widgets()
        self.parent.mode = 'instances'
        self.parent.create_widgets()

    def on_exit(self):
        self.parent.quit()


class TreeBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super(TreeBar, self).__init__(parent, *args, **kwargs)
        self.node_labels = []
        self.parent = parent
        self.background = kwargs['background']
        # LABELS
        self.hierarchy_label = ttk.Label(self, style='Heading.TLabel', text='CLASSES')

        # POSITION
        self.hierarchy_label.pack()

        # STYLING
        self.style = ttk.Style(parent)
        self.style.configure('Heading.TLabel', font=('Helvetica', 16))
        self.hierarchy_label.configure(background=self.background)

    def update_bar(self):
        if self.node_labels:
            for label in self.node_labels:
                label.pack_forget()
            self.node_labels.clear()
        tree = self.parent.tree
        if tree.root is not None:
            tree.tree_names = []
            tree.visit(tree.root)
            print('TREE NAMES', tree.tree_names)
            for i, lvl_and_name in enumerate(tree.tree_names):
                level, name = lvl_and_name
                label = ttk.Label(self, text=name, background=self.background)
                self.node_labels.append(label)
                label.pack(padx=(level * 25, 0), anchor=tk.NW)


class InputBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super(InputBar, self).__init__(parent, *args, **kwargs)
        self.parent = parent

        # Entries
        self.parent_entry = tk.Entry(self, width=20)
        self.children_entry = tk.Entry(self, width=40)
        # LABELS
        self.parent_entry_label = ttk.Label(self, text="PARENT", style='TLabel')
        self.children_entry_label = ttk.Label(self, text="CHILDREN", style='TLabel')
        # BUTTONS
        self.add_node_button = ttk.Button(
            self,
            command=parent.add_node,
            text='ADD'
        )
        # POSITION
        self.parent_entry.grid(row=1, column=0, padx=10)
        self.children_entry.grid(row=1, column=1, padx=10)
        self.parent_entry_label.grid(row=0, column=0, pady=5)
        self.children_entry_label.grid(row=0, column=1, pady=5)
        self.add_node_button.grid(row=1, column=2)

        # styling
        self.style = ttk.Style(parent)
        self.style.configure('TLabel', font=('Helvetica', 14))
        self.parent_entry_label.configure(background=parent.background)
        self.children_entry_label.configure(background=parent.background)


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.widgets = {}
        self.tree = Tree()
        self.parent = parent
        self.background = kwargs['background']
        self.menu_bar = Menu(self)
        self.mode = 'ontology'
        self.create_widgets()

    def create_widgets(self):
        if self.mode == 'ontology':
            self.widgets = {
                'tree_bar': TreeBar(self, background='grey'),
                'input_bar': InputBar(self, background=self.background)
            }
            self.widgets['tree_bar'].pack(side='left', fill='y')
            self.widgets['input_bar'].pack(anchor=tk.CENTER)
        elif self.mode == 'slots':
            self.widgets = {

            }
        elif self.mode == 'instances':
            self.widgets = {
                'tree_bar': TreeBar(self, background='grey'),
            }
            self.widgets['tree_bar'].pack(side='left', fill='y')
        elif self.mode == 'query':
            self.widgets = {

            }

    def add_node(self):
        parent = self.widgets['input_bar'].parent_entry.get()
        children = self.widgets['input_bar'].children_entry.get().split()
        print(children)
        self.tree.add_node(parent, children)
        self.widgets['tree_bar'].update_bar()


HEIGHT = 400
WIDTH = 800


def start():
    root = tk.Tk()
    root.geometry(f'{WIDTH}x{HEIGHT}')
    MainApplication(root, background='light grey').pack(side="top", fill="both", expand=True, )
    root.mainloop()
