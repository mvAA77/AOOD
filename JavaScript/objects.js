const diwk = {
    name: "Do I Wanna Know",
    artist: "Arctic Monkeys",
    genre: "Punk Rock"
}

function songName(song) {
    return song.name;
}

function songArtist(song) {
    return song.artist;
}

function songGenre(song) {
    return song.genre;
}

const myLove = {
    name: "My Love Is Mine",
    artist: "Mitski",
    genre: "Pop"
}

const jkw = {
    name: "Just Keep Watching",
    artist: "Tate McRay",
    genre: "Pop"
}

console.log("The Name of this song is: " + songName(diwk));
console.log("The Artist of this song is: " + songArtist(diwk));
console.log("The genre of this song is: " + songGenre(diwk));
console.log("  ");

console.log("The Name of this song is: " + songName(myLove));
console.log("The Artist of this song is: " + songArtist(myLove));
console.log("The genre of this song is: " + songGenre(myLove));
console.log("  ");

console.log("The Name of this song is: " + songName(jkw));
console.log("The Artist of this song is: " + songArtist(jkw));
console.log("The genre of this song is: " + songGenre(jkw));
console.log("  ");