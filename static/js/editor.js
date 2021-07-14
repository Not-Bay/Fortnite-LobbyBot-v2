function visualEnable() {
    const visualEditor = document.getElementById('visual_editor');
    const visualSave = document.getElementById('visual_save');
    const visualSaveAndReload = document.getElementById('visual_save_and_reload');
    const rawEditor = document.getElementById('raw_editor');
    const rawSave = document.getElementById('raw_save');
    const rawSaveAndReload = document.getElementById('raw_save_and_reload');
    visualEditor.style.visibility = 'visible';
    visualEditor.style.opacity = 1;
    visualSave.style.display = 'block';
    visualSaveAndReload.style.display = 'block';
    rawEditor.style.visibility = 'hidden';
    rawEditor.style.opacity = 0;
    rawSave.style.display = 'none';
    rawSaveAndReload.style.display = 'none';
}

function rawEnable() {
    const visualEditor = document.getElementById('visual_editor');
    const visualSave = document.getElementById('visual_save');
    const visualSaveAndReload = document.getElementById('visual_save_and_reload');
    const rawEditor = document.getElementById('raw_editor');
    const rawSave = document.getElementById('raw_save');
    const rawSaveAndReload = document.getElementById('raw_save_and_reload');
    visualEditor.style.visibility = 'hidden';
    visualEditor.style.opacity = 0;
    visualSave.style.display = 'none';
    visualSaveAndReload.style.display = 'none';
    rawEditor.style.visibility = 'visible';
    rawEditor.style.opacity = 1;
    rawSave.style.display = 'block';
    rawSaveAndReload.style.display = 'block';
}

function saveVisual(reload = false) {
    const form = document.getElementById('visual_form');
    const formData = new FormData(form);
    const request = new XMLHttpRequest();
    if (reload) {
        request.open('POST', location.pathname + '/save?reload=true');
    } else {
        request.open('POST', location.pathname + '/save');
    }
    request.send(formData);
    request.onload = function (ev) {
        const data = JSON.parse(request.responseText);
        console.log(data);
        const res = document.getElementById('res');
        res.style.color = data.color;
        res.style.transform = 'translateX(-50%) translateY(0%)';
        res.innerText = data.text;

        res.ontransitionend = function () {
            setTimeout(function () {
                res.style.transform = 'translateX(-50%) translateY(-200px)';
            }, 1500);
        }

        editor.setValue(JSON.stringify(data.data, null, 4));

        for (let [key, value] of Object.entries(data.flat_data)) {
            const valueElement = document.getElementById(key);
            if (valueElement) {
                if (valueElement.tagName == 'INPUT' || valueElement.tagName == 'TEXTAREA') {
                    valueElement.value = value;
                } else {
                    Array.from(valueElement.children).forEach(select => {
                        if (value === null) {
                            if (select.value == 'null') {
                                select.selected = true;
                            }
                        } else if (typeof(value) === Boolean) {
                            if (select.value == value.toString()) {
                                select.selected = true;
                            }
                        } else {
                            if (select.value == value) {
                                select.selected = true;
                            }
                        }
                    });
                }
                valueElement.style.color = null;

                const label = valueElement.previousElementSibling;
                if (label) {
                    label.style.color = null;
                }

                if (key.indexOf("['clients']") != -1) {
                    const h1 = valueElement.parentElement.parentElement.firstElementChild;
                    if (h1) {
                        h1.style.color = null;
                    }
    
                    const client = h1.parentElement.parentElement.firstElementChild;
                    if (client) {
                        client.style.color = null;
                    }
                }
            }
        }

        if (data.errors.length > 0) {
            const shake = document.getElementById('shake');
            shake.style.animation = 'shake 400ms';
            setTimeout(function () {
                shake.style.animation = '';
            }, 400);
        }
        for (let key of data.errors) {
            const valueElement = document.getElementById(key);
            if (valueElement) {
                valueElement.style.backgroundColor = '#F04747';
            }
            valueElement.ontransitionend = function() {
                setTimeout(function () {
                    if (valueElement) {
                        valueElement.style.backgroundColor = '';
                    }
                }, 700);
            }
            const label = valueElement.previousElementSibling;
            if (label) {
                label.style.color = '#F04747';
            }

            if (key.indexOf("['clients']") != -1) {
                const h1 = valueElement.parentElement.parentElement.firstElementChild;
                if (h1) {
                    h1.style.color = '#F04747';
                }

                const client = h1.parentElement.parentElement.firstElementChild;
                if (client) {
                    client.style.color = '#F04747';
                }
            }
        }
    }
}

function saveRaw(reload = false) {
    try {
        const request = new XMLHttpRequest();
        if (reload) {
            request.open('POST', location.pathname + '/save-raw?reload=true');
        } else {
            request.open('POST', location.pathname + '/save-raw');
        }
        request.setRequestHeader('Content-Type', 'application/json');
        console.log(JSON.parse(editor.getValue()));
        request.send(JSON.stringify(JSON.parse(editor.getValue())));
        request.onload = function (ev) {
            const data = JSON.parse(request.responseText);
            const res = document.getElementById('res');
            res.style.color = data.color;
            res.style.transform = 'translateX(-50%) translateY(0%)';
            res.innerText = data.text;

            res.ontransitionend = function () {
                setTimeout(function () {
                    res.style.transform = 'translateX(-50%) translateY(-200px)';
                }, 1500);
            }

            editor.setValue(JSON.stringify(data.data, null, 4));

            for (let [key, value] of Object.entries(data.flat_data)) {
                const valueElement = document.getElementById(key);
                if (valueElement !== null) {
                    valueElement.value = value;
                }
            }

            if (data.errors.length > 0) {
                const shake = document.getElementById('shake');
                shake.style.animation = 'shake 400ms';
                setTimeout(function () {
                    shake.style.animation = '';
                }, 400);
            }
            for (let key of data.errors) {
                const label = document.getElementById('label_' + key);
                if (label !== null) {
                    label.style.color = '#F04747';
                }
                const valueElement = document.getElementById(key);
                if (valueElement !== null) {
                    valueElement.style.backgroundColor = '#F04747';
                }
                valueElement.ontransitionend = function() {
                    setTimeout(function () {
                        if (valueElement !== null) {
                            valueElement.style.backgroundColor = '';
                        }
                    }, 700);
                }
            }
        }
    } catch {
        const res = document.getElementById('res');
        res.style.color = '#F04747';
        res.style.transform = 'translateX(-50%) translateY(0%)';
        res.innerText = texts.invalid_json;

        res.ontransitionend = function () {
            setTimeout(function () {
                res.style.transform = 'translateX(-50%) translateY(-200px)';
            }, 1500);
        }

        const shake = document.getElementById('shake');
        shake.style.animation = 'shake 400ms';
        setTimeout(function () {
            shake.style.animation = '';
        }, 400);

        return (false);
    }
}


function replaceAttr(element, attr, before, after) {
    element.setAttribute(attr, element.getAttribute(attr).replace(before, after));
}

function fixId(items, id_before, id_after) {
    items.forEach(item => {
        // item = key_value
        if (item.classList.contains('editor_h')) {
            Array.from(item.children).forEach(child => {
                if (child.tagName == 'DIV') {
                    // child = openable
                    const item_items = Array.from(child.lastElementChild.children).filter(
                        child => child.tagName == 'DIV'
                    );
                    fixId(item_items, id_before, id_after);

                    child.classList.remove('open');
                    child.firstElementChild.onclick = function () {
                        child.classList.toggle('open');
                    }
                }
            })
        } else {
            let label, input;
            [label, input]  = item.children;
            if (input !== undefined) {
                if (input.classList.contains('value')) {
                    replaceAttr(label, 'for', id_before, id_after);
                    replaceAttr(input, 'id', id_before, id_after);
                    replaceAttr(input, 'name', id_before, id_after);
                } else {
                    // random_message
                    const button = Array.from(input.children).slice(-1)[0];
                    button.onclick = function () {
                        addListList(button, button.getAttribute('key').replace(id_before, id_after));
                    }
                    replaceAttr(button, 'key', id_before, id_after);

                    Array.from(input.children).forEach(item_child => {
                        if (item_child.tagName == 'DIV') {
                            replaceAttr(label, 'for', id_before, id_after);
                            const textarea = item_child.firstElementChild;
                            replaceAttr(textarea, 'id', id_before, id_after);
                            replaceAttr(textarea, 'name', id_before, id_after);
                        }
                    });
                }
            }
        }
    });
}


function removeListList(element) {
    element.parentNode.parentNode.removeChild(element.parentNode.nextElementSibling);
    element.parentNode.parentNode.removeChild(element.parentNode);
}

function addListList(element, key) {
    const parent = element.parentNode;
    const div = document.createElement('div');
    let num = 0;
    Array.from(element.parentNode.children).forEach(child => {
        if (child.tagName == 'DIV') {
            num += 1;
        }
    });
    const textarea = document.createElement('textarea');
    textarea.id = key + `[${num}]`;
    textarea.className = 'value';
    textarea.setAttribute('name', key + `[${num}]`);
    div.appendChild(textarea);

    const input = document.createElement('input');
    input.className = 'remove_button';
    input.type = 'button';
    input.value = texts.remove;
    input.onclick = function () {
        removeListList(input);
    }
    div.appendChild(input);

    parent.insertBefore(div, element);
}

function removeElement(element, prefix) {
    // prefix = "['clients']"
    // id_prefix = clients
    const id_prefix = element.parentElement.parentElement.getAttribute('id');
    const parent = element.parentElement.parentElement;  // clients
    const element_count = Array.from(parent.children).filter(
        child => child.tagName == 'DIV'
    ).length;  // Total count of clients
    const element_num = parseInt(element.parentElement.id.slice(id_prefix.length + 1));  // Number of client which trying to remove
    parent.removeChild(element.parentElement.nextElementSibling);  // br
    parent.removeChild(element.parentElement);  // client
    if (element_count != element_num) {
        let current_num = 0;
        Array.from(parent.children).forEach(child => {
            // child = client
            if (child.tagName == 'DIV') {
                if (element_count >= current_num) {
                    const num = parseInt(child.id.slice(id_prefix.length + 1));
                    child.id = `${id_prefix}_${current_num}`;
                    const id_before = `${prefix}[${num}]`;
                    const id_after = `${prefix}[${current_num}]`;
    
                    const request = new XMLHttpRequest();
                    request.open('POST', '/l');
                    request.setRequestHeader('Content-Type', 'application/json');
                    request.send(JSON.stringify({
                        text: id_prefix.slice(0, -1),
                        args: [current_num + 1],
                        kwargs: {}
                    }));
                    request.onload = function () {
                        child.children[0].textContent = request.responseText;
                    }

                    const items = Array.from(child.children[1].children).filter(
                        child => child.tagName == 'DIV'
                    );
                    fixId(items, id_before, id_after);
                }
                current_num += 1
            }
        });
    }
}

function addElement(element, prefix) {
    // prefix = "['clients']"
    // id_prefix = clients
    const id_prefix = element.parentElement.getAttribute('id');
    const parent = element.parentElement;  // clients
    let copyElement = null;
    Array.from(parent.childNodes).forEach(child => {
        if (child.tagName == 'DIV') {
            copyElement = child;
        }
    });
    if (copyElement === null) {
        const request = new XMLHttpRequest();
        if (id_prefix == 'ng_names' || id_prefix == 'ng_words') {
            request.open('POST', `${location.pathname}/add-${id_prefix.replace('_', '-').slice(0, -1)}/` + element.parentNode.getAttribute('client_num'));
        } else {
            request.open('POST', `${location.pathname}/add-${id_prefix.replace('_', '-').slice(0, -1)}`);
        }
        request.send(null);
        request.onload = function () {
            console.log(request.responseText);
            if (request.status == 204) {
                window.location.reload();
            }
        }
    } else {
        const newElement = copyElement.cloneNode(true);
        const num = parseInt(newElement.id.slice(id_prefix.length + 1));
        newElement.setAttribute('id', `${id_prefix}_${num + 1}`);
        newElement.setAttribute('num', `${num + 1}`);
        const id_before = `${prefix}[${num}]`;
        const id_after = `${prefix}[${num + 1}]`;

        const request = new XMLHttpRequest();
        request.open('POST', '/l');
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify({
            text: id_prefix.slice(0, -1),
            args: [num + 2],
            kwargs: {}
        }));
        request.onload = function () {
            newElement.firstElementChild.textContent = request.responseText;
        }

        newElement.firstElementChild.onclick = function () {
            newElement.classList.toggle('open');
        }

        const items = Array.from(newElement.lastElementChild.children).filter(
            child => child.tagName == 'DIV'
        );
        items.forEach(item => {
            let label, input;
            [label, input]  = item.children;
            if (input !== undefined) {
                if (input.tagName == 'DIV') {
                    while (input.firstChild) {
                        input.removeChild(input.firstChild);
                    }
                } else {
                    replaceAttr(label, 'for', id_before, id_after);
                    replaceAttr(input, 'id', id_before, id_after);
                    replaceAttr(input, 'name', id_before, id_after);
                    if (input.tagName == 'INPUT' || input.tagName == 'TEXTAREA') {
                        input.value = '';
                    } else {
                        Array.from(input.children).forEach(select => {
                            select.selected = false;
                        });   
                    }
                }
            }
        });
        parent.insertBefore(newElement, element);
        parent.insertBefore(document.createElement('br'), element);
    }
}

var copied_element;
function copy(element) {
    copied_element = element.parentElement;
}

function paste(element, prefix) {
    // prefix = "['clients']"
    // id_prefix = clients
    const id_prefix = element.parentElement.parentElement.getAttribute('id');
    if (copied_element) {
        const parent = element.parentElement.parentElement;  // clients
        const next_element = element.parentElement.nextElementSibling.nextElementSibling;  // next client
        const element_num = parseInt(element.parentElement.id.slice(id_prefix.length + 1));
        const copied_element_num = parseInt(copied_element.id.slice(id_prefix.length + 1));
        const element_open = element.parentElement.classList.contains('open');
        const copied_element_open = copied_element.classList.contains('open');
        parent.removeChild(element.parentElement.nextElementSibling);
        parent.removeChild(element.parentElement);

        const child = copied_element.cloneNode(true);
        child.id = `${id_prefix}_${element_num}`;
        const id_before = `${prefix}[${copied_element_num}]`
        const id_after = `${prefix}[${element_num}]`
        
        const request = new XMLHttpRequest();
        request.open('POST', '/l');
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify({
            text: id_prefix.slice(0, -1),
            args: [element_num + 1],
            kwargs: {}
        }));
        request.onload = function () {
            child.firstElementChild.textContent = request.responseText;
        }

        child.firstElementChild.onclick = function () {
            child.classList.toggle('open');
        }

        const items = Array.from(child.lastElementChild.children).filter(
            child => child.tagName == 'DIV'
        );
        fixId(items, id_before, id_after);

        if (element_open && !copied_element_open) {
            child.classList.add('open');
        }

        parent.insertBefore(child, next_element);
        parent.insertBefore(document.createElement('br'), next_element);
    }
}

function applyToAll(element, prefix_keys, keys) {
    element = element.previousElementSibling;
    let elements = document.getElementsByClassName('apply_to_all_button');
    if (element.tagName == 'DIV' && element.classList.contains('list_list')) {
        elements = Array.from(elements).filter(e => (
            e.previousElementSibling && e.previousElementSibling.id
            && e.previousElementSibling.id == element.id
            && e.previousElementSibling.tagName == element.tagName
            && e.previousElementSibling != element
        ));
    } else {
        elements = Array.from(elements).filter(e => (
            e.previousElementSibling && e.previousElementSibling.id
            && e.previousElementSibling.id.startsWith(prefix_keys)
            && e.previousElementSibling.id.endsWith(keys)
            && e.previousElementSibling.tagName == element.tagName
            && e.previousElementSibling != element
        ));
    }
    Array.from(elements).forEach(e => {
        const valueElement = e.previousElementSibling;
        if (element.tagName == 'INPUT' || element.tagName == 'TEXTAREA') {
            valueElement.value = element.value;
        } else if (element.tagName == 'DIV' && element.classList.contains('list_list')) {
            const clientNum = parseInt(element.parentElement.parentElement.parentElement.getAttribute('num'));
            const valueClientNum = parseInt(valueElement.parentElement.parentElement.parentElement.getAttribute('num'));
            const id_before = `${prefix_keys}[${clientNum}]`;
            const id_after = `${prefix_keys}[${valueClientNum}]`;
            const newElement = element.cloneNode(true);
            const parent = valueElement.parentElement;
            parent.removeChild(valueElement);
            parent.insertBefore(newElement, e);
            Array.from(newElement.children).forEach(child => {
                if (child.tagName == 'DIV') {
                    replaceAttr(child.firstElementChild, 'id', id_before, id_after);
                    replaceAttr(child.firstElementChild, 'name', id_before, id_after);
                } else {
                    child.onclick = function () {
                        addListList(child, child.getAttribute('key').replace(id_before, id_after));
                    }
                }
            });
        } else {
            for (let i = 0; i < valueElement.children.length; i++) {
                const select = element.children[i];
                const valueSelect = valueElement.children[i];
                valueSelect.selected = select.selected;
            }
        }
    });
}
