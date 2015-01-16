from Tkinter import *
import tkMessageBox
import tkSimpleDialog
from eventBasedAnimationClassNew import EventBasedAnimationClass
import pygame, copy, random, time, math
import pygame.midi
import pygame.key
pygame.init()
pygame.mixer.init()
pygame.midi.init()
player=pygame.midi.Output(0)

class MusicBook(EventBasedAnimationClass):
    def __init__(self):
        super(MusicBook, self).__init__(width=800, height=800) 
        self.root = Tk()
        self.pageIndex=0
        self.timerDelay=5
        self.book=[]
        first_sheet=SheetMusic(self.root, len(self.book)) 
        self.book.append(first_sheet) 
        self.sheet_on_display=first_sheet
        self.max_sheets=10 
        self.musicPlaying=False
        self.counter=0
        self.counterHere=0
        self.startMode=True

    def nextSheet(self):
        # to switch to next sheet
        if self.pageIndex<(len(self.book)-1):
            self.pageIndex+=1
        return(self.book[self.pageIndex])
    
    def previousSheet(self):
        # to switch to previous sheet
        if self.pageIndex>0:
            self.pageIndex-=1
        return(self.book[self.pageIndex])
    
    def choose(self, message, title):
        response= tkSimpleDialog.askstring(title, message)
        return response  

    def start(self):
        # making custom title for sheet music 
        message="Enter a title for your project"
        title="Title"
        self.response=self.choose(message, title)
    
    def onTimerFired(self):
        if self.musicPlaying:
            self.sheet_on_display.playing=True
            if self.sheet_on_display.pageDonePlaying==True:
                if self.book.index(self.sheet_on_display)==len(self.book)-1:
                    for sheet in self.book:
                        sheet.pageDonePlaying=False
                    self.musicPlaying=False
                else:
                    self.sheet_on_display.canvas.pack_forget()
                    self.sheet_on_display=self.nextSheet()
                    self.sheet_on_display.canvas.pack()
        self.sheet_on_display.onTimerFired()

    def onKeyPressed(self, event):
        if event.keysym=="p":
            # to play all pages 
            self.sheet_on_display.pageDonePlaying=False
            self.sheet_on_display.canvas.pack_forget()
            self.sheet_on_display=self.book[0]
            self.sheet_on_display.canvas.pack()
            self.pageIndex=0
            self.musicPlaying=True
            self.sheet_on_display.pageDonePlaying=False
            for sheet in self.book:
                for clef in sheet.clefs:
                    clef.playing=True
        else:
            self.sheet_on_display.onKeyPressed(event)

    def onMousePressed(self, event):
        if event.x>=730 and event.x<=795 and event.y>=650 and event.y<=680:
            # clicked on next sheet button
            self.sheet_on_display.canvas.pack_forget()
            self.sheet_on_display=self.nextSheet()
            self.sheet_on_display.canvas.pack()
        if event.x>=680 and event.x<=710 and event.y>=650 and event.y<=680:
            # clicked on previous sheet button
            self.sheet_on_display.pageDonePlaying=True
            self.musicPlaying=False
            self.sheet_on_display.canvas.pack_forget()
            self.sheet_on_display=self.previousSheet()
            self.sheet_on_display.canvas.pack()
        if event.x>=720 and event.x<=780 and event.y>=20 and event.y<=80:
            # clicked on new sheet button 
            newSheet=SheetMusic(self.root, len(self.book))
            newSheet.title, newSheet.startScreen= self.response, False
            newSheet.keySigChosen=self.sheet_on_display.keySigChosen
            self.book.append(newSheet)
            self.sheet_on_display.canvas.pack_forget()
            self.sheet_on_display=self.nextSheet()
            self.sheet_on_display.canvas.pack()
        self.sheet_on_display.onMousePressed(event)

    def redrawAll(self):
        self.sheet_on_display.redrawAll()
        self.counterHere+=1
        if self.startMode and self.counterHere==2:
            self.start()
            self.sheet_on_display.title=self.response
            self.startMode=False

    def onMouseMotion(self,event):
        self.sheet_on_display.onMouseMotion(event)

class SheetMusic(object):
    def __init__(self, rootwindow, pagenumber, width=800, height=800):
        self.width, self.height=width, height
        self.canvas=Canvas(rootwindow, width=self.width, height=self.height)
        self.canvas.pack()
        self.pagenumber=pagenumber
        self.title="Fun With Music"
        self.keySigChosen="C"
        self.key_signatures=["C", "G", "D", "A", "E", "B", "FSharp",
                        "CSharp", "F", "BFlat", "EFlat", "AFlat",
                        "DFlat", "GFlat", "CFlat"]
        self.clefs=[]
        self.rootwindow=rootwindow
        self.clefs.append(Clef("treble", len(self.clefs)))
        self.clefs.append(Clef("bass", len(self.clefs)))
        self.clefs.append(Clef("treble", len(self.clefs)))
        self.clefs.append(Clef("bass", len(self.clefs)))
        self.noteLevel=2
        self.accidentalLevel=2
        self.restLevel=0
        self.eventx, self.eventy=0, 0
        self.startEventX, self.startEventY=0, 0
        self.start_clickedX, self.start_clickedY=0, 0
        self.measures=1 
        self.lineHeight, self.lineMargin, self.measuresPerLine=80, 20, 4
        self.widthLines=(self.width-2*self.lineMargin)/self.measuresPerLine
        self.heightLines=self.lineHeight/4
        self.heightFromTop=(self.width/2)/self.measures-self.width/4
        self.thirdLine=2*self.heightLines+self.heightFromTop
        self.numRows=4
        self.noteHeight, self.noteWidth= 7, 11 
        self.sharpMode=False
        self.flatMode=False
        self.dotMode=False
        self.quarterNoteMode=False
        self.halfNoteMode, self.eighthNoteMode=False, False
        self.quarterRestMode, self.eighthRestMode=False, False
        self.playing=False
        self.clickedPause=False
        self.mouseOverPause=False
        self.mouseOverC=False
        self.stop=False
        self.pageDonePlaying=False
        self.noteIndexClicked, self.chordIndexClicked=-1, -1
        self.clefIndexClicked, self.accidentalIndexClicked=-1, -1
        self.chordIndex=0
        self.noteIndex=0
        self.startScreen=True
        self.helpScreen=False
        self.new=True
        self.initAnimation()
        
    def initAnimation(self):
        self.background=PhotoImage(file="background5.gif")
        self.menubackground=PhotoImage(file="keysignatures.gif")
        self.newPageIcon=PhotoImage(file="newPageIcon.gif")

    def onTimerFired(self):
        if self.playing:
            stillPlaying=self.playClefs(self.clefs[:2])
            if stillPlaying==False:
                nowPlaying=self.playClefs(self.clefs[2:])
                if nowPlaying==False:
                    self.pageDonePlaying, self.playing=True, False
                
    def playClefs(self, clefs):
        # plays treble and bass clefs together
        # plays pairs of clefs consecutively
        for clef in clefs:
            if clef.playing:
                self.quarterNoteMode, self.halfNoteMode=False, False
                self.eighthNoteMode=False
                self.quarterRestMode, self.eighthRestMode=False, False
                self.sharpMode, self.flatMode=False, False
                clef.play()
            elif clef.chords!=[]:
                chord=clef.chords[clef.chordIndex]
                for note in chord.notes:
                    player.note_off(note.sound, 127)
                    note.playedDuration=0
                    if self.stop:
                        note.sweepingBar=0
                        clef.chordIndex=0
                if self.stop:
                    clef.chordIndex=0
                if clefs.index(clef)==1 and clefs[0].playing==False:
                    return False
        self.stop=False

                        
    def chordCheck(self, cx, clefPosition):
        for i in xrange(len(self.clefs[clefPosition].chords)):
            # checks if clicked in chord
            if cx==self.clefs[clefPosition].chords[i].cx:
                return i
        else: return -1

                        
    def onMouseMotion(self, event):
        self.startEventX, self.startEventY=event.x, event.y
        self.mouseX, self.mouseY=event.x, event.y
        self.eventx, self.eventy=event.x, event.y
        if (event.x>=100 and event.x<=130
            and event.y>=50 and event.y<=80
            and self.clickedPause!=True):
            self.mouseOverPause=True
        else:
            self.mouseOverPause=False
        if not (self.sharpMode or self.flatMode or self.dotMode):
            self.xPosition(event)

    def xPosition(self, event):
        # determines position of note
        # autocorrects note based on time signature :)
        self.eventx=event.x
        total=0.0
        width=self.widthLines/8.0
        clefType, clefTop, clefPosition=self.clickedInStaff(event.y)
        if clefType!=False:
            clef=self.clefs[clefPosition]
            if len(clef.chords)==0:
                self.eventx=width
                return self.eventx
            for chord in clef.chords:
                chordDuration=chord.notes[0].hold
                total+=chordDuration
                if clef.chords.index(chord)==len(clef.chords)-1:
                    lastNote=chord.notes[0]
            total=float(total)
            perMeasure=float(1.2)
            column=int(round(total/perMeasure, 4))
            fraction=(total-column*perMeasure)/perMeasure
            left=column*self.widthLines+self.lineMargin
            x=(column+1)*perMeasure-total
            if (self.eighthNoteMode or
                self.quarterNoteMode or
                self.quarterRestMode or
                self.halfNoteMode or self.eighthRestMode):
                self.eventx=left+fraction*self.widthLines+0.5*width
            if (self.halfNoteMode and (x<0.599)
            and (event.x>lastNote.cx+width) or (event.x<lastNote.cx-width)):
                self.halfNoteMode, self.quarterRestMode=False, True
            if (self.quarterNoteMode
                and (((column+1)*perMeasure-total)<0.299)
                and (event.x>lastNote.cx+width or event.x<lastNote.cx-width)):
                self.quarterNoteMode, self.eighthRestMode=False, True
            if event.x<=lastNote.cx+0.5*width:
                for chord in clef.chords:
                    note=chord.notes[0]
                    if event.x<=(note.cx+0.5*width) and event.x>=(note.cx-0.5*width):
                        if self.eighthNoteMode and note.typeNote=="eighth":
                            self.eventx=note.cx
                        elif self.quarterNoteMode and note.typeNote=="quarter":
                            self.eventx=note.cx
                        elif self.halfNoteMode and note.typeNote=="half":
                            self.eventx=note.cx
        return self.eventx

    def onMousePressed(self, event):
        cx, cy= event.x, event.y
        self.start_clickedX, self.start_clickedY=event.x, event.y
        clefType, clefTop, clefPosition=self.clickedInStaff(cy)
        if clefType!=False:
            heightFromTop=clefTop
            for row in xrange(self.numRows):
                top=row*self.heightLines+heightFromTop
                bottom=(row+1)*self.heightLines+heightFromTop
                aboveStaff=top-self.heightLines
                belowStaff=bottom+self.heightLines
                if cy>=(top-self.noteHeight) and cy<=(top+self.noteHeight):
                    cy=top
                elif ((row==0
                      and cy>=(aboveStaff+self.noteHeight)
                      and cy<=top-self.noteHeight)): cy=top-((top-aboveStaff)/2)
                elif cy>=(top+self.noteHeight) and cy<=(bottom-self.noteHeight):
                     cy=bottom-(bottom-top)/2
                elif (row ==3 and cy>=(bottom-self.noteHeight)
                    and cy<=(bottom+self.noteHeight)):
                    cy=bottom
                elif ((row==3 and cy<=(belowStaff-self.noteHeight)
                       and cy>=(bottom+self.noteHeight))):
                      cy=bottom+((belowStaff-bottom)/2)
            if not (self.sharpMode or self.flatMode or self.dotMode):
                cx=self.xPosition(event)
            if self.quarterNoteMode==True:
                note=Note("quarter", cx, cy, clefType, clefTop)
            elif self.halfNoteMode==True:
                note=Note("half", cx, cy, clefType, clefTop)
            elif self.eighthNoteMode==True:
                note=Note("eighth", cx, cy, clefType, clefTop)
            elif self.sharpMode==True:
                accidental=Accidental("sharp", cx, cy)
            elif self.flatMode==True:
                accidental=Accidental("flat", cx, cy)
            elif self.quarterRestMode==True:
                note=Note("quarter rest", cx, cy, clefType, clefTop)
            elif self.eighthRestMode==True:
                note=Note("eighth rest", cx, cy, clefType, clefTop)
            elif self.dotMode==True:
                accidental=Accidental("dot", cx, cy)
            if (self.quarterNoteMode or self.halfNoteMode
                or self.eighthNoteMode or self.quarterRestMode
                or self.eighthRestMode):
                note.keysig(self.clefs[clefPosition])
                i=self.chordCheck(cx, clefPosition)
                if i!=-1:
                    self.clefs[clefPosition].chords[i].notes.append(note)
                else:
                    self.clefs[clefPosition].chords.append(Chord(cx))
                    self.clefs[clefPosition].chords[-1].notes.append(note)
            elif self.sharpMode or self.flatMode or self.dotMode:
                accidental.findNotes(self.clefs[clefPosition])
                self.clefs[clefPosition].accidentals.append(accidental)
        self.clickedInNote(event)

    

    # determine if user clicked in note or button
    def clickedInNote(self, event):
        sharpWidth=3
        noteWidth=3
        for c in xrange(len(self.clefs)):
            clef=self.clefs[c]
            for z in xrange(len(clef.chords)):
                chord=clef.chords[z]
                for i in xrange(len(chord.notes)):
                    note=chord.notes[i]
                    if (event.x>(note.cx-noteWidth) and event.x<(note.cx+noteWidth)
                        and event.y>(note.cy-noteWidth)
                        and event.y<(note.cy+noteWidth)):
                        self.clefIndexClicked=c
                        self.chordIndexClicked=z
                        self.noteIndexClicked=i
            for z in xrange(len(clef.accidentals)):
                accidental=clef.accidentals[z]
                if (event.x>(accidental.cx-sharpWidth) and event.x<(accidental.cx+sharpWidth)
                    and event.y>(accidental.cy-sharpWidth)
                    and event.y<(accidental.cy+sharpWidth)):
                        self.clefIndexClicked=c
                        self.accidentalIndexClicked=z
        # play button
        if event.x>=50 and event.x<=80 and event.y>=50 and event.y<=80:
            self.playing=True
            for clef in self.clefs:
                clef.sortNotes()
                clef.playing=True
            self.clickedPause=False
            self.stop=False
        # pause button
        if event.x>=100 and event.x<=130 and event.y>=50 and event.y<=80:
            for clef in self.clefs:
                if clef.playing==True:
                    clef.playing=False
                    self.clickedPause=True
                    self.stop=False
        # stop button
        if event.x>=150 and event.x<=180 and event.y>=50 and event.y<=80:
            for clef in self.clefs:
                clef.playing=False
                self.clickedPause=False
                self.stop=True

    def clickedInStaff(self, cy):
        # checks if clicked in staff
        for clef in self.clefs:
            top=clef.heightFromTop-self.heightLines/2
            bottom=4*clef.heightLines+clef.heightFromTop+self.heightLines/2
            if cy>=top and cy<=bottom:
                return clef.type, clef.heightFromTop, clef.position
        return False, False, False
        

    def onKeyPressed(self, event):
        if event.keysym=="Up":
            # to change type of note, rest, or accidental
            if self.quarterNoteMode or self.halfNoteMode or self.eighthNoteMode:
                self.noteLevel+=1
                if self.noteLevel%3==0:
                    self.halfNoteMode, self.quarterNoteMode=False, False
                    self.eighthNoteMode=True
                elif self.noteLevel%3==1:
                    self.halfNoteMode, self.quarterNoteMode=True, False
                    self.eighthNoteMode=False
                elif self.noteLevel%3==2:
                    self.eighthNoteMode=False
                    self.halfNoteMode, self.quarterNoteMode=False, True
            elif self.sharpMode or self.flatMode or self.dotMode:
                self.accidentalLevel+=1
                if self.accidentalLevel%3==0:
                    self.sharpMode, self.dotMode=False, False
                    self.flatMode=True
                elif self.accidentalLevel%3==1:
                    self.dotMode, self.flatMode=True, False
                    self.sharpMode=False
                elif self.accidentalLevel%3==2:
                    self.flatMode=False
                    self.dotMode, self.sharpMode=False, True
            elif self.quarterRestMode or self.eighthRestMode:
                self.restLevel+=1
                if self.restLevel%2==0:
                    self.eighthRestMode,self.quarterRestMode=False, True
                else: self.eighthRestMode, self.quarterRestMode=True, False
        elif event.keysym=="r":
            # to reset page 
            self.clefs=[]
            self.clefs.append(Clef("treble", len(self.clefs)))
            self.clefs.append(Clef("bass", len(self.clefs)))
            self.clefs.append(Clef("treble", len(self.clefs)))
            self.clefs.append(Clef("bass", len(self.clefs)))
            self.noteLevel=2
            self.accidentalLevel=2
            self.restLevel=0
            self.eventx, self.eventy=0, 0
            self.startEventX, self.startEventY=0, 0
            self.start_clickedX, self.start_clickedY=0, 0
            self.sharpMode=False
            self.flatMode=False
            self.dotMode=False
            self.quarterNoteMode=False
            self.halfNoteMode, self.eighthNoteMode=False, False
            self.quarterRestMode, self.eighthRestMode=False, False
            self.playing=False
            self.clickedPause=False
            self.mouseOverPause=False
            self.mouseOverC=False
            self.stop=False
            self.pageDonePlaying=False
            self.noteIndexClicked, self.chordIndexClicked=-1, -1
            self.clefIndexClicked, self.accidentalIndexClicked=-1, -1
            self.chordIndex=0
            self.noteIndex=0
            self.helpScreen=False
            self.resetSignature()
        elif event.keysym=="q":
            # to quit the help screen
            self.helpScreen=False
        elif event.keysym=="h":
            # to access the help screen
            self.helpScreen=True
        elif event.keysym=="d":
            # to delete notes
            if self.noteIndexClicked!=-1:
                if self.clefs[self.clefIndexClicked].chords!=[]:
                    self.clefs[self.clefIndexClicked].chords[self.chordIndexClicked].notes.pop(self.noteIndexClicked)
                    if self.clefs[self.clefIndexClicked].chords[self.chordIndexClicked].notes==[]:
                        self.clefs[self.clefIndexClicked].chords.pop(self.chordIndexClicked)
                self.noteIndexClicked=-1
            elif self.accidentalIndexClicked!=-1:
                if self.clefs[self.clefIndexClicked].accidentals!=[]:
                    accidental=self.clefs[self.clefIndexClicked].accidentals[self.accidentalIndexClicked]
                    accidental.justDeleted=True
                    accidental.findNotes(self.clefs[self.clefIndexClicked])
                    self.clefs[self.clefIndexClicked].accidentals.pop(self.accidentalIndexClicked)
                self.accidentalIndexClicked=-1
        elif (event.keysym=="Escape"):
            # to escape editing mode 
            self.helpScreen=False
            self.quarterNoteMode, self.halfNoteMode=False, False
            self.eighthNoteMode, self.quarterRestMode=False, False
            self.dotMode, self.sharpMode, self.flatMode=False, False, False
            self.eighthRestMode=False


    
        
        

    # taken verbatim from
    # https://mail.python.org/pipermail/python-list/2000-December/022013.html
    # to rotate oval 
    def poly_oval(self, x0,y0, x1,y1, steps=20, rotation=0):
        # rotation is in degrees anti-clockwise
        rotation = rotation * math.pi / 180.0
        # major and minor axes
        a = (x1 - x0) / 2.0
        b = (y1 - y0) / 2.0
        # center
        xc = x0 + a
        yc = y0 + b
        point_list = []
        # create the oval as a list of points
        for i in range(steps):
            # Calculate the angle for this step
            theta = (math.pi * 2) * (float(i) / steps)
            x1 = a * math.cos(theta)
            y1 = b * math.sin(theta)
            # rotate x, y
            x = (x1 * math.cos(rotation)) + (y1 * math.sin(rotation))
            y = (y1 * math.cos(rotation)) - (x1 * math.sin(rotation))
            point_list.append(round(x + xc))
            point_list.append(round(y + yc))
        return point_list

    def drawMovingNote(self, text, font="Maestro 50"):
        # draws note as user moves mouse
        fill="RosyBrown"
        adjust=-7
        for clef in self.clefs:
            if self.eventy<=self.thirdLine:
                self.canvas.create_text(self.eventx, self.eventy+adjust,
                                        text=text.upper(), font=font, fill=fill)
                break
            elif self.eventy>clef.thirdLine and self.eventy<=clef.bottom:
                self.canvas.create_text(self.eventx, self.eventy+adjust,
                                        text=text, font=font, fill=fill)
                break
            elif self.eventy>(clef.heightFromTop-self.heightLines) and self.eventy<=clef.thirdLine:
                self.canvas.create_text(self.eventx, self.eventy+adjust,
                                        text=text.upper(), font=font, fill=fill)
                break
            elif self.eventy>clef.bottom and self.eventy<(clef.connectLine-self.heightLines):
                self.canvas.create_text(self.eventx, self.eventy+adjust,
                                        text=text, font=font, fill=fill)
                break

    

    def drawNote(self):
        # draws all notes created 
        adjust=-7
        font="Maestro 50"
        for clef in self.clefs:
            chords=clef.chords
            if chords!=[]:
                for chord in chords:
                    for note in chord.notes:
                        cx, cy= note.cx, note.cy
                        thirdLine=2*self.heightLines+note.clefTop
                        if cy>thirdLine:
                            self.canvas.create_text(cx, cy+adjust,
                                            text=note.text, font=note.font)
                        else:
                            self.canvas.create_text(cx, cy+adjust,
                                            text=note.text.upper(), font=note.font)
                    
    def drawMovingAccidental(self, text):
        # draws accidental as user moves mouse
        fill="RosyBrown"
        font="Maestro 40"
        if text==".":
            font="Maestro 60"
            adjust=-17
        else: adjust=-12
        self.canvas.create_text(self.eventx, self.eventy+adjust, text=text,
                                font=font, fill=fill)

    def drawAccidental(self):
        # draws all accidentals created 
        for clef in self.clefs:
            for accidental in clef.accidentals:
                if accidental.type=="dot": adjust=-17
                else: adjust=-12
                self.canvas.create_text(accidental.cx, accidental.cy+adjust,
                                text=accidental.text, font=accidental.font)
            for accidental in clef.keysig:
                adjust=-12
                self.canvas.create_text(accidental.cx, accidental.cy+adjust,
                                text=accidental.text, font=accidental.font)


    def drawClefStaves(self):
        firstMeasureMargin=18
        for clef in self.clefs:
            # drawing measures 
            for row in xrange(self.numRows):
                for col in xrange(self.measuresPerLine):
                    left= col*clef.widthLines+clef.lineMargin
                    top= row*clef.heightLines+clef.heightFromTop
                    right=(col+1)*clef.widthLines + clef.lineMargin
                    bottom=(row+1)*clef.heightLines + clef.heightFromTop
                    if col==0: left=left-firstMeasureMargin
                    else: left=left
                    self.canvas.create_rectangle(left, top, right, bottom)
                    # connecting clefs 
                    if clef.type=="treble":
                        if row==0 and col==0:
                            self.canvas.create_line(left, top, left,
                                                    clef.connectLine)
                        elif row==self.numRows-1:
                            self.canvas.create_line(right, top, right,
                                                    clef.connectLine)
            # drawing clef and time signature
            self.drawClefTimeSig(clef)
            
    def drawClefTimeSig(self, clef):
        self.canvas.create_text(clef.clefX, clef.clefY, text=clef.text,
                                    font=clef.font)
        self.canvas.create_text(clef.timeSigX, clef.timeSigY1, text="4",
                                    font="Maestro 55")
        self.canvas.create_text(clef.timeSigX, clef.timeSigY2, text="4",
                                font="Maestro 55")
            

    def drawSweepingBar(self):
        # a sweeping bar hits notes as they play :)
        for clef in self.clefs:
            bottomLine=4*self.heightLines+clef.heightFromTop
            for chord in clef.chords:
                for note in chord.notes:
                    self.canvas.create_line(note.sweepingBar,
                            clef.heightFromTop, note.sweepingBar,
                            bottomLine, width=3, fill="RosyBrown")

    def drawPlayButton(self):
        play=False
        for clef in self.clefs:
            if clef.playing:
                play=True
        if not play:
            self.canvas.create_polygon(50, 50, 50, 80, 80, 65,
                                    fill="black", activefill="gray",
                                       activestipple="gray25")
        else:
            self.canvas.create_polygon(50, 50, 50, 80, 80, 65,
                                   fill="gray",stipple="gray25",
                                       outline="RosyBrown")

    def drawPauseButton(self):
        if self.mouseOverPause==True:
            self.canvas.create_rectangle(100, 50, 110, 80, fill="gray",
                                outline="", stipple="gray25")
            self.canvas.create_rectangle(120, 50, 130, 80, fill="gray",
                                outline="", stipple="gray25")
        elif self.clickedPause==True:
            self.canvas.create_rectangle(100, 50, 110, 80, fill="gray",
                                outline="RosyBrown", stipple="gray25")
            self.canvas.create_rectangle(120, 50, 130, 80, fill="gray",
                                outline="RosyBrown", stipple="gray25")
        else:
            self.canvas.create_rectangle(100, 50, 110, 80, fill="black",
                                outline="")
            self.canvas.create_rectangle(120, 50, 130, 80, fill="black",
                                outline="")
    def drawStopButton(self):
        if self.stop==True:
            self.canvas.create_rectangle(150, 50, 180, 80, fill="gray",
                                    stipple="gray25", outline="RosyBrown")
        else:
            self.canvas.create_rectangle(150, 50, 180, 80, fill="black",
                                    outline="", activefill="gray",
                                         activestipple="gray25")

    def drawPageButtons(self):
        self.canvas.create_polygon(730, 650, 730, 680, 795, 665,
                                   fill="RosyBrown",activefill="gray",
                                   activestipple="gray25")
        self.canvas.create_polygon(710, 650, 710, 680, 645, 665,
                                   fill="RosyBrown",activefill="gray",
                                   activestipple="gray25")
            
        

    # creates title
    def drawTitle(self):
        fill="black"
        topMargin=60
        leftMargin, top=115, 105
        self.canvas.create_text(leftMargin, top,
                    text="Press 'p' to play all pages",
                                font=("Mf Young & Beautiful", "16", "bold"))
        
        top-=80
        self.canvas.create_text(leftMargin, top,
                text="Press 'h' for help", font=("Mf Young & Beautiful", "16"))
        self.canvas.create_text(self.width/2, topMargin,
                                text="%s"%self.title,
                            font=("Mardian Demo", "60"), fill=fill)
        topMargin+=60
        self.canvas.create_text(self.width/2, topMargin,text="W",
                                font=("There can only be one Beaver Im", "40"),
                                fill=fill)
        # page number
        bottomMargin=130
        self.canvas.create_text(self.width/2, self.height-bottomMargin,
                                text="page: %d"%(self.pagenumber+1),
                                font=("Mardian Demo", "60"), fill=fill)
        # new page icon
        x, y, size=750, 50, 60
        left, top, right, bottom=x-size/2, y-size/2, x+size/2, y+size/2
        if (self.startEventX>left and self.startEventY>top
                and self.startEventX<right and self.startEventY<bottom):
            self.canvas.create_rectangle(left, top, right, bottom,
                        fill="rosyBrown", stipple="gray25",outline="")
        self.canvas.create_image(x, y, image=self.newPageIcon)

        
    def makeKeySignature(self):
        # draws key signature based on user's decision
        sharpMajors, flatMajors=self.key_signatures[:8], self.key_signatures[8:]
        for clef in self.clefs:
            if self.keySigChosen in sharpMajors:
                index, sep=sharpMajors.index(self.keySigChosen),12
                clef.timeSigX=48+index*sep+3
                for i in xrange(1, index+1):
                    self.keySigHelperSharps(sharpMajors[i], clef, (i-1)*sep)
            elif self.keySigChosen in flatMajors:
                index, sep=flatMajors.index(self.keySigChosen), 10
                clef.timeSigX=50+index*sep+3
                for i in xrange(index+1):
                    self.keySigHelperFlats(flatMajors[i], clef, (i-1)*sep)



    def keySigHelperSharps(self, letter, clef, x):
        accidental, cx="sharp", 48+x
        if clef.type=="treble": difference=0
        else: difference=self.heightLines
        if letter=="G":
            clef.keysig.append(Accidental(accidental, cx,
                            clef.heightFromTop+difference))
        elif letter=="D":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.heightFromTop+1.5*self.heightLines+difference))
        elif letter=="A":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.heightFromTop-0.5*self.heightLines+difference))
        elif letter=="E":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.heightFromTop+self.heightLines+difference))
        elif letter=="B":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.thirdLine+0.5*self.heightLines+difference))
        elif letter=="FSharp":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.heightFromTop+0.5*self.heightLines+difference))
        elif letter=="CSharp":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.thirdLine+difference))

    def keySigHelperFlats(self, letter, clef, x):
        accidental, cx="flat", 50+x
        if clef.type=="treble": difference=0
        else: difference=self.heightLines
        if letter=="F":
            clef.keysig.append(Accidental(accidental, cx,
                            clef.thirdLine+difference))
        elif letter=="BFlat":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.heightFromTop+0.5*self.heightLines+difference))
        elif letter=="EFlat":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.thirdLine+0.5*self.heightLines+difference))
        elif letter=="AFlat":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.heightFromTop+self.heightLines+difference))
        elif letter=="DFlat":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.thirdLine+self.heightLines+difference))
        elif letter=="GFlat":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.thirdLine-0.5*self.heightLines+difference))
        elif letter=="CFlat":
            clef.keysig.append(Accidental(accidental, cx,
                    clef.thirdLine+1.5*self.heightLines+difference))
            
                
        
    def keySignaturesList(self):
        # list of key signature coordinates
        return [[50, 90, 128, 217], [128, 90, 201, 217],
                            [201, 90, 280, 217], [280, 90,365, 217],
                            [365, 90,452, 217], [452, 90,553, 217],
                            [553, 90,672, 217],[672, 90,747, 217],
                            [50, 292, 156, 411], [156, 292, 223, 411],
                            [223, 292, 307, 411], [307, 292, 410, 411],
                            [410, 292, 532, 411], [532, 292, 661, 411],
                            [661, 292, 747, 411]]

        
    def drawStartScreen(self):
        width=5
        color="rosyBrown"
        margin=30
        self.canvas.create_text(self.width/2, margin, text="e",
                                font=("There can only be one Beaver Im", "70"),
                                fill="black")
        margin=250
        self.canvas.create_image(self.width/2, margin,
                                 image=self.menubackground)
        key_signaturesList=self.keySignaturesList()
        rows =len(key_signaturesList)
        for row in xrange(rows):
            left=key_signaturesList[row][0]
            top=key_signaturesList[row][1]
            right=key_signaturesList[row][2]
            bottom=key_signaturesList[row][3]
            if (self.startEventX>left and self.startEventY>top
                and self.startEventX<right and self.startEventY<bottom):
                self.canvas.create_rectangle(left, top, right, bottom,
                                             outline=color, width=width)
            if (self.start_clickedX>left and self.start_clickedY>top
                and self.start_clickedX<right and self.start_clickedY<bottom):
                self.keySigChosen=self.key_signatures[row]
                self.makeKeySignature()
                self.startScreen=False

    def newPage(self):
        if self.pagenumber>0: self.makeKeySignature()
        self.new=False

    def resetSignature(self):
        self.makeKeySignature()

    def clickInUIButton(self, x, y, width, height, type):
        # clicked in buttons in top right corner
        # ( to enter editing mode )
        if (self.start_clickedX>=x-width and self.start_clickedX<=x+width
            and self.start_clickedY>=y-height and self.start_clickedY<=y+height):
            if type=="note": # chose note 
                self.quarterNoteMode, self.halfNoteMode=True, False
                self.sharpMode, self.flatMode, self.dotMode=False, False, False
                self.eighthNoteMode=False
                self.quarterRestMode, self.eighthRestMode=False, False
            elif type=="accidental": # chose accidental 
                self.quarterNoteMode, self.halfNoteMode=False, False
                self.sharpMode, self.flatMode, self.dotMode=True, False, False
                self.eighthNoteMode=False
                self.quarterRestMode=False
            elif type=="rest": # chose rest 
                self.quarterNoteMode, self.halfNoteMode=False, False
                self.sharpMode, self.flatMode, self.dotMode=False, False, False
                self.eighthNoteMode=False
                self.quarterRestMode=True
            self.start_clickedX, self.start_clickedY=0, 0
        
        
    def drawUIButtons(self):
        # drawing the buttons in the top right corner 
        framex, framey=630, 150
        x, y, width, height=630, 150, 10, 10
        font="Maestro 40"
        self.clickInUIButton(x, y, width, height, "note")
        if ((self.startEventX>=x-width and self.startEventX<=x+width
            and self.startEventY>=y-height and self.startEventY<=y+height)
            or (self.quarterNoteMode or
                self.halfNoteMode or self.eighthNoteMode)):
            fill="rosyBrown"
        else: fill="black"
        self.canvas.create_text(x, y, text="q", font=font, fill=fill)
        self.canvas.create_text(x, y, text="Z", font="CalligraphicFramesSoft 80")
        x, y, height=680, 130, 18
        self.clickInUIButton(x, y, width, height, "accidental")
        if ((self.startEventX>=x-width and self.startEventX<=x+width
            and self.startEventY>=y-height and self.startEventY<=y+height)
            or (self.sharpMode or self.dotMode or self.flatMode)):
            fill="rosyBrown"
        else: fill= "black"
        framex+=50
        self.canvas.create_text(x, y, text="#", font=font, fill=fill)
        self.canvas.create_text(framex, framey, text="Z", font="CalligraphicFramesSoft 80")
        x, y=730, 135
        self.clickInUIButton(x, y, width, height, "rest")
        framex+=50
        if ((self.startEventX>=x-width and self.startEventX<=x+width
            and self.startEventY>=y-height and self.startEventY<=y+height)
            or (self.quarterRestMode or self.eighthRestMode)):
            fill="rosyBrown"
        else: fill="black"
        self.canvas.create_text(x, y, text="A", font="MetDemo 40", fill=fill)
        self.canvas.create_text(framex, framey, text="Z", font="CalligraphicFramesSoft 80")

    def drawHelpScreen(self):
        # help screen 
        font=("Mf Young & Beautiful", "20")
        x, y=self.width/2, 300
        self.canvas.create_text(x, y,
            text="Click buttons to place notes, accidentals, or rests",
                                font=font)
        y+=50
        self.canvas.create_text(x, y,
            text="Use the up arrow key to switch between types", font=font)
        y+=50
        self.canvas.create_text(x, y, text="Press 'esc' to exit editing mode",
                                font=font)
        y+=50
        self.canvas.create_text(x, y,
        text="To add a new page, click on icon in the upper right-hand corner",
                                font=font)
        y+=50
        self.canvas.create_text(x, y,
            text="Use the arrows in the lower right-hand\
corner to navigate between pages",
                                font=font)
        y+=50
        self.canvas.create_text(x, y, text="Press 'q' to exist this screen",
                                font=font)
        
    def redrawAll(self):
        self.canvas.delete(ALL)
        self.canvas.create_image(400, 310, image=self.background)
        if self.new: self.newPage()
        if self.startScreen: self.drawStartScreen()
        elif self.helpScreen: self.drawHelpScreen()
        else:
            self.drawTitle()
            self.drawUIButtons()
            self.drawClefStaves()
            if self.quarterNoteMode==True:
                self.drawMovingNote("q")
            elif self.halfNoteMode==True:
                self.drawMovingNote("h")
            elif self.eighthNoteMode==True:
                self.drawMovingNote("e")
            elif self.sharpMode==True:
                self.drawMovingAccidental("#")
            elif self.flatMode==True:
                self.drawMovingAccidental("b")
            elif self.quarterRestMode==True:
                self.drawMovingNote("A", "MetDemo 60")
            elif self.eighthRestMode==True:
                self.drawMovingNote("S", "MetDemo 50")
            elif self.dotMode==True:
                self.drawMovingAccidental(".")
            self.drawNote()
            self.drawAccidental()
            if self.clefs!=[]:
                self.drawSweepingBar()
            self.drawPlayButton()
            self.drawPauseButton()
            self.drawStopButton()
            self.drawPageButtons()
        
        
        
    
    
class Note(object):
    def __init__(self, typeNote, cx, cy, clefType, clefTop):
        self.typeNote=typeNote
        self.cx, self.cy=cx, cy
        self.font="Maestro 50"
        self.playedDuration=0
        self.sweepingBar=0
        self.clefType=clefType
        self.clefTop=clefTop
        self.numRows=4
        self.heightLines=20
        if self.typeNote=="quarter":
            self.hold=.3
            self.text="q"
        elif self.typeNote=="half":
            self.hold=0.6
            self.text="h"
        elif self.typeNote=="eighth":
            self.hold=0.15
            self.text="e"
        elif self.typeNote=="quarter rest":
            adjust=50
            self.cy=self.clefTop+adjust
            self.hold=0.3
            self.text="A"
            self.font="MetDemo 60"
        elif self.typeNote=="eighth rest":
            adjust=45
            self.cy=self.clefTop+adjust
            self.hold=0.15
            self.text="S"
            self.font="MetDemo 50"
        for row in xrange(self.numRows):  
            top= row*self.heightLines+self.clefTop
            bottom=(row+1)*self.heightLines + self.clefTop
            aboveStaff=top-self.heightLines
            belowStaff=bottom+self.heightLines
            # to determine note's sound based on its position on the staff
            if self.cy==top:
                if self.clefType=="treble":
                    if row==0: self.sound=77
                    elif row==1: self.sound=74
                    elif row==2: self.sound=71
                    elif row==3: self.sound=67
                else:
                    if row==0: self.sound=57
                    elif row==1: self.sound=53
                    elif row==2: self.sound=50
                    elif row==3: self.sound=47
            elif self.cy==top-((top-aboveStaff)/2) and row==0:
                if self.clefType=="treble":
                    self.sound=79
                else: self.sound=59
            elif self.cy==bottom+((belowStaff-bottom)/2) and row==3:
                if self.clefType=="treble": self.sound=62
                else: self.sound=41
            elif self.cy==bottom and row==3:
                if self.clefType=="treble": self.sound=64
                else: self.sound=43
            elif self.cy==bottom-((bottom-top)/2):
                if self.clefType=="treble":
                    if row==0:self.sound=76
                    elif row==1:self.sound=72
                    elif row==2:self.sound=69
                    elif row==3: self.sound=65
                else:
                    if row==0:self.sound=55
                    elif row==1:self.sound=52
                    elif row==2:self.sound=48
                    elif row==3: self.sound=45
                    
            elif self.cy==bottom+((bottom-top)/2) and row==3:
                if self.clefType=="treble":
                    self.sound=62
                else:
                    self.sound=41
        
    
                
    def startOrKeepOrStopPlaying(self):
        # return True if the note is still on
        # return False if stopped playing this note
        if self.typeNote=="quarter rest" or self.typeNote=="eighth rest":
            if self.playedDuration==0:
                self.sweepingBar=self.cx-11
                self.playedDuration+=.02
                return True
            elif self.playedDuration<(self.hold-0.02):
                self.playedDuration+=.02
                return True
            else:
                self.playedDuration=0
                self.sweepingBar=0
                return False
        else:
            if self.playedDuration==0:
                player.note_on(self.sound, 127)
                self.sweepingBar=self.cx-11
                self.playedDuration+=.02
                return True
            elif self.playedDuration<(self.hold-.02):
                self.playedDuration+=.02
                return True
            else:
                self.playedDuration=0
                self.sweepingBar=0
                player.note_off(self.sound, 127)
                return False

    def keysig(self, clef):
        # edits note based on key signature 
        for accidental in clef.keysig:
            if (self.cy==accidental.cy
                or self.cy==accidental.cy+3.5*clef.heightLines):
                if accidental.type=="sharp":
                    self.sound+=1
                elif accidental.type=="flat":
                    self.sound-=1

        

class Chord(object):
    def __init__(self, cx):
        self.cx=cx
        self.notes=[]
        
class Accidental(object):
    def __init__(self, typeAccidental, cx, cy):
        self.type=typeAccidental
        self.cx, self.cy=cx, cy
        self.font="Maestro 40"
        if self.type=="sharp":
            self.text="#"
        elif self.type=="flat":
            self.text="b"
        elif self.type=="dot":
            self.text="."
            self.font="Maestro 60"
        self.justDeleted=False
            
    def findNotes(self, clef):
        # determines if accidental in proximity of note
        # edits the note based on accidental 
        accidentalDistance=22
        for chord in clef.chords:
            for note in chord.notes:
                if self.cy==note.cy and self.cx>=(note.cx-accidentalDistance) and self.cx<=(note.cx):
                    if self.type=="sharp":
                        if self.justDeleted:
                            note.sound-=1
                        else:
                            note.sound+=1
                    elif self.type=="flat":
                        if self.justDeleted:
                            note.sound+=1
                        else:
                            note.sound-=1
                elif self.cy==note.cy and self.cx>=(note.cx) and self.cx<=(note.cx+accidentalDistance):
                    if self.type=="dot":
                        if self.justDeleted:
                            note.hold=note.hold/1.5
                        else:
                            note.hold=note.hold*1.5
        self.justDeleted=False

   
class Clef(object):
    def __init__(self, typeClef, position):
        self.width, self.height=800, 800 
        self.type=typeClef
        self.position=position
        self.lineHeight, self.lineMargin, self.measuresPerLine=80, 20, 4
        self.topMargin=40
        self.widthLines=(self.width-2*self.lineMargin)/self.measuresPerLine
        self.heightLines=self.lineHeight/4
        top=self.width/4
        self.heightFromTop=top+self.position*(self.topMargin+self.lineHeight)
        self.connectLine=self.heightFromTop+self.lineHeight+self.topMargin
        self.numRows=4
        self.clefX=20
        if self.type=="treble":
            self.font="Maestro 40"
            self.text="&"
            self.clefY=self.heightFromTop+2*self.heightLines
        elif self.type=="bass":
            self.font="Maestro 50"
            self.text="?"
            adjust=35
            self.clefY=self.heightFromTop+2*self.heightLines-adjust
        self.timeSigX=70
        self.timeSigY1=self.heightFromTop
        self.timeSigY2=self.heightFromTop+2*self.heightLines
        self.thirdLine=2*self.heightLines+self.heightFromTop
        self.bottom=4*self.heightLines+self.heightFromTop
        self.chords=[]
        self.accidentals=[]
        self.keysig=[]
        self.chordIndex=0
        self.playing=False

    def play(self):
        # plays the clef
        if self.chords!=[] and self.chordIndex!=len(self.chords):
            chord=self.chords[self.chordIndex]
            for i in xrange(len(chord.notes)):
                note=chord.notes[i]
                stillPlay=note.startOrKeepOrStopPlaying()
                if stillPlay==False and i==(len(chord.notes)-1):
                    self.chordIndex+=1
        elif self.chordIndex==len(self.chords):
            self.playing=False
            self.chordIndex=0

    def compareByPosition(self, chord1, chord2):
        # sorts the chords in order from left to right
        return cmp(chord1.cx, chord2.cx)

    def sortNotes(self):
        # sorts the chords in order from left to right
        self.chords=sorted(self.chords, self.compareByPosition)


MusicBook().run()
