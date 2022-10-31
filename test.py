import mido

#mid = mido.MidiFile('happyfarmer_60.mid')
#mid = mido.MidiFile('Dvorak_Humoreske_mb.mid')
#mid = mido.MidiFile('originalMIDI1.mid')
mid = mido.MidiFile('burgmuller-op100-la-chevaleresque.mid')
#mid = mido.MidiFile('Burgmuller_100_25_kifujin.mid')
#mid = mido.MidiFile('originalMIDI6.mid')
#print(mid.ticks_per_beat) 
#tickは4分音符を分割した長さの単位で，
#4分音符＝480ticks，8分音符=240ticks
#つまり1ticksをsに変換できれば時間が分かる
#↑はtempoでわかるらしい
#timeは前の指示の何秒後にこの音を鳴らすか
#4分音符は455ticks + 消音25ticksか？

#拍子やテンポ，その強弱はトラックという場所に格納される
#トラックはメッセージと呼ばれる命令の集合で構成される
for track in enumerate(mid.tracks):
    print(track)

for msg in mid.tracks[0]:
    #恐らく           ↑の数字はMidiTrackのことchannnel毎に分かれてる？
    if msg.type == 'note_on':
        print(msg)
        #print(msg.velocity) #音の強さ
        #print(msg.time)     #Δタイム

#for i, track in enumerate(mid.tracks):
#    print('Track {}: {}'.format(i, track.name))
#    for msg in track:
#        print(msg)
#        msg_string = str(msg)
#        print(msg_string[0])
        #なんと文字列変換成功！
        #MetaMessageクラスがよくわからない．
        #MetaMessageクラスにアクセスできないからどうしようもないが
        #文字列に変換できたので最悪文字列を解析すれば何とかなりそう
"""
#これで拍子が取れるようになった
for i, track in enumerate(mid.tracks):
    for msg in track:
        #print(msg)
        msg_string = str(msg)
        if(('numerator' in msg_string) and ('denominator' in msg_string)):
            numerator_index = msg_string.find('numerator') + 10
            denominator_index = msg_string.find('denominator') + 12
            numerator = int(msg_string[numerator_index])
            denominator = int(msg_string[denominator_index])
            print(msg)
            #print(numerator_index)
            print("numerator = %d" %numerator)
            print("denominator = %d" %denominator)
            
        #msg_string = str(msg)
        #point = msg_string.find('numerator')
        #print(point)
        #if('numerator' in msg_string):
        #        print("True")
"""
#これでtempoが取れるようになった
#tempoはms/beat
#デフォルトは4分音符1つに0.5秒=120bpm
"""
def get_tempo(mid):
    for msg in mid:
        if msg.type == 'set_tempo':
            return msg.tempo
    return 500000

print(get_tempo(mid))
"""