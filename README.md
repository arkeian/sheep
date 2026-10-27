# Sheep: Simple Diffie-Hellman and ElGamal Encryption and Decryption Program 🐑


**Sheep** is a simple program  implementation of ElGamal encryption and decryption with Diffie-Hellman key generation. It demonstrates the underlying operations manually without built-in frameworks, including modular arithmetic, primality testing, and plaintext chunking in both Java and Python.

## Quick Start

Run all commands from the repository root. Both versions accept the path to one UTF-8 text file and print the generated keys, ciphertext, and recovered plaintext.

### Java

Java 17 or newer is required.

1. Compile the Java source files:

   ```bash
   mkdir -p java/out
   javac -d java/out java/src/*.java
   ```

2. Run the program with a text file:

   ```bash
   java -cp java/out Main message.txt
   ```

### Python

Python 3.10 or newer is required. The Python version uses only the standard library, so no packages need to be installed.

Run the program as a module with a text file:

```bash
python3 -m python.src.Main message.txt
```
