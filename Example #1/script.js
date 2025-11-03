var population = {
    roaches: 10,
    double: function() {
      //setInterval (function() {
        this.roaches = this.roaches * 2;
      //}, 3000);
      return this.roaches;
    },
    spray: function() {
      return this.roaches * .3;
    },
    getRoaches: function() {
      return this.roaches;
    }
  }
  
  /*
  //Originally my student had the code in a FOR loop
  //I showed them how they can take the same code
  //and put it in a setInterval() function (see below)
  for(var i = 0; i < 3; i++) {
    console.log("Before:" + population.getRoaches());
    population.roaches = population.double();
    console.log("After Double:" + population.getRoaches());  
    population.roaches = population.spray();
    console.log("After Spray:" + population.getRoaches());  
  }
  */
  setInterval (function() {
    console.log("Before:" + population.getRoaches());
    population.roaches = population.double();
    console.log("After Double:" + population.getRoaches());  
    population.roaches = population.spray();
    console.log("After Spray:" + population.getRoaches());
  }, 3000);
  
  
  