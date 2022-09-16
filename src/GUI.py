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
        file_menu.add_command(label="Выход", command=self.on_exit)

        mode_menu = tk.Menu(self)
        mode_menu.add_command(label="Классы", command=self.ontology_mode)
        mode_menu.add_command(label='Слоты', command=self.slots_mode)
        mode_menu.add_command(label='Сущности', command=self.instance_mode)
        mode_menu.add_command(label='Запрос', command=self.query_mode)
        mode_menu.add_command(label='Иерархия', command=self.hierarchy_mode)
        # MAIN MENU
        self.add_cascade(label="Файл", menu=file_menu)
        self.add_cascade(label='Режим', menu=mode_menu)

    def show_hierarchy(self):
        tree = self.parent.tree
        tree.image = gv.Digraph()
        tree.image.format = 'png'
        tree.build_graph(tree.root)
        tree.image.render(directory='./img')

    def forget_widgets(self):
        if 'instance_bar' in self.parent.widgets.keys():
            if self.parent.widgets['instance_bar'].configure_slots_frame is not None:
                self.parent.widgets['instance_bar'].configure_slots_frame.pack_forget()
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
        self.parent.widgets['tree_bar'].update_bar()

    def hierarchy_mode(self):
        self.show_hierarchy()
        self.forget_widgets()
        self.parent.mode = 'hierarchy'
        self.parent.create_widgets()

    def on_exit(self):
        self.parent.quit()


class ImageBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super(ImageBar, self).__init__(parent, *args, **kwargs)
        try:
            self.img = tk.PhotoImage(file='./img/Digraph.gv.PNG')
            tk.Label(
                self,
                image=self.img
            ).pack()

        except Exception as e:
            print(e)


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


class InstanceBar(NavBar):
    def __init__(self, parent, header, *args, **kwargs):
        super(InstanceBar, self).__init__(parent, header, *args, **kwargs)
        self.current_instance = None
        print('TREE NAMES IN INSTANCE', self.parent.tree.tree_names)
        self.class_names = list(map(lambda x: x[1], self.parent.tree.tree_names))
        self.tree = parent.tree
        self.instances = []
        self.background = kwargs['background']
        # FOR INSTANCE SLOTS CONFIGURATION
        self.configure_slots_frame = None
        self.entries = []
        self.labels = []
        # FRAMES
        button_frame = tk.Frame(self, background=self.background)
        combobox_frame = tk.Frame(self, background=self.background)
        # LABELS
        create_instance_label = ttk.Label(button_frame, text='Добавить сущность')
        classes_label = ttk.Label(combobox_frame, text='Классы')
        instance_label = ttk.Label(combobox_frame, text='Сущности')
        # BUTTONS
        self.new_instance_button = ttk.Button(
            button_frame,
            text='+',
            command=self.add_instance
        )
        # COMBOBOXES
        self.classes_combobox = ttk.Combobox(
            combobox_frame,
            values=self.class_names
        )
        self.classes_combobox.bind('<<ComboboxSelected>>', self.find_instances)
        self.instance_combobox = ttk.Combobox(
            combobox_frame,
            values=self.instances
        )
        self.instance_combobox.bind('<<ComboboxSelected>>', self.show_and_update_slots)
        # POSITIONING
        button_frame.pack()
        combobox_frame.pack()
        self.new_instance_button.grid(row=0, column=1, padx=5)
        create_instance_label.grid(row=0, column=0, padx=5)
        classes_label.grid(row=0, column=0, padx=3, sticky=tk.W)
        instance_label.grid(row=1, column=0, padx=3, sticky=tk.W)
        self.classes_combobox.grid(row=0, column=1)
        self.instance_combobox.grid(row=1, column=1)
        # STYLING
        create_instance_label.configure(background=self.background)
        classes_label.configure(background=self.background)
        instance_label.configure(background=self.background)
        # STYLING

    def add_instance(self):
        self.w = PopupForInstances(self.main_window, self, header='Новая сущность')
        self.new_instance_button['state'] = 'disabled'
        self.main_window.wait_window(self.w.top)
        self.new_instance_button['state'] = 'normal'

    def find_instances(self, event):
        node = self.tree.find_node(self.tree.root, target=self.classes_combobox.get())
        if node is None:
            return
        for i in node.children:
            print(i.class_name)

        instances = []
        for child in node.children:
            if child.is_instance:
                instances.append(child)
        self.instance_combobox['value'] = list(map(lambda x: x.class_name, instances))

    def show_and_update_slots(self, event):
        style = self.style
        background = '#CFCFCF'
        tree = self.parent.tree
        if self.configure_slots_frame is not None:
            self.configure_slots_frame.pack_forget()
            self.entries.clear()
        # FRAMES
        self.configure_slots_frame = tk.Frame(self.parent, background=background)
        entries_frame = tk.Frame(self.configure_slots_frame, background=background)
        button_frame = tk.Frame(self.configure_slots_frame, background=background)
        # LABELS
        self.instance_name_label = ttk.Label(entries_frame, text='Имя сущности:', background=background)
        header = ttk.Label(
            self.configure_slots_frame,
            text='ИЗМЕНИТЬ ЗНАЧЕНИЯ СЛОТОВ',
            style='Heading.TLabel',
            background=background
        )
        # BUTTONS
        self.update_button = ttk.Button(
            button_frame,
            text='Изменить',
            command=self.update_slots
        )
        # ENTRIES
        self.instance_name_entry = ttk.Entry(entries_frame)
        self.current_instance = tree.find_node(tree.root, self.instance_combobox.get())
        self.instance_name_entry.insert(0, self.current_instance.class_name)
        for i, (slot_name, value) in enumerate(self.current_instance.slots.items()):
            label = ttk.Label(entries_frame, text=slot_name, background=background)
            entry = ttk.Entry(entries_frame)
            entry.insert(0, value[0])
            self.entries.append(entry)
            label.grid(row=i + 1, column=0, padx=3)
            entry.grid(row=i + 1, column=1, padx=3)
        # PLACING
        self.configure_slots_frame.pack(side='right', fill='both', expand=True)
        header.pack()
        entries_frame.pack()
        button_frame.pack(side=tk.BOTTOM)
        self.update_button.pack()
        self.instance_name_label.grid(row=0, column=0, padx=5)
        self.instance_name_entry.grid(row=0, column=1, padx=5)
        # STYLING

    def update_slots(self):
        self.current_instance.class_name = self.instance_name_entry.get()
        for i, (slot_name, value) in enumerate(self.current_instance.slots.items()):
            self.current_instance.slots[slot_name] = (self.entries[i].get(), value[1])


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
                label = ttk.Label(self, text=name, background=self.background, style='Heading.TLabel')
                self.node_labels.append(label)
                label.pack(padx=(level * 25, 0), anchor=tk.NW)


class FindBar(NavBar):
    def __init__(self, parent, *args, **kwargs):
        super(FindBar, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.background = kwargs['background']
        self.tree = parent.tree
        self.instances = []
        self.main_window = self.parent.parent
        # FRAMES
        combobox_frame = tk.Frame(self, background=self.background)
        # COMBOBOXES
        self.instances_combobox = ttk.Combobox(combobox_frame, values=[i.class_name for i in self.tree.query_result])
        self.instances_combobox.bind('<<ComboboxSelected>>', self.show_instance_info)
        # PLACING
        combobox_frame.pack(side='bottom', fill='x')
        self.instances_combobox.pack()

    def update_bar(self):
        for label in self.instances:
            label.pack_forget()
        self.instances.clear()
        for i in self.tree.query_result:
            label = ttk.Label(self, text=i.class_name, background=self.background)
            label.pack()
            self.instances.append(label)
        self.instances_combobox['values'] = [i.class_name for i in self.tree.query_result]

    def show_instance_info(self, event):
        self.w = PopupInstanceInfo(self.main_window, self, header='ИНФОРМАЦИЯ О СУЩНОСТИ')
        self.main_window.wait_window(self.w.top)


class QueryBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super(QueryBar, self).__init__(parent, *args, **kwargs)
        self.parent = parent
        self.background = kwargs['background']
        # INIT STUFF
        self.tree = parent.tree
        self.current_slots = []
        self.current_class = None
        # FRAMES
        header_frame = tk.Frame(self, background=self.background)
        query_frame = tk.Frame(self, background=self.background)
        # LABELS
        class_label = ttk.Label(query_frame, style='TLabel', text='КЛАСС', background=self.background)
        slot_label = ttk.Label(query_frame, style='TLabel', text='СЛОТ', background=self.background)
        value_label = ttk.Label(query_frame, style='TLabel', text='ЗНАЧЕНИЕ', background=self.background)
        header = ttk.Label(header_frame, text='ЗАПРОС', style='Heading.TLabel', background=self.background)
        # ENTRIES
        self.value_entry = ttk.Entry(query_frame, width=20)
        # COMBOBOXES
        self.classes_combobox = ttk.Combobox(
            query_frame,
            values=list(map(lambda x: x[1], self.tree.tree_names)))
        self.classes_combobox.bind('<<ComboboxSelected>>', self.get_slots)
        self.variants = ttk.Combobox(
            query_frame,
            values=[
                'равен',
                'больше',
                'меньше'
            ]
        )
        # BUTTONS
        self.find_button = ttk.Button(
            query_frame,
            text='Найти',
            command=self.find_instances
        )
        self.slots_combobox = ttk.Combobox(query_frame, values=self.current_slots)
        # PACKING
        header_frame.pack()
        header.pack(anchor=tk.CENTER)
        query_frame.pack(side='left', fill='both', expand=True, pady=30)
        class_label.grid(row=0, column=0, padx=3, pady=5)
        slot_label.grid(row=0, column=1, padx=3, pady=5)
        value_label.grid(row=0, column=3, padx=3, pady=5)
        self.classes_combobox.grid(row=1, column=0, padx=3)
        self.slots_combobox.grid(row=1, column=1, padx=3)
        self.variants.grid(row=1, column=2, padx=3)
        self.value_entry.grid(row=1, column=3, padx=3)
        self.find_button.grid(row=1, column=4, padx=3)

    def get_slots(self, event):
        self.current_class = self.tree.find_node(self.tree.root, self.classes_combobox.get())
        self.current_slots = list(self.current_class.slots.keys())
        self.slots_combobox['value'] = self.current_slots

    def find_instances(self):
        mode = self.variants.get()
        # visit and find !instances! that satisfy query settings
        tree = self.tree
        tree.query_result = []
        # query settings
        slot = self.slots_combobox.get()
        v_type = self.current_class.slots[slot]
        value = Tree.convert.get(v_type)(self.value_entry.get())
        tree.visit(tree.root, slot=slot, query=True, mode=mode, value=value)
        self.parent.widgets['find_bar'].update_bar()


class InputBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super(InputBar, self).__init__(parent, *args, **kwargs)
        self.parent = parent

        # Entries
        self.parent_entry = tk.Entry(self, width=20)
        self.children_entry = tk.Entry(self, width=40)
        # LABELS
        self.parent_entry_label = ttk.Label(self, text="КЛАСС-РОДИТЕЛЬ", style='TLabel')
        self.children_entry_label = ttk.Label(self, text="КЛАСС-ПРЕДОК", style='TLabel')
        # BUTTONS
        self.add_node_button = ttk.Button(
            self,
            command=parent.add_node,
            text='Добавить'
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
        self.assigned_class_labels = []
        # LABELS
        assigned_classes_label = ttk.Label(self, text='СВЯЗАННЫЕ КЛАССЫ', style='TLabel')
        slots_label = ttk.Label(self, text='СЛОТ', style='Heading.TLabel')
        classes_label = ttk.Label(self, text='КЛАСС', style='Heading.TLabel')
        # WIDGETS
        self.slots_combo = ttk.Combobox(self, values=list(self.slots.keys()))
        self.classes_combo = ttk.Combobox(self, values=list(map(lambda x: x[1], parent.tree.tree_names)))
        self.slots_combo.bind('<<ComboboxSelected>>', self.show_classes)
        # BUTTONS
        self.assign_slots_button = ttk.Button(
            self,
            text='СВЯЗАТЬ',
            command=self.assign_slots
        )
        # PLACING
        self.slots_combo.grid(row=1, column=0, padx=10)
        self.classes_combo.grid(row=1, column=1, padx=10)
        self.assign_slots_button.grid(row=1, column=2, padx=10)
        slots_label.grid(row=0, column=0, pady=5)
        classes_label.grid(row=0, column=1, pady=5)
        assigned_classes_label.grid(row=2, column=0, pady=30)
        # STYLING
        self.style = ttk.Style(parent)
        self.style.configure('Heading.TLabel', font=('Helvetica', 14))
        self.style.configure('TLabel', font=('Helvetica', 10))
        slots_label.configure(background=parent.background)
        classes_label.configure(background=parent.background)
        assigned_classes_label.configure(background=parent.background)

    def show_classes(self, event):
        for label in self.assigned_class_labels:
            label.grid_forget()
        self.assigned_class_labels.clear()
        tree = self.parent.tree
        tree.classes_with_slots = []
        slot = self.slots_combo.get()
        tree.visit(tree.root, slot=(slot, self.parent.slots[slot]), get_classes=True)
        classes = tree.classes_with_slots
        for i, c in enumerate(classes):
            label = ttk.Label(self, text=c, background=self.parent.background)
            label.grid(row=3 + i, column=0, sticky=tk.W, padx=(20, 0))
            self.assigned_class_labels.append(label)

    def assign_slots(self):
        tree = self.parent.tree
        root = tree.root

        slot = self.slots_combo.get()
        target_class = self.classes_combo.get()
        node = tree.find_node(root, target_class)
        tree.visit(node, slot=(slot, self.parent.slots[slot]))
        self.show_classes(event=None)


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


class PopupInstanceInfo(PopupWindow):
    def __init__(self, master_window, parent, header):
        super(PopupInstanceInfo, self).__init__(master_window, parent, header)
        self.top.geometry('400x200')
        self.parent = parent
        self.tree = self.parent.tree
        self.tree.ancestors = []
        self.ancestors_labels = []
        node = self.tree.find_node(self.tree.root, self.parent.instances_combobox.get())
        self.tree.find_ancestors(node)
        # FRAMES
        button_frame = tk.Frame(self.top)
        ancestors_frame = tk.Frame(self.top)
        info_frame = tk.Frame(self.top)
        # BUTTONS
        self.confirm_button = ttk.Button(
            button_frame,
            text='Закрыть',
            command=self.cleanup
        )
        # LABELS
        ancestor_label = tk.Label(ancestors_frame, text='ПРЕДКИ:')
        ancestor_label.grid(row=0, column=0, padx=10)
        for i, name in enumerate(self.tree.ancestors):
            label = ttk.Label(ancestors_frame, text=name)
            label.grid(row=0, column=i + 1, padx=3)

        slot_label = ttk.Label(info_frame, text='СЛОТ')
        value_label = ttk.Label(info_frame, text='ЗНАЧЕНИЕ')
        slot_label.grid(row=0, column=0, padx=30)
        value_label.grid(row=0, column=1, padx=30)

        for i, (slot_name, value) in enumerate(node.slots.items()):
            name = tk.Label(info_frame, text=slot_name)
            val = tk.Label(info_frame, text=value)
            name.grid(row=i + 1, column=0, padx=30)
            val.grid(row=i + 1, column=1, padx=30)

        # PLACING
        button_frame.pack(side='bottom')
        ancestors_frame.pack(side='bottom')
        info_frame.pack(pady=30)
        self.confirm_button.pack(side='bottom')

    def cleanup(self):
        self.top.destroy()


class PopupForInstances(PopupWindow):
    def __init__(self, master_window, parent, header):
        super(PopupForInstances, self).__init__(master_window, parent, header)
        self.top.geometry('400x200')
        self.parent = parent
        self.labels = []
        self.entries = []
        self.chosen_class = None

        # FRAMES
        classes_combobox_frame = tk.Frame(self.top)
        button_frame = tk.Frame(self.top)
        self.entries_frame = tk.Frame(self.top)
        # LABELS
        classes_label = ttk.Label(classes_combobox_frame, text='Выберите класс:')
        # COMBOBOXES
        self.classes_combobox = ttk.Combobox(
            classes_combobox_frame,
            values=list(map(lambda x: x[1], self.parent.tree.tree_names))
        )
        self.classes_combobox.bind('<<ComboboxSelected>>', self.create_entries)
        # ENTRIES

        # BUTTONS
        self.ok_button = ttk.Button(
            button_frame,
            text='Подтвердить',
            command=self.cleanup
        )
        # PLACING
        classes_combobox_frame.pack()
        classes_label.grid(row=0, column=0, padx=5, pady=10)
        self.classes_combobox.grid(row=0, column=1, padx=5, pady=10)
        self.entries_frame.pack()
        button_frame.pack(side=tk.BOTTOM)
        self.ok_button.pack()

    def create_entries(self, event):
        instance_name_label = ttk.Label(self.entries_frame, text='Имя сущности:')
        self.instance_name_entry = ttk.Entry(self.entries_frame)
        instance_name_label.grid(row=0, column=0, sticky=tk.W, padx=3, pady=5)
        self.instance_name_entry.grid(row=0, column=1)
        for entry, label in zip(self.entries, self.labels):
            entry.grid_forget()
            label.grid_forget()
        self.entries.clear()
        tree = self.parent.tree
        # get class from tree by name in instanceBar class_combobox
        self.chosen_class = tree.find_node(tree.root, self.classes_combobox.get())
        if self.chosen_class is None:
            return
        # create entries according to slots
        for i, slot_name in enumerate(self.chosen_class.slots.keys()):
            label = ttk.Label(self.entries_frame, text=f'{slot_name}:')
            entry = ttk.Entry(self.entries_frame, width=40)
            self.entries.append(entry)
            self.labels.append(label)
            label.grid(row=i + 1, column=0, padx=3, sticky=tk.W)
            entry.grid(row=i + 1, column=1, padx=3)

    def cleanup(self):
        instance = Node(parent=self.chosen_class, is_instance=True)
        instance.class_name = self.instance_name_entry.get()
        for i, (slot_name, value) in enumerate(self.chosen_class.slots.items()):
            instance.slots[slot_name] = (self.entries[i].get(), value)
        self.chosen_class.children.append(instance)
        print(instance.slots)
        self.top.destroy()


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
                                    text='Подтвердить',
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
            self.parent.parent.slots[name] = self.types.get()
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
                                             text='Новый слот',
                                             command=self.add_slot)
        # POSITION
        tool_bar.pack(side='top')
        self.create_slot_button.pack()

    def add_slot(self):
        self.w = PopupForSlots(self.main_window, self, header='НОВЫЙ СЛОТ')
        self.create_slot_button['state'] = 'disabled'
        self.main_window.wait_window(self.w.top)
        self.create_slot_button['state'] = 'normal'
        self.update_slots()

    def update_slots(self):
        for label in self.slot_labels:
            label.pack_forget()
        for i, (name, value) in enumerate(self.parent.slots.items()):
            label = ttk.Label(self, text=f'{name}:{value}', background=self.background, style='Heading.TLabel')
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
                'tree_bar': TreeBar(self, 'КЛАССЫ', background='#ABABAB'),
                'input_bar': InputBar(self, background=self.background),
            }
            self.widgets['tree_bar'].pack(side='left', fill='y')
            self.widgets['input_bar'].pack(anchor=tk.CENTER)
        elif self.mode == 'slots':
            self.widgets = {
                'slots_bar': SlotsBar(self, 'СЛОТЫ', background='#ABABAB'),
                'slots_configuration': ConfigureSlots(self, background=self.background)
            }
            self.widgets['slots_bar'].pack(side='left', fill='y', ipadx=25)
            self.widgets['slots_configuration'].pack()
        elif self.mode == 'instances':
            self.widgets = {
                'tree_bar': TreeBar(self, 'КЛАССЫ', background='#ABABAB'),
                'instance_bar': InstanceBar(self, 'СУЩНОСТИ', background='light grey')
            }
            self.widgets['tree_bar'].pack(side='left', fill='y')
            self.widgets['instance_bar'].pack(side='left', fill='y')
        elif self.mode == 'query':
            self.widgets = {
                'query_bar': QueryBar(self, background='light grey'),
                'find_bar': FindBar(self, 'РЕЗУЛЬТАТ ПОИСКА', background='#ABABAB', )
            }
            self.widgets['query_bar'].pack(side='left', fill='both', expand=True)
            self.widgets['find_bar'].pack(side='right', fill='y')
        elif self.mode == 'hierarchy':
            self.widgets = {
                'image': ImageBar(self, background=self.background)
            }
            self.widgets['image'].pack(expand=1)

    def add_node(self):
        parent = self.widgets['input_bar'].parent_entry.get()
        children = self.widgets['input_bar'].children_entry.get().split()
        print(children)
        self.tree.add_node(parent, children)
        self.widgets['tree_bar'].update_bar()


HEIGHT = 400
WIDTH = 900


def start():
    root = tk.Tk()
    root.geometry(f'{WIDTH}x{HEIGHT}')
    MainApplication(root, background='#BCBCBC').pack(side="top", fill="both", expand=True, )
    root.mainloop()
