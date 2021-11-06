## Commands
### Settings
|  Key (Raw value)  |  Description  |
| ---- | ---- |
|  Whitelist commands (whitelist_commands)  |  Set identifier of commands which can be used for whitelist users or above  |
|  User commands (user_commands)  |  Set identifier of commands which can be used for users or above  |
|  Apply prefix to item search (prefix_to_item_search)  |  Whether prefix is needed to run item search  |
For other settings, see below  

All commands written in here is command's 'identifier'  
Actual word to run command is configurable in commands editor (commands.json)  
[] values are required, () values are optional  

### List of commands
|  Identifier  |  Usage  |  Description  |
| ---- | ---- | ---- |
|  exec  |  exec [Program]  |  Run program  |
|  clear  |  clear  |  Clear console  |
|  help  |  help [Command's identifier/Command's run word]  |  Show command usage  |
|  stat  |  stat [command/ng_word/most] [Command's identifier/Command's run word/NG word name] |  Show number of remarks and most spoken user. If second argument is most, show most spoken command and most spoken NG word  |
|  ping  |  ping  |  Show bot's ping  |
|  prev  |  prev  |  Run previous command  |
|  send_all  |  send_all [Message]  |  Send message to all bots(Run command)  |
|  restart  | restart  |  Reboot program  |
|  relogin  |  relogin  |  Relogin to bot  |
|  reload  |  reload  |  Reload this bot's config  |
|  reload_all  |  reload_all  |  Reload all bot's config  |
|  add_blacklist  |  add_blacklist [Name/ID]  |  Add user to blacklist  |
|  remove_blacklist  |  remove_blacklist [Name/ID]  |  Remove user from blacklist  |
|  add_whitelist  |  add_whitelist [Name/ID]  |  Add user to whitelist  |
|  remove_whitelist  |  remove_whitelist [Name/ID]  |  Remove user from whitelist  |
|  discord_add_blacklist  |  discord_add_blacklist [ID]  |  Add user to Discord blacklist  |
|  discord_remove_blacklist  |  discord_remove_blacklist [ID]  |  Remove user from Discord blacklist  |
|  discord_add_whitelist  |  discord_add_whitelist [ID]  |  Add user to Discord whitelist  |
|  discord_remove_whitelist  |  discord_remove_whitelist [ID]  |  Remove user from Discord whitelist  |
|  add_invitelist  |  add_invitelist [Name/ID]  |  Add user to invitelist  |
|  remove_invitelist  |  remove_invitelist [Name/ID]  |  Remove user from invitelist  |
|  ng_outfit_for  |  ng_outfit_for [user/whitelist/blacklist/owner/bot/null]  |  Change `ng_outfit_for` value in config  |
|  ng_outfit_operation  |  ng_outfit_operation [chatban/remove/block/blacklist/null]  |  Change `ng_outfit_operation` value in config  |
|  outfit_mimic_for  |  outfit_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (Name/ID)  |  Change `outfit_mimic_for` value in config  |
|  ng_backpack_for  |  ng_backpack_for [user/whitelist/blacklist/owner/bot/null]  |  Change `ng_backpack_for` value in config  |
|  ng_backpack_operation  |  ng_backpack_operation [chatban/remove/block/blacklist/null]  |  Change `ng_backpack_operation` value in config  |
|  backpack_mimic_for  |  backpack_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (Name/ID)  |  Change `backpack_mimic_for` value in config  |
|  ng_pickaxe_for  |  ng_pickaxe_for [user/whitelist/blacklist/owner/bot/null]  |  Change `ng_pickaxe_for` value in config  |
|  ng_pickaxe_operation  |  ng_pickaxe_operation [chatban/remove/block/blacklist/null]  |  Change `ng_pickaxe_operation` value in config  |
|  pickaxe_mimic_for  |  pickaxe_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (Name/ID)  |  Change `pickaxe_mimic_for` value in config  |
|  ng_emote_for  |  ng_emote_for [user/whitelist/blacklist/owner/bot/null]  |  Change `ng_emote_for` value in config  |
|  ng_emote_operation  |  ng_emote_operation [chatban/remove/block/blacklist/null]  |  Change `ng_emote_operation` value in config  |
|  emote_mimic_for  |  emote_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (Name/ID)  |  Change `emote_mimic_for` value in config  |
|  ng_platform_for  |  ng_platform_for [user/whitelist/blacklist/owner/bot/null]  |  Change `ng_platform_for` value in config  |
|  ng_platform_operation  |  ng_platform_operation [chatban/remove/block/blacklist/null]  |  Change `ng_platform_operation` value in config  |
|  ng_name_for  |  ng_name_for [user/whitelist/blacklist/owner/bot/null]  |  Change `ng_name_for` value in config  |
|  ng_name_operation  |  ng_name_operation [chatban/remove/block/blacklist/null]  |  Change `ng_name_operation` value in config  |
|  accept_invite_for  |  accept_invite_for [user/whitelist/blacklist/owner/bot/null]  |  Change `accept_invite_for` value in config  |
|  decline_invite_when  |  decline_invite_when [user/whitelist/blacklist/owner/bot/null]  |Change `decline_invite_when` value in config  |
|  invite_interval_for  |  invite_interval_for [user/whitelist/blacklist/owner/bot/null]  |  Change `invite_interval_for` value in config  |
|  accept_friend_for  |  accept_friend_for [user/whitelist/blacklist/owner/bot/null]  |  Change `accept_friend_for` value in config  |
|  whisper_enable_for  |  whisper_enable_for [user/whitelist/blacklist/owner/bot/null]  |  Change `whisper_enable_for` value in config  |
|  party_chat_enable_for  |  party_chat_enable_for [user/whitelist/blacklist/owner/bot/null]  |  Change `party_chat_enable_for` value in config  |
|  permission_command_operation  |  permission_command_operation [chatban/remove/block/blacklist/null]  |  Change `permission_command_operation` value in config  |
|  accept_join_for  |  accept_join_for [user/whitelist/blacklist/owner/bot/null]  |  Change `accept_join_for` value in config  |
|  chat_max_for  |  chat_max_for [user/whitelist/blacklist/owner/bot/null]  |  Change `chat_max_for` value in config  |
|  chat_max_operation  |  chat_max_operation [chatban/remove/block/blacklist/null]  |  Change `chat_max_operation` value in config  |
|  hide_for  |  hide_for [user/whitelist/blacklist/owner/bot/null]  |  Change `hide_for` value in config  |
|  blacklist_operation  |  blacklist_operation [chatban/remove/block/blacklist/null]  |  Change `blacklist_operation` value in config  |
|  botlist_operation  |  botlist_operation [chatban/remove/block/blacklist/null]  |  Change `botlist_operation` value in config  |
|  discord_chat_max_for  |  discord_chat_max_for [user/whitelist/blacklist/owner/bot/null]  |  Change `discord_chat_max_for` value in config  |
|  discord_command_enable_for  |  discord_command_enable_for [user/whitelist/blacklist/owner/bot/null]  |  Change `discord_command_enable_for` value in config  |
|  ng_word_for  |  ng_word_for [user/whitelist/blacklist/owner/bot/null]  |  Change `ng_word_for` value in config  |
|  ng_word_operation  |  ng_word_operation [chatban/remove/block/blacklist/null]  |  Change `ng_word_operation` value in config  |
|  get_user  |  get_user [Name/ID]  |  Search user and show name  |
|  get_friend  |  get_friend [Name/ID]  |  Search friend and show info  |
|  get_pending  | get_pending [Name/ID]  |  Search friend request and show name  |
|  get_block  |  get_block [Name/ID]  |  Search block list and show name  |
|  get_member  |  get_member [Name/ID]  |  Search party member and show info  |
|  party_info  |  party_info  |  Show party info  |
|  friend_count  |  friend_count  |  Show friend count  |
|  pending_count  |  pending_count  |  Show friend request count  |
|  block_count  |  block_count  |  Show block count  |
|  friend_list  |  friend_list  |  Show friend list  |
|  pending_list  |  pending_list  |  Show friend request list  |
|  block_list  |  block_list  |  Show block list  |
|  add_friend  |  add_friend [Name/ID]  |  Add user to friend  |
|  remove_friend  |  remove_friend [Name/ID]  |  Remove user from friend  |
|  remove_friends  |  remove_friends [数]  |  Remove random specified number of friends. Can be stopped with stop command<br>May this command will take a time  |
|  remove_all_friend  |  remove_all_friend  |  Remove all friends. Can be stopped with stop command<br>May this command will take a time  |
|  remove_offline_for  |  remove_offline_for [Days] (Hours) (Minutes)  |  Remove friends that was offline for specified time. Can be stopped with stop command<br>May this command will take a time  |
|  accept_pending  |  accept_pending [Name/ID]  |  Accept friend request from user  |
|  decline_pending  |  decline_pending [Name/ID]  |  Decline friend request from user  |
|  incoming_pending  |  incoming_pending [accept/decline]  |  Accept/Decline received friend requests. Can be stopped with stop command<br>May this command will take a time  |
|  cancel_outgoing_pending  |  cancel_outgoing_pending  |  Cancel sent friend requests. Can be stopped with stop command<br>May this command will take a time  |
|  block_user  |  block_user [Name/ID]  |  Block user  |
|  unblock_user  |  unblock_user [Name/ID]  |  Unblock user  |
|  unblock_all_user  |  unblock_all_user  |  Unblock all users. Can be stopped with stop command<br>May this command will take a time  |
|  join  |  join [Name/ID]  |  Join user's party  |
|  join_id  |  join_id [Party ID]  |  Join party using party id  |
|  request_to_join  |  request_to_join [Name/ID]  |  Send request to join to user  |
|  leave  |  leave  |  Leave party  |
|  invite  |  invite [Name/ID]  |  Invite user  |
|  invite_list_users  |  invite_list_users  |  Invite users which in invitelist  |
|  message  |  message [Name/ID] : [Message]  |  Send message to user  |
|  party_message  |  party_message [Message]  |  Send message to party  |
|  avatar  |  avatar [ID] (Color)  |  Set avatar<br>Information of color setting is [here](config.md#Colors)  |
|  status  |  status [Message]  |  Set status  |
|  banner  |  banner [Banner ID] [Banner color]  |  Set banner<br>Banner ids is [here](https://fnitems.hyperserver.xyz/banners)  |
|  level  |  level [Number]  |  Set level  |
|  privacy  |  privacy [public, friends_allow_friends_of_friends, friends, private_allow_friends_of_friends, private]  |  Set party's privacy  |
|  voice_chat  |  voice_chat [true/false]  |  Enable/Disable voice chat. This won't affect to members which joined before run this command  |
|  promote  |  promote [Name/ID]  |  Promote party leader to user  |
|  kick  |  kick [Name/ID]  |  Kick user from party  |
|  chatban  |  chatban [Name/ID] : (Reason)  |  Chatban user  |
|  hide  |  hide (Name/ID)  |  Hide user in party. If user is not specified, hide all users(Depend on `hide_for` setting in config)  |
|  show  |  show (Name/ID)  |  Show user in party. If user is not specified, show all users  |
|  ready  |  ready  |  Set ready state to Ready  |
|  unready  |  unready  |  Set ready state to Unready  |
|  sitout  | sitout  |  Set ready state to Sitting out  |
|  match  |  match (数値)  |  Set match state. If number is not specified, it'll be 100 remaining  |
|  unmatch  |  unmatch  |  Cancel match state  |
|  swap  |  swap [Name/ID]  |  Swap position with user  |
|  stop  |  stop  |  Stop stoppable commands  |
|  new_items  |  new_items  |  Show items which added in update  |
|  shop_items  |  shop_items  |  Show items which in item shop  |
|  enlightenment  |  enlightenment [Season] [Number]  |  Set enlightenment<br>Used in 8ball vs Scratch's glitch, Agent Peely's gold etc  |
|  corruption  |  corruption [Number]  |  Set corruption<br>Used in Corrupted Arachne etc  |
|  all_outfit  |  all_outfit  |  Show all outfits  |
|  all_backpack  |  all_backpack  |  Show all backpacks  |
|  all_pet  |  all_pet  |  Show all pets  |
|  all_pickaxe  |  all_pickaxe  |  Show all pickaxes  |
|  all_emote  |  all_emote  |  Show all emotes  |
|  all_emoji  |  all_emoji  |  Show all emote icons  |
|  all_toy  |  all_toy  |  Show all toys  |
|  cid  |  cid [ID]  |  Search outfit with ID and change outfit  |
|  bid  |  bid [ID]  |  Search backpack with ID and change backpack  |
|  petcarrier  |  petcarrier [ID]  |  Search pet with ID and change backpack  |
|  pickaxe_id  |  pickaxe_id [ID]  |  Search pickaxe with ID and change pickaxe  |
|  eid  |  eid [ID]  |  Search emote with ID and change emote  |
|  emoji_id  |  emoji_id [ID]  |  Search emote icon with ID and change emote  |
|  toy_id  |  toy_id [ID]  |  Search toy with ID and change emote  |
|  id  |  id [ID]  |  Search item with ID and change ID  |
|  outfit  |  outfit [Name]  |  Search outfit and change outfit  |
|  random_outfit  |  random_outfit  |  Change to random outfit  |
|  clear_outfit  |  clear_outfit  |  Clear outfit  |
|  backpack  |  backpack [Name]  |  Search backpack and change backpack  |
|  random_backpack  |  random_backpack  |  Change to random backpack  |
|  pet  |  pet [Name]  |  Search pet and change backpack  |
|  random_pet  |  random_pet  |  Change to random pet  |
|  clear_backpack  |  clear_backpack  |  Clear backpack  |
|  pickaxe  |  pickaxe [Name]  |  Search pickaxe and change pickaxe  |
|  random_pickaxe  |  random_pickaxe  |  Change to random pickaxe  |
|  clear_pickaxe  |  clear_pickaxe  |  Clear pickaxe  |
|  emote  |  emote [Name]  |  Search emote and change emote  |
|  random_emote  |  random_emote  |  Change to random emote  |
|  emoji  |  emoji [Name]  |  Search emote icon and change emote  |
|  random_emoji  |  random_emoji  |  Change to random emoji  |
|  toy  |  toy [Name]  |  Search toy and change emote  |
|  random_toy  |  random_toy  |  Change to random toy  |
|  clear_emote  |  clear_emote  |  Clear emote  |
|  item  |  item [Name]  |  Search item and change item  |
|  random_item  |  random_item  |  Change to random item  |
|  playlist_id  |  playlist_id [ID]  |  Search playlist with ID and change playlist  |
|  playlist  |  playlist [Name]  |  Search playlist and change playlist  |
|  set  |  set [Name]  |  Search item with set name and change item  |
|  set_style  |  set_style [outfit/backpack/pickaxe]  |  Show styles which available on current item and change to specified style  |
|  add_style  |  add_style [outfit/backpack/pickaxe]  |  Show styles which available on current item and add specified style to current style<br>Example: Change to blue style using set_style, and add Stage 1 style using add_style  |
|  set_variant  |  set_variant [outfit/backpack/pickaxe] [[variant](#variant)] [Number]  |  **For advanced users Normally please use set_style and add_style**<br>Change to specified variant  |
|  add_variant  |  add_variant [outfit/backpack/pickaxe] [[variant](#variant)] [Number]  |  **For advanced users Normally please use set_style and add_style**<br>Add specified variant to current variant  |
|  cosmetic_preset  |  cosmetic_preset [save/load] [Number]  |  Save/Load item preset  |

### Other identifiers
|  Identifier  |  Description  |
| ---- | ---- |
|  cid_  |  Item change using CID  |
|  bid_  |  Item change using BID  |
|  petcarrier_  |  Item change using PetCarrier  |
|  petid_  |  Item change using PetID  |
|  pickaxe_id_  |  Item change using Pickaxe_ID  |
|  eid_  |  Item change using EID  |
|  emoji_  |  Item change using Emoji ID  |
|  toy_  |  Item change using Toy ID  |
|  playlist_  |  Playlist change using ID  |
|  item_search  |  Item search using Item name  |

### Others
Words which use in commands  

|  Identifier  |  Description  |
| ---- | ---- |
|  command  |  Use in stat command. Means command  |
|  ng_word  |  Use in stat command. Means ng word  |
|  most  |  Use in stat command. Means most  |
|  user  |  Means user type, user  |
|  whitelist  |  Means user type, whitelist  |
|  blacklist  |  Means user type, blacklist  |
|  owner  |  Means user type, owner  |
|  bot  |  Means user type, bot  |
|  null  |  Means none  |
|  chatban  |  Means operation, chatban  |
|  remove  |  Means operation, remove friend  |
|  block  |  Means operation, block  |
|  blacklist  |  Means operation, blacklist  |
|  add   |  Use in outfit_mimic_for, backpack_mimic_for, pickaxe_mimic_for, emote_mimic_for commands. Means add  |
|  remove   |  Use in outfit_mimic_for, backpack_mimic_for, pickaxe_mimic_for, emote_mimic_for commands. Means remove  |
|  true  |  Use in voice_chat command. Means on  |
|  false  |  Use in voice_chat command. Means off  |
|  accept  |  Use in incoming_pending command. Means accept  |
|  decline  |  Use in incoming_pending command. Means decline  |
|  public  |  Use in privacy command. Means public
|  friends_allow_friends_of_friends  |  Use in privacy command. Means friends only (allow friends of friends)  |
|  friends  |  Use in privacy command. Means friends only  |
|  private_allow_friends_of_friends  |  Use in privacy command. Means private (allow friends of friends)  |
|  private  |  Use in privacy command. Means private  |
|  outfit  |  Use in set_style, add_style, set_variant, add_variant command. Means outfit  |
|  backpack  |  Use in set_style, add_style, set_variant, add_variant command. Means backpack  |
|  pickaxe  |  Use in set_style, add_style, set_variant, add_variant command. Means pickaxe  |
|  save  |  Use in cosmetic_preset. Means save  |
|  load  |  Use in cosmetic_preset. Means load  |

### variant
pattern/numeric/clothing_color/jersey_color/parts/progressive/particle/material/emissive
