

const initial = (year) => {
    if (((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0)) {
        console.log(year + ": This is a Leap Year");
        return "This is a Leap Year";
    } else {
         return "Not Leap Year";
    }
};

for (let i = 1900; i < 2026; i++) {
    initial(i);
}