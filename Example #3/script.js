class BacteriaPopulation {
    constructor(initialPopulation) {
      this.population = initialPopulation;
  }
  
    doublePop() {
      setInterval(() => {
        this.population *= 2;
        document.getElementById("result").innerHTML += `Bacteria population has doubled to  ${this.population} cells.<br>`;
    
        if (this.population > 3e3) {
          this.population = 100;
          document.getElementById("result").innerHTML += `A famine occured, ${this.population} cells remain.<br>`;
        }
      }, 3000);
    }
  
    spray() {
      setInterval(() => {
        this.population = Math.floor(this.population * 0.8);
        document.getElementById("result").innerHTML += `Antibacterial spray has been applied. Current population is ${this.population} cells.<br>`;
      }, 5000);
    }
  }
  
  let petriDish = new BacteriaPopulation(10);
  petriDish.doublePop();
  petriDish.spray(); 
  