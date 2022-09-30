from asyncio.windows_events import NULL
import mido
import time

class MIDIanalyzer:
    def __init__(self):
        self.mid = NULL
        #拍子
        self.numerator = 4     #デフォルトは4
        self.denominator = 4   #デフォルトは4で
        #時間関連
        self.tempo = 500000    #四分音符1個にかかる時間．㎲．デフォルトは500000
        self.length = 0.0      #曲の長さを格納する．デフォルトは0.0
        self.microsec_per_ticks = 0
        self.microsec_per_measure = 0
        #音の種類関連
        self.track_num = 0     #trackの数を格納する/多分，基本的にchannel毎にtrackは分かれるぽい？
        #音の情報
        self.time = NULL       #前の音からの時間(ticks)
        self.velocity = NULL   #音の強さ
        self.note = NULL       #音の高さ(ドレミ的な)
        #休符の種類を格納
        self.rests = NULL
    
    def getMIDIfile(self, filename):
        #MIDIファイル読み込み
        self.mid = mido.MidiFile(filename)
    
    def getTimeSignature(self):
        #拍子を取得
        #変拍子は考えない．むずい
        for i, track in enumerate(self.mid.tracks):
            for msg in track:
                msg_string = str(msg)
                if(('numerator' in msg_string) and ('denominator' in msg_string)):
                    numerator_index = msg_string.find('numerator') + 10
                    denominator_index = msg_string.find('denominator') + 12
                    self.numerator = int(msg_string[numerator_index])
                    self.denominator = int(msg_string[denominator_index])    

    def getTempo(self):
        #4分音符1個あたりのマイクロ秒を取得
        for msg in self.mid:
            if msg.type == "set_tempo":
                self.tempo = msg.tempo

        self.microsec_per_ticks = self.tempo/self.mid.ticks_per_beat
    
    def getLength(self):
        #曲全体の時間を取得(s)
        self.length = self.mid.length
    
    def getTracknum(self):
        #Trackの数を取得
        self.track_num = len(self.mid.tracks)
    
    def getNoteData(self):
        #Track毎にNote_onのnote,velocity,timeを取得するメソッド
        
        #note等の情報はtrack毎に取得しなければならないので2次元配列にする
        self.note = [[] for i in range(self.track_num)]
        self.velocity = [[] for i in range(self.track_num)]
        self.time = [[] for i in range(self.track_num)]
        self.rests = [[] for i in range(self.track_num)]
        #track毎に値を取得
        for i in range(self.track_num):
            for msg in self.mid.tracks[i]:
                if msg.type == 'note_on':
                    self.note[i].append(msg.note)
                    self.velocity[i].append(msg.velocity)
                    self.time[i].append(msg.time)
                    self.rests[i].append('note')
        
    
    def getRests(self):
        #曲全体の休符を取得する

        #track毎に休符位置を取得
        for i in range(self.track_num):
            #同じindexのtime[i]は「前の音から何ticks後」を示していることに注意
            #よって休符(velocity[i]=0)の長さはtime[i+1]となる
            for j in range(0, len(self.note[i])-1, 1):
                #音の強さが0＝音が鳴らない時，何休符か判定
                #休符でない音と音の間の切れ目はテキトーに設定
                if(self.velocity[i][j]==0):      
                    #4分休符
                    if ((480 <= self.time[i][j+1]) and (self.time[i][j+1] < 480 + 96)):
                        self.rests[i][j] = 'quarter'
                    #2分休符
                    elif ((480*2 <= self.time[i][j+1]) and (self.time[i][j+1] < 480*2 + 96)):
                        self.rests[i][j] = 'half'
                    #全休符
                    elif ((480*self.numerator <= self.time[i][j+1]) and (self.time[i][j+1] < 480*self.numerator + 96)):
                        self.rests[i][j] = 'whole'
                    #8分休符
                    elif ((240 <= self.time[i][j+1]) and (self.time[i][j+1] < 240 + 48)):
                        self.rests[i][j] = '8th'
                    elif ((120 <= self.time[i][j+1]) and (self.time[i][j+1] < 120 + 24)):
                        self.rests[i][j] = '16th'
                    #ただの音の間の切れ目
                    elif self.time[i][j+1] < 48:
                        self.rests[i][j] = 'not rest'
                    #それ以外は解析不可とする(できるけどしない)
                    else:
                        self.rests[i][j] = 'cannot analize'
                        
    def printBeat(self):
        #リアルタイムで拍子を表示
        time_now = 0.0
        while(time_now + self.tempo/(10**6) < self.length):
            for i in range(1,self.numerator+1,1):
                print(i)
                time.sleep(self.tempo/(10**6))
                time_now += self.tempo/(10**6)
        
        print("finish!")
        print(time_now)
    
    def checkBugs(self):
        print("ticks per beat = %d" %self.mid.ticks_per_beat)
        print("numerator = %d" %self.numerator)
        print("denominator = %d" %self.denominator)    
        print("tempo = %d [micro_s]" %self.tempo)
        print("SpT = %f [micro_s]" %self.microsec_per_ticks)
        print("length = %f [s]" %self.length)
        print("tracks = %d" %self.track_num)

        for i in range(0, len(self.velocity[0])-1, 1):
            print({'vel': self.velocity[0][i], 'time':self.time[0][i+1], 'rest':self.rests[0][i]})

if __name__=="__main__":
    midanalyzer = MIDIanalyzer()
    midanalyzer.getMIDIfile('happyfarmer_60.mid')
    midanalyzer.getTimeSignature()
    midanalyzer.getTempo()
    midanalyzer.getLength()
    midanalyzer.getTracknum()
    midanalyzer.getNoteData()
    midanalyzer.getRests()
    #midanalyzer.printBeat()