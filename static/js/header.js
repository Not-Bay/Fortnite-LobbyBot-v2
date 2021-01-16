const HREFS = [
    '/',
    '/config-editor',
    '/commands-editor',
    '/custom-commands-editor',
    '/replies-editor',
    '/boot-switch',
    '/clients-viewer'
];
const headerList = document.getElementById('header-list');
headerList.classList.add('pc-header-list');

HREFS.forEach(href => {
    const li = document.createElement('li');
    li.className = 'header-item';
    console.log(location.pathname);
    if (href == location.pathname) {
        const p = document.createElement('p');
        p.textContent = texts[href]
        li.appendChild(p);
    } else {
        const a = document.createElement('a');
        a.href = href;
        a.textContent = texts[href];
        li.appendChild(a);
    }
    headerList.appendChild(li);
});

document.getElementById('header-button').addEventListener('click', function() {
    document.getElementById('header-button').classList.toggle('header-button-open');
    document.getElementById('header-list').classList.toggle('header-list-open');
})

const logo = document.getElementById('pc-logo');
const header = document.getElementById('header-list');
const headerButton = document.getElementById('header-button');

function fitSize(){
    header.classList.add('pc-header-list');
    header.classList.remove('phone-header-list');
    if ((logo.clientWidth + header.clientWidth) > (window.innerWidth - 20)) {
        header.classList.add('phone-header-list');
        header.classList.remove('pc-header-list');
        headerButton.classList.add('header-button');
    } else {
        header.classList.add('pc-header-list');
        header.classList.remove('phone-header-list');
        headerButton.classList.remove('header-button');
    }
}

fitSize();

document.body.onresize = function () {
    fitSize();
}