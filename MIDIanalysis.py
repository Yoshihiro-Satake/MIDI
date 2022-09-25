from asyncio.windows_events import NULL
import mido
import time

class MIDIanalyzer:
    def __init__(self):
        self.mid = NULL
        #拍子
        self.numerator = 4   #デフォルトは4
        self.denominator = 4 #デフォルトは4で
        #時間関連
        self.tempo = 500000  #四分音符1個にかかる時間．㎲．デフォルトは500000
        self.length = 0.0    #曲の長さを格納する．デフォルトは0.0
        self.microsec_per_ticks = 0
        self.microsec_per_measure = 0
        #音の種類関連
        self.track_num = 0   #trackの数を格納する
    
    def GetMIDIfile(self, filename):
        #MIDIファイル読み込み
        self.mid = mido.MidiFile(filename)
        #下はテスト用
        print(self.mid.ticks_per_beat)
    
    def GetTimeSignature(self):
        #拍子を取得
        for i, track in enumerate(self.mid.tracks):
            for msg in track:
                msg_string = str(msg)
                if(('numerator' in msg_string) and ('denominator' in msg_string)):
                    numerator_index = msg_string.find('numerator') + 10
                    denominator_index = msg_string.find('denominator') + 12
                    self.numerator = int(msg_string[numerator_index])
                    self.denominator = int(msg_string[denominator_index])
                    #下２行はテスト用
                    print("numerator = %d" %self.numerator)
                    print("denominator = %d" %self.denominator)
    

    def GetTempo(self):
        #4分音符1個あたりのマイクロ秒を取得
        for msg in self.mid:
            if msg.type == "set_tempo":
                self.tempo = msg.tempo
                #下１行はテスト用
                print(self.tempo)
        #下１行はテスト用
        print(self.tempo)

        self.microsec_per_ticks = self.tempo/self.mid.ticks_per_beat
        #下１行はテスト用
        print(self.microsec_per_ticks)
    
    def GetLength(self):
        #曲全体の時間を取得(s)
        self.length = self.mid.length
        #下１行はテスト用
        print(self.length)
    
    def GetTracknum(self):
        #Trackの数を取得
        self.track_num = len(self.mid.tracks)
        #下１行はテスト用
        print(self.track_num)
    
    def PrintBeat(self):
        #リアルタイムで拍子を表示
        time_now = 0.0
        while(time_now + self.tempo/(10**6) < self.length):
            for i in range(1,self.numerator+1,1):
                print(i)
                time.sleep(self.tempo/(10**6))
                time_now += self.tempo/(10**6)
        
        print("finish!")
        print(time_now)


if __name__=="__main__":
    midanalyzer = MIDIanalyzer()
    midanalyzer.GetMIDIfile('happyfarmer_60.mid')
    midanalyzer.GetTimeSignature()
    midanalyzer.GetTempo()
    midanalyzer.GetLength()
    midanalyzer.GetTracknum()
    midanalyzer.PrintBeat()