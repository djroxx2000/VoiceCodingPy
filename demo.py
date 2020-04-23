import tkinter 
import os	 
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
	__thisLineNumberBar = Text(__root, width = 4, state = 'disabled', wrap='none')
	__thisTextArea = Text(__root) 
	__thisMenuBar = Menu(__root) 
	__thisFileMenu = Menu(__thisMenuBar, tearoff=0)
	__thisEditMenu = Menu(__thisMenuBar, tearoff=0)
	__thisHelpMenu = Menu(__thisMenuBar, tearoff=0)
	__thisCursorInfoBar = Label(__thisTextArea, text = "Line: 1 | Column: 1")

	__thisKeyWordList = ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'self']
	
	# To add scrollbar 
	__thisScrollBar = Scrollbar(__thisTextArea)
	__file = None

	#Voice Recognition Object
	voice = sr.Recognizer()


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
		top = (screenHeight / 2) - (self.__thisHeight /2) 
		
		# For top and bottom 
		self.__root.geometry('%dx%d+%d+%d' % (self.__thisWidth, self.__thisHeight, left, top)) 

		# To make the textarea auto resizable 
		self.__root.grid_rowconfigure(0, weight=1) 
		self.__root.grid_columnconfigure(0, weight=1) 

		# Add controls (widget) 
		self.__thisLineNumberBar.pack(side=LEFT,fill='y')
		self.__thisTextArea.pack(expand='yes', fill='both')

		# Equal font size for Text
		self.__thisTextArea.config(font=("Helvetica",32))
		self.__thisLineNumberBar.config(font=("Helvetica", 13))

		# Change editor element data
		self.__thisTextArea.bind('<Any-KeyPress>', self.on_content_changed)
		
		# To open new file 
		self.__thisFileMenu.add_command(label="New", command=self.__newFile)	 
		
		# To open a already existing file 
		self.__thisFileMenu.add_command(label="Open", command=self.__openFile) 
		
		# To save current file 
		self.__thisFileMenu.add_command(label="Save", command=self.__saveFile)	 

		# To create a line in the dialog		 
		self.__thisFileMenu.add_separator()										 
		self.__thisFileMenu.add_command(label="Exit", command=self.__quitApplication) 
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
	
		# To give a feature of selecting all text
		self.__thisEditMenu.add_command(label="Select All", command=self.__select_all)
		
		# To give a feature of editing 
		self.__thisMenuBar.add_cascade(label="Edit", menu=self.__thisEditMenu)	 
		
		# To create a feature of description of the notepad 
		self.__thisHelpMenu.add_command(label="About Notepad", command=self.__showAbout) 
		self.__thisMenuBar.add_cascade(label="Help", menu=self.__thisHelpMenu) 

		self.__root.config(menu=self.__thisMenuBar)

		self.__thisScrollBar.pack(side=RIGHT,fill=Y,anchor='e')
		self.__thisCursorInfoBar.pack(expand='no', fill='none', side='right', anchor='se')


		# Scrollbar will adjust automatically according to the content
		self.__thisScrollBar.config(command=self.multiple_yview)
		self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set)
		self.__thisLineNumberBar.config(yscrollcommand=self.__thisScrollBar.set)

        # Textarea Config: Current_line_background_color | Font_style
		self.__thisTextArea.tag_configure("current_line", background="#e9e9e9")
		self.__thisTextArea.configure(font=("Source Code Pro", 13), highlightbackground="#1e90ff", highlightcolor="#f4f4f4")

        # Highlight Current Line
		self._highlight()

        # Right Click Pop-Up Menu
		self.menu = Menu(self.__thisTextArea.master)
		self.menu.add_command(label="Copy", command=self.__copy)
		self.menu.add_command(label="Cut", command=self.__cut)
		self.menu.add_command(label="Paste", command=self.__paste)
		self.menu.add_command(label="Undo", command=self.__undo)
		self.menu.add_command(label="Redo", command=self.__redo)
		self.menu.add_command(label="Search", command=self.find_text)
		self.menu.add_command(label="Speak", command=self.voice_command)
		self.menu.add_separator()
		self.menu.add_command(label="Select All", command=self.__select_all)
		self.menu.add_separator()
		self.__thisTextArea.bind("<Button-3>",self.show_menu_)

		# Close Window
		self.__root.protocol("WM_DELETE_WINDOW", self.__quitApplication)
		

	def voice_command(self):
		try:
			with sr.Microphone() as source:
				self.voice.adjust_for_ambient_noise(source)
				stream = self.voice.listen(source)

				id_text = self.voice.recognize_google(stream)

				if id_text == "quit application":
					self.__quitApplication()
				self.insert_word(id_text)
		except sr.RequestError as e:
			print("Could not request results: {0}".format(e))

		except sr.UnknownValueError:
			print("I did not understand that")
			self.insert_word("I did not understand")

	def __quitApplication(self):
		answer = False
		if self.__root.title() == "Untitled - Notepad" and self.__thisTextArea.get(1.0, END) != "\n":
			answer = messagebox.askyesno("Warning","File not saved! Do you want to exit?")
		if answer == False and self.__thisTextArea.get(1.0, END) != "\n":
			self.__saveFile()
		if answer == True or self.__thisTextArea.get(1.0, END) == "\n":
			self.__root.destroy()

	def __showAbout(self):
		showinfo("Notepad","Created by: Karan Shah & Dhananjay Shettigar")

	def __openFile(self):
		self.__file = askopenfilename(defaultextension=".py", filetypes=[("Python Files","*.py")])
		if self.__file == "":
			# no file to open
			self.__file = None
		else:
			# Try to open the file
			# set the window title
			self.__root.title(os.path.basename(self.__file) + " - Notepad")
			self.__thisTextArea.delete(1.0,END)

			file = open(self.__file,"r")

			self.__thisTextArea.insert(1.0,file.read())

			file.close()


	def __newFile(self):
		self.__root.title("Untitled - Notepad")
		self.__file = None
		self.__thisTextArea.delete(1.0,END)

	def __saveFile(self):

		if self.__file == None:
			# Save as new file
			self.__file = asksaveasfilename(initialfile='demo.py', defaultextension=".py", filetypes=[("Python Files","*.py"), ("Python Files","*.py")])
			if self.__file == "": 
				self.__file = None
			else:
				# Try to save the file
				file = open(self.__file,"w")
				file.write(self.__thisTextArea.get(1.0,END))
				file.close()
				
				# Change the window title
				self.__root.title(os.path.basename(self.__file) + " - Notepad")
		else:
			file = open(self.__file,"w")
			file.write(self.__thisTextArea.get(1.0,END))
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
		self.__thisTextArea.tag_add("sel",'1.0','end')
		return

	def run(self):
		# Run main application
		self.__root.mainloop()

	def _highlight(self, interval=100):
		'''
			Updates the 'current line' highlighting every "interval" milliseconds
			Syntax Highlighting
		'''

		self.__thisTextArea.tag_config("highlightKeyword", foreground="orange")
		self.__thisTextArea.tag_remove("current_line", 1.0, "end")
		self.__thisTextArea.tag_add("current_line", "insert linestart", "insert lineend+1c")
		self.__thisTextArea.after(interval, self._highlight)

	def show_menu_(self, event):
		# Show Right Click Menu
  		self.menu.tk_popup(event.x, event.y)

	def get_line_numbers(self):
		output = ''
		row,col = self.__thisTextArea.index("end").split('.')
		for i in range(1,int(row)):
			output += str(i) + "\n"
		return output
	
	def update_line_numbers(self, event=None):
		line_numbers= self.get_line_numbers()
		self.__thisLineNumberBar.config(state='normal')
		self.__thisLineNumberBar.delete('1.0','end')
		self.__thisLineNumberBar.insert('1.0',line_numbers)
		self.__thisLineNumberBar.config(state='disabled')

	def update_cursor_info_bar(self, event=None):
		row, col = self.__thisTextArea.index(INSERT).split('.')
		line_num, col_num = str(int(row)), str(int(col) + 1)  # col starts at 0
		infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
		self.__thisCursorInfoBar.config(text=infotext)

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

		Label(__thisSearchWindow, text="Find All:").grid(row=0, column=0, sticky='e')

		search_entry_widget = Entry(__thisSearchWindow, width=25)
		search_entry_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
		search_entry_widget.focus_set()
		ignore_case_value = IntVar()
		Checkbutton(__thisSearchWindow, text='Ignore Case', variable=ignore_case_value).grid(row=1, column=1, sticky='e', padx=2, pady=2)

		Button(__thisSearchWindow, text="Find All", underline=0, 
		command = lambda: self.search_output(search_entry_widget.get(), 
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
		pos=self.__thisTextArea.index('insert')
		self.__thisTextArea.insert(pos,words)




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
notepad = Notepad(width=600,height=400)
notepad.run()