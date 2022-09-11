function keyCheck(element, e) {
    if (e.key == 'Enter') {
        send(element);
    }
}

function send(element) {
    const formData = new FormData(element.parentElement);
    const request = new XMLHttpRequest();
    request.open('POST', '/login');
    request.send(formData);
    request.onload = function (ev) {
        const data = JSON.parse(request.responseText);
        if (data.success) {
            element.parentElement.style = '';
            window.location.reload();
        } else {
            element.parentElement.classList.add('error');
        }
    }
}

function pass_view() {
    const pass_view = document.getElementById("password_view");
    const pass_input = document.getElementById("password_input");

    if ( pass_input.type === 'password' ) {
        pass_input.type = 'text';
        pass_view.value = texts.hide;
    } else {
        pass_input.type = 'password';
        pass_view.value = texts.show;
    }
}