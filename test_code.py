"""
Test code for the AI Code Translator and Scanner
"""

import os
import asyncio
import logging
from integrated_ai import IntegratedTranslatorAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_translator():
    """Test the code translator."""
    print("\nTesting Code Translator...")
    
    # Get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
        
    try:
        # Initialize translator
        translator = IntegratedTranslatorAI(api_key=api_key)
        
        # Test 1: Simple Python to JavaScript
        print("\nTest 1: Simple Python to JavaScript")
        print("--------------------------------------------------")
        
        python_code = """
def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

# Example usage
numbers = [1, 2, 3, 4, 5]
average = calculate_average(numbers)
print(f"The average is: {average}")
"""

        result = await translator.translate_code(python_code, "javascript")
        
        print("\nOriginal Python Code:")
        print("--------------------------------------------------")
        print(python_code)
        print("--------------------------------------------------")
        
        print("\nTranslated JavaScript Code:")
        print("--------------------------------------------------")
        print(result["translated_code"])
        print("--------------------------------------------------")
        
        # Test 2: Complex Python with classes to C++
        print("\nTest 2: Complex Python with classes to C++")
        print("--------------------------------------------------")
        
        python_code = """
class BankAccount:
    """A simple bank account class."""

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self.balance = balance
        self.transactions = []

    def deposit(self, amount: float) -> None:
        """Deposit money into the account."""
        if amount <= 0:
            raise ValueError("Amount must be positive")

        self.balance += amount
        self.transactions.append({"type": "deposit", "amount": amount})
        print(f"Deposited ${amount:.2f}. New balance: ${self.balance:.2f}")

    def withdraw(self, amount: float) -> None:
        """Withdraw money from the account."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")

        self.balance -= amount
        self.transactions.append({"type": "withdraw", "amount": amount})
        print(f"Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}")

    def get_balance(self) -> float:
        """Get the current balance."""
        return self.balance

    def get_transactions(self) -> list:
        """Get a list of all transactions."""
        return self.transactions

# Example usage
account = BankAccount("John Doe", 1000.0)
account.deposit(500.0)
account.withdraw(200.0)
print(f"Final balance: ${account.get_balance():.2f}")
"""

        result = await translator.translate_code(python_code, "cpp")
        
        print("\nOriginal Python Code:")
        print("--------------------------------------------------")
        print(python_code)
        print("--------------------------------------------------")
        
        print("\nTranslated C++ Code:")
        print("--------------------------------------------------")
        print(result["translated_code"])
        print("--------------------------------------------------")
        
        # Test 3: JavaScript to Python
        print("\nTest 3: JavaScript to Python")
        print("--------------------------------------------------")
        
        js_code = """
function calculateFactorial(n) {
    if (n < 0) {
        throw new Error("Factorial is not defined for negative numbers");
    }
    if (n === 0 || n === 1) {
        return 1;
    }
    return n * calculateFactorial(n - 1);
}

// Example usage
const number = 5;
const result = calculateFactorial(number);
console.log(`The factorial of ${number} is ${result}`);
"""

        result = await translator.translate_code(js_code, "python")
        
        print("\nOriginal JavaScript Code:")
        print("--------------------------------------------------")
        print(js_code)
        print("--------------------------------------------------")
        
        print("\nTranslated Python Code:")
        print("--------------------------------------------------")
        print(result["translated_code"])
        print("--------------------------------------------------")
        
        # Test 4: Error Handling - Empty Code
        print("\nTest Error Handling - Empty Code")
        print("--------------------------------------------------")
        
        try:
            result = await translator.translate_code("", "javascript")
            print("\nTranslation Result:")
            print("--------------------------------------------------")
            print(f"Success: {result['success']}")
            print(f"Error: {result['error']}")
            print("--------------------------------------------------")
        except Exception as e:
            print("\nTranslation Result:")
            print("--------------------------------------------------")
            print(f"Success: False")
            print(f"Error: {str(e)}")
            print("--------------------------------------------------")
            
        # Test 5: Error Handling - Invalid Language
        print("\nTest Error Handling - Invalid Language")
        print("--------------------------------------------------")
        
        try:
            result = await translator.translate_code(python_code, "invalid")
            print("\nTranslation Result:")
            print("--------------------------------------------------")
            print(f"Success: {result['success']}")
            print(f"Error: {result['error']}")
            print("--------------------------------------------------")
        except Exception as e:
            print("\nTranslation Result:")
            print("--------------------------------------------------")
            print(f"Success: False")
            print(f"Error: {str(e)}")
            print("--------------------------------------------------")
            
    except Exception as e:
        print(f"Error in test_translator: {str(e)}")
        raise

async def test_vulnerability_scanner():
    """Test the vulnerability scanner."""
    print("\nTesting Vulnerability Scanner...")
    
    # Get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
        
    try:
        # Initialize translator
        translator = IntegratedTranslatorAI(api_key=api_key)
        
        # Test vulnerable code
        code = """
# SQL Injection vulnerability
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

# XSS vulnerability
print(f"Welcome, {username}!")

# Buffer overflow vulnerability (in C-like pseudocode)
buffer = [0] * 10
data = "A" * 20  # Too long for buffer
"""

        print("\nScanning code for vulnerabilities...")
        vulnerabilities = await translator.scan_code(code, "python")
        
        print("\nVulnerabilities Found:")
        print("--------------------------------------------------")
        
        for i, vuln in enumerate(vulnerabilities, 1):
            print(f"\nVulnerability {i}:")
            print(f"Type: {vuln['category']}")
            print(f"Severity: {vuln['severity']}")
            print(f"Description: {vuln['description']}")
            print(f"Line: {vuln['line']}")
            print(f"Code: {vuln['code']}")
            print(f"Fix: {vuln['fix']}")
        
        print("--------------------------------------------------")
        
        # Test error handling - invalid language
        print("\nTest Error Handling - Invalid Language")
        print("--------------------------------------------------")
        
        try:
            vulnerabilities = await translator.scan_code(code, "invalid")
            print("\nScan Result:")
            print("--------------------------------------------------")
            print(f"Vulnerabilities found: {len(vulnerabilities)}")
            print("--------------------------------------------------")
        except Exception as e:
            print("\nScan Result:")
            print("--------------------------------------------------")
            print(f"Error: {str(e)}")
            print("--------------------------------------------------")
            
        # Test error handling - empty code
        print("\nTest Error Handling - Empty Code")
        print("--------------------------------------------------")
        
        try:
            vulnerabilities = await translator.scan_code("", "python")
            print("\nScan Result:")
            print("--------------------------------------------------")
            print(f"Vulnerabilities found: {len(vulnerabilities)}")
            print("--------------------------------------------------")
        except Exception as e:
            print("\nScan Result:")
            print("--------------------------------------------------")
            print(f"Error: {str(e)}")
            print("--------------------------------------------------")
            
    except Exception as e:
        print(f"Error in test_vulnerability_scanner: {str(e)}")
        raise

async def main():
    """Main function to run tests."""
    await test_translator()
    await test_vulnerability_scanner()

if __name__ == "__main__":
    asyncio.run(main())
