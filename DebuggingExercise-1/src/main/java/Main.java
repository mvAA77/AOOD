class Main {
  
  public static void main(String[] args) {

    errorMethodOne();
    errorMethodTwo();

    int[] myArray = {1,2,3,4};
    errorMethodThree(myArray); // Method Does not take two arguments

    MySum sum1 = new MySum(); // Class name and file name
    int sum = sum1.mySum(5,6); // Method name is mySum not sum, also static reference is changed
    System.out.println(sum); // Variable name is sum not answer

    MyMultiplication multiply = new MyMultiplication(); // Missing new keyword
    int multi = multiply.multiple(5,5);
    System.out.println(multi);

    System.out.println(errorMethodFour("Hello")); // Missing losing Brackets

    int number = 0; // Change null to 0

    if (number > 0) {
      System.out.println("Positive number");
    }

  }

  public static void errorMethodOne() {

    System.out.println("       1"); // Typo in print1n
    System.out.println("     2 3");
    System.out.println("   4 5 6"); // Missing Closing Quotes, Typo in System
    System.out.println("7 8 9 10"); // Missing Semi Colon
    
  }

  public static void errorMethodTwo() {

    int width = 0;
    int length = 40;
    
    int ratio = width / length; // Divide by zero error
    
    System.out.println(ratio);

  }

  public static void errorMethodThree(int[] myArray) {

    for(int i=0; i < myArray.length; i++) {

      System.out.println(myArray[i]); // Doing i < 5 does work if myArray is shorter than 5 elements

    }

  }

  public static char errorMethodFour(String word) { // ErrorMethodFour instead of errorMethodFor, also change to static

    return word.charAt(0); // Originaly void method: Void method cannot return anything

  }

  
  
}

