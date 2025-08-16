#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A simple calculator program for testing code translation
This module provides basic mathematical operations
"""

import math

class Calculator:
    """A basic calculator class with common operations"""
    
    def __init__(self):
        # Initialize the calculator with default settings
        self.history = []
        self.last_result = 0
        print("Calculator initialized successfully")
    
    def add(self, a, b):
        """Add two numbers and return the result"""
        # Perform addition operation
        result = a + b
        self.history.append(f"Addition: {a} + {b} = {result}")
        print("Addition completed")  # Log the operation
        return result
    
    def multiply(self, x, y):
        """Multiply two numbers together"""
        # Calculate the product
        product = x * y
        self.history.append(f"Multiplication: {x} * {y} = {product}")
        return product
    
    def get_square_root(self, number):
        """Calculate the square root of a number"""
        if number < 0:
            error_message = "Cannot calculate square root of negative number"
            print(error_message)
            return None
        
        # Use math library for precise calculation
        result = math.sqrt(number)
        success_message = "Square root calculation successful"
        print(success_message)
        return result
    
    def show_history(self):
        """Display the calculation history"""
        if not self.history:
            print("No calculations performed yet")
            return
        
        # Print all previous calculations
        print("Calculation History:")
        for i, operation in enumerate(self.history, 1):
            print(f"{i}. {operation}")

def main():
    """Main function to demonstrate calculator usage"""
    # Create calculator instance
    calc = Calculator()
    
    # Perform some test calculations
    result1 = calc.add(10, 5)
    print(f"First result: {result1}")
    
    result2 = calc.multiply(4, 7)
    print(f"Second result: {result2}")
    
    # Test square root function
    sqrt_result = calc.get_square_root(16)
    if sqrt_result:
        print(f"Square root result: {sqrt_result}")
    
    # Show calculation history
    calc.show_history()
    
    completion_message = "Program execution completed successfully"
    print(completion_message)

if __name__ == "__main__":
    # Entry point for the program
    print("Starting calculator program...")
    main()
    print("Thank you for using the calculator!")
