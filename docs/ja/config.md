## コンフィグ
基本的にはWebのコンフィグエディターから設定を変更してください  
**生のconfigファイルを編集するのは上級者向け機能です**  
**予期せぬバグが発生する可能性があります**  

### クライアント (clients)
#### フォートナイト (fortnite)
|  キー (生の値)  |  説明  |
| ---- | ---- |
|  メールアドレス (email)  |  ボットとして起動させるアカウントのメールアドレス  |
|  ニックネーム (nickname)  |  Web起動スイッチで使用する名前  |
|  所有者 (owner)  |  所有者として指定するユーザーの名前かID<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  コスチューム (outfit)  |  ボットが初期で使用するコスチュームの名前かID  |
|  コスチュームのスタイル (outfit_style)  |  ボットが初期で使用するコスチュームのスタイルの名前かID  |
|  NGコスチューム (ng_outfits)  |  NGに指定するコスチュームの名前かID<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  NGコスチュームの適用先 (ng_outfit_for)  |  NGコスチュームを適用するユーザーの種類  |
|  NGコスチューム発動時の操作  |  NGコスチュームが発動した時に実行する操作  |
|  NGコスチューム発動時のリプライ  |  NGコスチュームが発動した時に送るテキスト  |
|  参加時のコスチューム (join_outfit)  |  パーティーに参加した際に使用するコスチュームの名前かID  |
|  参加時のコスチュームのスタイル (join_outfit_style)  |  パーティーに参加した際に使用するコスチュームのスタイルの名前かID  |
|  参加時のコスチュームを発動 (join_outfit_when)  |  どの動作で参加時のコスチュームを発動するか  |
|  離脱時のコスチューム (leave_outfit)  |  パーティーを離脱した際に使用するコスチュームの名前かID  |
|  離脱時のコスチュームのスタイル (leave_outfit_style)  |  パーティーを離脱した際に使用するコスチュームのスタイルの名前かID  |
|  離脱時のコスチュームを発動 (leave_outfit_when)  |  どの動作で離脱時のコスチュームを発動するか  |
|  コスチュームミミックの適用先 (outfit_mimic_for)  |  コスチュームミミックを適用するユーザーの種類  |
|  コスチュームロックの適用先 (outfit_lock_for)  |  コスチュームロックを適用するユーザーの種類  |
|  バックパック (backpack)  |  ボットが初期で使用するバックパックの名前かID  |
|  バックパックのスタイル (backpack_style)  |  ボットが初期で使用するバックパックのスタイルの名前かID  |
|  NGバックパック (ng_backpacks)  |  NGに指定するバックパックの名前かID<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  NGバックパックの適用先 (ng_backpack_for)  |  NGバックパックを適用するユーザーの種類  |
|  NGバックパック発動時の操作  |  NGバックパックが発動した時に実行する操作  |
|  NGバックパック発動時のリプライ  |  NGバックパックが発動した時に送るテキスト  |
|  参加時のバックパック (join_backpack)  |  パーティーに参加した際に使用するバックパックの名前かID  |
|  参加時のバックパックのスタイル (join_backpack_style)  |  パーティーに参加した際に使用するバックパックのスタイルの名前かID  |
|  参加時のバックパックを発動 (join_backpack_when)  |  どの動作で参加時のバックパックを発動するか  |
|  離脱時のバックパック (leave_backpack)  |  パーティーを離脱した際に使用するバックパックの名前かID  |
|  離脱時のバックパックのスタイル (leave_backpack_style)  |  パーティーを離脱した際に使用するバックパックのスタイルの名前かID  |
|  離脱時のバックパックを発動 (leave_backpack_when)  |  どの動作で離脱時のバックパックを発動するか  |
|  バックパックミミックの適用先 (backpack_mimic_for)  |  バックパックミミックを適用するユーザーの種類  |
|  バックパックロックの適用先 (backpack_lock_for)  |  バックパックロックを適用するユーザーの種類  |
|  収集ツール (pickaxe)  |  ボットが初期で使用する収集ツールの名前かID  |
|  収集ツールのスタイル (pickaxe_style)  |  ボットが初期で使用する収集ツールのスタイルの名前かID  |
|  収集ツールを表示 (do_point)  |  収集ツールの切り替え時に自動でポイントアウトを実行するか  |
|  NG収集ツール (ng_pickaxes)  |  NGに指定する収集ツールの名前かID<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  NG収集ツールの適用先 (ng_pickaxe_for)  |  NG収集ツールを適用するユーザーの種類  |
|  NG収集ツール発動時の操作  |  NG収集ツールが発動した時に実行する操作  |
|  NG収集ツール発動時のリプライ  |  NG収集ツールが発動した時に送るテキスト  |
|  参加時の収集ツール (join_pickaxe)  |  パーティーに参加した際に使用する収集ツールの名前かID  |
|  参加時の収集ツールのスタイル (join_pickaxe_style)  |  パーティーに参加した際に使用する収集ツールのスタイルの名前かID  |
|  参加時の収集ツールを発動 (join_pickaxe_when)  |  どの動作で参加時の収集ツールを発動するか  |
|  離脱時の収集ツール (leave_pickaxe)  |  パーティーを離脱した際に使用する収集ツールの名前かID  |
|  離脱時の収集ツールのスタイル (leave_pickaxe_style)  |  パーティーを離脱した際に使用する収集ツールのスタイルの名前かID  |
|  離脱時の収集ツールを発動 (leave_pickaxe_when)  |  どの動作で離脱時の収集ツールを発動するか  |
|  収集ツールミミックの適用先 (pickaxe_mimic_for)  |  収集ツールミミックを適用するユーザーの種類  |
|  収集ツールロックの適用先 (pickaxe_lock_for)  |  収集ツールロックを適用するユーザーの種類  |
|  エモート (emote)  |  ボットが初期で使用するエモートの名前かID  |
|  エモートのセクション (emote_section)  |  ボットが初期で使用するエモートのセクション  |
|  NGエモート (ng_emotes)  |  NGに指定するエモートの名前かID<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  NGエモートの適用先 (ng_emote_for)  |  NGエモートを適用するユーザーの種類  |
|  NGエモート発動時の操作  |  NGエモートが発動した時に実行する操作  |
|  NGエモート発動時のリプライ  |  NGエモートが発動した時に送るテキスト  |
|  参加時のエモート (join_emote)  |  パーティーに参加した際に使用するエモートの名前かID  |
|  参加時のエモートのセクション (join_emote_section)  |  パーティーに参加した際に使用するエモートのセクション  |
|  参加時のエモートを発動 (join_emote_when)  |  どの動作で参加時のエモートを発動するか  |
|  離脱時のエモート (leave_emote)  |  パーティーを離脱した際に使用するエモートの名前かID  |
|  離脱時のエモートのセクション (leave_emote_section)  |  パーティーを離脱した際に使用するエモートのセクション  |
|  離脱時のエモートを発動 (leave_emote_when)  |  どの動作で離脱時のエモートを発動するか  |
|  エモートミミックの適用先 (emote_mimic_for)  |  エモートミミックを適用するユーザーの種類  |
|  エモートロックの適用先 (emote_lock_for)  |  エモートロックを適用するユーザーの種類  |
|  パーティー離脱の遅延 (leave_delay_for)  |  パーティー離脱をどのくらい遅延させるか  |
|  reloadコマンド時に装備品をリセットするか (refresh_on_reload)  |  reloadコマンド時に装備品をリセットするか  |

##### パーティー (party)
|  キー (生の値)  |  説明  |
| --- | --- |
|  プライバシー (privacy)  |  パーティーのプライバシー  |
|  パーティーの最大サイズ (max_size)  |  パーティーの最大サイズ  |
|  位置変更を許可 (allow_swap)  |  位置変更(スクワッドフォーメーション)を許可  |
|  プレイリスト (playlist)  |  パーティーのプレイリスト(ゲームモード)  |
|  ボイスチャットを無効化 (disable_voice_chat)  |  パーティーのボイスチャットを無効化  |

|  キー (生の値)  |  説明  |
| --- | --- |
|  アバターID (avatar_id)  |  アバターのID<br>`{bot}`とすることで現在使用しているコスチュームのアイコンになる(非対応の物も多い)  |
|  アバターの色 (avatar_color)  |  アバターの色<br>詳細は[こちら](#色)  |
|  バナーのID (banner_id)  |  バナーのID<br>一覧は[こちら](https://fnitems.hyperserver.xyz/banners)  |
|  バナーの色 (banner_color)  |  バナーの色  |
|  レベル (level)  |  レベル  |
|  ティア (tier)  |  ティア  |
|  プラットフォーム (platform)  |  プラットフォーム  |
|  NGプラットフォーム (ng_platforms)  |  NGに指定するプラットフォーム  |
|  NGプラットフォームの適用先 (ng_platform_for)  |  NGプラットフォームを適用するユーザーの種類  |
|  NGプラットフォーム発動時の操作 (ng_platform_operation)  |  NGプラットフォームが発動したときの操作  |
|  NGプラットフォーム発動時のリプライ  |  NGプラットフォームが発動した時に送るテキスト  |

##### NGネーム (ng_names)
|  キー (生の値)  |  説明  |
| --- | --- |
|  マッチ方式 (matchmethod)  |  単語がどのように入っていたら発動するか  |
|  単語 (word)  |  このNGネームに使う単語  |

|  キー (生の値)  |  説明  |
| --- | --- |
|  NGネームの適用先 (ng_name_for)  |  NGネームを適用するユーザーの種類  |
|  NGネーム発動時の操作 (ng_name_operation)  |  NGネームが発動した時の操作  |
|  NGネーム発動時のリプライ  |  NGネームが発動した時に送るテキスト  |
|  ステータス (status)  |  ステータス<br>[変数](#変数)が使える  |
|  招待を承諾 (accept_invite_for)  |  招待を承諾するユーザーの種類  |
|  パーティーにいるとき招待を拒否 (decline_invite_when)  |  パーティーにいるときに招待を拒否するユーザーの種類  |
|  招待承諾の間隔 (invite_interval)  |  招待を承諾してから次招待を承諾するようになるまでに時間(秒)  |
|  招待承諾の間隔の適用先 (invite_interval_for)  |  招待承諾の間隔を適用するユーザーの種類  |
|  フレンドリクエストを承諾 (accept_friend_for)  |  フレンドリクエストを承諾するユーザーの種類  |
|  パーティーメンバーなどにフレンドリクエストを送信 (send_friend_request)  |  パーティーメンバーなどにフレンドリクエストを自動送信するか  |
|  ささやきからのコマンドを許可 (whisper_enable_for)  |  ささやきからのコマンドを許可するユーザーの種類  |
|  パーティーチャットからのコマンドを許可 (party_chat_enable_for)  |  パーティーチャットからのコマンドを許可するユーザーの種類  |
|  権限不足時の操作 (permission_command_operation)  |  権限不足時(所有者限定コマンドを実行したときなど)の操作  |
|  パーティー参加を許可 (accept_join_for)  |  パーティー参加を許可するユーザーの種類  |
|  パーティー参加時のメッセージ (join_message)  |  パーティー参加時にパーティーチャットに送るメッセージ<br>[変数](#変数)が使える  |
|  パーティー参加時のささやきメッセージ (join_message_whisper)  |  パーティー参加時にささやきに送るメッセージ<br>[変数](#変数)が使える  |
|  パーティー参加時のランダムメッセージ (random_message)  |  パーティー参加時にパーティチャットに送るメッセージ<br>一つがランダムで選ばれる<br>[変数](#変数)が使える  |
|  パーティー参加時のささやきのランダムメッセージ (random_message_whisper)  |  パーティー参加時にささやきに送るメッセージ<br>一つがランダムで選ばれる<br>[変数](#変数)が使える  |
|  チャットの最大文字数 (chat_max)  |  チャットで許可する最大文字数  |
|  最大文字数の適用先 (chat_max_for)  |  チャットの最大文字数を適用するユーザーの種類  |
|  最大文字数発動時の操作 (chat_max_operation)  |  チャットの最大文字数発動時の操作  |
|  切断されたユーザーをキック (kick_disconnect)  |  切断状態になったユーザーをキックするか  |
|  マッチ状態のユーザーをキック (kick_in_match)  |  マッチ状態になったユーザーをキックするか  |
|  パーティーで非表示 (hide_for)  |  パーティーで非表示にするユーザーの種類  |
|  ブラックリスト (blacklist)  |  ブラックリストに指定するユーザーの名前かID<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  ブラックリストユーザーの操作 (blacklist_operation)  |  ブラックリストのユーザーにする操作  |
|  ホワイトリスト (whitelist)  |  ホワイトリストに指定するユーザーの名前かID<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  招待リスト (invitelist)  |  招待リストに指定するユーザー<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  ボットリスト (botlist)  |  ボットリストに指定するユーザー<br>これ自体に特に効果はなく、識別にだけ用いられる  |
|  ボットリストの操作 (botlist_operation)  |  ボットリストのユーザーにする操作  |
|  プレフィックス (prefix)  |  コマンドの初めにつける文字列  |

##### プログラム実行 (exec)
|  キー (生の値)  |  説明  |
| --- | --- |
|  起動時のプログラム (ready)  |  起動時に実行するプログラム  |
|  参加リクエスト時のプログラム (party_join_request)  |  参加リクエスト時に実行するプログラム  |
|  招待時のプログラム (party_invite)  |  招待受け取り時に実行するプログラム  |
|  フレンドリクエスト時のプログラム (friend_request)  |  フレンドリクエスト受け取り時に実行するプログラム  |
|  フレンド追加時のプログラム (friend_add)  |  フレンド追加時に実行するプログラム  |
|  フレンド削除時のプログラム (friend_remove)  |  フレンド削除時に実行するプログラム  |
|  メンバー参加時のプログラム (party_member_join)  |  メンバー参加時に実行するプログラム  |
|  メンバー離脱時のプログラム (party_member_leave)  |  メンバー離脱時に実行するプログラム  |
|  メンバー承認リクエスト時のプログラム (party_member_confirm)  |  メンバー承認リクエスト時に実行するプログラム  |
|  メンバーキック時のプログラム (party_member_kick)  |  メンバーキック時に実行するプログラム  |
|  リーダー譲渡時のプログラム (party_member_promote)  |  リーダー譲渡時に実行するプログラム  |
|  パーティー更新時のプログラム (party_update)  |  パーティー更新時に実行するプログラム  |
|  メンバー更新時のプログラム (party_member_update)  |  メンバー更新時に実行するプログラム  |
|  メンバー切断時のプログラム (party_member_disconnect)  |  メンバー切断時に実行するプログラム  |

#### Discord (discord)
|  キー (生の値)  |  説明  |
| --- | --- |
|  Discordボットを起動 (enabled)  |  Discordボットを起動するか  |
|  Discordボットのトークン (token)  | Discordボットのトークン  |
|  所有者 (owner)  |  所有者として指定するユーザーの名前かID<br>これ自体に特に効果はなく、識別にだけ用いられる<br>IDの取得方法は[こちら](https://support.discord.com/hc/ja/articles/206346498)  |
|  コマンドチャンネル (channels)  |  コマンドチャンネルに指定するチャンネル名<br>詳細は[こちら](#コマンドチャンネル)  |
|  ステータス (status)  |  ステータスに表示する文字列<br>[変数](#変数)が使える  |
|  ステータスの種類 (status_type)  |  ステータスの種類  |
|  チャットの最大文字数 (chat_max)  |  チャットで許可する最大文字数  |
|  最大文字数の適用先 (chat_max_for)  |  チャットの最大文字数を適用するユーザーの種類  |
|  コマンドを許可 (command_enable_for)  |  Discordからのコマンドを許可するユーザーの種類  |
|  ブラックリスト (blacklist)  |  Discordのブラックリストに指定するユーザーのID<br>これ自体に特に効果はなく、識別にだけ用いられる<br>IDの取得方法は[こちら](https://support.discord.com/hc/ja/articles/206346498)  |
|  ホワイトリスト (whitelist)  | Discordのホワイトリストに指定するユーザーのID<br>これ自体に特に効果はなく、識別にだけ用いられる<br>IDの取得方法は[こちら](https://support.discord.com/hc/ja/articles/206346498)  |
|  プレフィックス (prefix)  |  コマンドの初めにつける文字列  |

##### プログラム実行 (exec)
|  キー (生の値)  |  説明  |
| --- | --- |
|  起動時のプログラム (ready)  |  起動時に実行するプログラム  |

#### NGワード (ng_words)
|  キー (生の値)  |  説明  |
| --- | --- |
|  回数 (count)  |  NGワードを実行するために必要なNGワードの入力回数  |
|  マッチ方式 (matchmethod)  |  単語がどのように入っていたら発動するか  |
|  単語 (words)  |  このNGワードに指定する単語  |

|  キー (生の値)  |  説明  |
| --- | --- |
|  NGワードの適用先 (ng_word_for)  |  NGワードを適用するユーザーの種類  |
|  NGワード発動時の操作 (ng_word_operation)  |  NGワードが発動した時の操作  |
|  NGワード発動時のリプライ  |  NGワードが発動した時に送るテキスト  |
|  再ログインまでの時間 (relogin_in)  |  このボットが起動してから再ログインするまでの時間(秒)  |
|  最大検索数 (search_max)  |  検索機能があるコマンドを使用するときに、結果を表示する最大数  |
|  ログを無効化 (no_logs)  |  このボットのログを無効化するか  |
|  ログレベル (loglevel)  |  ログにどのくらい情報を出すか  |
|  Discordログ (discord_log)  |  Discordにログを送信するためのWebhookのURL<br>Webhookの作成方法は[こちら](https://support.discord.com/hc/ja/articles/228383668)  |
|  2000文字以上を省略 (omit_over2000)  |  Discordログで2000文字以上を省略するか  |
|  ログが過剰に溜まった場合スキップ (skip_if_overflow)  |  Discordのログの送信が間に合わず過剰に溜まった場合はスキップするか  |
|  大文字小文字を区別しない (case_insensitive)  |  コマンドなどで大文字小文字を区別しないか  |
|  漢字を平仮名に変換 (convert_kanji)  |  コマンドなどで漢字を自動的に平仮名に変換して認識させるか  |

### Discord (discord)
上記のDiscordを参照

### Web (web)
|  キー (生の値)  |  説明  |
| --- | --- |
|  Webを有効化 (enabled)  |  Webサーバーを起動するか  |
|  WebサーバーのIP (ip)  |  Webサーバーに使用するIP<br>`{ip}`とすることで自動で設定する  |
|  Webサーバーのポート (port)  |  Webサーバーに使用するポート  |
|  Webサーバーのパスワード  (password)  |  Webサーバーのログインに使用するパスワード  |
|  ログインが必要 (login_required)  |  Webサーバーへのアクセスにパスワードを要求するか  |
|  コマンドを有効化 (command_web)  |  Webサーバーからのコマンドを許可するか  |
|  アクセスログを表示 (access_log)  |  Webサーバーのアクセスログを表示するか  |
|  プレフィックス (prefix)  |  コマンドの初めにつける文字列  |

|  キー (生の値)  |  説明  |
| --- | --- |
|  起動時にアップデートを確認 (check_update_on_startup)  |  起動時にアップデートを確認するか  |
|  再起動までの時間 (restart_in)  |  ボットが起動してから再起動するまでの時間(秒)  |
|  ボットの言語 (lang)  |  ボットの表示言語  |
|  ボットの検索言語 (search_lang)  |  ボットのアイテム検索に使う言語  |
|  ボットのサブ検索言語 (sub_search_lang)  |  ボットのアイテム検索に使うサブ言語  |
|  使用するAPI (api)  |  アイテムデータの取得に使うAPI  |
|  APIキー (api_key)  |  APIがFortniteApi.ioの時に使用するAPIキー  |
|  Discordログ (discord_log)  |  Discordにログを送信するためのwebhookのURL<br>Webhookの作成方法は[こちら](https://support.discord.com/hc/ja/articles/228383668)  |
|  2000文字以上を省略 (omit_over2000)  |  Discordログで2000文字以上を省略するか  |
|  ログが過剰に溜まった場合スキップ (skip_if_overflow)  |  Discordのログの送信が間に合わず過剰に溜まった場合はスキップするか  |
|  メールアドレスを隠す  |  Discordログでメールアドレスを隠すか  |
|  パスワードを隠す  |  Discordログでパスワードを隠すか  |
|  トークンを隠す  |  DiscordログでDiscordボットのトークンを隠すか  |
|  Webhookを隠す  |  DiscordログでWebhookのURLを隠すか  |
|  Weburlを隠す  |  DiscordログでWebサーバーのURLを隠すか  |
|  ログを無効化 (no_logs)  |  ログを無効化するか  |
|  ログレベル (loglevel)  |  ログにどのくらい情報を出すか  |
|  デバッグ情報を表示 (debug)  |  fortnitepyのデバッグ情報を表示するか  |


## その他の解説
### 変数
場合によって変動する値を組み込みたい際に使用する  
書き込む際は名前を{}で囲んで使う (例: バトルロイヤルロビー - {party_size} / {party_max_size})  

#### 基本の変数
|  名前  |  説明  |
| --- | --- |
|  self  |  クライアントのインスタンス  |
|  client  |  クライアントのインスタンス  |
|  discord_bot  |  クライアントのDiscordボット  |
|  party  |  クライアントのパーティー  |
|  party_id  |  クライアントのパーティーのID  |
|  party_size  |  クライアントのパーティーのサイズ  |
|  party_max_size  |  クライアントのパーティーの最大サイズ  |
|  friends  |  クライアントのフレンドのインスタンス<br>List\[fortnitepy.Friend\]  |
|  friend_count  |  クライアントのフレンド数  |
|  online_friends  |  クライアントのオンラインのフレンドのインスタンス<br>List\[fortnitepy.Friend\]  |
|  online_friend_count  |  クランとのオンラインのフレンドの数  |
|  offline_friends  |  クライアントのオフラインのフレンドのインスタンス<br>List\[fortnitepy.Friend\]  |
|  offline_friend_count  |  クランとのオフラインのフレンドの数  |
|  pending_friends  |  クライアントの送信/受信したフレンドリクエストのインスタンス<br>List\[Union\[fortnitepy.IncomingPendingFriend, fortnitepy.OutgoingPendingFriend\]\]  |
|  pending_count  |  クライアントの送信/受信したフレンドリクエスト数  |
|  incoming_pending_friends  |  クライアントの受信したフレンドリクエストのインスタンス<br>List\[fortnitepy.IncomingPendingFriend\]  |
|  incoming_pending_count  |  クライアントの受信したフレンドリクエスト数  |
|  outgoing_pending_friends  |  クライアントの送信したフレンドリクエストのインスタンス<br>List\[fortnitepy.OutgoingPendingFriend\]  |
|  outgoing_pending_count  |  クライアントの送信したフレンドリクエスト数  |
|  blocked_users  |  クライアントがブロックしたユーザーのインスタンス<br>List\[fortnitepy.BlockedUser\]  |
|  block_count  |  クライアントがブロックしたユーザー数  |
|  display_name  |  クライアントのディスプレイネーム  |
|  account_id  |  クライアントのアカウントID  |
|  uptime  |  クライアントの起動時間のインスタンス<br>datetime.timedelta  |
|  uptime_days  |  クライアントの起動時間(日)  |
|  uptime_hours  |  クライアントの起動時間(時間)  |
|  uptime_minutes  |  クライアントの起動時間(分)  |
|  uptime_seconds  |  クライアントの起動時間(秒)  |
|  owner  |  所有者のインスタンス<br>List[fortnitepy.User]  |
|  whitelist  |  ホワイトリストのユーザーのインスタンス<br>List[fortnitepy.User]  |
|  blacklist  |  ブラックリストのユーザーのインスタンス<br>List[fortnitepy.User]  |
|  botlist  |  ボットリストのユーザーのインスタンス<br>List[fortnitepy.User]  |
|  invitelist  |  招待リストのユーザーのインスタンス<br>List[fortnitepy.User]  |

#### パーティー参加時のメッセージで使える追加変数
|  名前  |  説明  |
| --- | --- |
|  member  |  参加したメンバーのインスタンス<br>fortnitepy.PartyMember  |
|  member_display_name  |  参加したメンバーのディスプレイネーム  |
|  member_id  |  参加したメンバーのID  |
|  inviter  |  招待したユーザーのインスタンス (ボット自身が招待されて参加した場合のみ)<br>Optional[fortnitepy.Friend]  |

#### カスタムコマンド/リプライで使える追加変数
|  名前  |  説明  |
| --- | --- |
|  message  |  メッセージのインスタンス<br>Union[fortnitepy.FriendMessage, fortnitepy.PartyMessage, discord.Message, DummyMessage]  |
|  author  |  メッセージの送り主のインスタンス<br>Union[fortnitepy.User, discord.User, WebUser]  |
|  author_display_name  |  メッセージの送り主のディスプレイネーム  |
|  author_id  |  メッセージの送り主のID  |

### 色
カラーコードを3色指定するか  
例: #FFFFFF,#FFFFFF,#FFFFFF
コマンドの場合: #FFFFFF #FFFFFF #FFFFFF  
カラーコードの取得先: [RGB_Color](https://www.rapidtables.com/web/color/RGB_Color.html "rapidtables.com")  

ここから一つ選ぶ  

|  名前  |  プレビュー  |
| --- | --- |
|  TEAL  |  ![TEAL](https://user-images.githubusercontent.com/53356872/103505315-49356480-4e9d-11eb-9efe-7b4397601d75.png)  |
|  SWEET_RED  |  ![SWEET_RED](https://user-images.githubusercontent.com/53356872/103505369-69652380-4e9d-11eb-8332-ba35a22d5bc6.png)  |
|  LIGHT_ORANGE  |  ![LIGHT_ORANGE](https://user-images.githubusercontent.com/53356872/103505432-8e599680-4e9d-11eb-8996-88163d49210f.png)  |
|  GREEN  |  ![GREEN](https://user-images.githubusercontent.com/53356872/103505533-cbbe2400-4e9d-11eb-9b30-bc51705a320d.png)  |
|  LIGHT_BLUE  |  ![LIGHT_BLUE](https://user-images.githubusercontent.com/53356872/103505558-e09ab780-4e9d-11eb-99bd-6cb58634c5a7.png)  |
|  DARK_BLUE  |  ![DARK_BLUE](https://user-images.githubusercontent.com/53356872/103505598-00ca7680-4e9e-11eb-90bf-2488295586a4.png)  |
|  PINK  |  ![PINK](https://user-images.githubusercontent.com/53356872/103505630-13dd4680-4e9e-11eb-81db-f24686d296d7.png)  |
|  RED  |  ![RED](https://user-images.githubusercontent.com/53356872/103505689-366f5f80-4e9e-11eb-89f2-640375b00264.png)  |
|  GRAY  |  ![GRAY](https://user-images.githubusercontent.com/53356872/103505718-48510280-4e9e-11eb-9e58-7fa3f4c33128.png)  |
|  ORANGE  |  ![ORANGE](https://user-images.githubusercontent.com/53356872/103505467-a3362a00-4e9d-11eb-83bd-b1df0abe89dd.png)  |
|  DARK_PURPLE  |  ![DARK_PURPLE](https://user-images.githubusercontent.com/53356872/103505756-5c94ff80-4e9e-11eb-9559-57f566f08b9b.png)  |
|  LIME  |  ![LIME](https://user-images.githubusercontent.com/53356872/103505788-70d8fc80-4e9e-11eb-924d-1823668ab6ac.png)  |
|  INDIGO  |  ![INDIGO](https://user-images.githubusercontent.com/53356872/103505816-851cf980-4e9e-11eb-985d-ecceb4ce5967.png)  |

### コマンドチャンネル
設定がデフォルトの`{name}-command-channel`の場合で、ボットの名前が`Example Bot01`の場合  
Discord内でのコマンドチャンネルは`example-bot01-command-channel`になる  
(チャンネル名では大文字、スペースが使えないため。`{name}`がボットの名前に置き換えられている)  

### コマンドチャンネルで使える変数
|  名前  |  説明  |
| --- | --- |
|  name  |  ボットのディスプレイネーム  |
|  id  |  ボットのID  |
|  discord_name  |  Discordボットのディスプレイネーム  |
|  discord_id  |  DiscordボットのID  |
|  discord_nickname  |  Discordボットのニックネーム  |
|  num  |  ボットの番号(コンフィグでの順番)  |
|  all  |  全てのチャンネルをコマンドチャンネルにする  |
