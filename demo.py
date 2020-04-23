import tkinter 
import os	 
from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import *
from tkinter.filedialog import *

class Notepad():
	__root = Tk() 

	# default window width and height 
	__thisWidth = 300
	__thisHeight = 300
	__thisTextArea = Text(__root) 
	__thisMenuBar = Menu(__root) 
	__thisFileMenu = Menu(__thisMenuBar, tearoff=0)
	__thisEditMenu = Menu(__thisMenuBar, tearoff=0)
	__thisHelpMenu = Menu(__thisMenuBar, tearoff=0)

	__thisKeyWordList = ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'self']
	
	# To add scrollbar 
	__thisScrollBar = Scrollbar(__thisTextArea)
	__file = None

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
		self.__thisTextArea.grid(sticky = N + E + S + W) 
		
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

		self.__thisScrollBar.pack(side=RIGHT,fill=Y)

		# Scrollbar will adjust automatically according to the content
		self.__thisScrollBar.config(command=self.__thisTextArea.yview)
		self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set)

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
		self.menu.add_separator()
		self.menu.add_command(label="Select All", command=self.__select_all)
		self.menu.add_separator()
		self.__thisTextArea.bind("<Button-3>",self.show_menu_)

		# Close Window
		self.__root.protocol("WM_DELETE_WINDOW", self.__quitApplication)

	def __quitApplication(self):
		answer = False
		if self.__root.title() == "Untitled - Notepad" and self.__thisTextArea.get(1.0, END) != "\n":
			answer = messagebox.askyesno("Warning","File not saved! Do you want to exit?")
		if answer == True or self.__thisTextArea.get(1.0, END) == "\n":
			self.__root.destroy()

	def __showAbout(self):
		showinfo("Notepad","Created by: Karan Shah & Dhanajay Shettigar")

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


# Run main application
notepad = Notepad(width=600,height=400)
notepad.run()