import Tkinter as tk
from Tkinter import *
import tkFont

class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        #self.scale("all",0,0,wscale,hscale)

class ControlFrame(Frame):
	def __init__(self, parentObject):
		self.curri = 1
		self.maxi = 1
		
		Frame.__init__(self, parentObject)
		
		self.grid(row=1, column=0, sticky='nsew')
		self.columnconfigure(0, weight=1)
		
		self.l = Label(self, text=str(self.curri)+'/'+str(self.maxi))
		self.l.grid(row=0, column=0, sticky=tk.S+tk.N)
		
		self.bprev = Button(self, text='Previous', command=self.getPreviousDocument, width=10)
		self.bprev.grid(row=0, column=0, sticky='nsw')
		
		self.bnext = Button(self, text='Next', command=self.getNextDocument, width=10)
		self.bnext.grid(row=0, column=0, sticky='nse')
		
	def getPreviousDocument(self):
		if self.curri>1:
			self.curri -= 1
			self.l.configure(text=str(self.curri)+'/'+str(self.maxi))
			
	def getNextDocument(self):
		if self.curri<self.maxi:
			self.curri += 1
			self.l.configure(text=str(self.curri)+'/'+str(self.maxi))

			
			
			
			
			
			
class ScrollingFrame(Frame):
	def __init__(self, parentObject, background, p1s, p2s, alignments):
		self.p1s = p1s
		self.p2s = p2s
		self.alignments = alignments
		self.global_x_offset = 400
		self.global_y_offset = 50
		self.max_chars_per_line = 30
		self.offset_between_paragraphs = 20
		self.font_size = 16
		self.font = tkFont.Font(family='Helvetica', size=self.font_size, weight='bold')
		
		Frame.__init__(self, parentObject, background=background)
		
		self.grid(row=0, column=0, sticky=N+S+E+W)
		self.canvas = Canvas(self, borderwidth=0, background=background, highlightthickness=0)
		self.frame = Frame(self.canvas, background=background)

		self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview, background=background)
		self.canvas.configure(yscrollcommand=self.vsb.set)
		self.vsb.grid(row=0, column=1, sticky=N+S)

		#self.hsb = Scrollbar(self, orient="horizontal", command=self.canvas.xview, background=background)
		#self.canvas.configure(xscrollcommand=self.hsb.set)
		#self.hsb.grid(row=1, column=0, sticky=E+W)

		self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
		self.window = self.canvas.create_window(0,0, window=self.frame, anchor="nw", tags="self.frame")

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self.frame.bind("<Configure>", self.onFrameConfigure)
		
		self.drawc = ResizingCanvas(self.frame, bg="#FFFFFF", highlightthickness=0)
		self.drawc.pack(fill=BOTH, expand=YES)
		
		self.drawAlignments()

	def onFrameConfigure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
		
	def getAccumulatedOffsetsAndSizes(self, paragraphs):
		offsets = [0]
		sizes = []
		total = 0
		for i, p in enumerate(paragraphs):
			local_total = self.offset_between_paragraphs
			for j, s in enumerate(p):
				lines = len(s)/self.max_chars_per_line
				lines += 1
				local_total += self.font_size*lines
			sizes.append(local_total)
			total += local_total
			offsets.append(total)
		return offsets, sizes
		
	def drawAlignments(self):
		#Get offsets and sizes of each paragraph:
		offsets1, sizes1 = self.getAccumulatedOffsetsAndSizes(self.p1s)
		for i, p in enumerate(self.p1s):
			curroffset_y = self.global_y_offset+offsets1[i]
			for j, s in enumerate(p):
				lines = len(s)/self.max_chars_per_line
				lines += 1
				for k in range(0, lines):
					text = s[self.max_chars_per_line*k:self.max_chars_per_line*(k+1)]
					self.drawc.create_text(self.global_x_offset, curroffset_y, text=text, font=self.font, justify=tk.RIGHT, anchor=tk.E)
					curroffset_y += self.font_size
		
		#Get offsets and sizes of each paragraph:
		offsets2, sizes2 = self.getAccumulatedOffsetsAndSizes(self.p2s)
		for i, p in enumerate(self.p2s):
			curroffset_y = self.global_y_offset+offsets2[i]
			for j, s in enumerate(p):
				lines = len(s)/self.max_chars_per_line
				lines += 1
				for k in range(0, lines):
					text = s[self.max_chars_per_line*k:self.max_chars_per_line*(k+1)]
					self.drawc.create_text(1000-self.global_x_offset, curroffset_y, text=text, font=self.font, justify=tk.LEFT, anchor=tk.W)
					curroffset_y += self.font_size
					
		self.canvas.itemconfig(self.window, width=1000, height=self.global_y_offset+max(offsets1[-1],offsets2[-1]))
		
		#self.drawc.create_line(0, 0, 200, 100)
		#self.drawc.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
		#self.drawc.create_rectangle(50, 25, 150, 75, fill="blue")

root = Tk()
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.wm_title("Alignment Visualizer")
root.config(background='#FFFFFF')
root.geometry('1020x600')
root.resizable(False, True)

long = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbcccccccccccccccccccccccccccccccccc'
p1s = [[long, 'b', 'c'], ['d','e'], ['4', long], ['6', '7'], [long, 'b', 'c'], ['d','e'], ['4', long], ['6', '7'], [long, 'b', 'c'], ['d','e'], ['4', long], ['6', '7']]
p2s = [['a','b'], ['c'], ['d',long,'4','5']]
alignments = [[[0],[0,1]], [[1,2],[2]]]

canvasframe = ScrollingFrame(root, '#FFFFFF', p1s, p2s, alignments)

controlframe = ControlFrame(root)

#canvasframe.configure(width=400, height=9000)

root.mainloop()