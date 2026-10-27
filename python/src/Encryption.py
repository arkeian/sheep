from secrets import SystemRandom
from typing import ClassVar, final

from .ModularArithmetic import ModularArithmetic
from .RandomNumberGenerator import RandomNumberGenerator


@final
class Encryption:
    # Satu byte memiliki 2^8 = 256 kemungkinan nilai.
    BYTE_BASE: ClassVar[int] = 256

    # Membangkitkan bilangan acak yang sulit ditebak menggunakan SecureRandom.
    random: ClassVar[SystemRandom] = SystemRandom()

    @staticmethod
    def calculatePlaintextChunkSize(p: int | None) -> int:
        # ElGamal mengenkripsi bilangan bulat P dalam interval 0 <= P < p.
        # Jika seluruh byte pesan dibaca sebagai satu bilangan, nilainya dapat mencapai atau melebihi p.
        # Karena itu, byte pesan dibagi menjadi beberapa potongan, yang disebut chunk.
        # Metode ini menentukan jumlah byte terbanyak per chunk agar setiap nilainya tetap kurang dari p.

        # Satu byte dapat menyatakan nilai 0 sampai 255. Jika k byte digabungkan,
        # nilai terbesarnya adalah 256^k - 1.
        # Agar nilai tersebut kurang dari p, ukuran chunk harus memenuhi 256^k <= p.

        # Contoh, p = 65537:
        # -> 2 byte dapat menyatakan nilai sampai 256^2 - 1 = 65535, yang masih kurang dari p.
        # -> 3 byte dapat menyatakan nilai sampai 256^3 - 1 = 16777215, yang melebihi p.
        # Jadi, ukuran chunk dipilih sebesar 2 byte.

        # 1. Memastikan p cukup besar untuk memuat seluruh kemungkinan nilai satu byte, yaitu 0 sampai 255.
        if p is None or p < Encryption.BYTE_BASE:
            raise ValueError("[Encryption.calculatePlaintextChunkSize.INVALID_P] p harus bernilai minimal 256 agar dapat memuat satu byte.")

        # 2. Memulai perhitungan dari ukuran 0 byte. limit menyimpan nilai 256^chunkSize.
        chunkSize = 0
        limit = 1

        # 3. Menambah ukuran satu byte selama 256^(chunkSize + 1) masih tidak melebihi p.
        while limit * Encryption.BYTE_BASE <= p:
            limit *= Encryption.BYTE_BASE
            chunkSize += 1

        return chunkSize

    @staticmethod
    def createPlaintextChunks(plaintextBytes: bytes | None, chunkSize: int) -> list[int]:
        # Memotong deretan byte pesan menjadi beberapa chunk, lalu membaca setiap chunk sebagai bilangan bulat.
        # Setiap byte menempati satu posisi pada bilangan berbasis 256.
        # Contoh, dua byte bernilai 1 dan 2 dibaca sebagai 1 x 256 + 2 = 258.
        # Byte di sebelah kiri memiliki nilai posisi lebih besar, seperti digit kiri pada bilangan desimal.

        # 1. Memastikan deretan byte pesan tidak null.
        if plaintextBytes is None:
            raise ValueError("[Encryption.createPlaintextChunks.NULL_PLAINTEXT] Plaintext tidak boleh null.")

        # 2. Memastikan setiap chunk dapat memuat setidaknya satu byte.
        if chunkSize < 1:
            raise ValueError("[Encryption.createPlaintextChunks.INVALID_CHUNK_SIZE] Ukuran chunk harus bernilai positif.")

        # 3. Menghitung jumlah chunk. Pesan kosong menghasilkan 0 chunk.
        # Bagian terakhir tetap dihitung sebagai satu chunk meskipun jumlah bytenya kurang dari chunkSize.
        chunkCount = 0 if len(plaintextBytes) == 0 else (len(plaintextBytes) - 1) // chunkSize + 1
        plaintextChunks = [0] * chunkCount

        # 4. Mengambil byte untuk setiap chunk, kemudian mengubahnya menjadi BigInteger.
        for i in range(len(plaintextChunks)):
            # start adalah indeks byte pertama, sedangkan end adalah batas akhir dari pesan yang tidak ikut disalin.
            # Math.min memastikan batas pengambilan tidak melewati akhir pesan.
            start = i * chunkSize
            end = min(start + chunkSize, len(plaintextBytes))
            chunkBytes = plaintextBytes[start:end]

            # Angka 1 meminta BigInteger membaca byte sebagai bilangan non-negatif,
            # sehingga bit paling kiri tidak dipakai sebagai tanda bilangan negatif.
            plaintextChunks[i] = int.from_bytes(chunkBytes, byteorder="big", signed=False)

        return plaintextChunks

    @staticmethod
    def generateSecretRandomNumber(p: int | None) -> int:
        # Memilih bilangan acak rahasia r yang digunakan pada perpangkatan C1 dan C2.
        # Pengambilan r diulang untuk setiap chunk agar pesan yang sama dapat menghasilkan ciphertext berbeda.
        # Nilai r tidak dikirim sebagai bagian dari ciphertext.
        # Pada implementasi ini, r dipilih dari 2 sampai p - 2, atau 1 < r < p - 1.

        # 1. Memastikan p bernilai minimal 5.
        if p is None or p < 5:
            raise ValueError("[Encryption.generateSecretRandomNumber.INVALID_P] p harus bernilai minimal 5.")

        # 2. Mengambil angka acak dari 0 sampai p - 4 menggunakan batas atas p - 3.
        # Penambahan 2 menggeser rentang tersebut menjadi 2 sampai p - 2.
        return RandomNumberGenerator.generateUniformRandomInteger(p - 3, Encryption.random) + 2

    @staticmethod
    def encrypt(plaintextBytes: bytes, e1: int | None, e2: int | None, p: int | None) -> list[list[int]]:
        # Mengenkripsi byte pesan menggunakan kunci publik penerima, yaitu (e1, e2, p).
        # Nilai e1 adalah basis perpangkatan, p adalah modulus prima,
        # dan e2 = e1^d mod p, dengan d sebagai kunci privat penerima.

        # Pesan dibagi menjadi chunk dan setiap chunk dibaca sebagai bilangan P yang kurang dari p.
        # Untuk setiap P, pengirim mengambil r secara acak, lalu menghitung:
        # C1 = e1^r mod p.
        # C2 = (e2^r x P) mod p.
        # Kedua angka tersebut disimpan sebagai pasangan {C1, C2}, satu pasangan untuk setiap chunk.

        # 1. Memastikan seluruh bagian kunci publik tidak null.
        if e1 is None or e2 is None or p is None:
            raise ValueError("[Encryption.encrypt.NULL_KEY_VALUE] e1, e2, dan p tidak boleh null.")

        # 2. Memastikan e1 dan e2 berada dalam interval 0 < nilai < p.
        if e1 <= 0 or e1 >= p or e2 <= 0 or e2 >= p:
            raise ValueError("[Encryption.encrypt.INVALID_PUBLIC_KEY] e1 dan e2 harus berada pada interval 0 < nilai < p.")

        # 3. Menentukan ukuran chunk, lalu membentuk bilangan pesan untuk setiap chunk.
        chunkSize = Encryption.calculatePlaintextChunkSize(p)
        plaintextChunks = Encryption.createPlaintextChunks(plaintextBytes, chunkSize)

        # 4. Menyiapkan satu baris untuk setiap chunk, dengan dua tempat untuk C1 dan C2.
        ciphertext = [[0, 0] for _ in plaintextChunks]

        # 5. Mengenkripsi setiap chunk dengan pengambilan r pada masing-masing perhitungan.
        for i in range(len(plaintextChunks)):
            r = Encryption.generateSecretRandomNumber(p)

            # Menghitung C1 = e1^r mod p.
            c1 = ModularArithmetic.modularExponentiation(e1, r, p)

            # sharedSecret menyimpan hasil e2^r mod p, yaitu pengali untuk menyamarkan bilangan pesan P.
            sharedSecret = ModularArithmetic.modularExponentiation(e2, r, p)
            c2 = sharedSecret * plaintextChunks[i] % p

            # Kolom 0 menyimpan C1 dan kolom 1 menyimpan C2 untuk chunk ke-i.
            ciphertext[i][0] = c1
            ciphertext[i][1] = c2

        return ciphertext
