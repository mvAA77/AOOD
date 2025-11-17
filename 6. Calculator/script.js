const result = document.getElementById("result");

function insert(value) {
    result.value += value;
}

function clr() {
    result.value = "";
}

function factorial(n) {
    if (n < 0) return NaN;
    if (n === 0) return 1;
    let total = 1;
    for (let i = 1; i <= n; i++) total *= i;
    return total;
}


function solve() {
    try {
        let expression = result.value;

        expression = expression.replace(/π/g, Math.PI);
        expression = expression.replace(/e/g, Math.E);

        if (expression.includes("!")) {
            let num = parseInt(expression.replace("!", ""));
            result.value = factorial(num);
            return;
        }

        expression = expression.replace(/√/g, "Math.sqrt");

        if (expression.includes("^")) {
            let parts = expression.split("^");
            expression = `Math.pow(${parts[0]}, ${parts[1]})`;
        }

        expression = expression.replace(/÷/g, "/");
        expression = expression.replace(/x/g, "*");

        expression = expression.replace(/%/g, "/100");

        result.value = eval(expression);
    }
    catch {
        result.value = "Error";
    }
}


function squareRoot() {
    result.value = "√(" + result.value + ")";
}


const button = document.getElementById('switchFile');

button.addEventListener('click', function() {
globalThis.location.href = 'file.html';
});

function loadFileFromPath(filePath) {
    fetch(filePath)
        .then(resp => resp.text())
        .then(text => {
            result.value = text;
        })
        .catch(() => {
            result.value = "Invalid path or file cannot be loaded.";
        });
}
