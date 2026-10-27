from __future__ import annotations

from dataclasses import dataclass
from secrets import SystemRandom
from typing import ClassVar, final

from .ModularArithmetic import ModularArithmetic
from .PrimalityTest import PrimalityTest
from .RandomNumberGenerator import RandomNumberGenerator


@final
class DHKeyGeneration:
    # Ukuran ini dipilih agar demonstrasi manual tetap cepat dijalankan.
    # Untuk penggunaan nyata, ElGamal memerlukan parameter yang lebih besar dan format ciphertext yang terautentikasi.
    PRIME_BIT_LENGTH: ClassVar[int] = 256

    # Jumlah putaran yang diminta untuk setiap pengujian Miller-Rabin.
    PRIMALITY_ROUNDS: ClassVar[int] = 25

    # Membangkitkan bilangan acak yang sulit ditebak menggunakan SecureRandom.
    random: ClassVar[SystemRandom] = SystemRandom()

    # Menyimpan modulus p, komponen publik e1 dan e2, serta kunci privat d dalam satu paket.
    @final
    @dataclass(frozen=True)
    class KeyPair:
        p: int
        e1: int
        e2: int
        d: int

    @staticmethod
    def generateKeyPair() -> DHKeyGeneration.KeyPair:
        # Membentuk kunci publik (e1, e2, p) dan kunci privat d.
        # Seperti pada struktur perpangkatan Diffie-Hellman, e1 dan p bersifat publik,
        # sedangkan d dirahasiakan dan digunakan untuk menghitung e2 = e1^d mod p.

        # Modulus p dipilih dalam bentuk p = 2q + 1, dengan p dan q prima. Bentuk ini disebut safe prime.
        # Kita membangkitkan q terlebih dahulu, kemudian menguji apakah 2q + 1 juga prima.
        # q dipilih sepanjang PRIME_BIT_LENGTH - 1 bit agar p memiliki panjang PRIME_BIT_LENGTH bit.
        # Pengujian keduanya menggunakan Miller-Rabin, sehingga hasilnya tetap berupa probable prime.

        # 1. Mengulang pembentukan q dan p sampai keduanya lolos pengujian.
        while True:
            q = PrimalityTest.generatePrime(DHKeyGeneration.PRIME_BIT_LENGTH - 1, DHKeyGeneration.PRIMALITY_ROUNDS)
            p = q * 2 + 1
            if PrimalityTest.isPrime(p, DHKeyGeneration.PRIMALITY_ROUNDS):
                break

        # 2. Memilih e1 sebagai generator, yaitu basis yang pangkat-pangkatnya modulo p
        # dapat menghasilkan seluruh bilangan dari 1 sampai p - 1.
        # Pada modulus prima, pangkat terkecil yang menghasilkan sisa 1 harus membagi p - 1.
        # Karena p - 1 = 2q, pilihannya adalah 1, 2, q, atau 2q.
        # Jika e1^2 dan e1^q belum bersisa 1, pangkat terkecil tersebut harus 2q, yaitu p - 1.

        # Contoh, p = 23 dan q = 11:
        # -> 5^2 mod 23 = 2.
        # -> 5^11 mod 23 = 22.
        # Kedua hasil bukan 1, sehingga 5 dapat dipilih sebagai generator untuk modulus 23.
        while True:
            # Mengambil e1 dari 2 sampai p - 2.
            e1 = RandomNumberGenerator.generateUniformRandomInteger(p - 3, DHKeyGeneration.random) + 2
            if (ModularArithmetic.modularExponentiation(e1, 2, p) != 1
                    and ModularArithmetic.modularExponentiation(e1, q, p) != 1):
                break

        # 3. Memilih kunci privat d secara acak dari 2 sampai p - 2, atau 1 < d < p - 1.
        d = RandomNumberGenerator.generateUniformRandomInteger(p - 3, DHKeyGeneration.random) + 2

        # 4. Menghitung komponen publik e2 dari e1 dan kunci privat d.
        e2 = ModularArithmetic.modularExponentiation(e1, d, p)

        return DHKeyGeneration.KeyPair(p, e1, e2, d)
