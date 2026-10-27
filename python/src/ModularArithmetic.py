from typing import final


@final
class ModularArithmetic:
    @staticmethod
    def modularExponentiation(base: int, exponent: int, modulus: int) -> int:
        # Mereduksi proses pencarian remainder (sisa), di mana pada base^exponent mod modulus, perpangkatan langsung
        # terhadap angka yang sangat besar dinyatakan tidak efisien. Sehingga, base^exponent direduksi terlebih dahulu
        # menjadi angka yang lebih wajar.

        # Contoh:
        # 5^13 mod 3, daripada menghitung langsung, perpangkatan tersebut direduksi terlebih dahulu menggunakan strategi
        # biner pada eksponen (nama resminya Repeated Squaring Algorithm atau Binary Exponentiation). Di mana 13
        # dalam biner nilainya yakni 1101, atau 1000 + 0100 + 0001, atau dalam desimal 8 + 4 + 1. Sehingga perpangkatan
        # awal dirubah sedemikian rupa sehingga mejadi: 5^(8+4+1) atau (5^8 x 5^4 x 5^1) mod 3.

        # Perlu diperhatikan properti modulus adalah:
        # 1. (a x b) mod n = [(a mod n) x (b mod n)] mod n

        # 2. a^b mod n ≡ (a mod n)^b mod n
        # Atau dalam bahasa sehari-hari, sisa pembagian dengan n dari a^b dan sisa pembagian dengan n dari (a mod n)^b,
        # selalu menghasilkan nilai sisa yang sama (kongruen).
        # Contoh:
        # 5^2 mod 3
        # ->   = 25 mod 3
        #      = 1 (karena 8 x 3 = 24)
        # (5 mod 3)^2 mod 3
        # ->   = 2^2 mod 3
        #      = 4 mod 3
        #      = 1
        # Jadi, 5^2 mod 3 dan (5 mod 3)^2 mod 3 sama-sama menghasilkan sisa 1.

        # Kedua properti ini digunakan pada (5^8 x 5^4 x 5^1) mod 3, sehingga:
        # [(5^8 mod 3) x (5^4 mod 3) x (5^1 mod 3)] mod 3
        # Diketahui bahwa:
        # a. 5^2 mod 3 = 1, dan
        # b. Properti perpangkatan a^b x a^c = a^(b + c)
        # Maka:
        # 5^8 mod 3
        # ->   = (5^2 x 5^2 x 5^2 x 5^2) mod 3
        #      = (1 x 1 x 1 x 1) mod 3
        #      = 1 mod 3
        #      = 1
        # 5^4 mod 3
        # ->   = (5^2 x 5^2) mod 3
        #      = (1 x 1) mod 3
        #      = 1 mod 3
        #      = 1
        # 5^1 mod 3
        # ->   = 5 mod 3
        #      = 2

        # Subtitusi hasil kembali ke [(5^8 mod 3) x (5^4 mod 3) x (5^1 mod 3)] mod 3:
        # ->   = (1 x 1 x 2) mod 3
        #      = 2 mod 3
        #      = 2

        # Jadi dapat disimpulkan bahwa 5^13 mod 3 = 2, tanpa perlu menghitung berapa nilai dari 5^13.

        # Adapun dalam penerjemahan ke kode, ada sedikit perbedaan, di mana dalam implementasinya, kita tidak perlu
        # memecah eksponen menjadi penjumlahan pangkat-pangkat dari 2 secara manual, melainkan algoritma bekerja dengan
        # membaca digit biner eksponen dari kanan ke kiri.
        # Contoh, menggunakan kasus angka yang sama, yakni 13 atau 1101:
        # 1101 -> Digit paling kanan 1, atau ganjil, maka 5^1 dipakai.
        # 110  -> Digit paling kanan 0, atau genap, maka 5^2 dilewati.
        # 11   -> Digit paling kanan 1, atau ganjil, maka 5^4 dipakai.
        # 1    -> Digit paling kanan 1, atau ganjil, maka 5^8 dipakai.
        # 0    -> Menandakan jika semua digit sudah dibaca dan proses berhenti.

        # Untuk melakukan hal tersebut, terdapat tiga variabel yang perlu diperhatikan:
        # 1. result   = Menyimpan hasil perkalian dari perpangkatan yang dipilih.
        # 2. base     = Menyimpan nilai perpangkatan yang diperiksa, setelah direduksi modulo.
        # 3. exponent = Menentukan apakah perpangkatan tersebut akan digunakan, dengan melihat digit binernya.

        # Di mana langkah implementasinya:
        # 1. Memastikan modulus bernilai positif:
        if modulus <= 0:
            raise ValueError(f"[ModularArithmetic.modularExponentiation.INVALID_MODULUS] Modulus harus bernilai positif. (Nilai diterima: {modulus})")

        # 2. Memastikan eksponen tidak bernilai negatif:
        if exponent < 0:
            raise ValueError(f"[ModularArithmetic.modularExponentiation.INVALID_EXPONENT] Eksponen harus bernilai non-negatif. (Nilai diterima: {exponent})")

        # 3. Inisiasi awal result dengan nilai 1, karena 1 merupakan properti perkalian, yakni:
        # a x 1 = a
        # Artinya, perkalian suatu bilangan dengan 1 tidak akan mengubah nilai bilangan tersebut.

        # Di mana nantinya akan digunakan untuk rumus:
        # result = (result x base) mod modulus

        # Contoh, pada kasus 5^13 mod 3:
        # (Inisiasi awal)
        # result   = 1

        # (Iterasi 1)
        # result   = (1 x (5^1 mod 3)) mod 3
        #          = (1 x 2) mod 3
        #          = 2

        # (Iterasi 2, genap, tidak berubah)
        # result   = 2

        # (Iterasi 3)
        # result   = (2 x (5^4 mod 3)) mod 3
        #          = (2 x 1) mod 3
        #          = 2

        # (Iterasi 4)
        # result = (2 x (5^8 mod 3)) mod 3
        #        = (2 x 1) mod 3
        #        = 2

        # Sehingga, nilai result akhir adalah 2, di mana hal ini sesuai dengan:
        # 5^13 mod 3 = (5^1 x 5^4 x 5^8) mod 3 = 2

        # Kemudian, result juga direduksi modulo untuk menangani kasus modulus = 1, karena 1 mod 1 = 0.
        result = 1 % modulus

        # 4. Reduksi awal base dengan modulus menggunakan properti:
        # a^b mod n = (a mod n)^b mod n
        base %= modulus

        # 5. Selama exponent bernilai lebih dari 0, maka algoritma akan melakukan tiga operasi, yakni:
        while exponent > 0:

            # 5.1. Memeriksa apakah exponent ganjil atau genap, dengan memeriksa digit biner paling kanan.
            #  a. Apabila ganjil, maka result = (result x base) mod modulus, dan
            #  b. Apabila genap, maka result tidak berubah.
            if exponent & 1:
                result = result * base % modulus

            # 5.2. Mengkuadratkan base, kemudian mod dengan modulus ntuk mendapatkan perpangkatan berikutnya.
            # Di mana hal ini sesuai dengan properti eksponen, yakni:
            # (a^b)^2 = a^(2b)

            # Contoh:
            # (5^1)^2 = 5^2
            # (5^2)^2 = 5^(2 x 2) = 5^4
            # (5^4)^2 = 5^(2 x 4) = 5^8
            base = base * base % modulus

            # 5.3. Menggeser seluruh digit biner exponent satu posisi ke kanan.
            exponent >>= 1

        return result

    @staticmethod
    def modularInverse(value: int, modulus: int) -> int:
        # Pada ElGamal, kunci publik memuat e1, e2, dan modulus prima p.
        # Nilai e1 menjadi basis perpangkatan, sedangkan e2 = e1^d mod p, dengan d sebagai kunci privat.
        # Pengirim memilih bilangan acak rahasia r, lalu menghitung C1 = e1^r mod p
        # dan C2 = (e2^r x P) mod p, dengan P sebagai nilai pesan dalam interval 0 <= P < p.

        # Untuk memperoleh P kembali, kita perlu melakukan kebalikan dari perkalian dengan e2^r.
        # Penerima dapat menghitung e2^r mod p dari C1 menggunakan kunci privat d, karena:
        # C1^d mod p
        # -> = e1^(rd) mod p
        # -> = (e1^d)^r mod p
        # -> = e2^r mod p.

        # Pada perkalian biasa, kebalikan dari mengalikan dengan 5 adalah membagi dengan 5,
        # atau mengalikan dengan 1/5. Angka 1/5 disebut invers perkalian dari 5 karena 5 x (1/5) = 1.

        # Dalam modulo, pasangan pengali yang dicari adalah bilangan bulat yang membuat perkaliannya bersisa 1.
        # Pasangan ini disebut invers modulo, dan kita tuliskan dengan nama inverse:
        # (value x inverse) mod modulus = 1.

        # Contoh, P = 7, p = 23, dan hasil e2^r mod p = 5:
        # -> Enkripsi menghasilkan C2 = 7 x 5 mod 23 = 12.
        # -> Invers dari 5 modulo 23 adalah 14, karena 5 x 14 mod 23 = 70 mod 23 = 1.
        # -> Mengalikan C2 dengan 14 menghasilkan 12 x 14 mod 23 = 168 mod 23 = 7.
        # Pesan 7 diperoleh kembali karena pasangan pengali 5 dan 14 bersisa 1:
        # (7 x 5 x 14) mod 23 = (7 x 1) mod 23 = 7.

        # Pada metode ini, value diisi dengan hasil C1^d mod p dan modulus diisi dengan p.
        # Metode mencari invers dari value. Pada contoh di atas, masukannya 5 dan 23, sedangkan hasilnya 14.
        # Hasil perhitungan invers itulah yang digunakan sebagai inverse dalam rumus:
        # (C2 x inverse) mod p = (P x e2^r x inverse) mod p
        #                     = (P x 1) mod p
        #                     = P.

        # Jadi, kita perlu mencari pengali yang memenuhi (value x inverse) mod modulus = 1.
        # Extended Euclidean Algorithm membantu mencarinya dengan menghitung faktor persekutuan terbesar (FPB), disebut gcd,
        # beserta dua bilangan bulat x dan y yang memenuhi:
        # (value)x + (modulus)y = gcd(value, modulus).

        # Jika gcd = 1, persamaannya menjadi (value)x + (modulus)y = 1.
        # Dengan value = 5 dan modulus = 23, persamaannya menjadi 5x + 23y = 1, di mana nilai x dan y dicari menggunakan XGCD.
        # Contoh, untuk value = 5 dan modulus = 23, XGCD menghasilkan x = -9 dan y = 2:
        # -> 5(-9) + 23(2) = 1.
        # -> -45 + 46 = 1.
        # Di sini x bernilai negatif agar penjumlahan kedua hasil perkalian menghasilkan 1.
        # Karena 46 habis dibagi 23, persamaan tersebut juga menunjukkan (-45) mod 23 = 1.
        # Jadi, -9 memenuhi syarat sebagai invers dari 5 modulo 23.

        # 1. Memastikan modulus lebih besar dari 1.
        if modulus <= 1:
            raise ValueError(f"[ModularArithmetic.modularInverse.INVALID_MODULUS] Modulus harus lebih besar dari 1. (Nilai diterima: {modulus})")

        # 2. Mengambil sisa pembagian value agar berada dalam interval 0 <= value < modulus.
        value %= modulus

        # 3. Mencari FPB beserta x dan y. Urutan hasilnya adalah {gcd, x, y}.
        result = ModularArithmetic.extendedEuclidianAlgorithmXGCD(value, modulus)

        # 4. Jika FPB bukan 1, maka invers tidak ada karena value dan modulus memiliki faktor bersama selain 1.
        if result[0] != 1:
            raise ArithmeticError("[ModularArithmetic.modularInverse.NO_INVERSE] Bilangan dan modulus harus relatif prima.")

        # 5. Mengambil x dari result[1], kemudian memilih nilai invers dalam interval 0 <= inverse < modulus.
        # Pada contoh tadi, x = -9. Dengan modulus 23, nilai dalam interval tersebut adalah -9 + 23 = 14.
        # Penambahan 23 tidak mengubah sisa perkaliannya dalam modulo 23:
        # 5(-9) mod 23 = 1, dan 5 x 14 mod 23 = 1.
        # Karena itu, metode mengembalikan 14 sebagai invers dari 5 modulo 23.
        return result[1] % modulus

    @staticmethod
    def extendedEuclidianAlgorithmXGCD(a: int, b: int) -> list[int]:
        # Mencari FPB dari a dan b, serta dua bilangan bulat x dan y yang memenuhi ax + by = gcd(a, b).

        # Algoritma Euclid menggunakan sifat gcd(a, b) = gcd(b, a mod b).
        # Caranya adalah dengan mengambil sisa pembagian a dengan b, kemudian b di modulus dengan sisa tersebut.
        # Hal ini diulangi sampai sisanya 0, dengan pembagi pada langkah terakhir adalah FPBnya.

        # Contoh, a = 5 dan b = 23:
        # -> 5 mod 23 = 5,
        # -> 23 mod 5 = 3,
        # -> 5 mod 3 = 2,
        # -> 3 mod 2 = 1,
        # -> 2 mod 1 = 0.
        # Pembagi terakhir adalah 1, sehingga gcd(5, 23) = 1.

        # Kita juga perlu mengetahui x dan y pada persamaan 5x + 23y = 1.
        # Untuk itu, setiap angka pada perhitungan tadi ditulis dengan pengali untuk 5 dan pengali untuk 23.
        # Mulai dari kedua angka awal:
        # -> 5 = 5(1) + 23(0). Pengali untuk 5 adalah 1, dan pengali untuk 23 adalah 0.
        # -> 23 = 5(0) + 23(1). Pengali untuk 5 adalah 0, dan pengali untuk 23 adalah 1.

        # Penulisan 5(-4) di bawah berarti 5 dikalikan -4.

        # Dari 23 mod 5 = 3, kita memperoleh:
        # 3 = 23 - 4 x 5
        #   = 5(-4) + 23(1).
        # Jadi, pengali untuk 5 adalah -4, sedangkan pengali untuk 23 adalah 1.

        # Berikutnya, sisa 2 diperoleh dari 5 - 3.
        # Gantikan 5 dengan 5(1) + 23(0), serta 3 dengan 5(-4) + 23(1):
        # 2 = [5(1) + 23(0)] - [5(-4) + 23(1)].
        # Pengali untuk 5 dikurangi pengali untuk 5, begitu pula pengali untuk 23:
        # 2 = 5(1 - (-4)) + 23(0 - 1)
        #   = 5(5) + 23(-1).

        # Terakhir, sisa 1 diperoleh dari 3 - 2.
        # Gantikan 3 dan 2 dengan hasil yang menggunakan 5 dan 23 di atas:
        # 1 = [5(-4) + 23(1)] - [5(5) + 23(-1)]
        #   = 5(-4 - 5) + 23(1 - (-1))
        #   = 5(-9) + 23(2).
        # Karena 1 adalah FPB, persamaan ini sudah memenuhi 5x + 23y = 1.
        # Dengan demikian, x = -9 dan y = 2.

        # 1. Memastikan kedua bilangan tidak negatif.
        if a < 0 or b < 0:
            raise ValueError("[ModularArithmetic.extendedEuclidianAlgorithmXGCD.INVALID_INPUT] Bilangan a dan b harus non-negatif.")

        # 2. Menyimpan dua angka yang sedang diperiksa.
        # previousX dan previousY adalah pengali untuk a dan b pada previousRemainder.
        # x dan y adalah pengali untuk a dan b pada remainder.
        # Nilai awalnya mengikuti a = a(1) + b(0), serta b = a(0) + b(1).
        previousRemainder = a
        remainder = b
        previousX = 1
        x = 0
        previousY = 0
        y = 1

        # 3. Mengulangi perhitungan sampai sisanya 0.
        while remainder != 0:
            # Menentukan berapa kali remainder dapat dikurangkan dari previousRemainder tanpa menjadi negatif.
            # Contoh, 23 dapat dikurangi 5 sebanyak 4 kali, sehingga quotient = 4.
            quotient = previousRemainder // remainder

            # Menghitung sisanya. Pada contoh tersebut: 23 - 4 x 5 = 3.
            nextRemainder = previousRemainder - quotient * remainder

            # Mengikuti pengurangan yang sama untuk kedua pengali, seperti pada contoh sisa 3, 2, dan 1 di atas.
            # Pengali milik angka pertama dikurangi quotient kali pengali milik angka kedua.
            # nextX adalah pengali untuk a pada sisa baru, sedangkan nextY adalah pengali untuk b.
            nextX = previousX - quotient * x
            nextY = previousY - quotient * y

            # Pada langkah berikutnya, gunakan pembagi sebagai angka pertama dan sisa baru sebagai angka kedua.
            # Pengali masing-masing dipindahkan bersama angka yang diwakilinya.
            previousRemainder = remainder
            remainder = nextRemainder
            previousX = x
            x = nextX
            previousY = y
            y = nextY

        # 4. previousRemainder adalah FPB. Dua pengalinya disertakan dalam urutan {gcd, x, y}.
        return [previousRemainder, previousX, previousY]
