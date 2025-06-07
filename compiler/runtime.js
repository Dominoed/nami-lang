// --- Nami Reactive/Game Runtime ---
const state = {};
const subscribers = {};

function setVar(name, value) {
    state[name] = value;
    if (subscribers[name]) {
        for (const fn of subscribers[name]) fn(value);
    }
}
function getVar(name) { return state[name]; }
function subscribeVar(name, fn) {
    if (!subscribers[name]) subscribers[name] = [];
    subscribers[name].push(fn);
}

function bindVars() {
    for (const name in state) {
        const el = document.getElementById('nami_var_' + name);
        if (el) {
            subscribeVar(name, val => { el.innerText = val; });
            el.innerText = state[name];
        }
        const input = document.getElementById('nami_input_' + name);
        if (input) {
            input.value = state[name] || "";
            input.addEventListener('input', e => setVar(name, e.target.value));
            subscribeVar(name, val => { input.value = val; });
        }
        const checkbox = document.getElementById('nami_input_' + name + '_checkbox');
        if (checkbox) {
            checkbox.checked = !!state[name];
            checkbox.addEventListener('change', e => setVar(name, checkbox.checked));
            subscribeVar(name, val => { checkbox.checked = !!val; });
        }
    }
}

document.addEventListener("DOMContentLoaded", bindVars);

// --- Game/Main Loop ---
let running = true;
function gameLoop() {
    if (running) {
        if (typeof namiTick === 'function') namiTick();
        requestAnimationFrame(gameLoop);
    }
}
gameLoop();

// --- Page navigation helper ---
function switchPage(pageId) {
    document.querySelectorAll('.nami-page').forEach(div => div.style.display = 'none');
    var el = document.getElementById(pageId);
    if (el) el.style.display = '';
}
document.addEventListener("DOMContentLoaded", function() {
    switchPage('page_HOME');
});