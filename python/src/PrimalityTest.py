from secrets import SystemRandom
from typing import ClassVar, final

from .ModularArithmetic import ModularArithmetic
from .RandomNumberGenerator import RandomNumberGenerator


@final
class PrimalityTest:
    # Membangkitkan bilangan acak yang sulit ditebak menggunakan SecureRandom.
    random: ClassVar[SystemRandom] = SystemRandom()

    @staticmethod
    def millerRabinRound(d: int, r: int, n: int) -> bool:
        # ElGamal dan Diffie-Hellman menggunakan bilangan prima sebagai modulus, sedangkan bilangan yang
        # dibangkitkan secara acak belum tentu prima, sehingga perlu dilakukan pengujian terlebih dahulu.

        # Pengujian ini menggunakan algoritma Miller-Rabin, yang mencari tanda bahwa kandidat bukan prima.
        # Kandidat tersebut disebut n, sedangkan angka yang dipakai untuk mengujinya disebut base.

        # Dasar awalnya adalah Teorema Fermat Kecil:
        # Jika n prima dan 1 <= base < n, maka base^(n-1) mod n = 1.
        # Namun, bilangan komposit tertentu juga dapat menghasilkan sisa 1, sehingga hasil ini saja
        # belum cukup untuk menyatakan bahwa n prima.

        # Miller-Rabin menerapkan teorema tersebut dengan memeriksa hasil antara melalui pengkuadratan berulang.
        # Untuk melakukannya, n-1 dibagi 2 berulang kali sampai hasilnya ganjil.

        # Hasil pembagian terakhir menjadi d, sedangkan total jumlah pembagian menjadi r, sehingga n-1 = d * 2^r.
        # Pengujian dimulai dari base^d mod n. Setiap pengkuadratan menggandakan eksponen,
        # sehingga setelah r kali pengkuadratan, eksponennya kembali menjadi n-1.

        # Satu putaran (round) menjalankan pemeriksaan dengan satu base acak.
        # Jika pemeriksaan gagal, n terbukti komposit dan seluruh pengujian dihentikan.
        # Jika lolos, pengujian diulang sampai jumlah putaran yang diminta pada rounds terpenuhi.
        # Semakin banyak putaran, semakin kecil peluang bilangan komposit lolos seluruh pengujian,
        # tetapi kandidat yang lolos tetap belum dapat dipastikan prima.

        # Contoh, kandidat n = 97:
        # n-1 = 96.
        # -> 96 / 2 = 48, r = 1.
        # -> 48 / 2 = 24, r = 2.
        # -> 24 / 2 = 12, r = 3.
        # -> 12 / 2 = 6, r = 4.
        # -> 6 / 2 = 3, r = 5.
        # Pembagian berhenti pada 3 karena sudah ganjil, sehingga d = 3, r = 5, dan 97 - 1 = 3 * 2^5.

        # Pada contoh n = 97, base dipilih secara acak dari 2 sampai 95. Misalkan angka yang terpilih adalah 5.
        # Dengan d = 3 yang sudah diperoleh sebelumnya, hasil awalnya adalah:
        # x = 5^3 mod 97 = 28.

        # Kemudian, hasil 28 dikuadratkan, lalu diambil sisa pembagiannya dengan 97:
        # 28^2 mod 97 = 8.

        # Langkah yang sama diulang memakai hasil sebelumnya:
        #  8^2 mod 97 = 64
        # 64^2 mod 97 = 22
        # 22^2 mod 97 = 96.

        # Pada pengkuadratan keempat, hasilnya sama dengan n-1, yaitu 96, sehingga putaran ini lolos dan berhenti.

        # 1. Memilih base dari 2 sampai n-2.
        # Angka 1 dan n-1 jika digunakan pada base^d mod n akan menghasilkan 1 atau n-1, baik untuk kandidat ganjil
        # prima maupun komposit, sehingga putaran selalu lolos.
        base = RandomNumberGenerator.generateUniformRandomInteger(n - 3, PrimalityTest.random) + 2

        # 2. Menghitung hasil awal base^d mod n.
        x = ModularArithmetic.modularExponentiation(base, d, n)

        # 3. Memeriksa hasil 1 atau n-1, jika iya maka putaran lolos.
        if x == 1 or x == n - 1:
            return True

        # 4. Melakukan pengkuadratan berikutnya paling banyak r-1 kali untuk mencari hasil n-1.
        # Pengkuadratan ke-r sudah mencapai base^(n-1), yang untuk n prima seharusnya bersisa 1.
        for _ in range(1, r):
            x = x * x % n

            # Jika hasil pengkuadratan adalah n-1, maka putaran lolos karena pengkuadratan berikutnya
            # akan menghasilkan sisa 1, sesuai dengan (n-1)^2 mod n = 1.
            if x == n - 1:
                return True

            # Jika hasil pengkuadratan adalah 1, maka n terbukti komposit karena nilai sebelumnya
            # bukan 1 maupun n-1. Pada modulus prima, hanya kedua nilai tersebut yang kuadratnya bersisa 1.
            if x == 1:
                return False

        # 5. Menolak kandidat karena hasil awal bukan 1 dan tidak ditemukan n-1 dalam pengkuadratan.
        return False

    @staticmethod
    def isPrime(candidateRandomInteger: int, rounds: int) -> bool:
        # Menyiapkan kandidat, kemudian mengulang pengujian Miller-Rabin sebanyak rounds.
        # Jika satu putaran membuktikan kandidat komposit, pengujian langsung dihentikan.

        # 1. Memastikan jumlah putaran pengujian bernilai positif.
        if rounds < 1:
            raise ValueError(f"[PrimalityTest.isPrime.INVALID_ROUNDS] Rounds harus bernilai positif. (Nilai diterima: {rounds})")

        # 2. Jika kandidat bernilai kurang dari 2, maka bukan prima.
        if candidateRandomInteger < 2:
            return False

        # 3. Jika kandidat bernilai 2 atau 3, maka prima.
        if candidateRandomInteger == 2 or candidateRandomInteger == 3:
            return True

        # 4. Jika kandidat genap selain 2, maka bukan prima, karena selalu memiliki faktor 2.
        if candidateRandomInteger % 2 == 0:
            return False

        # 5. Menguraikan n-1 menjadi d * 2^r, dengan d ganjil dan n merupakan kandidat yang diuji.
        d = candidateRandomInteger - 1
        r = 0

        while d % 2 == 0:
            d //= 2
            r += 1

        # 6. Mengulang pengujian dengan pengambilan base acak pada setiap putaran.
        # Bilangan komposit dapat lolos untuk base tertentu, sehingga pengulangan mengurangi
        # peluang kandidat komposit lolos dari seluruh pengujian.
        for _ in range(rounds):
            if not PrimalityTest.millerRabinRound(d, r, candidateRandomInteger):
                return False

        # 7. Menerima kandidat yang lolos seluruh putaran sebagai probable prime,
        # yaitu kandidat yang belum terbukti komposit melalui pengujian ini.
        return True

    # Pemeriksaan tambahan untuk pendekatan safe prime: p = 2*q + 1, dengan p dan q prima.
    # Kedua bilangan diperiksa menggunakan Miller-Rabin, sehingga hasil true tetap probabilistik.
    @staticmethod
    def isSafePrime(p: int, rounds: int) -> bool:
        if not PrimalityTest.isPrime(p, rounds):
            return False

        q = (p - 1) // 2
        return PrimalityTest.isPrime(q, rounds)

    @staticmethod
    def generatePrime(bitLength: int, rounds: int) -> int:
        # Mencari bilangan prima ganjil dengan panjang biner sebanyak bitLength.
        # Kandidat acak diuji dengan Miller-Rabin. Jika terbukti komposit, kandidat baru dibangkitkan.

        # Ukuran bilangan dalam kriptografi biasanya dinyatakan dalam bit, yaitu jumlah digit pada bentuk binernya.
        # Setiap bit bernilai 0 atau 1. Kandidat dibentuk dari sejumlah bit acak sesuai bitLength.
        # Melalui pengaturan bit, kita dapat memastikan panjang kandidat sesuai yang diminta dan nilainya ganjil.

        # 1. Memastikan panjang biner minimal 2 bit, karena bilangan satu bit hanya 0 dan 1, yang bukan prima.
        if bitLength < 2:
            raise ValueError(f"[PrimalityTest.generatePrime.INVALID_BITLENGTH] bitLength harus bernilai lebih dari 2. (Nilai diterima: {bitLength})")

        # 2. Memastikan jumlah putaran pengujian bernilai positif.
        if rounds < 1:
            raise ValueError(f"[PrimalityTest.isPrime.INVALID_ROUNDS] Rounds harus bernilai positif. (Nilai diterima: {rounds})")

        # 3. Mengulang pencarian sampai ditemukan kandidat yang lolos pengujian.
        while True:
            # 4. Membangkitkan kandidat secara acak.
            # setBit(bitLength - 1) menetapkan bit paling kiri menjadi 1 agar panjang kandidat tepat bitLength bit.
            # Dengan demikian, rentangnya adalah 2^(bitLength - 1) <= candidate < 2^bitLength.
            # setBit(0) menetapkan bit paling kanan menjadi 1 agar kandidat ganjil.
            # Kandidat genap tidak dipilih karena bilangan prima genap hanyalah angka 2.
            candidate = PrimalityTest.random.getrandbits(bitLength) | (1 << (bitLength - 1)) | 1

            # 5. Mengembalikan kandidat yang lolos seluruh putaran Miller-Rabin sebagai probable prime.
            if PrimalityTest.isPrime(candidate, rounds):
                return candidate
