## PCでのボットの初回起動までの手順
**OSはWindowsだという前提で解説します**  
しばらくお待ちください....  
~~[動画での解説]()~~  


### Pythonのインストール
まずはPCに[Python 3.7](https://www.python.org/downloads/release/python-379 "python.org")をインストールします  
上記のリンクを開いたら、ページ下部にある`Windows x86-64 executable installer`  
をクリックしてPythonのインストーラーをダウンロードしてください  
ダウンロードが完了したらダウンロードしたインストーラーを起動してください  
起動したら`Add Python 3.7 to PATH`にチェックを入れ、`Install Now`をクリックし、インストールが完了するまで待ちます  

![インストーラー](https://user-images.githubusercontent.com/53356872/103261052-5527af00-49e3-11eb-8657-73d7dfd064d5.png)  

インストールが終わったらインストーラーを閉じます  

### gitのインストール
次に[git](https://git-scm.com/downloads "git-scm.com")をインストールします  
上記のリンクを開いたら、OSに合ったもの(今回はWindows)をクリックしてインストーラーをダウンロードしてください  
ダウンロードが完了したらダウンロードしたインストーラーを起動してください  

ライセンスを読み、`Next`をクリック  
![インストーラー](https://user-images.githubusercontent.com/53356872/104095053-185b9200-52d8-11eb-8f8b-3ca7b1c6e39e.png)  

特に拘りがなければそのまま`Next`  
![インストーラー](https://user-images.githubusercontent.com/53356872/104095103-5d7fc400-52d8-11eb-90e1-f00b5c378b7b.png)  

お好みで。良くわからなければそのまま`Next`  
![インストーラー](https://user-images.githubusercontent.com/53356872/104095141-94ee7080-52d8-11eb-89a8-1514b0c9b48f.png)  

お好みで
![インストーラー](https://user-images.githubusercontent.com/53356872/104095174-b51e2f80-52d8-11eb-98d0-8fc062e133b2.png)  

gitを使わないならそのまま`Next` * 9, `Install`  
使うなら読めば大体わかる...はず  

`Finish`をクリック  
![インストーラー](https://user-images.githubusercontent.com/53356872/104095506-86a15400-52da-11eb-8545-8a089c29a714.png)  

### Fortnite-LobbyBot-v2のセットアップ
Github上の[Fortnite-LobbyBot-v2のリポジトリ](https://github.com/gomashio1596/Fortnite-LobbyBot-v2 "github.com")を開き、`Code`ボタンを押して`Download Zip`を押します  
zipファイルのダウンロードが終わったら、そのファイルを解凍してください (解凍方法については解説しません)  
解凍したら中のファイルをPC上の適当な場所に配置してください  
中にあるINSTALLを実行してください (これは初回とアップデート時以外は実行する必要はありません)  

![ファイル](https://user-images.githubusercontent.com/53356872/104012669-91cd8480-51f3-11eb-9ae6-8dba0e75b927.png)  

インストールが終わったら画面を閉じ、RUNを実行してください (エラーが出た場合はPythonのバージョンなどが間違っている可能性があります)  
RUNを実行して出てきた画面をログやコンソールと呼びます  
`Webサーバーが 'XXX' で起動中です`の表示が出たら起動完了です  
ボットの[セットアップ](setup.md#セットアップの手順 "setup.md")に進んでください  
