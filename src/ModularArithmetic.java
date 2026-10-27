import java.math.BigInteger;

public class ModularArithmetic {
    public static BigInteger exponentiation(BigInteger base, BigInteger exponent, BigInteger modulus) {
        // Mereduksi proses pencarian remainder (sisa), di mana pada base^exponent mod modulus, perpangkatan langsung
        // terhadap angka yang sangat besar dinyatakan tidak efisien. Sehingga, base^exponent direduksi terlebih dahulu
        // menjadi angka yang lebih wajar.

        // Contoh:
        // 5^13 mod 3, daripada menghitung langsung, perpangkatan tersebut direduksi terlebih dahulu menggunakan strategi
        // biner pada eksponen (nama resminya Repeated Squaring Algorithm atau Binary Exponentiation). Di mana 13
        // dalam biner nilainya yakni 1101, atau 1000 + 0100 + 0001, atau dalam desimal 8 + 4 + 1. Sehingga perpangkatan
        // awal dirubah sedemikian rupa sehingga mejadi: 5^(8+4+1) atau (5^8 x 5^4 x 5^1) mod 3.

        // Perlu diperhatikan properti modulus adalah:
        // 1. (a x b) mod n = [(a mod n) x (b mod n)] mod n

        // 2. a^b mod n ≡ (a mod n)^b mod n
        // Atau dalam bahasa sehari-hari, sisa pembagian dengan n dari a^b dan sisa pembagian dengan n dari (a mod n)^b,
        // selalu menghasilkan nilai sisa yang sama (kongruen).
        // Contoh:
        // 5^2 mod 3
        // ->   = 25 mod 3
        //      = 1 (karena 8 x 3 = 24)
        // (5 mod 3)^2 mod 3
        // ->   = 2^2 mod 3
        //      = 4 mod 3
        //      = 1
        // Jadi, 5^2 mod 3 dan (5 mod 3)^2 mod 3 sama-sama menghasilkan sisa 1.

        // Kedua properti ini digunakan pada (5^8 x 5^4 x 5^1) mod 3, sehingga:
        // [(5^8 mod 3) x (5^4 mod 3) x (5^1 mod 3)] mod 3
        // Diketahui bahwa:
        // a. 5^2 mod 3 = 1, dan
        // b. Properti perpangkatan a^b x a^c = a^(b + c)
        // Maka:
        // 5^8 mod 3
        // ->   = (5^2 x 5^2 x 5^2 x 5^2) mod 3
        //      = (1 x 1 x 1 x 1) mod 3
        //      = 1 mod 3
        //      = 1
        // 5^4 mod 3
        // ->   = (5^2 x 5^2) mod 3
        //      = (1 x 1) mod 3
        //      = 1 mod 3
        //      = 1
        // 5^1 mod 3
        // ->   = 5 mod 3
        //      = 2

        // Subtitusi hasil kembali ke [(5^8 mod 3) x (5^4 mod 3) x (5^1 mod 3)] mod 3:
        // ->   = (1 x 1 x 2) mod 3
        //      = 2 mod 3
        //      = 2

        // Jadi dapat disimpulkan bahwa 5^13 mod 3 = 2, tanpa perlu menghitung berapa nilai dari 5^13.

        // Adapun dalam penerjemahan ke kode, ada sedikit perbedaan, di mana dalam implementasinya, kita tidak perlu
        // memecah eksponen menjadi penjumlahan pangkat-pangkat dari 2 secara manual, melainkan algoritma bekerja dengan
        // membaca digit biner eksponen dari kanan ke kiri.
        // Contoh, menggunakan kasus angka yang sama, yakni 13 atau 1101:
        // 1101 -> Digit paling kanan 1, atau ganjil, maka 5^1 dipakai.
        // 110  -> Digit paling kanan 0, atau genap, maka 5^2 dilewati.
        // 11   -> Digit paling kanan 1, atau ganjil, maka 5^4 dipakai.
        // 1    -> Digit paling kanan 1, atau ganjil, maka 5^8 dipakai.
        // 0    -> Menandakan jika semua digit sudah dibaca dan proses berhenti.

        // Untuk melakukan hal tersebut, terdapat tiga variabel yang perlu diperhatikan:
        // 1. result   = Menyimpan hasil perkalian dari perpangkatan yang dipilih.
        // 2. base     = Menyimpan nilai perpangkatan yang diperiksa, setelah direduksi modulo.
        // 3. exponent = Menentukan apakah perpangkatan tersebut akan digunakan, dengan melihat digit binernya.

        // Di mana langkah implementasinya:
        // 1. Memastikan modulus bernilai positif:
        if (modulus.signum() <= 0) {
            throw new IllegalArgumentException("[ModularArithmetic.exponentiation.INVALID_MODULUS] Modulus harus bernilai positif. (Nilai diterima: " + modulus + ")");
        }

        // 2. Memastikan eksponen tidak bernilai negatif:
        if (exponent.signum() < 0) {
            throw new IllegalArgumentException("[ModularArithmetic.exponentiation.INVALID_EXPONENT] Eksponen harus bernilai non-negatif. (Nilai diterima: " + exponent + ")");
        }

        // 3. Inisiasi awal result dengan nilai 1, karena 1 merupakan properti perkalian, yakni:
        // a x 1 = a
        // Artinya, perkalian suatu bilangan dengan 1 tidak akan mengubah nilai bilangan tersebut.

        // Di mana nantinya akan digunakan untuk rumus:
        // result = (result x base) mod modulus

        // Contoh, pada kasus 5^13 mod 3:
        // (Inisiasi awal)
        // result   = 1

        // (Iterasi 1)
        // result   = (1 x (5^1 mod 3)) mod 3
        //          = (1 x 2) mod 3
        //          = 2

        // (Iterasi 2, genap, tidak berubah)
        // result   = 2

        // (Iterasi 3)
        // result   = (2 x (5^4 mod 3)) mod 3
        //          = (2 x 1) mod 3
        //          = 2

        // (Iterasi 4)
        // result = (2 x (5^8 mod 3)) mod 3
        //        = (2 x 1) mod 3
        //        = 2

        // Sehingga, nilai result akhir adalah 2, di mana hal ini sesuai dengan:
        // 5^13 mod 3 = (5^1 x 5^4 x 5^8) mod 3 = 2

        // Kemudian, result juga direduksi modulo untuk menangani kasus modulus = 1, karena 1 mod 1 = 0.
        BigInteger result = BigInteger.ONE.mod(modulus);

        // 4. Reduksi awal base dengan modulus menggunakan properti:
        // a^b mod n = (a mod n)^b mod n
        base = base.mod(modulus);

        // 5. Selama exponent bernilai lebih dari 0, maka algoritma akan melakukan tiga operasi, yakni:
        while (exponent.signum() > 0) {

            // 5.1. Memeriksa apakah exponent ganjil atau genap, dengan memeriksa digit biner paling kanan.
            //  a. Apabila ganjil, maka result = (result x base) mod modulus, dan
            //  b. Apabila genap, maka result tidak berubah.
            if (exponent.testBit(0)) {
                result = result.multiply(base).mod(modulus);
            }

            // 5.2. Mengkuadratkan base, kemudian mod dengan modulus ntuk mendapatkan perpangkatan berikutnya.
            // Di mana hal ini sesuai dengan properti eksponen, yakni:
            // (a^b)^2 = a^(2b)

            // Contoh:
            // (5^1)^2 = 5^2
            // (5^2)^2 = 5^(2 x 2) = 5^4
            // (5^4)^2 = 5^(2 x 4) = 5^8
            base = base.multiply(base).mod(modulus);

            // 5.3. Menggeser seluruh digit biner exponent satu posisi ke kanan.
            exponent = exponent.shiftRight(1);
        }

        return result;
    }
}
