const move = Math.floor(Math.random() * (15 - 3 + 1)) + 3;
const input = prompt("Enter a phrase to encode (lowercase letters only): ");

const alphabet = 'abcdefghijklmnopqrstuvwxyz';
const alphabetArray = alphabet.split('');

const cipher = (shift, phrase) => {
    // Convert phrase to array of characters, map each character to its encoded version
    const encodedChars = phrase.split('').map(char => {
        // Only encode lowercase letters, leave other characters as-is
        if (alphabet.includes(char)) {
            let index = alphabetArray.indexOf(char);
            let newIndex = (index + shift) % 26; // Wrap around using modulo
            return alphabetArray[newIndex];
        } else {
            return char; // Keep non-alphabet characters unchanged
        }
    });
    
    // Join the array back into a string
    return encodedChars.join('');
};

let shifted = cipher(move, input);

document.body.innerHTML += `<p>Your shift value is: ${move}</p>`;
document.body.innerHTML += `<p>Your input is: ${input}</p>`;
document.body.innerHTML += `<p>Your encoded message is: ${shifted}</p>`;

console.log("Your shift value is: " + move);
console.log("Your input is: " + input);
console.log("Your encoded message is: " + shifted);