'''
SMFファイルを解析します

made by piitan_home
'''

from math import ceil
from copy import deepcopy as copy

from .data import Data, NoteData, SubData, ChannelInfo
from .data import hex2int, hex2binlist, bin2int, file_error


class _HeaderChunk():
    '''ヘッダチャンクの解析をします'''

    def __init__(self, data: Data):
        self.data = data
        self.format = None
        self.track_size = None
        self.division = None

    def analysis(self):
        '''analysis'''
        chunk_type = self.data.read(4)
        if chunk_type != '4D546864':
            file_error()

        (header_size, self.format, self.track_size,
         time_base) = self.data.read_all(4, 2, 2, 2)
        # 将来ファイルが拡張した時ように場所を計算しておく
        self.data.pos += hex2int(header_size)-6

        if hex2binlist(time_base, 1)[0] == '0':
            time_hex = hex2binlist(time_base, 1, 15)[1]
            self.division = bin2int(time_hex)
        else:
            raise Exception('設定されていないファイル形式:division-format2')


class _TrackChunkBase:
    def __init__(self, data: Data, header: _HeaderChunk, track_num):
        self.data = data
        self.header = header
        self.track_num = track_num
        self.time = 0

    def get_delta_time(self):
        '''可変長(主にデルタタイム)形式でデータを取得します'''
        txt = ''
        while True:
            flag, d = hex2binlist(self.data.read(1), 1, 7)
            txt += d
            if flag == '0':
                return bin2int(txt)

    def get_note(self, cur_time=None) -> NoteData:
        '''get note'''
        note = NoteData(self.track_num)
        if cur_time is None:
            note.cur_time = self.time
        else:
            note.cur_time = cur_time
        return note

    def get_sub_data(self, info=None) -> SubData:
        '''get sub_data'''
        sub_data = SubData(self.track_num)
        if not info is None:
            sub_data.info = info
        return sub_data


class _TrackChunkEvent(_TrackChunkBase):
    def __init__(self, data: Data, header: _HeaderChunk, track_num):
        super().__init__(data, header, track_num)
        self.long_flags = [[None for i in range(128)]for j in range(16)]
        self.channel_info = [ChannelInfo() for i in range(16)]
        self.note = []
        self.program = []
        self.__omni_off = False

    def get_volume(self, channel_num, velocity):
        '''get volume'''
        channel_info = self.channel_info[channel_num]
        expression = channel_info.expression
        channel_volume = channel_info.channel_volume
        return (expression * channel_volume * velocity) // (127**2)

    def add_note(self, note_num, channel_num):
        '''add note_list'''
        long_flags = self.long_flags[channel_num][note_num]
        if long_flags is not None:
            note = self.get_note(long_flags.cur_time)
            note.time = self.time - long_flags.cur_time
            note.channel_num = channel_num
            note.note_num = note_num
            note.velocity = self.get_volume(channel_num, long_flags.velocity)
            self.note.append(note)
            long_flags = None

    def midi_event_note(self, event, channel_num):
        '''midi event'''
        if event in ['8', '9']:  # ノートオフ, ノートオン
            # ノートナンバー
            note_num = hex2int(self.data.read(1))
            if event == '9':
                velocity = hex2int(self.data.read(1))
            else:
                velocity = 0
                self.data.pos += 1

            self.add_note(note_num, channel_num)

            if velocity != 0:
                note = self.get_note()
                note.velocity = velocity
                self.long_flags[channel_num][note_num] = note

    def midi_event_cc(self, channel_num, cc_num):
        'midi event control change'
        # オールサウンドオフ
        if cc_num == '07':
            self.channel_info[channel_num].channel_volume = hex2int(
                self.data.read(1))

        elif cc_num == '11':
            self.channel_info[channel_num].expression = hex2int(
                self.data.read(1))

        elif cc_num in ['78', '7B']:
            for i, long_flags in enumerate(self.long_flags):
                for j, _ in enumerate(long_flags):
                    self.add_note(j, i)
            self.data.pos += 1

        # omni
        elif cc_num == '7C':
            self.__omni_off = True
            self.data.pos += 1
        elif cc_num == '7D':
            self.__omni_off = False
            self.data.pos += 1
        elif cc_num == '7E':
            if self.__omni_off:
                self.data.pos += 2
            else:
                self.data.pos += 1

        else:
            self.data.pos += 1

    def midi_event(self, event, channel_num):
        '''midi event'''
        # ポリフォニックキープレッシャー(押されている鍵盤を押さえ直す)
        if event == 'A':
            self.data.pos += 2
        # プログラムチェンジ(音色の種類を変更)
        elif event == 'C':
            note = self.get_note()
            note.channel_num = channel_num
            note.program = hex2int(self.data.read(1))
            self.program.append(note)
        # チャンネルプレッシャー(ポリフォニックキープレッシャーのチャンネル全ての音)
        elif event == 'D':
            self.data.pos += 1
        elif event == 'E':  # ピッチベンド
            self.data.pos += 2


class _TrackChunk(_TrackChunkEvent):
    '''トラックチャンクの解析をします'''

    def __init__(self, data: Data, header: _HeaderChunk, track_num):
        super().__init__(data, header, track_num)
        self.tempo = []
        self.info = []
        self.__last_event = None

    def analysis(self):
        '''analysis'''
        chunk_type = self.data.read(4)
        if chunk_type != '4D54726B':
            file_error()

        size = hex2int(self.data.read(4))
        end = self.data.pos + size

        self.time = 0
        self.__last_event = None
        while end > self.data.pos:
            delta_time = self.get_delta_time()
            self.time += delta_time

            self.event()

    def event(self):
        '''event'''
        # ランニングステータス適用時
        data = self.data.read(1)
        if hex2binlist(data, 1)[0] == '0':
            self.data.pos -= 1
            event = self.__last_event
        else:
            event = data

        if event[0] in ['8', '9']:
            self.midi_event_note(event[0], hex2int(event[1]))
        elif event[0] in ['B']:
            self.midi_event_cc(hex2int(event[1]), self.data.read(1))
        elif event[0] in ['A', 'C', 'D', 'E']:
            self.midi_event(event[0], hex2int(event[1]))
        elif event in ['F0', 'F7']:
            self.sys_ex_event()
        elif event in ['FF']:
            self.meta_event(self.data.read(1), self.get_delta_time())

        self.__last_event = event

    def sys_ex_event(self):
        '''SysEx event'''
        length = self.get_delta_time()
        self.data.pos += length

    def meta_event(self, meta_event, length):
        '''meta event'''
        if hex2int(meta_event) <= hex2int('9'):
            sub_data = self.get_sub_data('comment')
            sub_data.data = self.data.read_ascii(length)
            self.info.append(sub_data)
        # トラック終端
        elif meta_event == '2F':
            pass

        # tempoについて
        # BPM(1分間の4分音符の個数) = tempo * division
        elif meta_event == '51':
            tempo = hex2int(self.data.read(length))
            tempo = 60000000 // tempo
            division = self.header.division
            tick = 60000 / (tempo * division)

            sub_data = self.get_sub_data()
            sub_data.data = tick
            sub_data.cur_time = self.time
            self.tempo.append(sub_data)

        elif meta_event == '54':
            self.data.pos += length

        elif meta_event == '58':
            nn = hex2int(self.data.read(1))
            dd = hex2int(self.data.read(1))
            self.data.pos += 2

            sub_data = self.get_sub_data('time_signature')
            sub_data.data = nn
            sub_data.data_2 = 2**dd
            self.info.append(sub_data)

        elif meta_event == '59':
            sf = self.data.read(1)
            mi = self.data.read(1)

            sub_data = self.get_sub_data('key_signature')
            sub_data.data = sf
            self.info.append(sub_data)

            sub_data = self.get_sub_data('key')
            sub_data.data = mi
            self.info.append(sub_data)
        else:
            self.data.pos += length


class UpdateTimes:
    '''update times'''

    def __init__(self, tempo, note, *args):
        self.tempo = tempo
        self.note = note
        self.data = args

    def update(self):
        '''update tempo'''
        old_tempo = copy(self.tempo)
        for i in range(1, len(old_tempo)):
            time_difference = old_tempo[i].cur_time - old_tempo[i-1].cur_time
            self.tempo[i].cur_time = (time_difference * self.tempo[i-1].data)\
                + self.tempo[i-1].cur_time

        self.__update_list(old_tempo, self.note, type_='note')
        for data in self.data:
            self.__update_list(old_tempo, data)

    def __update_list(self, old_tempo, data: list, type_=None):
        len_data = len(data)
        len_tempo = len(self.tempo)
        for i in range(len_data):
            for j in reversed(range(len_tempo)):
                # テンポ変更後なら
                if data[i].cur_time >= old_tempo[j].cur_time:
                    time_difference = data[i].cur_time - \
                        old_tempo[j].cur_time
                    data[i].cur_time = ceil(
                        time_difference * self.tempo[j].data + self.tempo[j].cur_time)
                    if type_ == 'note':
                        data[i].time = ceil(data[i].time * self.tempo[j].data)
                    break

class Analysis():
    '''class analysis'''

    def __init__(self, info: bytes):
        self.data = Data(info)
        self.header = None
        self.tempo = []
        self.program = []
        self.note = []
        self.info = []

    def analysis(self):
        '''analysis'''
        self.header = _HeaderChunk(self.data)
        self.header.analysis()
        for i in range(hex2int(self.header.track_size)):
            track = _TrackChunk(self.data, self.header, i)
            track.analysis()
            self.info += track.info
            self.note += track.note
            self.program += track.program
            self.tempo += track.tempo
            del track
        self.note.sort()
        self.tempo.sort()
        times = UpdateTimes(self.tempo, self.note, self.program)
        times.update()

    def get_data(self):
        '''get data'''
        return [vars(i) for i in self.note]

    def get_program(self):
        '''get program'''
        return [vars(i) for i in self.program]

    def get_info(self):
        '''get info'''
        return [vars(i) for i in self.info]
