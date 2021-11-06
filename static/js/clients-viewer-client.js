const openables = document.getElementsByClassName('openable');
Array.from(openables).forEach(openable => {
    openable.firstElementChild.onclick = function () {
        openable.classList.toggle('open');
    }
});

console.log('Connecting to websocket');
const socket = new WebSocket(getWsAddr());

function sendEvent(event, wait_event, user_id) {
    socket.send(JSON.stringify({event: event, wait_event: wait_event, user_id: user_id}));
}

function acceptFriend(wait_event, user_id) {
    sendEvent('accept_friend', wait_event, user_id);
}

function addFriend(wait_event, user_id) {
    sendEvent('add_friend', wait_event, user_id);
}

function blockUser(wait_event, user_id) {
    sendEvent('block_user', wait_event, user_id);
}

function removeOrDeclineFriend(wait_event, user_id) {
    sendEvent('remove_or_decline_friend', wait_event, user_id);
}

function unblockUser(wait_event, user_id) {
    sendEvent('unblock_user', wait_event, user_id);
}

function promoteMember(wait_event, user_id) {
    sendEvent('member_promote', wait_event, user_id);
}

function kickMember(wait_event, user_id) {
    sendEvent('member_kick', wait_event, user_id);
}

function joinFriend(user_id) {
    socket.send(JSON.stringify({
        event: 'join_friend',
        user_id: user_id
    }));
}

function acceptJoinRequest(user_id) {
    socket.send(JSON.stringify({
        event: 'accept_join_request',
        user_id: user_id
    }));
}

function declineJoinRequest(user_id) {
    socket.send(JSON.stringify({
        event: 'decline_join_request',
        user_id: user_id
    }));
}

function sendWhisper(element) {
    const user_id = element.parentElement.parentElement.id.slice('whisper_to_'.length);
    const input = element.previousElementSibling;
    socket.send(JSON.stringify({
        event: 'friend_message',
        user_id: user_id,
        content: input.value
    }));
    element.previousElementSibling.value = '';
}

function whisperKeyPress(key, element) {
    if (key == 'Enter') {
        sendWhisper(element);
    }
}

function sendPartyMessage(element) {
    const input = element.previousElementSibling;
    socket.send(JSON.stringify({
        event: 'party_message',
        content: input.value
    }));
    element.previousElementSibling.value = '';
}

function partyChatKeyPress(key, element) {
    if (key == 'Enter') {
        sendPartyMessage(element);
    }
}

function sendCommand(element) {
    const input = element.previousElementSibling;
    socket.send(JSON.stringify({
        event: 'command',
        content: input.value
    }));
    setTimeout(function () {
        element.previousElementSibling.value = '';
    }, 0.01)
}

function commandKeyPress(event, element) {
    if (event.key == 'Enter' && !event.shiftKey) {
        sendCommand(element);
    }
}

function leaveParty() {
    socket.send(JSON.stringify({
        event: 'leave_party'
    }));
}

socket.addEventListener('open', function(ev) {
    console.log('Successfully connected to websocket');
})

socket.addEventListener('close', function (ev) {
    console.log('Websocket connection is closing');
})

socket.addEventListener('message', function(ev) {
    const client = JSON.parse(ev.data);
    console.log(client);

    const name = document.getElementById('name');
    const party = document.getElementById('party_name');
    const incoming_friend_request = document.getElementById('incoming_friend_request');
    const outgoing_friend_request = document.getElementById('outgoing_friend_request');
    const join_request = document.getElementById('join_request');
    const friend = document.getElementById('friend');
    const blocked_user = document.getElementById('blocked_user');
    const member = document.getElementById('member');
    const friend_message = document.getElementById('friend_message');
    const party_message = document.getElementById('party_message')
    
    if (client.type == 'full' || client.type == 'diff') {
        name.textContent = client.name;
        party.textContent = client.party;
        incoming_friend_request.firstElementChild.textContent = client.incoming_friend_request;
        outgoing_friend_request.firstElementChild.textContent = client.outgoing_friend_request;
        join_request.firstElementChild.textContent = client.join_request
        friend.firstElementChild.textContent = client.friend;
        blocked_user.firstElementChild.textContent = client.blocked_user;
        member.firstElementChild.textContent = client.party_member;
    }

    function constructIncomingFriendRequest(element, pending) {
        const div = document.createElement('div');
        div.setAttribute('user_id', pending.id);

        const accept = document.createElement('input');
        accept.type = 'button';
        accept.classList.add('gray_button');
        accept.value = texts.accept
        accept.onclick = function () {
            acceptFriend('friend_add', pending.id);
        }
        div.appendChild(accept);

        const decline = document.createElement('input');
        decline.type = 'button';
        decline.classList.add('red_button');
        decline.value = texts.decline
        decline.onclick = function () {
            removeOrDeclineFriend('friend_request_decline', pending.id);
        }
        div.appendChild(decline);

        const block = document.createElement('input');
        block.type = 'button';
        block.classList.add('red_button');
        block.value = texts.block
        block.onclick = function () {
            blockUser('user_block', pending.id);
        }
        div.appendChild(block);

        const span = document.createElement('span');
        span.classList.add('user');
        span.textContent = pending.name;
        div.appendChild(span);

        element.appendChild(div);
    }

    function constructOutgoingFriendRequest(element, pending) {
        const div = document.createElement('div');
        div.setAttribute('user_id', pending.id);

        const cancel = document.createElement('input');
        cancel.type = 'button';
        cancel.classList.add('red_button');
        cancel.value = texts.cancel
        cancel.onclick = function () {
            removeOrDeclineFriend('friend_request_abort', pending.id);
        }
        div.appendChild(cancel);

        const block = document.createElement('input');
        block.type = 'button';
        block.classList.add('red_button');
        block.value = texts.block
        block.onclick = function () {
            blockUser('user_block', pending.id);
        }
        div.appendChild(block);

        const span = document.createElement('span');
        span.classList.add('user');
        span.textContent = pending.name;
        div.appendChild(span);

        element.appendChild(div);
    }

    function constructJoinRequest(element, request) {
        const div = document.createElement('div');
        div.setAttribute('user_id', request.id);

        const accept = document.createElement('input');
        accept.type = 'button';
        accept.classList.add('gray_button');
        accept.value = texts.accept
        accept.onclick = function () {
            acceptJoinRequest(request.id);
        }
        div.appendChild(accept);

        const decline = document.createElement('input');
        decline.type = 'button';
        decline.classList.add('red_button');
        decline.value = texts.decline
        decline.onclick = function () {
            declineJoinRequest(request.id);
        }
        div.appendChild(decline);

        const span = document.createElement('span');
        span.classList.add('user');
        span.textContent = request.name;
        div.appendChild(span);

        element.appendChild(div);
    }

    function constructFriend(element, friend) {
        const div = document.createElement('div');
        div.setAttribute('user_id', friend.id);

        if (friend.is_joinable) {
            const join = document.createElement('input');
            join.type = 'button';
            join.classList.add('gray_button');
            join.value = texts.join;
            join.onclick = function () {
                joinFriend(friend.id);
            }
            div.appendChild(join);
        }

        const whisper = document.createElement('input');
        whisper.type = 'button';
        whisper.classList.add('gray_button');
        whisper.value = texts.whisper;
        whisper.onclick = function () {
            constructWhisper(member.id, null);
        }
        div.appendChild(whisper);

        const remove = document.createElement('input');
        remove.type = 'button';
        remove.classList.add('red_button');
        remove.value = texts.remove
        remove.onclick = function () {
            removeOrDeclineFriend('friend_remove', friend.id);
        }
        div.appendChild(remove);

        const block = document.createElement('input');
        block.type = 'button';
        block.classList.add('red_button');
        block.value = texts.block
        block.onclick = function () {
            blockUser('user_block', friend.id);
        }
        div.appendChild(block);

        const span = document.createElement('span');
        span.classList.add('user');
        span.textContent = friend.name;
        if (friend.is_online) {
            span.classList.add('online');
        } else {
            span.classList.add('offline');
        }
        div.appendChild(span);

        element.appendChild(div);
    }

    function constructBlockedUser(element, blocked_user) {
        const div = document.createElement('div');
        div.setAttribute('user_id', blocked_user.id);

        const unblock = document.createElement('input');
        unblock.type = 'button';
        unblock.classList.add('gray_button');
        unblock.value = texts.unblock
        unblock.onclick = function () {
            unblockUser('user_unblock', blocked_user.id);
        }
        div.appendChild(unblock);

        const span = document.createElement('span');
        span.classList.add('user');
        span.textContent = blocked_user.name;
        div.appendChild(span);

        element.appendChild(div);
    }

    function constructPartyMember(element, member) {
        const div = document.createElement('div');
        div.classList.add('member');
        div.setAttribute('user_id', member.id);
        div.setAttribute('position', member.position);

        if (client.client_party_member.id != member.id){
            const promote = document.createElement('input');
            promote.type = 'button';
            promote.classList.add('gray_button');
            promote.classList.add('party_button');
            promote.value = texts.promote;
            promote.onclick = function () {
                promoteMember('party_member_promote', member.id)
            }
            div.appendChild(promote);

            const kick = document.createElement('input');
            kick.type = 'button';
            kick.classList.add('gray_button');
            kick.classList.add('party_button');
            kick.value = texts.kick;
            kick.onclick = function () {
                kickMember('party_member_kick', member.id)
            }
            div.appendChild(kick);
        }

        if (member.is_incoming_pending) {
            const accept = document.createElement('input');
            accept.type = 'button';
            accept.classList.add('gray_button');
            accept.value = texts.accept;
            accept.onclick = function () {
                acceptFriend('friend_add', member.id);
            }
            div.appendChild(accept);

            const decline = document.createElement('input');
            decline.type = 'button';
            decline.classList.add('red_button');
            decline.value = texts.decline;
            decline.onclick = function () {
                removeOrDeclineFriend('friend_request_decline', member.id);
            }
            div.appendChild(decline);

            const block = document.createElement('input');
            block.type = 'button';
            block.classList.add('red_button');
            block.value = texts.block;
            block.onclick = function () {
                blockUser('user_block', member.id);
            }
            div.appendChild(block);
        } else if (member.is_outgoing_pending) {
            const cancel = document.createElement('input');
            cancel.type = 'button';
            cancel.classList.add('red_button');
            cancel.value = texts.cancel;
            cancel.onclick = function () {
                removeOrDeclineFriend('friend_request_abort', member.id);
            }
            div.appendChild(cancel);

            const block = document.createElement('input');
            block.type = 'button';
            block.classList.add('red_button');
            block.value = texts.block;
            block.onclick = function () {
                blockUser('user_block', member.id);
            }
            div.appendChild(block);
        } else if (member.is_friend) {
            const whisper = document.createElement('input');
            whisper.type = 'button';
            whisper.classList.add('gray_button');
            whisper.value = texts.whisper;
            whisper.onclick = function () {
                constructWhisper(member.id, member.display_name, null);
            }
            div.appendChild(whisper);

            const remove = document.createElement('input');
            remove.type = 'button';
            remove.classList.add('red_button');
            remove.value = texts.remove;
            remove.onclick = function () {
                removeOrDeclineFriend('friend_remove', member.id);
            }
            div.appendChild(remove);

            const block = document.createElement('input');
            block.type = 'button';
            block.classList.add('red_button');
            block.value = texts.block;
            block.onclick = function () {
                blockUser('user_block', member.id);
            }
            div.appendChild(block);
        } else if (member.is_blocked) {
            const unblock = document.createElement('input');
            unblock.type = 'button';
            unblock.classList.add('gray_button');
            unblock.value = texts.unblock;
            unblock.onclick = function () {
                unblockUser('user_unblock', member.id);
            }
            div.appendChild(unblock);
        }

        const container = document.createElement('div');
        container.classList.add('container');
        if (member.is_leader) {
            container.classList.add('leader');
        }

        const img = document.createElement('img');
        img.classList.add('banner');
        img.src = member.banner;
        img.onerror = function () {
            img.onerror = null;
            img.src = '/static/images/banner.jpg';
        }
        container.appendChild(img);

        const level = document.createElement('span');
        level.classList.add('level');
        level.textContent = String(member.level);
        div.appendChild(level);

        div.appendChild(container);

        const span = document.createElement('span');
        span.classList.add('user');
        span.textContent = member.name;

        div.appendChild(span);
        div.appendChild(document.createElement('br'));

        const keys = [
            'outfit',
            'backpack',
            'pickaxe',
            'emote'
        ]
        keys.forEach(key => {
            if (member[key] != null) {
                const img_div = document.createElement('div');
                img_div.classList.add('img_div');
                const img = document.createElement('img');
                img.src = member[key]['url'];
                img.onerror = function () {
                    img.onerror = null;
                    img.src = `/static/images/${key}.jpg`;
                }
                img_div.appendChild(img);
                const p = document.createElement('p');
                p.textContent = member[key]['name'];
                img_div.appendChild(p);
                div.appendChild(img_div);
            }
        });

        element.appendChild(div);
    }

    function constructWhisper(to, display_name, whisper) {
        const whisper_content = friend_message.firstElementChild.nextElementSibling;
        if (document.getElementById(`whisper_to_${to}`)) {
            if (whisper == null) {
                return;
            }

            const whisper_to = document.getElementById(`whisper_to_${to}`);
            const whisper_to_content = whisper_to.lastElementChild;
            const container = document.createElement('pre');
            const span1 = document.createElement('span');
            span1.classList.add('whisper_date');
            span1.textContent = `${whisper.received_at} ${whisper.author.display_name}: `;
            container.appendChild(span1);
            const span2 = document.createElement('span');
            span2.classList.add('whisper_content');
            span2.textContent = whisper.content;
            container.appendChild(span2);
            whisper_to_content.insertBefore(container, whisper_to_content.lastElementChild.previousElementSibling);

            whisper_to_content.scrollTo(0, whisper_to_content.scrollHeight);
        } else {
            const whisper_to = document.createElement('div');
            whisper_to.id = `whisper_to_${to}`;
            whisper_to.classList.add('openable');

            const span = document.createElement('span');
            span.textContent = display_name;
            whisper_to.appendChild(span);
            
            const delete_button = document.createElement('input');
            delete_button.classList.add('gray_button');
            delete_button.style = 'margin-left: 5px;';
            delete_button.type = 'button';
            delete_button.value = texts.remove;
            delete_button.onclick = function () {
                whisper_content.removeChild(whisper_to);
            }
            whisper_to.appendChild(delete_button);

            const whisper_to_content = document.createElement('div');
            whisper_to_content.classList.add('whisper');
            whisper_to_content.classList.add('content');

            if (whisper != null) {
                const container = document.createElement('pre');
                const span1 = document.createElement('span');
                span1.classList.add('whisper_date');
                span1.textContent = `${whisper.received_at} ${whisper.author.display_name}: `;
                container.appendChild(span1);
                const span2 = document.createElement('span');
                span2.classList.add('whisper_content');
                span2.textContent = whisper.content;
                container.appendChild(span2);
                whisper_to_content.appendChild(container);
            }

            whisper_to.appendChild(whisper_to_content);
            whisper_content.appendChild(whisper_to);

            const input = document.createElement('input');
            input.classList.add('chat_input');
            input.type = 'text';
            whisper_to_content.appendChild(input);

            const submit = document.createElement('input');
            submit.classList.add('chat_submit');
            submit.type = 'submit';
            submit.onclick = function () {
                sendWhisper(submit);
            }
            whisper_to_content.appendChild(submit);
            input.onkeydown = function (event) {
                whisperKeyPress(event.key, submit);
            }

            whisper_to.firstElementChild.onclick = function () {
                whisper_to.classList.toggle('open');
            }

            whisper_to_content.scrollTo(0, whisper_to_content.scrollHeight);
        }

    }

    function constructPartyChat(party_chat) {
        const party_chat_content = party_message.firstElementChild.nextElementSibling;
        const container = document.createElement('pre');
        const span1 = document.createElement('span');
        span1.classList.add('party_chat_date');
        span1.textContent = `${party_chat.received_at} ${party_chat.author.display_name}: `;
        container.appendChild(span1);
        const span2 = document.createElement('span');
        span2.classList.add('party_chat_content');
        span2.textContent = party_chat.content;
        container.appendChild(span2);
        party_chat_content.insertBefore(container, party_chat_content.lastElementChild.previousElementSibling);

        party_chat_content.scrollTo(0, party_chat_content.scrollHeight);
    }

    function fullUpdate() {
        const incoming_friend_requests = client.friend_requests.filter(
            request => request.type == 'incoming'
        );

        const incoming_friend_request_content = incoming_friend_request.firstElementChild.nextElementSibling;
        incoming_friend_request_content.innerHTML = '';
        incoming_friend_requests.forEach(pending => {
            constructIncomingFriendRequest(incoming_friend_request_content, pending);
        });

        const outgoing_friend_requests = client.friend_requests.filter(
            request => request.type == 'outgoing'
        );

        const outgoing_friend_request_content = outgoing_friend_request.firstElementChild.nextElementSibling;
        outgoing_friend_request_content.innerHTML = '';
        outgoing_friend_requests.forEach(pending => {
            constructOutgoingFriendRequest(outgoing_friend_request_content, pending);
        });

        const join_request_content = join_request.firstElementChild.nextElementSibling;
        join_request_content.innerHTML = '';
        client.join_requests.forEach(request => {
            constructJoinRequest(join_request_content, request);
        });

        const online_friends =  client.friends.filter(
            friend => friend.is_online
        );
        const offline_friends =  client.friends.filter(
            friend => !friend.is_online
        );

        const friend_content = friend.firstElementChild.nextElementSibling;
        friend_content.innerHTML = '';
        online_friends.concat(offline_friends).forEach(friend => {
            constructFriend(friend_content, friend);
        });

        const blocked_user_content = blocked_user.firstElementChild.nextElementSibling;
        blocked_user_content.innerHTML = '';
        client.blocked_users.forEach(blocked_user => {
            constructBlockedUser(blocked_user_content, blocked_user);
        });
    
        const member_content = member.firstElementChild.nextElementSibling;
        member_content.innerHTML = '';
        client.party_members.forEach(member => {
            constructPartyMember(member_content, member);
        });

        function comparePosition(a, b) {
            return (parseInt(a.getAttribute('position')) - parseInt(b.getAttribute('position')));
        }

        const sorted_members = Array.from(member_content.children).sort(comparePosition);
        sorted_members.forEach(member => {
            member_content.appendChild(member_content.removeChild(member));
        });

        const whisper_content = friend_message.firstElementChild.nextElementSibling;
        whisper_content.innerHTML = '';

        for (let [to, data] of Object.entries(client.whisper)) {
            data.content.forEach(whisper => {
                constructWhisper(to, data.display_name, whisper)
            });
        };

        client.party_chat.forEach(party_chat => {
            constructPartyChat(party_chat);
        });
    }

    function diffUpdate() {
        const removed_incoming_friend_requests = client.removed.friend_requests.filter(
            request => request.type == 'incoming'
        );
        const added_incoming_friend_requests = client.added.friend_requests.filter(
            request => request.type == 'incoming'
        );

        const incoming_friend_request_content = incoming_friend_request.firstElementChild.nextElementSibling;
        removed_incoming_friend_requests.forEach(pending => {
            Array.from(incoming_friend_request_content.children).forEach(child => {
                if (child.getAttribute('user_id') == pending.id) {
                    incoming_friend_request_content.removeChild(child);
                }
            });
        });
        added_incoming_friend_requests.forEach(pending => {
            constructIncomingFriendRequest(incoming_friend_request_content, pending);
        });

        const removed_outgoing_friend_requests = client.removed.friend_requests.filter(
            request => request.type == 'outgoing'
        );
        const added_outgoing_friend_requests = client.added.friend_requests.filter(
            request => request.type == 'outgoing'
        );

        const outgoing_friend_request_content = outgoing_friend_request.firstElementChild.nextElementSibling;
        removed_outgoing_friend_requests.forEach(pending => {
            Array.from(outgoing_friend_request_content.children).forEach(child => {
                if (child.getAttribute('user_id') == pending.id) {
                    outgoing_friend_request_content.removeChild(child);
                }
            });
        });
        added_outgoing_friend_requests.forEach(pending => {
            constructOutgoingFriendRequest(outgoing_friend_request_content, pending);
        });

        const join_request_content = join_request.firstElementChild.nextElementSibling;
        join_request_content.innerHTML = '';
        client.removed.join_requests.forEach(request => {
            Array.from(join_request_content.children).forEach(child => {
                if (child.getAttribute('user_id') == request.id) {
                    join_request_content.removeChild(child);
                }
            });
        });
        client.added.join_requests.forEach(request => {
            constructJoinRequest(join_request_content, request);
        });

        const removed_online_friends =  client.removed.friends.filter(
            friend => friend.is_online
        );
        const removed_offline_friends =  client.removed.friends.filter(
            friend => !friend.is_online
        );
        const added_online_friends =  client.added.friends.filter(
            friend => friend.is_online
        );
        const added_offline_friends =  client.added.friends.filter(
            friend => !friend.is_online
        );

        const friend_content = friend.firstElementChild.nextElementSibling;
        removed_online_friends.concat(removed_offline_friends).forEach(friend => {
            Array.from(friend_content.children).forEach(child => {
                if (child.getAttribute('user_id') == friend.id) {
                    friend_content.removeChild(child);
                }
            });
        });
        added_online_friends.concat(added_offline_friends).forEach(friend => {
            constructFriend(friend_content, friend);
        });

        const blocked_user_content = blocked_user.firstElementChild.nextElementSibling;
        client.removed.blocked_users.forEach(blocked_user => {
            Array.from(blocked_user_content.children).forEach(child => {
                if (child.getAttribute('user_id') == blocked_user.id) {
                    blocked_user_content.removeChild(child);
                }
            });
        });
        client.added.blocked_users.forEach(blocked_user => {
            constructBlockedUser(blocked_user_content, blocked_user);
        });

        const member_content = member.firstElementChild.nextElementSibling;
        client.removed.party_members.forEach(member => {
            Array.from(member_content.children).forEach(child => {
                if (child.getAttribute('user_id') == member.id) {
                    member_content.removeChild(child);
                }
            });
        });
        client.added.party_members.forEach(member => {
            constructPartyMember(member_content, member);
        });

        function comparePosition(a, b) {
            return (parseInt(a.getAttribute('position')) - parseInt(b.getAttribute('position')));
        }

        const sortedMembers = Array.from(member_content.children).sort(comparePosition);
        sortedMembers.forEach(member => {
            member_content.appendChild(member_content.removeChild(member));
        });
    }

    if (client.type == 'full') {
        fullUpdate();
        styleTag = document.createElement('style');
        styleTag.innerHTML = '.content {display: none;}';
        document.getElementsByTagName('head')[0].appendChild(styleTag);
    } else if (client.type == 'diff') {
        diffUpdate();
    } else if (client.type == 'friend_message') {
        constructWhisper(client.to, client.author.display_name, client);
    } else if (client.type == 'party_message') {
        constructPartyChat(client);
    } else if (client.type == 'clear_party_message') {
        const party_chat_content = party_message.firstElementChild.nextElementSibling;
        while (party_chat_content.firstElementChild) {
            if (party_chat_content.firstElementChild.tagName == 'PRE') {
                party_chat_content.removeChild(party_chat_content.firstElementChild);
            } else {
                break;
            }
        }
    } else if (client.type == 'response') {
        const res = document.getElementById('res');
        res.innerHTML = '';
        const pre = document.createElement('pre');
        pre.innerText = client.response;
        res.appendChild(pre);
    }

    if (client.type == 'full' || client.type == 'diff') {
        const party_buttons = document.getElementsByClassName('party_button');
        Array.from(party_buttons).forEach(button => {
            if (client.client_party_member.is_leader) {
                button.style.display = 'inline-block';
            } else {
                button.style.display = 'none';
            }
        });
    }
})