## Comandos
### Configuraciones
|  Valor (Valor Raw)  |  Descripción  |
| ---- | ---- |
|  Comandos de lista blanca (whitelist_commands)  |  Establece los comandos que pueden ser utilizados por los usuarios de la lista blanca o superior  |
|  Comandos de usuario (user_commands)  |  Establece los comandos que pueden ser utilizados por los usuarios de la lista blanca o superior  |
|  Aplicar prefix a la búsqueda de items (prefix_to_item_search)  |  Determina si es necesario un prefix para buscar cosméticos  |
Para otras configuraciones, revisa abajo  

Todos los comandos escritos aquí son el "identificador" del comando.  
La palabra real para ejecutar el comando es configurable en el editor de comandos (commands.json)  
Valores en [] son requeridos, valores en () son opcionales  

### Lista de comandos
|  Identificador  |  Uso  |  Descripción  |
| ---- | ---- | ---- |
|  exec  |  exec [Programa]  |  Ejecuta un programa  |
|  clear  |  clear  |  Limpia la consola  |
|  help  |  help [Identificador del comando o palabra para ejecutarlo]  |  Muestra la ayuda del comando ingresado  |
|  stat  |  stat [command/ng_word] [Identificador del comando o palabra para ejecutarlo o la palabra NG] |  Muestra el número de observaciones y el usuario más hablado. Si el segundo argumento es "most" se mostrará el comando más usado y la palabra NG más usada  |
|  ping  |  ping  |  Muestra el ping del bot  |
|  prev  |  prev  |  Ejecuta el comando anterior  |
|  send_all  |  send_all [Mensaje]  |  Envia un mensaje a todos los bots(Ejecuta comandos)  |
|  restart  | restart  |  Reinicia el programa  |
|  relogin  |  relogin  |  Reinicia la sesión del bot  |
|  reload  |  reload  |  Recarga esta configuración del bot  |
|  reload_all  |  reload_all  |  Recarga toda la configuración del bot  |
|  add_blacklist  |  add_blacklist [Nombre/ID]  |  Agrega un usuario a la lista negra  |
|  remove_blacklist  |  remove_blacklist [Nombre/ID]  |  Quita un usuario de la lista negra  |
|  add_whitelist  |  add_whitelist [Nombre/ID]  |  Agrega un usuario a la lista blanca  |
|  remove_whitelist  |  remove_whitelist [Nombre/ID]  |  Quita un usuario de la lista blanca  |
|  discord_add_blacklist  |  discord_add_blacklist [ID]  |  Agrega un usuario a la lista negra de Discord  |
|  discord_remove_blacklist  |  discord_remove_blacklist [ID]  |  Remueve un usuario de la lista negra de Discord  |
|  discord_add_whitelist  |  discord_add_whitelist [ID]  |  Agrega un usuario a la lista blanca de Discord  |
|  discord_remove_whitelist  |  discord_remove_whitelist [ID]  |  Remueve un usuario de la lista blanca de Discord  |
|  add_invitelist  |  add_invitelist [Nombre/ID]  |  Agrega un usuario a la lista de invitación  |
|  remove_invitelist  |  remove_invitelist [Nombre/ID]  |  Quita un usuario de la lisa de invitación  |
|  ng_outfit_for  |  ng_outfit_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `ng_outfit_for` en config  |
|  ng_outfit_operation  |  ng_outfit_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `ng_outfit_operation` en config  |
|  outfit_mimic_for  |  outfit_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (Nombre/ID)  |  Cambia el valor `outfit_mimic_for` en config  |
|  ng_backpack_for  |  ng_backpack_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `ng_backpack_for` en config  |
|  ng_backpack_operation  |  ng_backpack_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `ng_backpack_operation` en config  |
|  backpack_mimic_for  |  backpack_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (Nombre/ID)  |  Cambia el valor `backpack_mimic_for` en config  |
|  ng_pickaxe_for  |  ng_pickaxe_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `ng_pickaxe_for` en config  |
|  ng_pickaxe_operation  |  ng_pickaxe_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `ng_pickaxe_operation` en config  |
|  pickaxe_mimic_for  |  pickaxe_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (Nombre/ID)  |  Cambia el valor `pickaxe_mimic_for` en config  |
|  ng_emote_for  |  ng_emote_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `ng_emote_for` en config  |
|  ng_emote_operation  |  ng_emote_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `ng_emote_operation` en config  |
|  emote_mimic_for  |  emote_mimic_for [add/remove/user/whitelist/blacklist/owner/bot/null] (Nombre/ID)  |  Cambia el valor `emote_mimic_for` en config  |
|  ng_platform_for  |  ng_platform_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `ng_platform_for` en config  |
|  ng_platform_operation  |  ng_platform_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `ng_platform_operation` en config  |
|  ng_name_for  |  ng_name_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `ng_name_for` en config  |
|  ng_name_operation  |  ng_name_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `ng_name_operation` en config  |
|  accept_invite_for  |  accept_invite_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `accept_invite_for` en config  |
|  decline_invite_when  |  decline_invite_when [user/whitelist/blacklist/owner/bot/null]  |Cambia el valor `decline_invite_when` en config  |
|  invite_interval_for  |  invite_interval_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `invite_interval_for` en config  |
|  accept_friend_for  |  accept_friend_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `accept_friend_for` en config  |
|  whisper_enable_for  |  whisper_enable_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `whisper_enable_for` en config  |
|  party_chat_enable_for  |  party_chat_enable_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `party_chat_enable_for` en config  |
|  permission_command_operation  |  permission_command_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `permission_command_operation` en config  |
|  accept_join_for  |  accept_join_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `accept_join_for` en config  |
|  chat_max_for  |  chat_max_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `chat_max_for` en config  |
|  chat_max_operation  |  chat_max_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `chat_max_operation` en config  |
|  hide_for  |  hide_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `hide_for` en config  |
|  blacklist_operation  |  blacklist_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `blacklist_operation` en config  |
|  botlist_operation  |  botlist_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `botlist_operation` en config  |
|  discord_chat_max_for  |  discord_chat_max_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `discord_chat_max_for` en config  |
|  discord_command_enable_for  |  discord_command_enable_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `discord_command_enable_for` en config  |
|  ng_word_for  |  ng_word_for [user/whitelist/blacklist/owner/bot/null]  |  Cambia el valor `ng_word_for` en config  |
|  ng_word_operation  |  ng_word_operation [chatban/remove/block/blacklist/null]  |  Cambia el valor `ng_word_operation` en config  |
|  get_user  |  get_user [Nombre/ID]  |  Busca un usuario y muestra su nombre  |
|  get_friend  |  get_friend [Nombre/ID]  |  Busca un amigo y muestra información  |
|  get_pending  | get_pending [Nombre/ID]  |  Busca una solicitud de amistad y muestra información  |
|  get_block  |  get_block [Nombre/ID]  |  Busca un usuario bloqueado y muestra información  |
|  get_member  |  get_member [Nombre/ID]  |  Busca un miembro del grupo y muestra información  |
|  party_info  |  party_info  |  Show party info  |
|  friend_count  |  friend_count  |  Muestra la cantidad de amigos  |
|  pending_count  |  pending_count  |  Muestra la cantidad de solicitudes de amistad pendientes  |
|  block_count  |  block_count  |  Muestra la cantidad de bloqueados  |
|  friend_list  |  friend_list  |  Muestra la lista de amigos  |
|  pending_list  |  pending_list  |  Muestra la lista de solicitudes pendientes  |
|  block_list  |  block_list  |  Muestra la lista de bloqueados  |
|  add_friend  |  add_friend [Nombre/ID]  |  Añade un usuario a amigos  |
|  remove_friend  |  remove_friend [Nombre/ID]  |  Elimina a un usuario de amigos  |
|  remove_friends  |  remove_friends [cantidad]  |  Eliminar un número específico de amigos al azar. Puede ser detenido con el comando "stop"<br>Puede que este comando tarde un poco  |
|  remove_all_friend  |  remove_all_friend  |  Elimina a todos los amigos. Puede ser detenido con el comando "stop""<br>Este comando puede tardar un poco  |
|  remove_offline_for  |  remove_offline_for [Días] (Horas) (Minutos)  |  Elimina amigos desconectados por el tiempo especificado. Puede ser detenido con el comando "stop""<br>Este comando puede tardar un poco  |
|  accept_pending  |  accept_pending [Nombre/ID]  |  Acepta la solicitud de amistad de un usuario  |
|  decline_pending  |  decline_pending [Nombre/ID]  |  Rechaza la solicitud de amistad de un usuario  |
|  incoming_pending  |  incoming_pending [accept/decline]  |  Acepta/rechaza solicitudes de amistad recibidas. Puede ser detenido con el comando "stop""<br>Este comando puede tardar un poco  |
|  cancel_outgoing_pending  |  cancel_outgoing_pending  |  Cancela las solicitudes de amistad enviadas. Puede ser detenido con el comando "stop""<br>Este comando puede tardar un poco  |
|  block_user  |  block_user [Nombre/ID]  |  Bloquea un usuario  |
|  unblock_user  |  unblock_user [Nombre/ID]  |  Desbloquea un usuario  |
|  unblock_all_user  |  unblock_all_user  |  Desbloquea todos los usuarios. Puede ser detenido con el comando "stop""<br>Este comando puede tardar un poco  |
|  join  |  join [Nombre/ID]  |  Se une al grupo de un usuario  |
|  join_id  |  join_id [Party ID]  |  Se une a un grupo usando ID  |
|  request_to_join  |  request_to_join [Name/ID]  |  Enviar solicitud para unirse al usuario  |
|  leave  |  leave  |  Abandona el grupo  |
|  invite  |  invite [Nombre/ID]  |  Invita a un usuario  |
|  invite_list_users  |  invite_list_users  |  Invita a usuarios de la lista de invitación  |
|  Mensaje  |  Mensaje [Nombre/ID] : [Mensaje]  |  Envia un mensaje al usuario  |
|  party_Mensaje  |  party_Mensaje [Mensaje]  |  Envía un mensaje a la sala  |
|  avatar  |  avatar [ID] (Color)  |  Configura el avatar<br>Puedes ver los colores utilizables [aquí](config.md#Color)  |
|  status  |  status [Mensaje]  |  Configura el status  |
|  banner  |  banner [ID de banner] [Color del banner]  |  Configura el banner<br>Los ids puedes encontrarlos [aquí](https://fnitems.hyperserver.xyz/banners)  |
|  level  |  level [Number]  |  Configura el nivel  |
|  privacy  |  privacy [public, friends_allow_friends_of_friends, friends, private_allow_friends_of_friends, private]  |  Configura la privacidad de la sala  |
|  voice_chat  |  voice_chat [true/false]  |  Activa/desactiva el chat de voz de la sala. Esto no afecta a miembros que se unieron antes de unirse a la sala  |
|  promote  |  promote [Nombre/ID]  |  Promueve a lider a un usuario  |
|  kick  |  kick [Nombre/ID]  |  Expulsa a un usuario del grupo  |
|  chatban  |  chatban [Nombre/ID] : (Razón)  |  Banea del chat a un usuario  |
|  hide  |  hide (Nombre/ID)  |  Esconde al usuario en el grupo. Si el usuario no se especifica, esconde a todos en el grupo(Depende de la configuración `hide_for`)  |
|  show  |  show (Nombre/ID)  |  Muestra un usuario en el grupo. Si el usuario no se especifica se mostarán a todos los usuarios escondidos  |
|  ready  |  ready  |  Cambia el estado a listo  |
|  unready  |  unready  |  Cambia el estado a no listo  |
|  sitout  | sitout  |  Cambia el estado a no participando  |
|  match  |  match (Número)  |  Configura el estado en la partida. Si el número no se especifica se seleccionara automáticamente 100  |
|  unmatch  |  unmatch  |  Cancela el estado en la partida  |
|  swap  |  swap [Nombre/ID]  |  Cambia de posición con el usuario  |
|  stop  |  stop  |  Detiene comandos detenibles  |
|  new_items  |  new_items  |  Show items which added in update  |
|  shop_items  |  shop_items  |  Muestra los ítems en la tienda del juego  |
|  enlightenment  |  enlightenment [temporada] [número]  |  Configura el enlightenment<br>Usado en el efecto glitch de bola 8 vs bola blanca, Oro del agente plátano etc  |
|  corruption  |  corruption [Number]  |  Configura la corrupción<br>Usado en Araña corrupta etc...  |
|  all_outfit  |  all_outfit  |  Muestra todas las skins  |
|  all_backpack  |  all_backpack  |  Muestra todas las mochilas  |
|  all_pet  |  all_pet  |  Muestra todas las mascotas  |
|  all_pickaxe  |  all_pickaxe  |  Muestra todos los picos  |
|  all_emote  |  all_emote  |  Muestra todos los emotes  |
|  all_emoji  |  all_emoji  |  Muestra todos los emojis  |
|  all_toy  |  all_toy  |  Muestra todos los juguetes  |
|  cid  |  cid [ID]  |  Busca una skin por ID y la coloca  |
|  bid  |  bid [ID]  |  Busca una mochila por ID y la coloca  |
|  petcarrier  |  petcarrier [ID]  |   Busca una mascota por ID y la colocaa  |
|  pickaxe_id  |  pickaxe_id [ID]  |  Busca un pico por ID y lo coloca  |
|  eid  |  eid [ID]  |  Busca un emote por ID y lo coloca  |
|  emoji_id  |  emoji_id [ID]  |  Busca un emoji por ID y lo coloca  |
|  toy_id  |  toy_id [ID]  |  Busca un juguete por ID y lo coloca  |
|  id  |  id [ID]  |  Busca un item por ID y lo coloca  |
|  outfit  |  outfit [Nombre]  |  Busca una skin y la coloca  |
|  random_outfit  |  random_outfit  |  Cambiar a skin aleatorio  |
|  clear_outfit  |  clear_outfit  |  Remueve skin  |
|  backpack  |  backpack [Nombre]  |  Busca una mochila y la coloca  |
|  random_backpack  |  random_backpack  |  Cambiar a mochila aleatorio  |
|  pet  |  pet [Nombre]  |  Busca una mascota y la coloca  |
|  random_pet  |  random_pet  |  Cambiar a mascota aleatorio  |
|  clear_backpack  |  clear_backpack  |  Remueve la mochila  |
|  pickaxe  |  pickaxe [Nombre]  |  Busca un pico y lo coloca  |
|  random_pickaxe  |  random_pickaxe  |  Cambiar a pico aleatorio  |
|  clear_pickaxe  |  clear_pickaxe  |  Remueve el pico  |
|  emote  |  emote [Nombre]  |  Busca un emote y lo coloca  |
|  random_emote  |  random_emote  |  Cambiar a emote aleatorio  |
|  emoji  |  emoji [Nombre]  |  Busca un emoji y lo coloca  |
|  random_emoji  |  random_emoji  |  Cambiar a emoji aleatorio  |
|  toy  |  toy [Nombre]  |  Busca un juguete y lo coloca  |
|  random_toy  |  random_toy  |  Cambiar a juguete aleatorio  |
|  clear_emote  |  clear_emote  |  Remueve el emote  |
|  item  |  item [Nombre]  |  Busca un item y cambia al item  |
|  random_item  |  random_item  |  Cambiar a item aleatorio  |
|  playlist_id  |  playlist_id [ID]  |  Busca una playlist por ID y la coloca  |
|  playlist  |  playlist [Nombre]  |  Busca una playlist y la coloca  |
|  set  |  set [Nombre]  |  Busca un item por conjunto y lo coloca  |
|  set_style  |  set_style [outfit/backpack/pickaxe]  |  Muestra estilos disponibles para el cosmético actual y los coloca  |
|  add_style  |  add_style [outfit/backpack/pickaxe]  |  Muestra estilos disponibles para el cosmético actual y agrega un estilo al actual<br>Ejemplo: Cambia al estilo azul usando set_style, y agregando Stage 1 usando add_style  |
|  set_variant  |  set_variant [outfit/backpack/pickaxe] [[variante](#Variantes)] [Número]  |  **Esto es para usuarios avanzados. Utiliza set_style y add_style en su lugar**<br>Cambia a la variante especificada  |
|  add_variant  |  add_variant [outfit/backpack/pickaxe] [[variante](#Variantes)] [Número]  |  **Esto es para usuarios avanzados. Utiliza set_style y add_style en su lugar**<br>Agrega una variante a la variante actual  |
|  cosmetic_preset  |  cosmetic_preset [save/load] [número]  |  Guarda/Carga un conjunto guardado  |

### Otros identificadores
|  Identificador  |  Descripción  |
| ---- | ---- |
|  cid_  |  Cambia el item usando CID  |
|  bid_  |  Cambia el item usando BID  |
|  petcarrier_  |  Cambia el item usando PetCarrier  |
|  petid_  |  Cambia el item usando PetID  |
|  pickaxe_id_  |  Cambia el item usando Pickaxe_ID  |
|  eid_  |  Cambia el item usando EID  |
|  emoji_  |  Cambia el item usando ID de emoji  |
|  toy_  |  Cambia el item usando ID de juguete  |
|  playlist_  |  Cambia la playlist usando ID  |
|  item_search  |  Busca ítems por nombre  |

### Otros
Palabras a usar en comandos  

|  Identificador  |  Descripción  |
| ---- | ---- |
|  command  |  Usado en el comando stat. Se refiere a comando  |
|  ng_word  |  Usado en el comando stat. Se refiere a una palabra NG  |
|  most  |  Usado en el comando stat. Se refiere a la más  |
|  user  |  Se refiere al tipo de usuario  |
|  whitelist  |  Se refiere a la lista blanca  |
|  blacklist  |  Se refiere a la lista negra  |
|  owner  |  Se refiere al owner  |
|  bot  |  Se refiere al tipo de usuarioa bot  |
|  null  |  Significa ninguno  |
|  chatban  |  Se refiere a la operación de banear del chat  |
|  remove  |  Se refiere a la operación de remover de amigos  |
|  block  |  Se refiere a la operación de bloquear  |
|  blacklist  |  Se refiere a la operación de lista negra  |
|  add   |  Usado en el comandos outfit_mimic_for, backpack_mimic_for, pickaxe_mimic_for, emote_mimic_for. Significa agregar  |
|  remove  |  Usado en el comandos outfit_mimic_for, backpack_mimic_for, pickaxe_mimic_for, emote_mimic_for. Significa eliminar  |
|  true  |  Usado en el comando voice_chat. Significa habilitado  |
|  false  |  Usado en el comando voice_chat. Significa deshabilitado  |
|  accept  |  Usado en el comando incoming_pending . Significa aceptar  |
|  decline  |  Usado en el comando incoming_pending . Significa rechazar  |
|  public  |  Usado en el comando privacy. Significa público
|  friends_allow_friends_of_friends  |  Usado en el comando privacy. Significa solo amigos (permitir amigos de amigos)  |
|  friends  |  Usado en el comando privacy. Means friends only  |
|  private_allow_friends_of_friends  |  Usado en el comando privacy. Significa privado (permite amigos de amigos)  |
|  private  |  Usado en el comando privacy. Significa privado  |
|  outfit  |  Usado en el comando set_style, add_style, set_variant, add_variant. Significa skin  |
|  backpack  |  Usado en el comando set_style, add_style, set_variant, add_variant. Significa mochila  |
|  pickaxe  |  Usado en el comando set_style, add_style, set_variant, add_variant. Significa privado  |
|  save  |  Usado en cosmetic_preset. Significa guardar  |
|  load  |  Usado en cosmetic_preset. Significa cargar  |

### Variantes
pattern/numeric/clothing_color/jersey_color/parts/progressive/particle/material/emissive
