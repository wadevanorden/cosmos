function open_popup(platform) {
    var modal = document.getElementById("connect_platform_modal_"+platform);
    modal.style.display = "flex"
    modal.classList.add("showModal");
}

function close_hide(platform) {
    var modal = document.getElementById("connect_platform_modal_"+platform);
    modal.style.display = "none"
    modal.classList.remove("showModal");
}

async function filter_dropdown_open() {
    var filter_dropdown = document.getElementById("filters_dropdown");
    var button_close = document.getElementById("filters_dropdown_close");
    var button_open = document.getElementById("filters_dropdown_open");
    filter_dropdown.classList.add("showFilter");
    filter_dropdown.style.paddingBottom = '7%';
    button_open.style.display = 'none';
    button_close.style.display = 'block';
    filter_dropdown.style.borderTop = '3px solid black';
    await sleep(500)
    filter_dropdown.style.zIndex = '0';
}

function filter_dropdown_close() {
    var filter_dropdown = document.getElementById("filters_dropdown");
    var button_open = document.getElementById("filters_dropdown_open");
    var button_close = document.getElementById("filters_dropdown_close");
    filter_dropdown.classList.remove("showFilter");
    filter_dropdown.style.paddingBottom = '0%';
    filter_dropdown.style.zIndex = '-1';
    button_open.style.display = 'block';
    button_close.style.display = 'none';
    filter_dropdown.style.borderTop = '0px solid black';
}

window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
}

function update_connected_platforms(vars) {
    for (let i = 0; i < vars.length; i++) {
        var id = document.getElementById(vars[i]);
        id.style.color = "#3be03b"
    }
}

async function watch_for_signin() {
    var newScript = document.createElement("script");
    newScript.src = "http://www.example.com/my-script.js";
    target.appendChild(newScript);
}

async function getTaskStatus(tasks) {
    var tasks = JSON.parse(tasks);
    var done = true;
    while(tasks.length > 0) {
        if(done == true) {
            done = false;
            var xmlHttp = new XMLHttpRequest();
            var url = 'http://127.0.0.1:5000/taskstatus/'.concat(tasks[0])
            xmlHttp.open("GET", url, true);
            xmlHttp.send(null);
            xmlHttp.onreadystatechange = function () {
                if (xmlHttp.readyState == XMLHttpRequest.DONE) {
                    done = true;
                    tasks = JSON.parse(xmlHttp.response)
                    if(tasks.length == 0) {
                        location.reload();
                    }
                }
            };
        }
        else{
            await sleep(2000);
        }
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function filter_checkbox(filters) {
    var checked = [];
    var unchecked = [];
    var checkbox_filters = document.querySelectorAll("input.checkbox");
    for (let i = 0; i < checkbox_filters.length; i++) {
        if (checkbox_filters[i].checked == true) {
            checked.push(checkbox_filters[i].id)
        }
        else {
            unchecked.push(checkbox_filters[i].id)
        }
    }
    for (let i = 0; i < unchecked.length; i++) {
        if (unchecked[i] == 'no_achievements_filter') {
            var cards = document.getElementsByClassName("no_achievements");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'block'
            }
        }
        else if (unchecked[i] == 'perfect_game_filter') {
            var cards = document.getElementsByClassName("perfect");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'block'
            }
        }
        else if (unchecked[i] == 'regular_game_filter') {
            var cards = document.getElementsByClassName("regular");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'block'
            }
        }
        else if (unchecked[i] == 'steam_filter') {
            var cards = document.getElementsByClassName("steam");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'block'
            }
        }
        else if (unchecked[i] == 'xbox_filter') {
            var cards = document.getElementsByClassName("xbox");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'block'
            }
        }
        else if (unchecked[i] == 'playstation_filter') {
            cards = document.getElementsByClassName("playstation");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'block'
            }
        }
    }
    for (let i = 0; i < checked.length; i++) {
        if (checked[i] == 'no_achievements_filter') {
            var cards = document.getElementsByClassName("no_achievements");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'none'
            }
        }
        else if (checked[i] == 'perfect_game_filter') {
            var cards = document.getElementsByClassName("perfect");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'none'
            }
        }
        else if (checked[i] == 'regular_game_filter') {
            var cards = document.getElementsByClassName("regular");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'none'
            }
        }
        else if (checked[i] == 'steam_filter') {
            var cards = document.getElementsByClassName("steam");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'none'
            }
        }
        else if (checked[i] == 'xbox_filter') {
            var cards = document.getElementsByClassName("xbox");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'none'
            }
        }
        else if (checked[i] == 'playstation_filter') {
            cards = document.getElementsByClassName("playstation");
            for (let j = 0; j < cards.length; j++) {
                cards[j].parentElement.parentElement.parentElement.parentElement.style.display = 'none'
            }
        }
    }
}