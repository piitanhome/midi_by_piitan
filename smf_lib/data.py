'''データなどの読み取りを行います'''


def bin2int(num: bin) -> int:
    '''bin -> int'''
    return int(num, 2)


def hex2int(num: int) -> int:
    '''hex -> int'''
    return int(num, 16)


def hex2bin(num: hex) -> bin:
    '''hex -> bin'''
    return bin(hex2int(num))[2:]


def binlist(num: bin, length: int, *counts: int) -> bin:
    '''bin -> binlist'''
    data = num.zfill(length)
    i = 0
    l = []
    for count in counts:
        l.append(data[i: i+count])
        i += count
    return tuple(l)


def hex2binlist(num: hex, *counts: int) -> bin:
    '''hex -> binlist'''
    return binlist(hex2bin(num), len(num)*4, *counts)


def file_error():
    '''file error'''
    raise Exception('SMF(.mid)ファイルではないか、ファイルが破損しています')


class Data:
    '''データの読み取りなどを行います'''

    def __init__(self, info: bytes):
        self.__info = info
        self.__pos = 0

    def __read(self, number: int):
        data = self.__info[self.pos:self.pos+number]
        self.pos += number
        return data

    def read(self, number: int) -> hex:
        '''read -> return hex'''
        return self.__read(number).hex().upper()

    def read_all(self, *numbers: int) -> hex:
        '''read -> num1, num2, ...'''
        l = []
        for number in numbers:
            l.append(self.read(number))
        return tuple(l)

    def read_ascii(self, number: int):
        '''read -> return ascii(data)'''
        try:
            data = chr(self.__read(number))
        except Exception:
            data = 'error'
        return data

    @property
    def pos(self) -> int:
        '''pos'''
        return self.__pos

    @pos.setter
    def pos(self, obj):
        '''set pos'''
        if not isinstance(self.__pos, int):
            raise TypeError
        self.__pos = obj


class MiniData:
    '''class mini_data'''

    def __init__(self, track_num):
        self.track_num = track_num
        self.cur_time = None

    # ソート要員
    def __lt__(self, obj):
        return self.cur_time < obj.cur_time

    def __gt__(self, obj):
        return not self.__lt__(obj)


class NoteData(MiniData):
    '''class note_on'''

    def __init__(self, track_num):
        super().__init__(track_num)
        self.time = None
        self.channel_num = None
        self.note_num = None
        self.velocity = None


class SubData(MiniData):
    '''class sub_data'''

    def __init__(self, track_num):
        super().__init__(track_num)
        self.info = None
        self.data = None
        self.data_2 = None


class ChannelInfo(MiniData):
    '''class channel_info'''
    def __init__(self, track_num=None):
        super().__init__(track_num)
        self.channel_volume = 127
        self.expression = 127
