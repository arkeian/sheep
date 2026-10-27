import java.math.BigInteger;
import java.security.SecureRandom;

public class RandomNumberGenerator {
    // Membangkitkan bilangan acak yang sulit ditebak menggunakan SecureRandom.
    private static final SecureRandom random = new SecureRandom();

    public static BigInteger generateUniformRandomInteger(BigInteger upperExclusive, SecureRandom random) {
        // Menghasilkan satu bilangan bulat acak dari interval 0 sampai sebelum upperExclusive.
        // Upper exclusive menunjukkan batas atas interval tidak termasuk hasil yang boleh dipilih.

        // Contoh:
        // upperExclusive = 10
        // -> Angka yang boleh dihasilkan: 0, 1, 2, 3, 4, 5, 6, 7, 8, dan 9.
        // -> Angka 10 tidak termasuk, atau 0 <= value < 10.

        // Generasi angka ini menggunakan pendekatan uniform, di mana setiap angka yang diperbolehkan
        // memiliki peluang yang sama.
        // Pada contoh di atas terdapat 10 angka, sehingga peluang setiap angka adalah 1/10.

        // Pada upperExclusive = 10, diperlukan bit sebanyak 4 (1010), namun 4 bit bisa merepresentasikan angka
        // dari 0 sampai 15, sehingga perlu ditetapkan batas agar angka 10 sampai 15 tidak terpilih.
        // Jika kita menggunakan modulo untuk mereduksi angkanya, maka akan cenderung bias dan distribusi angka
        // menjadi tidak merata.

        // Contoh:
        // Angka 0 bisa didapatkan dari:
        //  a. 0 mod 10
        //  b. 10 mod 10
        // Sehingga, peluangnya 2/16.
        // Angka 6 bisa didapatkan dari:
        //  a. 6 mod 10
        //  Sehingga, peluangnya 1/16.

        // Maka dari itu, untuk menghindarinya, kandidat 10 sampai 15 ditolak dan diacak ulang (nama resminya adalah
        // Rejection Sampling), sehingga peluang setiap hasil 0 sampai 9 adalah 1/10.

        // 1. Memastikan upperExclusive bernilai positif.
        if (upperExclusive.compareTo(BigInteger.ZERO) <= 0) {
            throw new IllegalArgumentException("[RandomNumberGenerator.generateUniformRandomInteger.INVALID_UPPER_EXCLUSIVE] Upper Exclusive harus bernilai positif. (Nilai diterima: " + upperExclusive + ")");
        }

        // 2. Menghitung jumlah digit biner dari upperExclusive.
        // Kandidat dibentuk melalui bit acak, sehingga diperlukan jumlah bit yang cukup untuk mencakup seluruh
        // bilangan dalam interval yang diminta.
        int bits = upperExclusive.bitLength();

        // 3. Mengulang pengambilan kandidat sampai ditemukan angka dalam interval yang diminta.
        while (true) {
            // 4. Menggunakan jumlah posisi biner untuk membentuk kandidat.
            BigInteger value = new BigInteger(bits, random);

            // 5. Menerima kandidat jika nilainya lebih kecil dari upperExclusive.
            // Batas bawah tidak perlu diperiksa karena langkah 4 dimulai dari biner awal 0 (0000),
            // sehingga setiap kandidat sudah memenuhi syarat value >= 0.
            if (value.compareTo(upperExclusive) < 0) {
                return value;
            }
        }
    }
}