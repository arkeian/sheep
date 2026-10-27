import sys
from collections.abc import Sequence
from pathlib import Path
from typing import final

from .Decryption import Decryption
from .DHKeyGeneration import DHKeyGeneration
from .Encryption import Encryption


@final
class Main:
    @staticmethod
    def main(args: Sequence[str]) -> None:
        # Menjalankan seluruh proses: membaca file, membentuk kunci, mengenkripsi, lalu mengembalikan pesan.
        # Lokasi file diberikan ketika program dijalankan, misalnya: java Main pesan.txt.

        # 1. Memastikan pengguna memberikan tepat satu lokasi file.
        if len(args) != 1:
            print("[Main.main.INVALID_ARGUMENT_COUNT] Penggunaan: python3 -m python.src.Main <path-file-teks>")
            return

        try:
            # 2. Membaca seluruh byte file dan memeriksa apakah isinya dapat dibaca sebagai teks UTF-8.
            # Byte asli digunakan untuk enkripsi, sedangkan bentuk teksnya digunakan untuk tampilan.
            inputPath = Path(args[0])
            plaintextBytes = inputPath.read_bytes()
            plaintext = Decryption.decodeUtf8(plaintextBytes)

            # 3. Membentuk kunci, lalu menentukan jumlah byte per chunk berdasarkan modulus p.
            keyPair = DHKeyGeneration.generateKeyPair()
            chunkSize = Encryption.calculatePlaintextChunkSize(keyPair.p)

            # 4. Mengenkripsi byte pesan menggunakan kunci publik (e1, e2, p).
            # Hasilnya berupa pasangan {C1, C2} untuk setiap chunk.
            ciphertext = Encryption.encrypt(plaintextBytes, keyPair.e1, keyPair.e2, keyPair.p)

            # 5. Memulihkan pesan menggunakan kunci privat d.
            # Ukuran chunk dan panjang byte semula diperlukan untuk mengembalikan byte nol
            # di awal chunk serta panjang chunk terakhir.
            decryptedBytes = Decryption.decrypt(ciphertext, keyPair.d, keyPair.p, chunkSize, len(plaintextBytes))
            decryptedText = Decryption.decodeUtf8(decryptedBytes)

            # 6. Membandingkan seluruh byte hasil dekripsi dengan byte file semula.
            # Pemeriksaan ini juga mencakup byte nol yang mungkin tidak terlihat pada tampilan teks.
            if plaintextBytes != decryptedBytes:
                raise RuntimeError("[Main.main.DECRYPTION_MISMATCH] Hasil dekripsi tidak sama dengan isi file semula.")

            # 7. Menampilkan parameter, kunci, pesan semula, ciphertext, dan hasil dekripsi.
            Main.printResult(inputPath, plaintext, keyPair, chunkSize, ciphertext, decryptedText)
        except OSError as exception:
            # Melaporkan kegagalan membaca file.
            print(f"[Main.main.FILE_READ_ERROR] File tidak dapat dibaca: {exception}", file=sys.stderr)
        except (ValueError, RuntimeError, ArithmeticError) as exception:
            # Melaporkan data yang tidak sesuai atau kegagalan selama proses perhitungan.
            print(f"[Main.main.PROCESSING_ERROR] Program dihentikan: {exception}", file=sys.stderr)

    @staticmethod
    def printResult(inputPath: Path, plaintext: str, keyPair: DHKeyGeneration.KeyPair,
                    chunkSize: int, ciphertext: Sequence[Sequence[int]], decryptedText: str) -> None:
        # Menampilkan hasil seluruh tahap demonstrasi.
        # Nilai kunci turut ditampilkan agar parameter yang digunakan dapat diamati.
        print(f"File input       : {inputPath.absolute()}")
        print(f"Ukuran chunk     : {chunkSize} byte")
        print(f"Jumlah chunk     : {len(ciphertext)}")
        print(f"p                : {keyPair.p}")
        print(f"e1               : {keyPair.e1}")
        print(f"e2               : {keyPair.e2}")
        print(f"d (kunci privat) : {keyPair.d}")
        print()
        print("Plaintext:")
        print(plaintext)
        print()
        print("Ciphertext (C1, C2):")

        # Satu baris menampilkan pasangan C1 dan C2 untuk satu chunk, sesuai urutan pesan.
        for i in range(len(ciphertext)):
            print(f"{i + 1}. ({ciphertext[i][0]}, {ciphertext[i][1]})")

        print()
        print("Hasil dekripsi:")
        print(decryptedText)


if __name__ == "__main__":
    Main.main(sys.argv[1:])
