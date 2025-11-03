class bacteriaPop {
    constructor(population) {
      this.population = population;
      this.seconds = 0;
      this.doublingInterval = undefined;
    }
  
    doublePop() {
      this.population *= 2;
      this.seconds += 3;
      document.getElementById("display").innerHTML += `</br>There are ${this.population} cells after ${this.seconds} seconds</br>`;
    }
  
    controlDoubling(shouldClear = false) {
      if (shouldClear) {
        console.log(`this.doublingInterval: ${this.doublingInterval}`);
        clearInterval(this.doublingInterval);
        return;
      }
  
      if (this.doublingInterval) {
        return;
      }
  
      this.doublingInterval = setInterval(this.doublePop.bind(this), 3000);
    }
  
    spray() {
      this.population = Math.floor(this.population * 0.8);
      document.getElementById("display").innerHTML += `</br>Spray has been applied after ${this.seconds} seconds. Population is now ${this.population}</br>`;
    }
  }
  
  
  let bacteria1 = new bacteriaPop(15);
  bacteria1.controlDoubling();
  setInterval(bacteria1.spray.bind(bacteria1), 5000);
  setTimeout(bacteria1.controlDoubling.bind(bacteria1, true), 15000);
  
  
  
  //unrelated code that demonstrates a way to execute functions on a delay
  async function sleep(ms) {
    return new Promise(function(resolve, reject) {
      setTimeout(resolve, ms)
    });
  }
  
  async function exampleAsync() {
    for (let i = 0; i < 10; i++) {
      console.log('abc');
      let abc = await sleep(2000);
    }  
  }
  
  exampleAsync();