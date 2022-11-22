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
        self.ticks_per_beat = 480 #デフォルトは480
        self.tempo = 500000    #四分音符1個にかかる時間．㎲．デフォルトは500000
        self.length = 0.0      #曲の長さを格納する．デフォルトは0.0
        self.microsec_per_ticks = 0
        self.microsec_per_measure = 0
        #音の種類関連
        self.track_num = 0     #trackの数を格納する/多分，基本的にchannel毎にtrackは分かれるぽい？
        #音の情報
        self.delta_t = NULL       #前の音からの時間(ticks)
        self.velocity = NULL   #音の強さ
        self.note = NULL       #音の高さ(ドレミ的な)
        #休符の種類を格納
        self.rests = NULL
        #スラーか否かを格納
        self.slur = NULL
        #スタッカートか否かを格納
        self.staccato = NULL
        #そのMetaMessageが何小節目の指令値か記録
        self.bar = NULL
    
    def getMIDIfile(self, filename):
        #MIDIファイル読み込み
        self.mid = mido.MidiFile(filename)
    
    def getTicksPerBeat(self):
        self.ticks_per_beat = self.mid.ticks_per_beat
    
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
                #下１行はテスト用
                #print(self.tempo)

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
        self.delta_t = [[] for i in range(self.track_num)]
        self.rests = [[] for i in range(self.track_num)]
        self.slur = [[] for i in range(self.track_num)]
        self.staccato = [[] for i in range(self.track_num)]
        #track毎に値を取得
        for i in range(self.track_num):
            for msg in self.mid.tracks[i]:
                if msg.type == 'note_on':
                    self.note[i].append(msg.note)
                    self.velocity[i].append(msg.velocity)
                    self.delta_t[i].append(msg.time)
                    self.rests[i].append('note')
                    self.slur[i].append('No')
                    self.staccato[i].append('No')
    
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
                    if ((self.ticks_per_beat <= self.delta_t[i][j+1]) and (self.delta_t[i][j+1] < self.ticks_per_beat*1.2)):
                        self.rests[i][j] = 'quarter'
                    #2分休符
                    elif ((self.ticks_per_beat*2 <= self.delta_t[i][j+1]) and (self.delta_t[i][j+1] < self.ticks_per_beat*2.2)):
                        self.rests[i][j] = 'half'
                    #全休符
                    elif ((self.ticks_per_beat*self.numerator <= self.delta_t[i][j+1]) and (self.delta_t[i][j+1] < self.ticks_per_beat*self.numerator*1.1)):
                        self.rests[i][j] = 'whole'
                    #8分休符
                    elif ((self.ticks_per_beat*0.5 <= self.delta_t[i][j+1]) and (self.delta_t[i][j+1] < self.ticks_per_beat*0.5*1.2)):
                        self.rests[i][j] = '8th'
                    elif ((self.ticks_per_beat*0.25 <= self.delta_t[i][j+1]) and (self.delta_t[i][j+1] < self.ticks_per_beat*0.25*1.2)):
                        self.rests[i][j] = '16th'
                    #ただの音の間の切れ目
                    elif self.delta_t[i][j+1] < self.ticks_per_beat*0.1:
                        self.rests[i][j] = 'not rest'
                    #それ以外は解析不可とする(できるけどしない)
                    else:
                        self.rests[i][j] = 'cannot analize'        

    def getSlur(self):
        #曲全体のスラーを取得する
        #スラー終わりの音符はスラーに含まない(スラー線の右端の音符は伸ばさないため)

        #track毎に休符位置を取得
        for i in range(self.track_num):
            for j in range(1, len(self.note[i])-1, 1):  
                if(self.velocity[i][j-1] != 0 and self.velocity[i][j+1] != 0 and self.velocity[i][j] == 0 and self.delta_t[i][j+1] <= self.ticks_per_beat*0.01):
                    self.slur[i][j-1] = self.slur[i][j] = 'Yes'
                elif(self.velocity[i][j-1] != 0 and self.velocity[i][j] != 0 and self.delta_t[i][j+1] > 0):
                    self.slur[i][j-1] = self.slur[i][j] = 'Yes'
    
    def getStaccato(self):
        for i in range(self.track_num):
            for j in range(0, len(self.note[i])-1, 1):
                #4分音符
                if(self.velocity[i][j] != 0 and self.ticks_per_beat*0.5*0.98 <= self.delta_t[i][j+1] and self.delta_t[i][j+1] <= self.ticks_per_beat*0.5*1.05):
                    self.staccato[i][j] = '4Maybe'
                #8分音符
                elif(self.velocity[i][j] != 0 and self.ticks_per_beat*0.25*0.98 <= self.delta_t[i][j+1] and self.delta_t[i][j+1] <= self.ticks_per_beat*0.25*1.05):
                    self.staccato[i][j] = '8Maybe'

            #track内のスタッカートかもしれない部分に関して，連続して出ていたらスタッカートと判定する
            for j in range(4, len(self.note[i])-1, 1):
                staccato_count = 0
                for k in range(0, 5, 1):
                    if(self.staccato[i][j-k] == '4Maybe' or self.staccato[i][j-k] == '8Maybe' or self.staccato[i][j-k] == 'Yes'):
                        staccato_count += 1
                if(staccato_count >= 2):
                    for k in range(0, 5, 1):
                        if(self.staccato[i][j-k] == '4Maybe' or self.staccato[i][j-k] == '8Maybe'):
                            self.staccato[i][j-k] = 'Yes'

    def getAcsent(self):
        for i in range(0, self.track_num, 1):
            for j in range(0, len(self.velocity[i]), 1):
                Not0count = 0
                AveVelaround10Message = 0 #前後10messageの音の強さの平均
                for k in range(max(0, j-5), min(self.velocity[i], j+5), 1):
                    AveVelaround10Message += self.velocity[i][k]
                    Not0count = (Not0count+1) if (self.velocity[i][k] != 0) else Not0count
                AveVelaround10Message = AveVelaround10Message/Not0count



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

    def checkBug(self):
        print(self.mid.ticks_per_beat)        
        print("numerator = %d" %self.numerator)
        print("denominator = %d" %self.denominator)
        print(self.tempo)
        print(self.microsec_per_ticks)
        print("length = %f" %self.length)
        print("track_nom = %d" %self.track_num)
        for i in range(0, len(self.velocity[1])-1, 1):
            print({'note': self.note[1][i], 'vel': self.velocity[1][i], 'time':self.delta_t[1][i], 'rest':self.rests[1][i], 'slur':self.slur[1][i], 'staccato':self.staccato[1][i]})



if __name__=="__main__":
    midanalyzer = MIDIanalyzer()
    #midanalyzer.getMIDIfile('happyfarmer_60.mid')
    #midanalyzer.getMIDIfile('originalMIDI6.mid')
    midanalyzer.getMIDIfile('burgmuller-op100-la-chevaleresque.mid')
    #midanalyzer.getMIDIfile('Burgmuller_100_25_kifujin.mid')
    midanalyzer.getTicksPerBeat()
    midanalyzer.getTimeSignature()
    midanalyzer.getTempo()
    midanalyzer.getLength()
    midanalyzer.getTracknum()
    midanalyzer.getNoteData()
    midanalyzer.getRests()
    midanalyzer.getSlur()
    midanalyzer.getStaccato()
    #for msg in enumerate(midanalyzer.mid.tracks):
    #    print(msg)
    midanalyzer.checkBug()
    #midanalyzer.PrintBeat()