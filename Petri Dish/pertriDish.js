class PetriDish {
  constructor(initial) {
    this.population = initial;
  }


  doublepop(sec) {
    setInterval(() => {
      this.population *= 2
      return "Bacteria Count: " + this.population;
      }, 3000);

  }

  spray() {
    this.population =Math.floor(this.population * 0.8);
    return "Bacteria Count after spray: " + this.population;
  }
}

const dish = new PetriDish(10);
console.log(dish.doublepop());
console.log(dish.doublepop());
console.log(dish.doublepop());
console.log(dish.spray());
console.log(dish.doublepop());
console.log(dish.spray());
console.log(dish.doublepop());
console.log(dish.doublepop());
console.log(dish.spray());
console.log(dish.doublepop());
console.log(dish.spray());