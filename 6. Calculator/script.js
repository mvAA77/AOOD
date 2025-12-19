/*****************************************
 * DETECT WHICH PAGE WE ARE ON
 *****************************************/
const isCalculator = document.getElementById("result") !== null;
const isFilePage = document.getElementById("fileInput") !== null;


/*****************************************
 *  CALCULATOR PAGE (index.html)
 *****************************************/
if (isCalculator) {

    const result = document.getElementById("result");

    window.insert = function(value) {
        result.value += value;
    };

    window.clr = function() {
        result.value = "";
    };

    function factorial(n) {
        if (n < 0) return NaN;
        if (n === 0) return 1;
        let t = 1;
        for (let i = 1; i <= n; i++) t *= i;
        return t;
    }

    window.solve = function() {
        try {
            let expr = result.value;

            expr = expr.replace(/π/g, Math.PI);
            expr = expr.replace(/e/g, Math.E);

            if (expr.includes("!")) {
                let num = parseInt(expr);
                result.value = factorial(num);
                return;
            }

            expr = expr.replace(/√(\d+(\.\d+)?|\([^)]+\))/g, "Math.sqrt($1)");


            if (expr.includes("^")) {
                let p = expr.split("^");
                expr = `Math.pow(${p[0]}, ${p[1]})`;
            }

            expr = expr.replace(/x/g, "*");
            expr = expr.replace(/÷/g, "/");
            expr = expr.replace(/%/g, "%");

            result.value = eval(expr);
        }
        catch {
            result.value = "Error";
        }
    };

    // Switch to file.html
    const btn = document.getElementById("switchFile");
    if (btn) {
        btn.addEventListener("click", () => {
            location.href = "file.html";
        });
    }
}


/*****************************************
 *  FILE PAGE (file.html)
 *****************************************/
if (isFilePage) {

    const textarea = document.getElementById("fileInput");
    const message = document.getElementById("Message");

    /*************** FILE LOADING ***************/
    window.loadFile = function() {
        const path = document.getElementById("filePath").value.trim();
        if (!path) {
            message.innerHTML = "Please enter a file path.";
            return;
        }

        fetch(path)
            .then(r => {
                if (!r.ok) throw new Error("File not found");
                return r.text();
            })
            .then(text => {
                textarea.value = text;
                message.innerHTML = "Loaded file successfully.";
            })
            .catch(err => {
                message.innerHTML = "Error: " + err.message;
            });
    };

    window.loadLocalFile = function() {
        const file = document.getElementById("fileUpload").files[0];
        if (!file) {
            message.innerHTML = "No file selected.";
            return;
        }

        const reader = new FileReader();
        reader.onload = e => {
            textarea.value = e.target.result;
            message.innerHTML = "Loaded file successfully.";
        };
        reader.readAsText(file);
    };


    /*************** STATS LOGIC ***************/
    function nums() {
        return textarea.value
            .split(/[\s,]+/)
            .map(Number)
            .filter(n => !isNaN(n));
    }

    // Create or get a dedicated output container
    function getOutputContainer() {
        let container = document.getElementById("statsOutput");
        if (!container) {
            container = document.createElement("div");
            container.id = "statsOutput";
            container.style.marginTop = "20px";
            document.body.appendChild(container);
        }
        return container;
    }

    function printResult(label, value) {
        const container = getOutputContainer();
        container.innerHTML = `<p style="font-weight:bold">${label}: ${value}</p>`;
    }

    window.showMean = function() {
        let n = nums();
        if (!n.length) return printResult("Mean", "No numbers");
        printResult("Mean", n.reduce((a,b)=>a+b,0) / n.length);
    };

    window.showMedian = function() {
        let n = nums();
        if (!n.length) return printResult("Median", "No numbers");
        n.sort((a,b)=>a-b);
        let m = Math.floor(n.length/2);
        let med = n.length % 2 ? n[m] : (n[m-1] + n[m]) / 2;
        printResult("Median", med);
    };

    window.showMode = function() {
        let n = nums();
        if (!n.length) return printResult("Mode", "No numbers");
        let freq = {};
        n.forEach(x => freq[x] = (freq[x]||0)+1);
        let max = Math.max(...Object.values(freq));
        let modes = Object.keys(freq).filter(k => freq[k] == max);
        printResult("Mode", modes.join(", "));
    };

    window.showMax = function() {
        let n = nums();
        if (!n.length) return printResult("Max", "No numbers");
        printResult("Max", Math.max(...n));
    };

    window.showMin = function() {
        let n = nums();
        if (!n.length) return printResult("Min", "No numbers");
        printResult("Min", Math.min(...n));
    };

}
