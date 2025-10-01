const bestThing = "The most surprising thing of JavaScript is that variables are not constrained to one data type"
let reverse = "";

function reverseString(words) {
    for (let i = words.length - 1; i >= 0; i--) {
        reverse += words.charAt(i);
    }

    return reverse;
}

console.log(reverseString(bestThing));