import threading
import os
import sys
import time

import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import *
from tkinter.filedialog import *

import speech_recognition as sr


class Notepad():
    __root = Tk()

    # default window width and height
    __thisWidth = 300
    __thisHeight = 300
    __thisLineNumberBar = Text(
        __root, width=4, state='disabled', wrap='none', cursor='arrow')
    __thisTextArea = Text(__root, undo=True)
    __thisMenuBar = Menu(__root)
    __thisFileMenu = Menu(__thisMenuBar, tearoff=0)
    __thisEditMenu = Menu(__thisMenuBar, tearoff=0)
    __thisHelpMenu = Menu(__thisMenuBar, tearoff=0)
    __thisCursorInfoBar = Label(__thisTextArea, text="Line: 1 | Column: 1")
    __thisVoiceInfoBar = Label(__thisTextArea, text="Voice: Deactivated ")
    __thisVarDictLabel = Label(__thisTextArea)

    __thisKeyWordList = ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
                         'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'self']

    __thisIndentKeyWordList = ['if', 'elif', 'else', 'def',
                               'class', 'try', 'except', 'while', 'for', 'finally', 'with']

    # To add scrollbar
    __thisScrollBar = Scrollbar(__thisTextArea)
    __file = None

    # Store Variables as dictionary for easily spoken names
    __thisVariableList = {}

    # Toggle Variable Dictionary Label
    __thisVarDictShow = BooleanVar()
    __thisVarDictShow.set(False)

    # Voice Recognition Object
    voice = sr.Recognizer()
    voice_activate = BooleanVar()

    # Voice Recognition Toggle
    voice_activate.set(False)

    def __init__(self, **kwargs):
        # Open Maximized
        self.__root.state('zoomed')
        # Set icon
        try:
            self.__root.wm_iconbitmap("notepad.ico")
        except:
            pass

        # Set window size (the default is 300x300)

        try:
            self.__thisWidth = kwargs['width']
        except KeyError:
            pass

        try:
            self.__thisHeight = kwargs['height']
        except KeyError:
            pass

        # Set the window text
        self.__root.title("Untitled - Notepad")

        # Center the window
        screenWidth = self.__root.winfo_screenwidth()
        screenHeight = self.__root.winfo_screenheight()

        # For left-alling
        left = (screenWidth / 2) - (self.__thisWidth / 2)

        # For right-allign
        top = (screenHeight / 2) - (self.__thisHeight / 2)

        # For top and bottom
        self.__root.geometry('%dx%d+%d+%d' %
                             (self.__thisWidth, self.__thisHeight, left, top))

        # To make the textarea auto resizable
        self.__root.grid_rowconfigure(0, weight=1)
        self.__root.grid_columnconfigure(0, weight=1)

        # Add controls (widget)
        self.__thisLineNumberBar.pack(side=LEFT, fill='y')
        self.__thisTextArea.pack(expand='yes', fill='both')

        # Equal font size for Text
        self.__thisTextArea.config(font=("Helvetica", 32))
        self.__thisLineNumberBar.config(font=("Helvetica", 13))

        # Change editor element data
        self.__thisTextArea.bind('<Any-KeyPress>', self.on_content_changed)
        self.__thisTextArea.bind('<space>', self.highlight_keywords)
        self.__thisTextArea.bind('<Return>', self.highlight_keywords)

        # To open new file
        self.__thisFileMenu.add_command(label="New", command=self.__newFile)

        # To open a already existing file
        self.__thisFileMenu.add_command(label="Open", command=self.__openFile)

        # To save current file
        self.__thisFileMenu.add_command(label="Save", command=self.__saveFile)

        # To create a line in the dialog
        self.__thisFileMenu.add_separator()
        self.__thisFileMenu.add_command(
            label="Exit", command=self.__quitApplication)
        self.__thisMenuBar.add_cascade(label="File", menu=self.__thisFileMenu)

        # To give a feature of cut
        self.__thisEditMenu.add_command(label="Cut", command=self.__cut)

        # to give a feature of copy
        self.__thisEditMenu.add_command(label="Copy", command=self.__copy)

        # To give a feature of paste
        self.__thisEditMenu.add_command(label="Paste", command=self.__paste)

        # To give a feature of undo
        self.__thisEditMenu.add_command(label="Undo", command=self.__undo)

        # To give a feature of redo
        self.__thisEditMenu.add_command(label="Redo", command=self.__redo)

        # To give a feature of text search
        self.__thisEditMenu.add_command(label="Search", command=self.find_text)

        # To give feature of adding to voice friendly variable dictionary
        self.__thisEditMenu.add_command(
            label="Add Variable", command=self.var_dict_add)

        # To Show the current variables in dictionary
        self.__thisEditMenu.add_checkbutton(label="Show Variables", onvalue=1, offvalue=0,
                                            variable=self.__thisVarDictShow, command=self.var_dict_label_toggle)

        # To give a feature of selecting all text
        self.__thisEditMenu.add_command(
            label="Select All", command=self.__select_all)

        # To give a feature of editing
        self.__thisMenuBar.add_cascade(label="Edit", menu=self.__thisEditMenu)

        # To create a feature of description of the notepad
        self.__thisHelpMenu.add_command(
            label="About Notepad", command=self.__showAbout)
        self.__thisMenuBar.add_cascade(label="Help", menu=self.__thisHelpMenu)

        self.__root.config(menu=self.__thisMenuBar)

        self.__thisScrollBar.pack(side=RIGHT, fill=Y, anchor='e')
        self.__thisCursorInfoBar.pack(
            expand='no', fill='none', anchor='se', side=BOTTOM)
        self.__thisVoiceInfoBar.pack(
            expand='no', fill='none', anchor='se', side=BOTTOM)

        # Scrollbar will adjust automatically according to the content
        self.__thisScrollBar.config(command=self.multiple_yview)
        self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set)
        self.__thisLineNumberBar.config(
            yscrollcommand=self.__thisScrollBar.set)

        # Textarea Config: Current_line_background_color | Font_style
        self.__thisTextArea.tag_configure("current_line", background="#e9e9e9")
        self.__thisTextArea.configure(font=(
            "Source Code Pro", 13), highlightbackground="#1e90ff", highlightcolor="#f4f4f4")

        # Highlight Current Line
        self._highlight()

        # Text Area Theme
        self.__thisTextArea.config(fg="#FFFFFF", background="#1F1B24")
        self.__thisLineNumberBar.config(fg="#FFFFFF", background="#121212")

        # Right Click Pop-Up Menu
        self.menu = Menu(self.__thisTextArea.master)
        self.menu.add_command(label="Copy", command=self.__copy)
        self.menu.add_command(label="Cut", command=self.__cut)
        self.menu.add_command(label="Paste", command=self.__paste)
        self.menu.add_command(label="Undo", command=self.__undo)
        self.menu.add_command(label="Redo", command=self.__redo)
        self.menu.add_checkbutton(
            label="Activate Voice", onvalue=1, offvalue=0, variable=self.voice_activate, command=self.voice_toggle)
        self.menu.add_separator()
        self.menu.add_command(label="Select All", command=self.__select_all)
        self.menu.add_separator()
        self.__thisTextArea.bind("<Button-3>", self.show_menu_)

        # Close Window
        self.__root.protocol("WM_DELETE_WINDOW", self.__quitApplication)

    # Command to turn mic on for input
    def voice_command(self):
        def callback():
            current_tabs = 0
            while True:
                if self.voice_activate.get():
                    try:
                        self.__thisVoiceInfoBar.config(text="Voice: Active")
                        with sr.Microphone() as source:
                            self.voice.adjust_for_ambient_noise(source)
                            stream = self.voice.listen(source)

                            id_text = self.voice.recognize_google(stream)
                            split_text = id_text.split()
                            output_words = None

                            if id_text == "quit application":
                                self.__quitApplication()
                            elif "type" in split_text:
                                self.__thisVoiceInfoBar.config(
                                    text="Voice: Parsing Input")
                                split_text.remove("type")
                                output_words, current_tabs = self.parse_voice_input(
                                    split_text, current_tabs)
                            elif "command" in split_text:
                                self.__thisVoiceInfoBar.config(
                                    text="Voice: Parsing Command")
                                split_text.remove("command")
                                self.parse_voice_command(split_text)
                                continue

                            else:
                                continue

                            if output_words:
                                self.insert_word(output_words)
                            for i in range(current_tabs):
                                self.insert_word("\t")
                            self.on_content_changed()
                            self.__thisVoiceInfoBar.config(
                                text="Voice: Active(Waiting)")

                    except sr.RequestError as e:
                        print("Could not request results: {0}".format(e))

                    except sr.UnknownValueError:
                        print("I did not understand that")
                        self.__thisVoiceInfoBar.config(
                            text="Voice: Failed to understand")
                        time.sleep(1)
                else:
                    time.sleep(1)

        voice_thread = threading.Thread(target=callback)
        voice_thread.setDaemon(True)
        voice_thread.start()

    def parse_voice_input(self, words, current_tabs):
        words_parsed = 0
        output_words = []
        i = 0
        while i < len(words):
            # Keywords forming indent blocks
            words[i] = words[i].lower()

            if words[i] in self.__thisIndentKeyWordList:
                output_words.extend([words[i], ":"])
                current_tabs += 1

            # Leaving an indent block
            elif words[i] == "exit":
                if current_tabs > 0:
                    current_tabs -= 1

            # ToDo: Form variable dictionaries(type wanted variable name, assign to a number and translate every time)
            elif words[i] == "variable":
                var_in = words[i+1].lower()
                if var_in in self.__thisVariableList:
                    var_in = self.__thisVariableList[var_in]
                output_words.insert(words_parsed, var_in)
                i += 1

            elif words[i] == "equals" or words[i] == "=":
                output_words.insert(words_parsed, '==')

            elif words[i] == "equal" or words[i] == "assign":
                output_words.insert(words_parsed, '=')

            elif words[i] == "plus":
                output_words.insert(words_parsed, '+')

            elif words[i] == "minus" or words[i] == "subtract":
                output_words.insert(words_parsed, '-')

            elif words[i] == "multiply" or words[i] == "multiple":
                output_words.insert(words_parsed, '*')

            elif words[i] == "divide" or words[i] == "division":
                output_words.insert(words_parsed, '/')

            elif words[i] == "define":
                output_words.extend(['def', "():"])
                current_tabs += 1

            elif words[i] in ["true", "false", "none"]:
                output_words.insert(words_parsed, words[i].capitalize())

            # Commonly recognized word errors
            elif words[i].lower() == "falls":
                output_words.insert(words_parsed, 'False')

            elif words[i].lower() == "lf" or words[i].lower() == "ls":
                output_words.insert(words_parsed, 'elif')

            # All other words
            else:
                output_words.insert(words_parsed, words[i])

            i += 1
            words_parsed += 1
        output_words.append("\n")
        output = ' '.join(output_words)
        return output, current_tabs

    def parse_voice_command(self, words):
        i = 0
        if words[i] == "move":
            line = 0
            column = 0
            if i+2 < len(words):
                if words[i+1] == "line":
                    line = words[i+2]
                    i += 2

            if i+2 < len(words):
                if words[i+1] == "column":
                    column = words[i+2]

            pos = str(line) + "." + str(column)
            self.__thisTextArea.mark_set('index', pos)

        elif words[i] == "select":
            line = 0
            if i+2 < len(words):
                if words[i+1] == "line":
                    line = words[i+2]
                    i += 2
            if line == 0:
                self.__thisTextArea.tag_add('sel', 1.0, END)

            else:
                pos = str(line) + ".0"
                end = str(line) + ".end"
                self.__thisTextArea.tag_add('sel', pos, end)

        elif words[i] == "undo":
            self.__undo()

        elif words[i] == "redo":
            self.__redo()

        elif words[i] == "cut":
            self.__cut()

        elif words[i] == "copy":
            self.__copy()

        elif words[i] == "paste":
            self.__paste()

        elif words[i] == "save":
            self.__saveFile()

        else:
            self.__thisVoiceInfoBar.config(text="Voice: Command Failed")
            time.sleep(1)
            return

    def voice_toggle(self):
        if self.voice_activate.get():
            self.__thisVoiceInfoBar.config(text="Voice: Active")
        else:
            self.__thisVoiceInfoBar.config(text="Voice: Deactivated")

    def __quitApplication(self):
        self.stop_voice = True
        answer = False
        if self.__root.title() == "Untitled - Notepad" and self.__thisTextArea.get(1.0, END) != "\n":
            answer = messagebox.askyesno(
                "Warning", "File not saved! Do you want to exit?")
        if answer == False and self.__thisTextArea.get(1.0, END) != "\n":
            self.__saveFile()
        if answer == True or self.__thisTextArea.get(1.0, END) == "\n":
            self.__root.destroy()
        sys.exit()

    def __showAbout(self):
        showinfo("Notepad", "Created by: Karan Shah & Dhananjay Shettigar")

    def __openFile(self):
        self.__file = askopenfilename(defaultextension=".py", filetypes=[
            ("Python Files", "*.py")])
        if self.__file == "":
            # no file to open
            self.__file = None
        else:
            # Try to open the file
            # set the window title
            self.__root.title(os.path.basename(self.__file) + " - Notepad")
            self.__thisTextArea.delete(1.0, END)

            file = open(self.__file, "r")

            self.__thisTextArea.insert(1.0, file.read())

            file.close()

    def __newFile(self):
        self.__root.title("Untitled - Notepad")
        self.__file = None
        self.__thisTextArea.delete(1.0, END)

    def __saveFile(self):

        if self.__file == None:
            # Save as new file
            self.__file = asksaveasfilename(initialfile='demo.py',
                                            defaultextension=".py",
                                            filetypes=[("Python Files", "*.py"), ("Python Files", "*.py")])
            if self.__file == "":
                self.__file = None
            else:
                # Try to save the file
                file = open(self.__file, "w")
                file.write(self.__thisTextArea.get(1.0, END))
                file.close()

                # Change the window title
                self.__root.title(os.path.basename(self.__file) + " - Notepad")
        else:
            file = open(self.__file, "w")
            file.write(self.__thisTextArea.get(1.0, END))
            file.close()

    def __cut(self):
        self.__thisTextArea.event_generate("<<Cut>>")

    def __copy(self):
        self.__thisTextArea.event_generate("<<Copy>>")

    def __paste(self):
        self.__thisTextArea.event_generate("<<Paste>>")

    def __undo(self):
        self.__thisTextArea.event_generate("<<Undo>>")

    def __redo(self):
        self.__thisTextArea.event_generate("<<Redo>>")

    def __select_all(self):
        self.__thisTextArea.tag_add("sel", '1.0', 'end')
        return

    def run(self):
        # Run main application
        self.voice_command()
        self.__root.mainloop()

    def _highlight(self, interval=100):
        '''
                Updates the 'current line' highlighting every "interval" milliseconds
                Syntax Highlighting
        '''

        self.__thisTextArea.tag_config(
            "current_line", foreground="#000000", background="#a4a4a4")
        self.__thisTextArea.tag_remove("current_line", 1.0, "end")
        self.__thisTextArea.tag_add(
            "current_line", "insert linestart", "insert lineend+1c")
        self.__thisTextArea.after(interval, self._highlight)

    def show_menu_(self, event):
        # Show Right Click Menu
        self.menu.tk_popup(event.x, event.y)

    def get_line_numbers(self):
        output = ''
        row, col = self.__thisTextArea.index("end").split('.')
        for i in range(1, int(row)):
            output += str(i) + "\n"
        return output

    def update_line_numbers(self, event=None):
        line_numbers = self.get_line_numbers()
        self.__thisLineNumberBar.config(state='normal')
        self.__thisLineNumberBar.delete('1.0', 'end')
        self.__thisLineNumberBar.insert('1.0', line_numbers)
        self.__thisLineNumberBar.config(state='disabled')

    def update_cursor_info_bar(self, event=None):
        row, col = self.__thisTextArea.index(INSERT).split('.')
        line_num, col_num = str(int(row)), str(int(col) + 1)  # col starts at 0
        infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
        self.__thisCursorInfoBar.config(text=infotext)

    def highlight_keywords(self, event=None):
        pos_insert = self.__thisTextArea.index(INSERT)
        row, col = pos_insert.split('.')
        if pos_insert == END:
            row -= 1
        row_str = str(row)
        start_pos = row_str + ".0"
        positions = []

        while True:
            start_pos = self.__thisTextArea.search(
                " ", start_pos, stopindex=END, nocase=False)
            if not start_pos:
                break
            start_pos += "+1c"
            positions.append(start_pos)

        pos_len = len(positions)
        if pos_len != 0:
            start_pos = positions[pos_len-1]
        else:
            start_pos = row_str + ".0"
        last_word = self.__thisTextArea.get(start_pos, "end-1c")
        if last_word in self.__thisKeyWordList:
            self.__thisTextArea.tag_add('keyword', start_pos, "end-1c")
            self.__thisTextArea.tag_config('keyword', foreground='purple')

    def on_content_changed(self, event=None):
        self.update_line_numbers()
        self.update_cursor_info_bar()

    def multiple_yview(self, *args):
        self.__thisTextArea.yview(*args)
        self.__thisLineNumberBar.yview(*args)

    # search window
    def find_text(self, event=None):
        __thisSearchWindow = Toplevel(self.__root)
        __thisSearchWindow.title('Find Text')
        __thisSearchWindow.transient(self.__root)

        Label(__thisSearchWindow, text="Find All:").grid(
            row=0, column=0, sticky='e')

        search_entry_widget = Entry(__thisSearchWindow, width=25)
        search_entry_widget.grid(
            row=0, column=1, padx=2, pady=2, sticky='we')
        search_entry_widget.focus_set()
        ignore_case_value = IntVar()
        Checkbutton(__thisSearchWindow, text='Ignore Case', variable=ignore_case_value).grid(
            row=1, column=1, sticky='e', padx=2, pady=2)

        Button(__thisSearchWindow, text="Find All", underline=0,
               command=lambda: self.search_output(search_entry_widget.get(),
                                                  ignore_case_value.get(),
                                                  self.__thisTextArea,
                                                  __thisSearchWindow,
                                                  search_entry_widget)).grid(row=0, column=2, sticky='e' + 'w', padx=2, pady=2)

        def close_search_window():
            self.__thisTextArea.tag_remove('match', '1.0', END)
            __thisSearchWindow.destroy()
        __thisSearchWindow.protocol('WM_DELETE_WINDOW', close_search_window)
        return "break"

    def search_output(self, search_key, if_ignore_case, content_text,
                      search_toplevel, search_box):
        content_text.tag_remove('match', '1.0', END)
        matches_found = 0
        positions = []
        if search_key:
            start_pos = '1.0'
            while True:
                start_pos = content_text.search(search_key, start_pos,
                                                nocase=if_ignore_case, stopindex=END)
                if not start_pos:
                    break
                end_pos = '{}+{}c'.format(start_pos, len(search_key))
                positions.append(start_pos)
                content_text.tag_add('match', start_pos, end_pos)
                matches_found += 1
                start_pos = end_pos
            content_text.tag_config(
                'match', foreground='red', background='yellow')
        self.__thisTextArea.mark_set("insert", positions[0] + '+3c')
        self.__thisTextArea.focus_set()

        search_toplevel.title('{} matches found'.format(matches_found))

    def insert_word(self, words):
        pos = self.__thisTextArea.index('insert')
        self.__thisTextArea.insert(pos, words)

    def var_dict_add(self, event=None):
        __thisVarAddWindow = Toplevel(self.__root)
        __thisVarAddWindow.title('Variable Dictionary')
        __thisVarAddWindow.transient(self.__root)

        Label(__thisVarAddWindow, text="Add Voice Friendly Variable Pairs: ").grid(
            row=0, column=0, sticky='w')

        Label(__thisVarAddWindow, text="Voice Variable (As spoken): ").grid(
            row=1, column=0, sticky='w')
        voice_var_entry_widget = Entry(__thisVarAddWindow, width=25)
        voice_var_entry_widget.grid(
            row=2, column=0, padx=2, pady=2, sticky='we')

        Label(__thisVarAddWindow, text="Text Variable (In editor): ").grid(
            row=3, column=0, sticky='w')
        text_var_entry_widget = Entry(__thisVarAddWindow, width=25)
        text_var_entry_widget.grid(
            row=4, column=0, padx=2, pady=2, sticky='we')

        voice_var_entry_widget.focus_set()

        Button(__thisVarAddWindow, text="Add new variable pair", underline=0,
               command=lambda: add_variable()).grid(
                   row=5, column=0, sticky='e' + 'w', padx=2, pady=2)

        def add_variable():
            voice_var = voice_var_entry_widget.get()
            text_var = text_var_entry_widget.get()
            self.__thisVariableList.update({voice_var.lower(): text_var})
            voice_var_entry_widget.delete(0, END)
            text_var_entry_widget.delete(0, END)
            voice_var_entry_widget.focus_set()
            self.var_dict_label_toggle()

    def var_dict_label_toggle(self):
        if self.__thisVarDictShow.get():
            label_text = ["Voice : Text"]
            for voice_var, text_var in self.__thisVariableList.items():
                label_text.append("{} : {}".format(voice_var, text_var))
            label_text_joined = '\n'.join(label_text)
            self.__thisVarDictLabel.config(text=label_text_joined)
            self.__thisVarDictLabel.pack(
                expand='no', fill='none', side=TOP, anchor='ne')
        else:
            self.__thisVarDictLabel.pack_forget()

# class VoiceRecognition(Notepad):
# 	voice = sr.Recognizer()

# 	while 1:
# 		try:
# 			with sr.Microphone() as source:
# 				voice.adjust_for_ambient_noise(source)
# 				stream = voice.listen(source)

# 				id_text = voice.recognize_google(stream)

# 				if id_text == "end session":
# 					break
# 		except sr.RequestError as e:
# 			print("Could not request results: {0}".format(e))

# 		except sr.UnknownValueError:
# 			print("I did not understand that")
# 			# voice_label("I did not understand that")
# Run main application


notepad = Notepad(width=600, height=400)
notepad.run()
