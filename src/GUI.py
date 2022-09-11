import tkinter as tk
import tkinter.ttk as ttk
from tree import *
from copy import deepcopy


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
        self.parent.widgets['slots_bar'].update_slots()

    def instance_mode(self):
        self.forget_widgets()
        self.parent.mode = 'instances'
        self.parent.create_widgets()

    def on_exit(self):
        self.parent.quit()


class NavBar(tk.Frame):
    def __init__(self, parent, header: str, *args, **kwargs):
        super(NavBar, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.main_window = parent.parent
        self.background = kwargs['background']
        # LABELS
        self.header_label = ttk.Label(self, style='Heading.TLabel', text=header)

        # POSITION
        self.header_label.pack()

        # STYLING
        self.style = ttk.Style(parent)
        self.style.configure('Heading.TLabel', font=('Helvetica', 16))
        self.header_label.configure(background=self.background)


class TreeBar(NavBar):
    def __init__(self, parent, header, *args, **kwargs):
        super(TreeBar, self).__init__(parent, header, *args, **kwargs)
        self.node_labels = []

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


class ConfigureSlots(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super(ConfigureSlots, self).__init__(parent, *args, **kwargs)
        self.slots = parent.slots
        self.parent = parent
        # LABELS
        slots_label = ttk.Label(self, text='SLOT', style='Heading.TLabel')
        classes_label = ttk.Label(self, text='CLASS', style='Heading.TLabel')
        # WIDGETS
        self.slots_combo = ttk.Combobox(self, values=list(self.slots.keys()))
        self.classes_combo = ttk.Combobox(self, values=list(map(lambda x: x[1], parent.tree.tree_names)))
        # BUTTONS
        self.assign_slots_button = ttk.Button(
            self,
            text='Assign',
            command=self.assign_slots
        )
        # PLACING
        self.slots_combo.grid(row=1, column=0, padx=10)
        self.classes_combo.grid(row=1, column=1, padx=10)
        self.assign_slots_button.grid(row=1, column=2, padx=10)
        slots_label.grid(row=0, column=0, pady=5)
        classes_label.grid(row=0, column=1, pady=5)
        # STYLING
        self.style = ttk.Style(parent)
        self.style.configure('Heading.TLabel', font=('Helvetica', 14))
        slots_label.configure(background=parent.background)
        classes_label.configure(background=parent.background)

    def assign_slots(self):
        tree = self.parent.tree
        root = tree.root

        slot = self.slots_combo.get()
        target_class = self.classes_combo.get()
        node = tree.find_node(root, target_class)
        tree.visit(node, slot=slot)


class PopupWindow:
    def __init__(self, master_window, parent, header):
        self.parent = parent
        top = self.top = tk.Toplevel(master_window)
        # WIDGETS
        frame_for_header = tk.Frame(self.top)
        header_label = ttk.Label(frame_for_header, text=header)

        # POSITIONING
        frame_for_header.pack()
        header_label.pack()


class PopupForSlots(PopupWindow):
    def __init__(self, master_window, parent, header):
        super(PopupForSlots, self).__init__(master_window, parent, header)
        # FRAMES
        entry_frame = tk.Frame(self.top)
        button_frame = tk.Frame(self.top)
        # ENTRIES
        self.slot_entry = ttk.Entry(entry_frame, width=30)
        self.types = ttk.Combobox(entry_frame,
                                  values=[
                                      'int',
                                      'float',
                                      'string',
                                  ])
        # BUTTONS
        confirm_button = ttk.Button(button_frame,
                                    text='OK',
                                    command=self.cleanup)
        # POSITION
        entry_frame.pack(fill='both', expand=True, pady=25)
        button_frame.pack(fill=tk.Y)
        self.slot_entry.grid(row=0, column=0, padx=10)
        self.types.grid(row=0, column=1, padx=10)
        confirm_button.pack(side='bottom')

    def cleanup(self):
        name = self.slot_entry.get()
        if len(name) != 0:
            self.parent.parent.slots[name] = ('', self.types.get())
            print(self.parent.parent.slots[name])
            self.parent.parent.widgets['slots_configuration'].slots = deepcopy(self.parent.parent.slots)
            self.parent.parent.widgets['slots_configuration'].slots_combo['values'] = list(
                self.parent.parent.slots.keys())
        self.top.destroy()


class SlotsBar(NavBar):
    def __init__(self, parent, header, *args, **kwargs):
        super(SlotsBar, self).__init__(parent, header, *args, **kwargs)
        self.slot_labels = []
        # WIDGETS
        tool_bar = tk.Frame(self, background=parent.background)
        self.create_slot_button = ttk.Button(tool_bar,
                                             text='New slot',
                                             command=self.add_slot)
        # POSITION
        tool_bar.pack(side='top')
        self.create_slot_button.pack()

    def add_slot(self):
        self.w = PopupForSlots(self.main_window, self, header='NEW SLOT')
        self.create_slot_button['state'] = 'disabled'
        self.main_window.wait_window(self.w.top)
        self.create_slot_button['state'] = 'normal'
        self.update_slots()

    def update_slots(self):
        for label in self.slot_labels:
            label.pack_forget()
        for i, name in enumerate(self.parent.slots.keys()):
            label = ttk.Label(self, text=name, background=self.background)
            label.pack(anchor=tk.NW)
            self.slot_labels.append(label)


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.widgets = {}
        self.slots = {}
        self.tree = Tree()
        self.parent = parent
        self.background = kwargs['background']
        self.menu_bar = Menu(self)
        self.mode = 'ontology'
        self.create_widgets()

    def create_widgets(self):
        if self.mode == 'ontology':
            self.widgets = {
                'tree_bar': TreeBar(self, 'CLASSES', background='grey'),
                'input_bar': InputBar(self, background=self.background),
            }
            self.widgets['tree_bar'].pack(side='left', fill='y')
            self.widgets['input_bar'].pack(anchor=tk.CENTER)
        elif self.mode == 'slots':
            self.widgets = {
                'slots_bar': SlotsBar(self, 'SLOTS', background='grey'),
                'slots_configuration': ConfigureSlots(self, background=self.background)
            }
            self.widgets['slots_bar'].pack(side='left', fill='y', ipadx=25)
            self.widgets['slots_configuration'].pack()
        elif self.mode == 'instances':
            self.widgets = {
                'tree_bar': TreeBar(self, 'CLASSES', background='grey'),
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
