import sys
import mido

class track_analyzer:
    def __init__(self, ticks_per_beat, *args):
        self.pitchNames = ['C', 'C#(Db)', 'D', 'D#(Eb)', 'E', 'F', 'F#(Gb)', 'G', 'G#(Ab)', 'A', 'A#(Bb)', 'B']
        self.numPitchInOctave = len(self.pitchNames)
        self.noteVals = [[ticks_per_beat/8, 32], [ticks_per_beat/4, 16], [ticks_per_beat/2, 8], [ticks_per_beat, 4], [ticks_per_beat*2, 2], [ticks_per_beat*4, 1]]
        
        self.melody = []  # 取得した旋律が入る
        self.rest = -1  # 休符を表すnoteの値
        
        if len(args) == 1:
            track = args[0]
            self.get_melody(track)

    def get_melody(self, track):
        # --- 音符と休符を一旦何も考えずに抜き出す --- #

        tSum = 0  # 冒頭からの経過ticks
        tOn = None  # 音符開始時の経過ticks
        tOff = 0  # 休符開始時の経過ticks
        currNote = None  # 発音中の音の高さ

        for msg in track:
            # 経過ticksを計算
            tSum += msg.time

            if msg.type == 'note_on':
                # 発音時の処理
                if msg.velocity > 0:
                    # 直前に消音部があった場合には一旦休符として登録する
                    if currNote is None and tSum > tOff:
                        self.melody += [[self.rest, tSum - tOff]]

                    # 音程と発音のタイミングを保存しておく（melodyへの登録は消音のタイミングで行う）
                    currNote = msg.note
                    tOn = tSum
                    tOff = None

                # 消音時の処理
                else:
                    # 音程と音価をmelodyに登録する
                    self.melody += [[currNote, tSum - tOn]]
                    
                    # 消音のタイミングを保存しておく（melodyへの登録は次の発音のタイミングで行う）
                    currNote = None
                    tOn = None
                    tOff = tSum

        # --- 抜き出した休符が真の休符か音符の音価の一部なのかを判断する --- #

        i = 0
        while i < len(self.melody):
            if i > 0 and self.melody[i][0] == self.rest:
                maxBuff = self.melody[i - 1][1]/9  # /9 = *10/(100 - 10)、音価の10%未満の休符は音価の一部とみなす閾値
                if self.melody[i][1] < maxBuff:
                    # 休符は前の音符の音価の一部と推定
                    self.melody[i - 1][1] += self.melody[i][1]
                    self.melody.pop(i)
                    continue
                else:
                    # 真の休符だった場合：処理を後で追加する
                    pass

            i += 1
        
    def get_name(self, note):
        pitchName = self.pitchNames[note%self.numPitchInOctave]
        octave = note//self.numPitchInOctave
        return '%s%d' % (pitchName, octave)

    def ticks_to_notes(self, val):
        notes = ''
        for i in reversed(range(len(self.noteVals))):
            unitVal, unit = self.noteVals[i]
            n = val//unitVal
            if n > 0:
                if notes != '': notes += '＋'
                notes += '%s音符×%d' % ('全' if unit == 1 else '%d分' % unit, n)
                val -= n*unitVal
        if val > 0:
            if notes != '': notes += '＋'
            notes += '%dticks' % val
        return notes
    
    def output_melody(self):
        for note, val in self.melody:
            print(self.get_name(note), self.ticks_to_notes(val))
            
mid = mido.MidiFile('happyfarmer_60.mid')
for i, _tr in enumerate(mid.tracks):
    print('[Track#%02d]' % i)
    tr = track_analyzer(mid.ticks_per_beat, _tr)
    tr.output_melody()
    print()