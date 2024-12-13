'''midiを解析します
このファイルを実行してください'''

import os
import json
import pprint
from smf_lib import Analysis


class Main:
    '''class main'''

    def __init__(self):
        self.settings = None

    @staticmethod
    def read_json(path: str) -> dict:
        '''設定ファイルを読み込みます'''
        with open(path) as k:
            tmp = json.load(k)
        return tmp

    @staticmethod
    def read_data(path: str) -> bytes:
        '''データ本体を読み込みます'''
        with open(path, 'rb') as k:
            tmp = k.read()
        return tmp

    @staticmethod
    def save_data(path: str, data: str):
        '''save data'''
        with open(path, 'w') as k:
            k.write(data)

    @staticmethod
    def get_program_str(data: dict):
        '''change change data for Scratch'''
        return '\n'.join([f"{d['cur_time']}\n{d['track_num'] * 16 + d['channel_num']}\n{d['program']}" for d in data])

    @staticmethod
    def get_data_str(data: dict):
        '''change data for Scratch'''
        return '\n'.join([f"{d['cur_time']}\n{d['track_num'] * 16 + d['channel_num']}\n{d['note_num']}\n{d['time']}\n{d['velocity']}" for d in data])

    def main(self):
        '''main'''
        self.settings = self.read_json('settings.json')
        data = self.read_data(self.settings['file_name'])
        midi = Analysis(data)  # データを解析
        midi.analysis()

        #<--------これが音程や時間の入ったデータ(listに辞書が入っている)-------->
        data = midi.get_data()
        # これが楽器の種類
        program = midi.get_program()
        # 情報
        info = midi.get_info()

        #<-------------------ここから下はScratch用です------------------->
        data_str = self.get_data_str(data)
        program_str = self.get_program_str(program)
        self.save_data(self.settings['save_dir'] + '/note.text', data_str)
        self.save_data(self.settings['save_dir'] +
                       '/program.text', program_str)
        self.save_data(self.settings['save_dir'] +
                       '/info.text', pprint.pformat(info))


if __name__ == "__main__":
    main = Main()
    main.main()
