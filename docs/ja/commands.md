## コマンド
### 設定
|  キー (生の値)  |  説明  |
| ---- | ---- |
|  ホワイトリストコマンド (whitelist_commands)  |  ホワイトリスト以上のユーザーが使えるコマンドの識別名を設定する  |
|  ユーザーコマンド (user_commands)  |  ユーザー以上のユーザーが使えるコマンドの識別名を設定する  |
|  アイテム検索にプレフィックスを適用 (prefix_to_item_search)  |  アイテム検索をするのにプレフィックスが必要かどうか  |
その他は下記参照  

### コマンド一覧
ここに記すのは全てコマンドの'識別名'  
実際にコマンドの実行に必要な単語はコマンドエディター(commands.json)で設定可能  
[]内は必須項目、()内はオプション項目  

|  識別名  |  使用方法  |  説明  |
| ---- | ---- | ---- |
|  exec  |  exec [実行するプログラム]  |  指定したプログラムを実行する  |
|  clear  |  clear  |  コンソールをクリアする  |
|  help  |  help [コマンドの識別名/コマンドの発動ワード]  |  コマンドの使用方法を表示する  |
|  stat  |  stat [command/ng_word/most] [コマンドの識別名/コマンドの発動ワード/NGワード名] |  それぞれの発言回数、もっとも発言したユーザーを表示する。mostの場合、もっとも発言されたコマンド、NGワードを表示する  |
|  ping  |  ping  |  ボットの応答速度を計測する  |
|  prev  |  prev  |  一つ前に実行したコマンドを実行する  |
|  send_all  |  send_all [メッセージ]  |  全てのボットにメッセージを送信する(コマンドを実行)  |
|  restart  | restart  |  プログラムを再起動する  |
|  relogin  |  relogin  |  ボットに再ログインする  |
|  reload  |  reload  |  このボットの設定を再読み込みする  |
|  reload_all  |  reload_all  |  全てのボットの設定を再読み込みする  |
|  add_blacklist  |  add_blacklist [名前/ID]  |  ユーザーをブラックリストに追加する  |
|  remove_blacklist  |  remove_blacklist [名前/ID]  |  ユーザーをブラックリストから削除する  |
|  add_whitelist  |  add_whitelist [名前/ID]  |  ユーザーをホワイトリストに追加する  |
|  remove_whitelist  |  remove_whitelist [名前/ID]  |  ユーザーをホワイトリストから削除する  |
|  add_botlist  |  add_botlist [名前/ID]  |  ユーザーをボットリストに追加する  |
|  remove_botlist  |  remove_botlist [名前/ID]  |  ユーザーをボットリストから削除する  |
|  discord_add_blacklist  |  discord_add_blacklist [名前/ID]  |  ユーザーをDiscordのブラックリストに追加する  |
|  discord_remove_blacklist  |  discord_remove_blacklist [ID]  |  ユーザーをDiscordのブラックリストから削除する  |
|  discord_add_whitelist  |  discord_add_whitelist [ID]  |  ユーザーをDiscordのホワイトリストに追加する  |
|  discord_remove_whitelist  |  discord_remove_whitelist [ID]  |  ユーザーをDiscordのホワイトリストから削除する  |
|  add_invitelist  |  add_invitelist [名前/ID]  |  ユーザーを招待リストに追加する  |
|  remove_invitelist  |  remove_invitelist [名前/ID]  |  ユーザーを招待リストから削除する  |
|  ng_outfit_for  |  ng_outfit_for [user/whitelist/blacklist/owner/bot/null]  |  configの`ng_outfit_for`の値を変更する  |
|  ng_outfit_operation  |  ng_outfit_operation [chatban/remove/block/blacklist/null]  |  configの`ng_outfit_operation`の値を変更する  |
|  outfit_mimic_for  |  outfit_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (名前/ID)  |  configの`outfit_mimic_for`の値を変更する  |
|  ng_backpack_for  |  ng_backpack_for [user/whitelist/blacklist/owner/bot/null]  |  configの`ng_backpack_for`の値を変更する  |
|  ng_backpack_operation  |  ng_backpack_operation [chatban/remove/block/blacklist/null]  |  configの`ng_backpack_operation`の値を変更する  |
|  backpack_mimic_for  |  backpack_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (名前/ID)  |  configの`backpack_mimic_for`の値を変更する  |
|  ng_pickaxe_for  |  ng_pickaxe_for [user/whitelist/blacklist/owner/bot/null]  |  configの`ng_pickaxe_for`の値を変更する  |
|  ng_pickaxe_operation  |  ng_pickaxe_operation [chatban/remove/block/blacklist/null]  |  configの`ng_pickaxe_operation`の値を変更する  |
|  pickaxe_mimic_for  |  pickaxe_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (名前/ID)  |  configの`pickaxe_mimic_for`の値を変更する  |
|  ng_emote_for  |  ng_emote_for [user/whitelist/blacklist/owner/bot/null]  |  configの`ng_emote_for`の値を変更する  |
|  ng_emote_operation  |  ng_emote_operation [chatban/remove/block/blacklist/null]  |  configの`ng_emote_operation`の値を変更する  |
|  emote_mimic_for  |  emote_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (名前/ID)  |  configの`emote_mimic_for`の値を変更する  |
|  ng_platform_for  |  ng_platform_for [user/whitelist/blacklist/owner/bot/null]  |  configの`ng_platform_for`の値を変更する  |
|  ng_platform_operation  |  ng_platform_operation [chatban/remove/block/blacklist/null]  |  configの`ng_platform_operation`の値を変更する  |
|  ng_name_for  |  ng_name_for [user/whitelist/blacklist/owner/bot/null]  |  configの`ng_name_for`の値を変更する  |
|  ng_name_operation  |  ng_name_operation [chatban/remove/block/blacklist/null]  |  configの`ng_name_operation`の値を変更する  |
|  accept_invite_for  |  accept_invite_for [user/whitelist/blacklist/owner/bot/null]  |  configの`accept_invite_for`の値を変更する  |
|  decline_invite_when  |  decline_invite_when [user/whitelist/blacklist/owner/bot/null]  |configの`decline_invite_when`の値を変更する  |
|  invite_interval_for  |  invite_interval_for [user/whitelist/blacklist/owner/bot/null]  |  configの`invite_interval_for`の値を変更する  |
|  accept_friend_for  |  accept_friend_for [user/whitelist/blacklist/owner/bot/null]  |  configの`accept_friend_for`の値を変更する  |
|  whisper_enable_for  |  whisper_enable_for [user/whitelist/blacklist/owner/bot/null]  |  configの`whisper_enable_for`の値を変更する  |
|  party_chat_enable_for  |  party_chat_enable_for [user/whitelist/blacklist/owner/bot/null]  |  configの`party_chat_enable_for`の値を変更する  |
|  permission_command_operation  |  permission_command_operation [chatban/remove/block/blacklist/null]  |  configの`permission_command_operation`の値を変更する  |
|  accept_join_for  |  accept_join_for [user/whitelist/blacklist/owner/bot/null]  |  configの`accept_join_for`の値を変更する  |
|  chat_max_for  |  chat_max_for [user/whitelist/blacklist/owner/bot/null]  |  configの`chat_max_for`の値を変更する  |
|  chat_max_operation  |  chat_max_operation [chatban/remove/block/blacklist/null]  |  configの`chat_max_operation`の値を変更する  |
|  hide_for  |  hide_for [user/whitelist/blacklist/owner/bot/null]  |  configの`hide_for`の値を変更する  |
|  blacklist_operation  |  blacklist_operation [chatban/remove/block/blacklist/null]  |  configの`blacklist_operation`の値を変更する  |
|  botlist_operation  |  botlist_operation [chatban/remove/block/blacklist/null]  |  configの`botlist_operation`の値を変更する  |
|  discord_chat_max_for  |  discord_chat_max_for [user/whitelist/blacklist/owner/bot/null]  |  configの`discord_chat_max_for`の値を変更する  |
|  discord_command_enable_for  |  discord_command_enable_for [user/whitelist/blacklist/owner/bot/null]  |  configの`discord_command_enable_for`の値を変更する  |
|  ng_word_for  |  ng_word_for [user/whitelist/blacklist/owner/bot/null]  |  configの`ng_word_for`の値を変更する  |
|  ng_word_operation  |  ng_word_operation [chatban/remove/block/blacklist/null]  |  configの`ng_word_operation`の値を変更する  |
|  get_user  |  get_user [名前/ID]  |  ユーザーを検索し、名前を表示する  |
|  get_friend  |  get_friend [名前/ID]  |  フレンドを検索し、各種情報を表示する  |
|  get_pending  | get_pending [名前/ID]  |  フレンドリクエストを検索し、名前を表示する  |
|  get_block  |  get_block [名前/ID]  |  ブロックリストを検索し、名前を表示する  |
|  get_member  |  get_member [名前/ID]  |  パーティーメンバーを検索し、各種情報を表示する  |
|  party_info  |  party_info  |  パーティの情報を表示する  |
|  friend_count  |  friend_count  |  フレンド数を表示する  |
|  pending_count  |  pending_count  |  フレンドリクエスト数を表示する  |
|  block_count  |  block_count  |  ブロック数を表示する  |
|  friend_list  |  friend_list  |  フレンドリストを表示する  |
|  pending_list  |  pending_list  |  フレンドリクエストリストを表示する  |
|  block_list  |  block_list  |  ブロックリストを表示する  |
|  add_friend  |  add_friend [名前/ID]  |  ユーザーをフレンドに追加する  |
|  remove_friend  |  remove_friend [名前/ID]  |  ユーザーをフレンドから削除する  |
|  remove_friends  |  remove_friends [数]  |  指定した数のランダムなフレンドを削除する。stopコマンドで途中停止可能<br>この操作には時間がかかる場合があります  |
|  remove_all_friend  |  remove_all_friend  |  全てのフレンドを削除する。stopコマンドで途中停止可能<br>この操作には時間がかかる場合があります  |
|  remove_offline_for  |  remove_offline_for [日] (時間) (分)  |  指定した時間オフラインだったフレンドを削除する。stopコマンドで停止可能<br>この操作には時間がかかが場合はあります  |
|  accept_pending  |  accept_pending [名前/ID]  |  ユーザーからのフレンドリクエストを承諾する  |
|  decline_pending  |  decline_pending [名前/ID]  |  ユーザーからのフレンドリクエストを拒否する  |
|  incoming_pending  |  incoming_pending [accept/decline]  |  受信したフレンドリクエストを承諾/拒否する。stopコマンドで停止可能<br>この操作には時間がかかる場合があります  |
|  cancel_outgoing_pending  |  cancel_outgoing_pending  |  送信したフレンドリクエストをキャンセルする。stopコマンドで停止可能<br>この操作には時間がかかる場合があります  |
|  block_user  |  block_user [名前/ID]  |  ユーザーをブロックする  |
|  unblock_user  |  unblock_user [名前/ID]  |  ユーザーをブロック解除する  |
|  unblock_all_user  |  unblock_all_user  |  全てのユーザーをブロック解除する。stopコマンドで停止可能<br>この操作には時間がかかる場合があります  |
|  join  |  join [名前/ID]  |  ユーザーのパーティーに参加する  |
|  join_id  |  join_id [パーティーID]  |  パーティーIDからパーティーに参加する  |
|  request_to_join  |  request_to_join [名前/iD]  |  ユーザーに参加リクエストを送信する  |
|  leave  |  leave  |  パーティーを離脱する  |
|  invite  |  invite [名前/ID]  |  ユーザーを招待する  |
|  invite_list_users  |  invite_list_users  |  招待リストのユーザーを招待する  |
|  message  |  message [名前/ID] : [メッセージ]  |  ユーザーにメッセージを送信する  |
|  party_message  |  party_message [メッセージ]  |  パーティーにメッセージを送信する  |
|  avatar  |  avatar [ID] (色)  |  アバターを設定する<br>色の設定方法は[こちら](config.md#色)  |
|  status  |  status [メッセージ]  |  ステータスを設定する  |
|  banner  |  banner [バナーID] [バナーの色]  |  バナーを設定する<br>バナーIDは[こちら](https://fnitems.hyperserver.xyz/banners)  |
|  level  |  level [数値]  |  レベルを設定する  |
|  battlepass  |  battlepass [数値]  |  ティアを設定する  |
|  privacy  |  privacy [public, friends_allow_friends_of_friends, friends, private_allow_friends_of_friends, private]  |  パーティーのプライバシーを設定する  |
|  voice_chat  |  voice_chat [true/false]  |  ボイスチャットを有効/無効化する。このコマンドを実行する前にいたメンバーには効果がない  |
|  promote  |  promote [名前/ID]  |  ユーザーにパーティーリーダーを譲渡する  |
|  kick  |  kick [名前/ID]  |  ユーザーをパーティーからキックする  |
|  chatban  |  chatban [名前/ID] : (理由)  |  ユーザーをチャットバンする  |
|  hide  |  hide (名前/ID)  |  ユーザーをパーティーで非表示にする。指定しなかった場合全てのユーザー(configの`hide_for`の設定に依存)を非表示にする  |
|  show  |  show (名前/ID)  |  ユーザーをパーティーで表示する。指定しなかった場合全てのユーザーを表示する  |
|  ready  |  ready  |  準備状態を準備OKにする  |
|  unready  |  unready  |  準備状態を準備中にする  |
|  sitout  | sitout  |  準備状態を欠場中にする  |
|  match  |  match (数値)  |  マッチ状態を変更する。数値を指定しなかった場合残り100人になる  |
|  unmatch  |  unmatch  |  マッチ状態を解除する  |
|  swap  |  swap [名前/ID]  |  指定したユーザーと場所を交換する  |
|  stop  |  stop  |  停止可能な操作を停止させる  |
|  new_items  |  new_items  |  アップデートで追加されたアイテムを表示する  |
|  shop_items  |  shop_items  |  ショップにあるアイテムを表示する  |
|  enlightenment  |  enlightenment [シーズン] [数値]  |  enlightenmentを設定する<br>8ボールvsスクラッチのグリッチや、エージェントピーリーのゴールド等の値  |
|  corruption  |  corruption [数値]  |  corruptionを設定する<br>コラプテッドアラクネ等で使用されている  |
|  all_outfit  |  all_outfit  |  全てのコスチュームを表示する  |
|  all_backpack  |  all_backpack  |  全てのバックパックを表示する  |
|  all_pet  |  all_pet  |  全てのペットを表示する  |
|  all_pickaxe  |  all_pickaxe  |  全ての収集ツールを表示する  |
|  all_emote  |  all_emote  |  全てのエモートを表示する  |
|  all_emoji  |  all_emoji  |  全てのエモートアイコンを表示する  |
|  all_toy  |  all_toy  |  全てのおもちゃを表示する  |
|  cid  |  cid [ID]  |  IDでコスチュームを検索し、そのコスチュームに変更する  |
|  bid  |  bid [ID]  |  IDでバックパックを検索し、そのバックパックに変更する  |
|  petcarrier  |  petcarrier [ID]  |  IDでペットを検索し、そのペットに変更する  |
|  pickaxe_id  |  pickaxe_id [ID]  |  IDで収集ツールを検索し、その収集ツールに変更する  |
|  eid  |  eid [ID]  |  IDでエモートを検索し、そのエモートに変更する  |
|  emoji_id  |  emoji_id [ID]  |  IDでエモートアイコンを検索し、そのエモートアイコンに変更する  |
|  toy_id  |  toy_id [ID]  |  IDでおもちゃを検索し、そのおもちゃに変更する  |
|  id  |  id [ID]  |  IDでアイテムを検索し、そのアイテムに変更する  |
|  outfit  |  outfit [名前]  |  コスチュームを検索し、そのコスチュームに変更する  |
|  random_outfit |  random_outfit  |  ランダムなコスチュームに変更する  |
|  clear_outfit  |  clear_outfit  |  コスチュームをクリアする  |
|  backpack  |  backpack [名前]  |  バックパックを検索し、そのバックパックに変更する  |
|  random_backpack |  random_backpack  |  ランダムなバックパックに変更する  |
|  pet  |  pet [名前]  |  ペットを検索し、そのペットに変更する  |
|  random_pet |  random_pet  |  ランダムなペットに変更する  |
|  clear_backpack  |  clear_backpack  |  バックパックをクリアする  |
|  pickaxe  |  pickaxe [名前]  |  収集ツールを検索し、その収集ツールに変更する  
|  random_pickaxe |  random_pickaxe |  ランダムなコ収集ツールに変更する  ||
|  clear_pickaxe  |  clear_pickaxe  |  収集ツールをクリアする  |
|  emote  |  emote [名前]  |  エモートを検索し、そのエモートに変更する  |
|  random_emote |  random_emote  |  ランダムなエモートに変更する  |
|  emoji  |  emoji [名前]  |  エモートアイコンを検索し、そのエモートアイコンに変更する  |
|  random_emoji |  random_emoji  |  ランダムなエモートアイコンに変更する  |
|  toy  |  toy [名前]  |  おもちゃを検索し、そのおもちゃに変更する  |
|  random_toy |  random_toy  |  ランダムなおもちゃに変更する  |
|  clear_emote  |  clear_emote  |  エモートをクリアする  |
|  item  |  item [名前]  |  アイテムを検索し、そのアイテムに検索する  |
|  random_item |  random_item  |  ランダムなアイテムに変更する  |
|  playlist_id  |  playlist_id [ID]  |  IDでプレイリストを検索し、そのプレイリストに変更する  |
|  playlist  |  playlist [名前]  |  プレイリストを検索し、そのプレイリストに変更する  |
|  crowns  |  crowns [数値]  |  クラウン数を設定する  |
|  island_code  |  island_code [島コード]  |  モードをその島に変更する  |
|  set  |  set [名前]  |  セット名でアイテムを検索し、そのアイテムに変更する  |
|  set_style  |  set_style [outfit/backpack/pickaxe]  |  現在使用しているアイテムのスタイル一覧を表示し、指定したスタイルに設定する  |
|  add_style  |  add_style [outfit/backpack/pickaxe]  |  現在使用しているアイテムのスタイル一覧を表示し、指定したスタイルを現在のスタイルに統合する<br>例: ステージ1のスタイルにadd_styleで青を追加  |
|  set_variant  |  set_variant [outfit/backpack/pickaxe] [[variant](#variant)] [数値]  |  **上級者向け 通常はset_style, add_styleを使用してください**<br>指定したvariantに設定する  |
|  add_variant  |  add_variant [outfit/backpack/pickaxe] [[variant](#variant)] [数値]  |  **上級者向け 通常はset_style, add_styleを使用してください**<br>指定したvariantを現在のvariantに統合する  |
|  cosmetic_preset  |  cosmetic_preset [save/load] [数値]  |  アイテムプリセットを保存/読み込みする  |

### その他の識別名
|  識別名  |  説明  |
| ---- | ---- |
|  cid_  |  CIDを入力してのアイテム変更  |
|  bid_  |  BIDを入力してのアイテム変更  |
|  petcarrier_  |  PetCarrierを入力してのアイテム変更  |
|  petid_  |  PetIDを入力してのアイテム変更  |
|  pickaxe_id_  |  Pickaxe_IDを入力してのアイテム変更  |
|  eid_  |  EIDを入力してのアイテム変更  |
|  emoji_  |  Emoji IDを入力してのアイテム変更  |
|  toy_  |  Toy IDを入力してのアイテム変更  |
|  playlist_  |  IDを入力してのプレイリスト変更  |
|  item_search  |  アイテム名だけでのアイテム検索  |

### その他
コマンドで使用する単語  

|  識別名  |  説明  |
| ---- | ---- |
|  command  |  statコマンドで使う。コマンドを意味する  |
|  ng_word  |  statコマンドで使う。NGワードを意味する  |
|  most  |  statコマンドで使う。最もを意味する  |
|  user  |  ユーザーの種類、ユーザーを意味する  |
|  whitelist  |  ユーザーの種類、ホワイトリストを意味する  |
|  blacklist  |  ユーザーの種類、ブラックリストを意味する  |
|  owner  |  ユーザーの種類、所有者を意味する  |
|  bot  |  ユーザーの種類、ボットを意味する  |
|  null  |  なしを意味する  |
|  chatban  |  操作、チャットバンを意味する  |
|  remove  |  操作、フレンド削除を意味する  |
|  block  |  操作、ブロックを意味する  |
|  blacklist  |  操作、ブラックリストを意味する  |
|  add  |  outfit_mimic_for, backpack_mimic_for, pickaxe_mimic_for, emote_mimic_forコマンドで使う。追加を意味する  |
|  remove  |  outfit_mimic_for, backpack_mimic_for, pickaxe_mimic_for, emote_mimic_forコマンドで使う。削除を意味する  |
|  true  |  voice_chatコマンドで使う。オンを意味する  |
|  false  |  voice_chatコマンドで使う。オフを意味する  |
|  accept  |  incoming_pendingコマンドで使う。承諾を意味する  |
|  decline  |  incoming_pendingコマンドで使う。拒否を意味する  |
|  public  |  privacyコマンドで使う。パブリックを意味する
|  friends_allow_friends_of_friends  |  privacyコマンドで使う。フレンドのみ(フレンドのフレンドを許可)を意味する  |
|  friends  |  privacyコマンドで使う。フレンドのみを意味する  |
|  private_allow_friends_of_friends  |  privacyコマンドで使う。プライベート(フレンドのフレンドを許可)を意味する  |
|  private  |  privacyコマンドで使う。プライベートを意味する  |
|  outfit  |  set_style, add_style, set_variant, add_variantコマンドで使う。コスチュームを意味する  |
|  backpack  |  set_style, add_style, set_variant, add_variantコマンドで使う。コスチュームを意味するコマンドで使う。バックパックを意味する  |
|  pickaxe  |  set_style, add_style, set_variant, add_variantコマンドで使う。コスチュームを意味するコマンドで使う。収集ツールを意味する  |
|  save  |  cosmetic_presetコマンドで使う。保存を意味する  |
|  load  |  cosmetic_presetコマンドで使う。読み込みを意味する  |

### variant
pattern/numeric/clothing_color/jersey_color/parts/progressive/particle/material/emissive
