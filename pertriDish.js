const bacteria = {
  initial: 10,
  current: initial,
  doublepop : function(s) {
    this.current = this.initial *((2)^s)
    return "Bacteria Count: " + this.current
  },
  spray : function(s) {
    this.current = this.current * 0.1
  }
};
