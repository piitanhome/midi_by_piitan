MIDI解析ツールについて
* MIDI解析ツールとは、その名の通りMIDIファイルを解析できます
* Scratch(https://scratch.mit.edu/)で使用できる様なファイル形式となっていますので、扱いにくい可能性があります


ファイルの実行について
* Pythonの実行環境がないと実行できません
* Pythonのバージョンは3.7以上推奨です(バージョン3.8で動作確認)
* フォルダ "midi" に解析したいMIDIファイルを入れ、ファイル名を "input.mid"(半角英字) とし、main.pyを実行してください


単位や仕様について
* 特に断りのない場合、時間の単位はms(ミリ秒)です
* Scratchの場合、テンポを60に設定するといいです(1秒=1拍となる)


出力ファイルについて
* ファイルサイズが大きいので通常のテキストエディタでは開かないでください。

* "output" フォルダ内に出力されます
* note.textに音程が保存されています
* note.textのファイルに スタート時間 番号 音程 鳴らす時間 音の強さ の順に連続して出力されます(1つ1つ改行されています)

* program.textのファイルに楽器の種類が保存されます(Scratchとの互換性はないので無視してもいいです)
* program.textのファイルに スタート時間 番号 音の種類 の順に連続して出力されます

* info.textのファイルに.midファイルの著作権や拍子などが保存されます
* 'info':'time_signature'を含む辞書の data/data_2 拍子です


Scratch以外で使用する場合
* main.pyファイルを開き、mainクラス/main関数の"ここから下はScratch用です"と書かれている場所の下の部分（関数内の全て）を削除して好きな様に保存し、実行してください


注意点(MITライセンスなど)
* このソフトウェアを誰でも無償で無制限に扱っても良いです。
* ただし、著作権表示および本許諾表示をソフトウェアのすべての複製または重要な部分に記載してください。（出力されたデータを使用した場合も含む）
* 作者または著作権者は、ソフトウェアに関してなんら責任を負いません。


バグの改善について
* バグと思われるエラーが起きた場合はお知らせください
  [Scratch](https://scratch.mit.edu/users/piitan_home/)


作成者 
* piitan_home [Scratch](https://scratch.mit.edu/users/piitan_home/)


"midi_by_piitan" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License)
