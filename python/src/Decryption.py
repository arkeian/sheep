from collections.abc import Sequence
from typing import final

from .ModularArithmetic import ModularArithmetic


@final
class Decryption:
    @staticmethod
    def decodeUtf8(bytes: bytes) -> str:
        # Membaca deretan byte sebagai teks UTF-8.
        # REPORT membuat urutan byte yang tidak dapat dibaca dilaporkan sebagai kesalahan.
        # ByteBuffer.wrap menyediakan byte pesan dalam bentuk yang diterima oleh decoder.
        try:
            return bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exception:
            raise ValueError("[Decryption.decodeUtf8.INVALID_UTF8] File input harus berisi teks UTF-8 yang valid.") from exception

    @staticmethod
    def _toByteArray(value: int) -> bytes:
        if value == 0:
            return bytes([0])

        storedBytes = value.to_bytes((value.bit_length() + 7) // 8, byteorder="big", signed=False)
        return bytes([0]) + storedBytes if storedBytes[0] & 0x80 else storedBytes

    @staticmethod
    def createPlaintextBytes(plaintextChunks: Sequence[int | None] | None,
                             chunkSize: int, plaintextByteLength: int) -> bytes:
        # Menyusun bilangan hasil dekripsi menjadi deretan byte pesan semula.
        # BigInteger menyimpan nilai bilangan, sehingga byte nol di awal chunk tidak ikut dipertahankan.
        # Contoh, byte [0, 0, 5] dan [5] sama-sama menghasilkan bilangan 5.
        # Dari bilangan 5 saja, kita tidak dapat mengetahui apakah chunk awalnya berisi 1 byte atau 3 byte.

        # Karena itu, chunkSize dan plaintextByteLength menggunakan ukuran yang diketahui sebelum enkripsi.
        # chunkSize menentukan jumlah byte per chunk, sedangkan plaintextByteLength adalah jumlah byte seluruh pesan.
        # Kedua ukuran ini menentukan panjang setiap chunk, termasuk chunk terakhir yang mungkin lebih pendek.

        # 1. Memastikan deretan bilangan hasil dekripsi tidak null.
        if plaintextChunks is None:
            raise ValueError("[Decryption.createPlaintextBytes.NULL_CHUNKS] Plaintext chunks tidak boleh null.")

        # 2. Memastikan ukuran chunk positif dan panjang pesan tidak negatif.
        if chunkSize < 1 or plaintextByteLength < 0:
            raise ValueError("[Decryption.createPlaintextBytes.INVALID_LENGTH] Ukuran chunk harus positif dan panjang plaintext tidak boleh negatif.")

        # 3. Menghitung jumlah chunk berdasarkan panjang pesan semula.
        # Bagian terakhir tetap dihitung sebagai satu chunk meskipun jumlah bytenya kurang dari chunkSize.
        expectedChunkCount = 0 if plaintextByteLength == 0 else (plaintextByteLength - 1) // chunkSize + 1

        if len(plaintextChunks) != expectedChunkCount:
            raise ValueError("[Decryption.createPlaintextBytes.INVALID_CHUNK_COUNT] Jumlah chunk tidak sesuai dengan panjang plaintext.")

        # 4. Menyiapkan tempat untuk seluruh byte pesan. Array byte baru secara otomatis berisi nilai 0.
        plaintextBytes = bytearray(plaintextByteLength)

        # 5. Mengembalikan setiap bilangan chunk menjadi byte, lalu menempatkannya sesuai urutan pesan.
        for i in range(len(plaintextChunks)):
            plaintextChunk = plaintextChunks[i]

            # Bilangan pesan harus tersedia dan tidak bernilai negatif.
            if plaintextChunk is None or plaintextChunk < 0:
                raise ValueError("[Decryption.createPlaintextBytes.INVALID_CHUNK] Plaintext chunk harus berupa bilangan non-negatif.")

            # destinationStart adalah posisi awal chunk dalam deretan byte pesan.
            # expectedLength menentukan jumlah byte yang harus dimiliki chunk ini.
            # Untuk chunk terakhir, jumlahnya mengikuti sisa panjang pesan.
            destinationStart = i * chunkSize
            expectedLength = min(chunkSize, plaintextByteLength - destinationStart)
            storedBytes = Decryption._toByteArray(plaintextChunk)

            # toByteArray menyertakan tanda bilangan dalam bentuk byte.
            # Untuk bilangan positif, byte nol ditambahkan di depan jika byte pertama nilainya diawali bit 1.
            # sourceStart melewati byte penanda tersebut, lalu sourceLength menghitung byte yang akan disalin.
            sourceStart = 1 if len(storedBytes) > 1 and storedBytes[0] == 0 else 0
            sourceLength = len(storedBytes) - sourceStart

            # Jika byte bilangan melebihi panjang chunk semula, nilainya tidak dapat dimuat pada chunk tersebut.
            if sourceLength > expectedLength:
                raise ValueError("[Decryption.createPlaintextBytes.OVERSIZED_CHUNK] Nilai plaintext chunk melebihi ukuran yang seharusnya.")

            # Selisih panjang menunjukkan jumlah byte nol yang perlu ada di awal chunk.
            # Pada contoh [0, 0, 5], panjang yang diharapkan 3 byte, sedangkan bilangan 5 hanya memakai 1 byte.
            # Maka, 2 byte awal dibiarkan bernilai 0 dan byte 5 disalin setelahnya.
            paddingLength = expectedLength - sourceLength
            destination = destinationStart + paddingLength
            plaintextBytes[destination:destination + sourceLength] = storedBytes[sourceStart:]

        return bytes(plaintextBytes)

    @staticmethod
    def decrypt(ciphertext: Sequence[Sequence[int | None] | None] | None,
                d: int | None, p: int | None, chunkSize: int, plaintextByteLength: int) -> bytes:
        # Memulihkan pesan menggunakan kunci privat d dan modulus prima p.
        # Setiap ciphertext chunk berisi pasangan {C1, C2}, yang dibentuk saat enkripsi:
        # C1 = e1^r mod p.
        # C2 = (e2^r x P) mod p.
        # Di sini, e1 dan e2 adalah bagian kunci publik, r adalah bilangan acak pengirim,
        # dan P adalah bilangan pesan untuk satu chunk.

        # Karena e2 = e1^d mod p, penerima dapat menghitung pengali pada enkripsi melalui C1:
        # C1^d mod p = e1^(rd) mod p = e2^r mod p.
        # Hasil ini disimpan dalam sharedSecret.

        # Selanjutnya, cari invers dari sharedSecret dan simpan sebagai sharedSecretInverse, sehingga:
        # (sharedSecret x sharedSecretInverse) mod p = 1.
        # Dengan mengalikan C2 dengan invers tersebut:
        # (C2 x sharedSecretInverse) mod p
        # -> = (P x sharedSecret x sharedSecretInverse) mod p
        # -> = (P x 1) mod p
        # -> = P.

        # Setelah seluruh bilangan P diperoleh, byte pesan disusun kembali menggunakan chunkSize
        # dan plaintextByteLength yang diketahui dari ukuran pesan sebelum enkripsi.

        # 1. Memastikan ciphertext, kunci privat, dan modulus tidak null.
        if ciphertext is None or d is None or p is None:
            raise ValueError("[Decryption.decrypt.NULL_VALUE] Ciphertext, d, dan p tidak boleh null.")

        # 2. Memastikan ukuran chunk positif dan panjang pesan tidak negatif.
        if chunkSize < 1 or plaintextByteLength < 0:
            raise ValueError("[Decryption.decrypt.INVALID_LENGTH] Ukuran chunk harus positif dan panjang plaintext tidak boleh negatif.")

        # 3. Memastikan p bernilai minimal 5.
        if p < 5:
            raise ValueError("[Decryption.decrypt.INVALID_P] p harus bernilai minimal 5.")

        # 4. Memastikan kunci privat berada dalam interval 0 < d < p - 1.
        if d <= 0 or d >= p - 1:
            raise ValueError("[Decryption.decrypt.INVALID_PRIVATE_KEY] d harus berada pada interval 0 < d < p - 1.")

        # 5. Memastikan jumlah pasangan ciphertext sesuai dengan jumlah chunk pesan semula.
        expectedChunkCount = 0 if plaintextByteLength == 0 else (plaintextByteLength - 1) // chunkSize + 1

        if len(ciphertext) != expectedChunkCount:
            raise ValueError("[Decryption.decrypt.INVALID_LENGTH] Jumlah chunk ciphertext tidak sesuai dengan panjang plaintext.")

        # 6. Menyiapkan satu tempat untuk bilangan pesan hasil dekripsi dari setiap pasangan ciphertext.
        plaintextChunks = [0] * len(ciphertext)

        for i in range(len(ciphertext)):
            # Memastikan setiap baris berisi dua angka, yaitu C1 dan C2.
            ciphertextChunk = ciphertext[i]
            if ciphertextChunk is None or len(ciphertextChunk) != 2:
                raise ValueError("[Decryption.decrypt.INVALID_PAIR] Setiap ciphertext chunk harus berisi pasangan C1 dan C2.")

            c1 = ciphertextChunk[0]
            c2 = ciphertextChunk[1]

            # Memastikan C1 dan C2 tersedia serta berada dalam interval yang diperbolehkan.
            if c1 is None or c2 is None or c1 <= 0 or c1 >= p or c2 < 0 or c2 >= p:
                raise ValueError("[Decryption.decrypt.INVALID_CIPHERTEXT] C1 harus berada pada 0 < C1 < p dan C2 pada 0 <= C2 < p.")

            # Menghitung kembali pengali enkripsi e2^r mod p melalui C1^d mod p.
            sharedSecret = ModularArithmetic.modularExponentiation(c1, d, p)

            # Mencari pasangan pengali yang membuat hasil perkalian dengan sharedSecret bersisa 1.
            sharedSecretInverse = ModularArithmetic.modularInverse(sharedSecret, p)

            # Mengalikan C2 dengan invers tersebut untuk memperoleh bilangan pesan P.
            plaintextChunks[i] = c2 * sharedSecretInverse % p

        # 7. Menggabungkan seluruh chunk menjadi byte pesan dengan panjang masing-masing seperti semula.
        return Decryption.createPlaintextBytes(plaintextChunks, chunkSize, plaintextByteLength)
