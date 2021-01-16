// https://www.7-16.co.jp/laboratory/2047
function pseudo(id, css) {
    id = id + '-pseudoStyle';
    var element = document.getElementById(id);
    if (element == null) {
        styleTag = document.createElement('style');
        styleTag.id = id;
        styleTag.innerHTML = css;
        document.getElementsByTagName('head')[0].appendChild(styleTag);
    } else {
        element.innerHTML = css;
    }
}

function hasCSS(id, css) {
    id = id + '-pseudoStyle';
    var element = document.getElementById(id);
    if (element == null) {
        styleTag = document.createElement('style');
        styleTag.id = id;
        return styleTag.innerHTML == css;
    } else {
        return element.innerHTML == css;
    }
}