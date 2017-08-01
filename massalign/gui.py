from Tkinter import *
import tkFont
from abc import ABCMeta, abstractmethod

#Base class for GUI:
class GUI:

	__metaclass__ = ABCMeta

	@abstractmethod
	def displayParagraphAlignment(self):
		pass
		
	@abstractmethod
	def displaySentenceAlignment(self):
		pass

#Implements a basic GUI that displays paragraph and sentence alignments:
class BasicGUI(GUI):

	#Initializes object:
	def __init__(self):
		self.root = Tk()
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)
		self.root.wm_title("Alignment Visualizer")
		self.root.config(background='#FFFFFF')
		self.root.geometry('1250x600')
		self.root.resizable(False, True)
	
	#Displays alignments between two sets of paragraphs:
	def displayParagraphAlignment(self, p1s, p2s, alignments):
		self.frame = AlignmentDisplayFrame(self.root, '#FFFFFF', p1s, p2s, alignments)
		self.frame.drawAlignments()
		self.root.mainloop()
	
	#Displays alignments between two paragraphs:
	def displaySentenceAlignment(self, p1, p2, alignments):
		p1f = [[s] for s in p1]
		p2f = [[s] for s in p2]
		print p1f, '-', p2f
		self.displayParagraphAlignment(p1f, p2f, alignments)

#A canvas with dynamic size:
class ResizingCanvas(Canvas):

	#Initializes object:
	def __init__(self,parent,**kwargs):
		Canvas.__init__(self,parent,**kwargs)
		self.bind("<Configure>", self.on_resize)
		self.height = self.winfo_reqheight()
		self.width = self.winfo_reqwidth()

	#Updates the size of canvas upon window resizing:
	def on_resize(self,event):
		wscale = float(event.width)/self.width
		hscale = float(event.height)/self.height
		self.width = event.width
		self.height = event.height
		self.config(width=self.width, height=self.height)

#A frame that handles multiple alignments:
class ControlFrame(Frame):

	#Initializes object:
	def __init__(self, parentObject):
		self.curri = 1
		self.maxi = 1
		
		Frame.__init__(self, parentObject)
		
		self.grid(row=1, column=0, sticky='nsew')
		self.columnconfigure(0, weight=1)
		
		self.l = Label(self, text=str(self.curri)+'/'+str(self.maxi))
		self.l.grid(row=0, column=0, sticky='ns')
		
		self.bprev = Button(self, text='Previous', command=self.getPreviousDocument, width=10)
		self.bprev.grid(row=0, column=0, sticky='nsw')
		
		self.bnext = Button(self, text='Next', command=self.getNextDocument, width=10)
		self.bnext.grid(row=0, column=0, sticky='nse')
	
	#Decrements index label indicator:
	def getPreviousDocument(self):
		if self.curri>1:
			self.curri -= 1
			self.l.configure(text=str(self.curri)+'/'+str(self.maxi))
	
	#Increments index label indicator:
	def getNextDocument(self):
		if self.curri<self.maxi:
			self.curri += 1
			self.l.configure(text=str(self.curri)+'/'+str(self.maxi))

#A frame that displays alignments:
class AlignmentDisplayFrame(Frame):

	#Initializes object:
	def __init__(self, parentObject, background, p1s, p2s, alignments):
		#Store input parameters:
		self.p1s = p1s
		self.p2s = p2s
		self.alignments = alignments
		
		#Setup visual environment variables:
		self.permanent_width = 1200
		self.global_x_offset = 500
		self.global_y_offset = 50
		self.max_chars_per_line = 30
		self.offset_between_paragraphs = 25
		self.separation_between_lines = 8
		self.font_size = 10
		self.marker_radius = 7
		self.alignment_line_width = 4
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

	#Restructures underlying canvas upon update of main frame:
	def onFrameConfigure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
	
	#Gets offsets and sizes of all subsequent paragraphs:
	def getAccumulatedOffsetsAndSizes(self, paragraphs):
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
	def drawAlignments(self):
		#Get offsets and sizes of each paragraph:
		offsets1, sizes1 = self.getAccumulatedOffsetsAndSizes(self.p1s)
		for i, p in enumerate(self.p1s):
			#Control offset:
			curroffset_y = self.global_y_offset+offsets1[i]
			initial_y_offset = curroffset_y
			#For each paragraph do:
			for j, s in enumerate(p):
				#Determine how many lines it will take to represent the sentence:
				lines = len(s)/self.max_chars_per_line
				lines += 1
				#For each line, print it and update the offset:
				for k in range(0, lines):
					text = s[self.max_chars_per_line*k:self.max_chars_per_line*(k+1)]
					text_widget = self.drawc.create_text(self.global_x_offset, curroffset_y, text=text, font=self.font, justify='r', anchor='ne')
					curroffset_y += self.font_size+self.separation_between_lines
				#Print a rectangle around the sentence:
				recx0 = 10
				recx1 = self.global_x_offset+4
				recy0 = curroffset_y-lines*self.font_size-lines*self.separation_between_lines-self.separation_between_lines/2+4
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
				lines = len(s)/self.max_chars_per_line
				lines += 1
				#For each line, print it and update the offset:
				for k in range(0, lines):
					text = s[self.max_chars_per_line*k:self.max_chars_per_line*(k+1)]
					self.drawc.create_text(self.permanent_width-self.global_x_offset, curroffset_y, text=text, font=self.font, justify='l', anchor='nw')
					curroffset_y += self.font_size+self.separation_between_lines
				#Print a rectangle around the sentence:
				recx0 = self.permanent_width-self.global_x_offset-4
				recx1 = self.permanent_width-10
				recy0 = curroffset_y-lines*self.font_size-lines*self.separation_between_lines-self.separation_between_lines/2+4
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
					self.drawc.create_line(linex0, liney0, linex1, liney1, fill="red", width=self.alignment_line_width)
					self.drawc.create_oval(linex0, liney0-self.marker_radius, linex0+2*self.marker_radius, liney0+self.marker_radius, fill='green')
					self.drawc.create_oval(linex1-2*self.marker_radius-1, liney1-self.marker_radius, linex1-1, liney1+self.marker_radius, fill='green')
		
		#Set canvas to the appropriate size:
		self.canvas.itemconfig(self.window, width=self.permanent_width, height=self.global_y_offset+max(offsets1[-1],offsets2[-1]))

long = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbcccccccccccccccccccccccccccccccccc'
p1s = [[long, 'b', 'c'], ['d'], ['4', long], ['6', '7'], [long, 'b', 'c'], ['d','e'], ['4', long], ['6', '7'], [long, 'b', 'c'], ['d','e'], ['4', long], ['6', '7']]
p2s = [['a','b'], ['c'], ['d',long,'4','5']]
alignments = [[[0],[0,1]], [[1,2],[2]]]

bg = BasicGUI()
bg.displayParagraphAlignment(p1s, p2s, alignments)

p1 = p1s[0]
p2 = p2s[2]
alignments = [[[0],[3]], [[2],[1]]]

bg = BasicGUI()
bg.displaySentenceAlignment(p1, p2, alignments)