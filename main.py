import os
import platform
from music21 import note, stream, midi, interval, chord
from random import randint


# notes:
noteNames = ["C", "D", "E", "F", "G", "A", "B"]
# hash table for note values based on probability values:
noteOctaves = {0: "2", 1: "2", 2: "2", 3: "3", 4: "3", 5: "3", 6: "4", 7: "4", 8: "4", 9: "5", 10: "5",
               11: "5", 12: "6", 13: "6", 14: "7", 15: "1"}


class Composition: # class created for musical work
    def __init__(self):
        self.notes = [] # musical notes
        self.fitness = 0 # fitness value of the music (the lower, the better)

    def initializeNotes(self, base): # function to initialize notes
        for i in range(len(base.notes)):
            self.notes.append(randomNote(base.notes[i].duration))

    def assignRestsAndChords(self, base): # function to initialize chords and rests
        for i in range(len(base.notes)):
            if (type(base.notes[i]) != note.Note):
                self.notes[i] = base.notes[i]

    def assignDurations(self, base): # function to initialize note durations
        for i in range(len(base.notes)):
            self.notes[i].duration = base.notes[i].duration

    def calculateFitness(self, base): # function to measure fitness value
        self.fitness = 0  # less is better

        for i in range(len(self.notes)):
            if type(base.notes[i]) == note.Note:
                self.fitness += noteDiff(base.notes[i], self.notes[i])

'''
    Function to measure the numerical value of a given note.
    @param note1: note
    @return: measured numerical value
'''

def noteValue(note1):
    nameVal = (ord(note1.name[0].upper()) - ord('A') + 5) % 7
    octaveVal = note1.octave

    if len(note1.name) > 1:
        if note1.name[1] == '#': # sharp, raises the pitch by a half step
            octaveVal += 0.05
        else:                     # flat, lowers the pitch by a half step
            octaveVal -= 0.05

    return 10*octaveVal + nameVal

'''
    Function to measure the numerical difference between two notes.
    @param notes1: first music piece
    @param notes2: second music piece
    @return: measured numerical difference
'''

def noteDiff(note1, note2):
    return abs(noteValue(note1) - noteValue(note2))

'''
    Function to read music from a given file path.
    @param path: file path of the music
    @return: read music piece
'''

def readStream(path):
    mfIn = midi.MidiFile()
    mfIn.open(path)
    mfIn.read()
    mfIn.close()
    return midi.translate.midiFileToStream(mfIn).flat

'''
    Function to write the generated music to a file.
    @param notes: musical notes
    @param path: file path to write to
'''

def writeStream(notes, path):
    strm = stream.Stream()
    strm.append(notes)
    mfOut = midi.translate.streamToMidiFile(strm)
    mfOut.open(path, 'wb')
    mfOut.write()
    mfOut.close()

'''
    Function to create a random note.
    @param dur: duration of the current note
    @return: created note
'''

def randomNote(dur):
    # note is randomly selected from A-G:
    noteName = noteNames[randint(0, 6)]
    # note value is randomly selected from 1-7:
    noteOctave = noteOctaves[randint(0, 15)]
    newNote = note.Note(noteName + str(noteOctave))
    # duration of the note is assigned:
    newNote.duration = dur
    return newNote

'''
    Function to initialize the first generation.
    @param baseComposition: music piece to be imitated
    @return: initialized generation
'''

def initializeCompositions(baseComposition):
    compositions = []

    for _ in range(100):
        composition = Composition()
        # notes are initialized:
        composition.initializeNotes(baseComposition)
        # chords and rests are initialized:
        composition.assignRestsAndChords(baseComposition)
        # note durations are initialized:
        composition.assignDurations(baseComposition)
        # fitness value is measured:
        composition.calculateFitness(baseComposition)
        compositions.append(composition)

    return compositions

'''
    Function to select two parents for a new individual.
    @return: indices of the parents
'''

def selectParents():
    # 70% chance to select from the best 5 parents
    if randint(1, 10) <= 7:
        return randint(0, 5), randint(0, 5)
    # 21% chance to select from the best 10 parents
    elif randint(1, 10) <= 7:
        return randint(0, 10), randint(0, 10)

    # 9% chance to select from the best 25 parents
    return randint(0, 25), randint(0, 25)

'''
    Function to crossover the selected two parents.
    @param notes1: first music piece
    @param notes2: second music piece
    @return: music piece resulting from crossover
'''

def crossover(notes1, notes2):
    newNotes = []
    threshold = randint(0, len(notes1)-1) # position for crossover

    for i in range(threshold):
        # existing note is added to new music with 99% probability
        if type(notes1[i]) != note.Note or randint(1, 100) <= 99:
            newNotes.append(notes1[i])
        else:    # mutation
            newNotes.append(randomNote(notes1[i].duration))

    for i in range(threshold, len(notes1)):
        # existing note is added to new music with 99% probability
        if type(notes2[i]) != note.Note or randint(1, 100) <= 99:
            newNotes.append(notes2[i])
        else:  # mutation
            newNotes.append(randomNote(notes2[i].duration))

    return newNotes

'''
    Function to allow generations to evolve.
    @param compositions: current music pieces in the generation
    @param baseComposition: music piece to be imitated
    @return: evolved music pieces
'''

def evolution(compositions, baseComposition):
    newCompositions = []

    for i in range(len(compositions)):
        # parents of the music piece are selected:
        x, y = selectParents()
        composition = Composition()
        # new individual is created by crossing over the selected parents:
        composition.notes = crossover(compositions[x].notes, compositions[y].notes)
        # fitness value of the new individual is measured:
        composition.calculateFitness(baseComposition)
        # individual is added to the new generation:
        newCompositions.append(composition)

    return newCompositions

'''
    Function to clear the terminal screen.
'''

def clearScreen():
    if platform.system() == "Windows":
        os.system("cls")
    else:                  # Linux & Mac OS
        os.system("clear")


'''
    Function to print the program logo.
'''
def printBanner():
    clearScreen()
    print("\n\t#####################################")
    print("\t########## GENETIC COMPOSER ##########")
    print("\t#####################################\n")


def main():
    # user enters their own ".mid" file:
    print("\tEnter the file path: ", end=""),
    filePath = input()

    if filePath == "": # exit:
        exit()

    fileExists = os.path.exists(filePath)

    if (fileExists == False): # check if the file exists
        print("\n\tFile could not be read.\n")
        exit()

    # user input for the number of generations
    print("\tEnter the number of generations (recommended: 100): ", end="")
    gen = int(input())

    print("\n\tCreating variations...")

    baseComposition = Composition()
    baseComposition.notes = readStream(filePath) # .mid file is read

    # first generation is initialized:
    compositions = initializeCompositions(baseComposition)
    # resulting pieces are sorted by fitness values:
    compositions.sort(key=lambda composition: composition.fitness)

    print("\tStarting fitness value: ", compositions[0].fitness)

    for _ in range(gen):
        # generations evolve:
        compositions = evolution(compositions, baseComposition)
        # resulting pieces are sorted by fitness values:
        compositions.sort(key=lambda composition: composition.fitness)

    print("\t" + str(gen) + " generations resulted in a fitness value: ", compositions[0].fitness)

    filePath = filePath.replace(".mid", "_variation.mid")
    writeStream(compositions[0].notes, filePath) # variation music is written

    print("\n\tVariation created:", filePath)

if __name__ == '__main__':
    main()
