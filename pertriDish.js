class PetriDish {
  
  
  constructor(initial) {
    this.initial = initial;
    this.current = 1;
  }


  doublepop(sec) {
    let s = sec/3
    this.current = this.initial *((2)^s)
    return "Bacteria Count: " + this.current
  }

  spray() {
    this.current =Math.floor(this.current * 0.1);
    return "Bacteria Count after spray: " + this.current;
  }
}

const dish = new PetriDish(10);
console.log(dish.doublepop(9));
console.log(dish.spray());



