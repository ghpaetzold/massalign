from Tkinter import *
import tkFont, os
from abc import ABCMeta, abstractmethod

#Base class for GUI:
class GUI:

	__metaclass__ = ABCMeta

	@abstractmethod
	def displayParagraphAlignments(self):
		pass
		
	@abstractmethod
	def displaySentenceAlignments(self):
		pass

	@abstractmethod
	def displayListOfParagraphAlignments(self):
		pass
		
	@abstractmethod
	def displayListOfSentenceAlignments(self):
		pass
		
	@abstractmethod
	def displaySentenceAnnotations(self):
		pass

#Implements a basic GUI that displays paragraph and sentence alignments:
class BasicGUI(GUI):
	"""
	A basic GUI to showcase alignments and annotations.
	"""

	#Initializes object:
	def __init__(self):
		pass
	
	#Displays alignments between two sets of paragraphs:
	def displayParagraphAlignments(self, p1s, p2s, alignments):
		"""
		Displays alignments between two paragraphs.
		
		* *Parameters*:
			* **p1s**: A list of source paragraphs. A paragraph is a list of sentences.
			* **p2s**: A list of target paragraphs. A paragraph is a list of sentences.
			* **alignments**: An alignment path between the input paragraph lists.
		* *Output*:
			* Opens an interface showcasing aligned paragraphs.
		"""
		self.initializeRoot()
		self.main_frame = DisplayFrame(self.root, '#FFFFFF')
		self.main_frame.drawAlignments(p1s, p2s, alignments)
		self.root.mainloop()
	
	#Displays alignments between two paragraphs:
	def displaySentenceAlignments(self, p1, p2, alignments):
		"""
		Display sentence alignments between two paragraphs.
		
		* *Parameters*:
			* **p1**: A source paragraph. A paragraph is a list of sentences.
			* **p2**: A target paragraph. A paragraph is a list of sentences.
			* **alignments**: An alignment path between the input paragraphs.
		* *Output*:
			* Opens an interface showcasing sentence alignments for a paragraph pair.
		"""
		p1f = [[s] for s in p1]
		p2f = [[s] for s in p2]
		self.displayParagraphAlignments(p1f, p2f, alignments)
		
	#Displays alignments between various sets of paragraphs:
	def displayListOfParagraphAlignments(self, p1s_list, p2s_list, alignments_list):
		"""
		Displays alignments between lists of lists of paragraphs.
		Each list of paragraphs can represent a document, so this function allows you to see the paragraph alignments of an entire collection of documents through a single interface.
		
		* *Parameters*:
			* **p1s_list**: A source list of paragraph lists. A paragraph is a list of sentences.
			* **p2s_list**: A source list of paragraph lists. A paragraph is a list of sentences.
			* **alignments_list**: List of alignment paths between each pair of paragraph lists.
		* *Output*:
			* Opens an interface showcasing the aligned paragraphs for each pair of paragraph lists.
		"""
		self.initializeRoot()
		self.main_frame = DisplayFrame(self.root, '#FFFFFF')
		self.control_frame = ControlFrame(self.root, p1s_list, p2s_list, alignments_list, self.main_frame)
		self.root.mainloop()
	
	#Displays alignments between various sets of sentences:
	def displayListOfSentenceAlignments(self, p1_list, p2_list, alignments_list):
		"""
		Displays alignments between the sentences of each pair of paragraphs in a pair of paragraph lists.
		The interface will showcase the sentence-level alignments between each paragraph pair through a single interface.
		
		* *Parameters*:
			* **p1_list**: A source list of paragraphs. A paragraph is a list of sentences.
			* **p2_list**: A source list of paragraphs. A paragraph is a list of sentences.
			* **alignments_list**: List of alignment paths between each pair of paragraphs.
		* *Output*:
			* Opens an interface showcasing the aligned sentences for each pair of paragraphs.
		"""
		p1f_list = [[[s] for s in p1] for p1 in p1_list]
		p2f_list = [[[s] for s in p2] for p2 in p2_list]
		self.initializeRoot()
		self.main_frame = DisplayFrame(self.root, '#FFFFFF')
		self.control_frame = ControlFrame(self.root, p1f_list, p2f_list, alignments_list, self.main_frame)
		self.root.mainloop()
		
	#Displays annotations for a pair of sentences:
	def displaySentenceAnnotations(self, s1, s2, alignments, annotations):
		"""
		Displays word-level annotations for a pair of aligned sentences.
		
		* *Parameters*:
			* **s1**: A source sentence.
			* **s2**: A target sentence.
			* **alignments**: Word alignments in Pharaoh format.
			* **annotations**: Word-level annotations produced for the sentence pair.
		* *Output*:
			* Opens an interface showcasing the word-level annotations for the aligned sentences.
		"""
		self.initializeRoot()
		self.main_frame = DisplayFrame(self.root, '#FFFFFF')
		self.main_frame.drawAnnotations(s1, s2, alignments, annotations)
		self.root.mainloop()
	
	#Initializes root window of display:
	def initializeRoot(self):
		"""
		Initializes the GUI.
		"""
		self.root = Tk()
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)
		self.root.wm_title("Alignment Visualizer")
		self.root.config(background='#FFFFFF')
		self.root.geometry('1250x600+0+0')
		self.root.resizable(True, True)

#A canvas with dynamic size:
class ResizingCanvas(Canvas):
	"""
	A resizing canvas that allows for a GUI window to have a dynamic size.
	"""

	#Initializes object:
	def __init__(self,parent,**kwargs):
		Canvas.__init__(self,parent,**kwargs)
		self.bind("<Configure>", self.on_resize)
		self.height = self.winfo_reqheight()
		self.width = self.winfo_reqwidth()

	#Updates the size of canvas upon window resizing:
	def on_resize(self, event):
		"""
		Overrides the default resizing behaviour of Canvas objects.
		
		* *Parameters*:
			* **event**: A resizing event.
		"""
		wscale = float(event.width)/self.width
		hscale = float(event.height)/self.height
		self.width = event.width
		self.height = event.height
		self.config(width=self.width, height=self.height)

#A frame that handles multiple alignments:
class ControlFrame(Frame):
	"""
	A frame that allows for multiple alignments to be showcase at once through left/right navigation buttons.
	
	* *Parameters*:
		* **parentObject**: The parent frame.
		* **p1s_list**: A list of source paragraph lists. A paragraph is a list of sentences.
		* **p2s_list**: A list of target paragraph lists. A paragraph is a list of sentences.
		* **alignments_list**: A list containing the alignments for each pair of paragraph lists.
		* **main_frame**: The frame in which to draw the alignments.
	"""

	#Initializes object:
	def __init__(self, parentObject, p1s_list, p2s_list, alignments_list, main_frame):
		#Store parameters given:
		self.p1s_list = p1s_list
		self.p2s_list = p2s_list
		self.alignments_list = alignments_list
		self.main_frame = main_frame
		
		#Setup control variables:
		self.curri = 1
		self.maxi = len(p1s_list)
		
		#Setup frame:
		Frame.__init__(self, parentObject)
		self.grid(row=1, column=0, sticky='nsew')
		self.columnconfigure(0, weight=1)
		
		#Setup control label:
		self.l = Label(self, text=str(self.curri)+'/'+str(self.maxi))
		self.l.grid(row=0, column=0, sticky='ns')
		
		#Setup control buttons:
		self.bprev = Button(self, text='Previous', command=self.getPreviousAlignment, width=10)
		self.bprev.grid(row=0, column=0, sticky='nsw')
		self.bnext = Button(self, text='Next', command=self.getNextAlignment, width=10)
		self.bnext.grid(row=0, column=0, sticky='nse')
		
		#If there are instances available and they all have the same size, print the first one:
		if min(len(self.p1s_list),len(self.p2s_list),len(self.alignments_list))>0 and len(self.p1s_list)==len(self.p1s_list)==len(self.alignments_list):
			self.main_frame.drawAlignments(self.p1s_list[self.curri-1], self.p2s_list[self.curri-1], self.alignments_list[self.curri-1])
	
	#Decrements index label indicator:
	def getPreviousAlignment(self):
		"""
		Showcases the alignment between the previous pair of paragraph lists.
		"""
		#If there are instances available and they all have the same size, do:
		if min(len(self.p1s_list),len(self.p2s_list),len(self.alignments_list))>0 and len(self.p1s_list)==len(self.p1s_list)==len(self.alignments_list):
			#If there are any previous alignments, print them:
			if self.curri>1:
				self.main_frame.clearDrawingCanvas()
				self.curri -= 1
				self.l.configure(text=str(self.curri)+'/'+str(self.maxi))				
				self.main_frame.drawAlignments(self.p1s_list[self.curri-1], self.p2s_list[self.curri-1], self.alignments_list[self.curri-1])
	
	#Increments index label indicator:
	def getNextAlignment(self):
		"""
		Showcases the alignment between the next pair of paragraph lists.
		"""
		#If there are instances available and they all have the same size, do:
		if min(len(self.p1s_list),len(self.p2s_list),len(self.alignments_list))>0 and len(self.p1s_list)==len(self.p1s_list)==len(self.alignments_list):
			#If there are any next alignments, print them:
			if self.curri<self.maxi:
				self.main_frame.clearDrawingCanvas()
				self.curri += 1
				self.l.configure(text=str(self.curri)+'/'+str(self.maxi))
				self.main_frame.drawAlignments(self.p1s_list[self.curri-1], self.p2s_list[self.curri-1], self.alignments_list[self.curri-1])

#A frame that displays alignments:
class DisplayFrame(Frame):
	"""
	A frame in which to display alignments and annotations.
	
	* *Parameters*:
		* **parentObject**: The parent frame.
		* **background**: The background object.
	"""

	#Initializes object:
	def __init__(self, parentObject, background):
		#Setup visual environment variables:
		self.permanent_width = 1200
		self.global_x_offset = 500
		self.global_y_offset = 50
		self.max_chars_per_line = 70
		self.offset_between_paragraphs = 25
		self.separation_between_lines = 8
		self.font_size = 10
		self.marker_radius = 7
		self.alignment_line_width = 4
		self.word_rectangle_size = 60
		self.label_rectangle_size = 50
		self.font = tkFont.Font(family='Helvetica', size=self.font_size, weight='bold')
		
		#Create main frame:
		Frame.__init__(self, parentObject, background=background)
		self.grid(row=0, column=0, sticky=N+S+E+W)
		
		#Add underlying structure:
		self.canvas = Canvas(self, borderwidth=0, background=background, highlightthickness=0)
		self.frame = Frame(self.canvas, background=background)

		#Add vertical scrollbar:
		self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview, background=background)
		self.canvas.configure(yscrollcommand=self.vsb.set)
		self.vsb.grid(row=0, column=1, sticky=N+S)

		#self.hsb = Scrollbar(self, orient="horizontal", command=self.canvas.xview, background=background)
		#self.canvas.configure(xscrollcommand=self.hsb.set)
		#self.hsb.grid(row=1, column=0, sticky=E+W)

		#Setup underlying structure:
		self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
		self.window = self.canvas.create_window(0,0, window=self.frame, anchor="nw", tags="self.frame")
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		self.frame.bind("<Configure>", self.onFrameConfigure)
		
		#Create overlying drawing canvas:
		self.drawc = ResizingCanvas(self.frame, bg="#FFFFFF", highlightthickness=0)
		self.drawc.pack(fill=BOTH, expand=YES)
		
	#Clears the drawing canvas:
	def clearDrawingCanvas(self):
		"""
		Clears the drawing canvas.
		"""
		self.drawc.delete("all")

	#Restructures underlying canvas upon update of main frame:
	def onFrameConfigure(self, event):
		"""
		Restructures underlying canvas upon update of main frame.
		
		* *Parameters*:
			* **event**: A frame configure event.
		"""
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
		
	#Split lines for display:
	def getLineSplits(self, sentence):
		"""
		Split lines for display.
		
		* *Parameters*:
			* **sentence**: A sentence to split.
		* *Output*:
			* **lines**: A list of fragments of the input sentence.
		"""
		tokens = sentence.split(' ')
		lines = []
		i = 0
		line = ''
		while i<len(tokens):
			while i<len(tokens) and len(line+' '+tokens[i])<self.max_chars_per_line:
				line += ' '+tokens[i]
				i += 1
			lines.append(line)
			line = ''
		if len(lines[-1].strip())==1 and len(lines)>1:
			last = lines[-1]
			lines.remove(last)
			second_last = lines[-1]
			lines.remove(second_last)
			lines.append(second_last.strip()+' '+last)
		return lines
	
	#Gets offsets and sizes of all subsequent paragraphs:
	def getAccumulatedOffsetsAndSizes(self, paragraphs):
		"""
		Gets offsets and sizes for a list of paragraphs.
		
		* *Parameters*:
			* **paragraphs**: A list of paragraphs. A paragraph is a list of sentences.
		* *Output*:
			* **offsets**: The total accumulated vertical offset of each paragraph in the input list.
			* **sizes**: The individual vertical size of each paragraph in the input list.
		"""
		#Create resulting structures:
		offsets = [0]
		sizes = []
		
		#Calculate size of each sentence of each paragraph:
		total = 0
		for i, p in enumerate(paragraphs):
			local_total = self.offset_between_paragraphs
			for j, s in enumerate(p):
				lines = len(s)/self.max_chars_per_line
				lines += 1
				local_total += self.font_size*lines+self.separation_between_lines*lines
				
			#Add it to resulting structures:
			sizes.append(local_total)
			total += local_total
			offsets.append(total)
			
		#Return resulting structures:
		return offsets, sizes
	
	#Draws the alignments:
	def drawAlignments(self, p1s, p2s, alignments):
		"""
		Draws a set of alignments between two paragraph lists.
		
		* *Parameters*:
			* **p1s**: A list of source paragraphs. A paragraph is a list of sentences.
			* **p2s**: A list of target paragraphs. A paragraph is a list of sentences.
		* *Output*:
			* Opens an interface showcasing the alignments between the input paragraph lists.
		"""
		#Store input parameters:
		self.p1s = p1s
		self.p2s = p2s
		self.alignments = alignments
		
		#Get offsets and sizes of each paragraph:
		offsets1, sizes1 = self.getAccumulatedOffsetsAndSizes(self.p1s)
		for i, p in enumerate(self.p1s):
			#Control offset:
			curroffset_y = self.global_y_offset+offsets1[i]
			initial_y_offset = curroffset_y
			#For each paragraph do:
			for j, s in enumerate(p):
				#Determine how many lines it will take to represent the sentence:
				lines = self.getLineSplits(s)
				n_lines = len(lines)
				#For each line, print it and update the offset:
				for k in range(0, n_lines):
					text = lines[k]
					text_widget = self.drawc.create_text(self.global_x_offset, curroffset_y, text=text, font=self.font, justify='r', anchor='ne')
					curroffset_y += self.font_size+self.separation_between_lines
				#Print a rectangle around the sentence:
				recx0 = 10
				recx1 = self.global_x_offset+4
				recy0 = curroffset_y-n_lines*self.font_size-n_lines*self.separation_between_lines-self.separation_between_lines/2+4
				recy1 = curroffset_y-self.separation_between_lines/2+4
				self.drawc.create_rectangle(recx0, recy0, recx1, recy1, outline='black', width=1)
			#Print a rectangle around the paragraph:
			recx0 = 9
			recx1 = self.global_x_offset+4+2
			recy0 = initial_y_offset-self.separation_between_lines/2+4-1
			recy1 = curroffset_y-self.separation_between_lines/2+4+2
			self.drawc.create_rectangle(recx0, recy0, recx1, recy1, outline='black', width=3)
		
		#Get offsets and sizes of each paragraph:
		offsets2, sizes2 = self.getAccumulatedOffsetsAndSizes(self.p2s)
		for i, p in enumerate(self.p2s):
			#Control offset:
			curroffset_y = self.global_y_offset+offsets2[i]
			initial_y_offset = curroffset_y
			#For each paragraph do:
			for j, s in enumerate(p):
				#Determine how many lines it will take to represent the sentence:
				lines = self.getLineSplits(s)
				n_lines = len(lines)
				#For each line, print it and update the offset:
				for k in range(0, n_lines):
					text = lines[k]
					self.drawc.create_text(self.permanent_width-self.global_x_offset, curroffset_y, text=text, font=self.font, justify='l', anchor='nw')
					curroffset_y += self.font_size+self.separation_between_lines
				#Print a rectangle around the sentence:
				recx0 = self.permanent_width-self.global_x_offset-4
				recx1 = self.permanent_width-10
				recy0 = curroffset_y-n_lines*self.font_size-n_lines*self.separation_between_lines-self.separation_between_lines/2+4
				recy1 = curroffset_y-self.separation_between_lines/2+4
				self.drawc.create_rectangle(recx0, recy0, recx1, recy1, outline='black', width=1)
			#Print a rectangle around the paragraph:
			recx0 = self.permanent_width-self.global_x_offset-5
			recx1 = self.permanent_width-10+1
			recy0 = initial_y_offset-self.separation_between_lines/2+4-1
			recy1 = curroffset_y-self.separation_between_lines/2+4+2
			self.drawc.create_rectangle(recx0, recy0, recx1, recy1, outline='black', width=3)
		
		#Print each alignment available:
		for a in self.alignments:
			#Get aligned paragraph indexes:
			indexes1 = a[0]
			indexes2 = a[1]
			#For each pair of aligned indexes do:
			for i1 in indexes1:
				for i2 in indexes2:
					#Get appropriate coordinates and draw the line:
					linex0 = self.global_x_offset+4+2
					liney0 = self.global_y_offset+offsets1[i1]+((sizes1[i1]-self.separation_between_lines-self.offset_between_paragraphs)/2)
					linex1 = self.permanent_width-self.global_x_offset-4
					liney1 = self.global_y_offset+offsets2[i2]+((sizes2[i2]-self.separation_between_lines-self.offset_between_paragraphs)/2)
					self.drawc.create_line(linex0+self.marker_radius, liney0, linex1-self.marker_radius, liney1, fill="red", width=self.alignment_line_width)
					self.drawc.create_oval(linex0, liney0-self.marker_radius, linex0+2*self.marker_radius, liney0+self.marker_radius, fill='green')
					self.drawc.create_oval(linex1-2*self.marker_radius-1, liney1-self.marker_radius, linex1-1, liney1+self.marker_radius, fill='green')
		
		#Set canvas to the appropriate size:
		self.canvas.itemconfig(self.window, width=self.permanent_width, height=self.global_y_offset+max(offsets1[-1],offsets2[-1])+5)
		
	#Draws the annotations:
	def drawAnnotations(self, s1, s2, word_alignments, annotations):
		"""
		Draws a set of word-level annotations between two parallel sentences.
		
		* *Parameters*:
			* **s1**: A source sentence.
			* **s2**: A target sentence.
			* **word_alignments**: Word alignments in Pharaoh format.
			* **annotations**: Word-level annotations produced for the sentence pair.
		* *Output*:
			* Opens an interface showcasing the word-level annotations for the aligned sentences.
		"""
		#Store input parameters:
		self.s1 = [[w] for w in s1.strip().split(' ')]
		self.s2 = [[w] for w in s2.strip().split(' ')]
		self.word_alignments = self.formatWordAlignments(word_alignments)
		self.annotations = annotations
		
		#Reconfigure drawing canvas:
		self.offset_between_paragraphs = 0
		self.marker_radius = 5
		
		#Get offsets and sizes of each paragraph:
		offsets1, sizes1 = self.getAccumulatedOffsetsAndSizes(self.s1)
		for i, p in enumerate(self.s1):
			#Control offset:
			curroffset_y = self.global_y_offset+offsets1[i]
			initial_y_offset = curroffset_y
			#For each paragraph do:
			for j, s in enumerate(p):
				#Determine how many lines it will take to represent the sentence:
				lines = self.getLineSplits(s)
				n_lines = len(lines)
				#For each line, print it and update the offset:
				for k in range(0, n_lines):
					text = lines[k]
					text_widget = self.drawc.create_text(self.global_x_offset, curroffset_y, text=text, font=self.font, justify='r', anchor='ne')
					curroffset_y += self.font_size+self.separation_between_lines
				#Print a rectangle around the sentence:
				recx0 = self.global_x_offset-self.word_rectangle_size
				recx1 = self.global_x_offset+4
				recy0 = curroffset_y-n_lines*self.font_size-n_lines*self.separation_between_lines-self.separation_between_lines/2+4
				recy1 = curroffset_y-self.separation_between_lines/2+4
				self.drawc.create_rectangle(recx0, recy0, recx1, recy1, outline='black', width=1)
		
		#Get offsets and sizes of each paragraph:
		offsets2, sizes2 = self.getAccumulatedOffsetsAndSizes(self.s2)
		for i, p in enumerate(self.s2):
			#Control offset:
			curroffset_y = self.global_y_offset+offsets2[i]
			initial_y_offset = curroffset_y
			#For each paragraph do:
			for j, s in enumerate(p):
				#Determine how many lines it will take to represent the sentence:
				lines = self.getLineSplits(s)
				n_lines = len(lines)
				#For each line, print it and update the offset:
				for k in range(0, n_lines):
					text = lines[k]
					self.drawc.create_text(self.permanent_width-self.global_x_offset, curroffset_y, text=text, font=self.font, justify='l', anchor='nw')
					curroffset_y += self.font_size+self.separation_between_lines
				#Print a rectangle around the sentence:
				recx0 = self.permanent_width-self.global_x_offset-4
				recx1 = self.permanent_width-self.global_x_offset-4+self.word_rectangle_size
				recy0 = curroffset_y-n_lines*self.font_size-n_lines*self.separation_between_lines-self.separation_between_lines/2+4
				recy1 = curroffset_y-self.separation_between_lines/2+4
				self.drawc.create_rectangle(recx0, recy0, recx1, recy1, outline='black', width=1)
		
		#Print each alignment available:
		for a in self.word_alignments:
			#Get aligned paragraph indexes:
			indexes1 = a[0]
			indexes2 = a[1]
			#For each pair of aligned indexes do:
			for i1 in indexes1:
				for i2 in indexes2:
					#Get appropriate coordinates and draw the line:
					linex0 = self.global_x_offset+4
					liney0 = self.global_y_offset+offsets1[i1]+((sizes1[i1]-self.separation_between_lines-self.offset_between_paragraphs)/2)+4
					linex1 = self.permanent_width-self.global_x_offset-4
					liney1 = self.global_y_offset+offsets2[i2]+((sizes2[i2]-self.separation_between_lines-self.offset_between_paragraphs)/2)+4
					self.drawc.create_line(linex0+self.marker_radius, liney0, linex1-self.marker_radius, liney1, fill="red", width=self.alignment_line_width)
					self.drawc.create_oval(linex0, liney0-self.marker_radius, linex0+2*self.marker_radius, liney0+self.marker_radius, fill='green')
					self.drawc.create_oval(linex1-2*self.marker_radius-1, liney1-self.marker_radius, linex1-1, liney1+self.marker_radius, fill='green')
					
		#Print each source annotation available:
		for a in self.annotations['src']:
			#Get data:
			index = a['index']-1
			label = a['label']
			
			#Get appropriate coordinates and draw the line:
			recx0 = self.global_x_offset-self.word_rectangle_size-self.label_rectangle_size
			recx1 = self.global_x_offset-self.word_rectangle_size
			recy0 = self.global_y_offset+offsets1[index]-self.separation_between_lines/2+4
			recy1 = self.global_y_offset+offsets1[index]+self.font_size+self.separation_between_lines/2+4
			self.drawc.create_rectangle(recx0, recy0, recx1, recy1, outline='black', width=1)
			self.drawc.create_text(self.global_x_offset-self.word_rectangle_size-self.label_rectangle_size/2, self.global_y_offset+offsets1[index]+self.font_size/2+self.separation_between_lines/2, text=label, font=self.font, justify='center', anchor='center')
		
		#Print each source annotation available:
		for a in self.annotations['ref']:
			#Get data:
			index = a['index']-1
			label = a['label']
			
			#Get appropriate coordinates and draw the line:
			recx0 = self.permanent_width-self.global_x_offset-4+self.word_rectangle_size
			recx1 = self.permanent_width-self.global_x_offset-4+self.word_rectangle_size+self.label_rectangle_size
			recy0 = self.global_y_offset+offsets1[index]-self.separation_between_lines/2+4
			recy1 = self.global_y_offset+offsets1[index]+self.font_size+self.separation_between_lines/2+4
			self.drawc.create_rectangle(recx0, recy0, recx1, recy1, outline='black', width=1)
			self.drawc.create_text(self.permanent_width-self.global_x_offset-4+self.word_rectangle_size+self.label_rectangle_size/2, self.global_y_offset+offsets1[index]+self.font_size/2+self.separation_between_lines/2, text=label, font=self.font, justify='center', anchor='center')
		
		#Set canvas to the appropriate size:
		self.canvas.itemconfig(self.window, width=self.permanent_width, height=self.global_y_offset+max(offsets1[-1],offsets2[-1])+5)
		

	#Provides with word alignments in list form:
	def formatWordAlignments(self, word_alignments):
		"""
		Transforms Pharaoh alignments in text format onto a list of alignments.
		
		* *Parameters*:
			* **word_alignments**: A sentence containing the alignments in Pharaoh format.
		* *Output*:
			* **alignment_list**: A list of alignments in Pharaoh format.
		"""
		if isinstance(word_alignments, basestring):
			alignment_list = [[[int(v)-1] for v in w.split('-')] for w in word_alignments.strip().split(' ')]
			return alignment_list
		else:
			return word_alignments