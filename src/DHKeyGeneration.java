import java.math.BigInteger;
import java.security.SecureRandom;

public class DHKeyGeneration {
    // Ukuran ini dipilih agar demonstrasi manual tetap cepat dijalankan.
    // Untuk penggunaan nyata, ElGamal memerlukan parameter yang lebih besar dan format ciphertext yang terautentikasi.
    private static final int PRIME_BIT_LENGTH = 256;

    // Jumlah putaran yang diminta untuk setiap pengujian Miller-Rabin.
    private static final int PRIMALITY_ROUNDS = 25;

    // Membangkitkan bilangan acak yang sulit ditebak menggunakan SecureRandom.
    private static final SecureRandom random = new SecureRandom();

    // Menyimpan modulus p, komponen publik e1 dan e2, serta kunci privat d dalam satu paket.
    public record KeyPair(BigInteger p, BigInteger e1, BigInteger e2, BigInteger d) {
    }

    public static KeyPair generateKeyPair() {
        // Membentuk kunci publik (e1, e2, p) dan kunci privat d.
        // Seperti pada struktur perpangkatan Diffie-Hellman, e1 dan p bersifat publik,
        // sedangkan d dirahasiakan dan digunakan untuk menghitung e2 = e1^d mod p.

        // Modulus p dipilih dalam bentuk p = 2q + 1, dengan p dan q prima. Bentuk ini disebut safe prime.
        // Kita membangkitkan q terlebih dahulu, kemudian menguji apakah 2q + 1 juga prima.
        // q dipilih sepanjang PRIME_BIT_LENGTH - 1 bit agar p memiliki panjang PRIME_BIT_LENGTH bit.
        // Pengujian keduanya menggunakan Miller-Rabin, sehingga hasilnya tetap berupa probable prime.

        // 1. Mengulang pembentukan q dan p sampai keduanya lolos pengujian.
        BigInteger q;
        BigInteger p;

        do {
            q = PrimalityTest.generatePrime(PRIME_BIT_LENGTH - 1, PRIMALITY_ROUNDS);
            p = q.multiply(BigInteger.TWO).add(BigInteger.ONE);
        } while (!PrimalityTest.isPrime(p, PRIMALITY_ROUNDS));

        // 2. Memilih e1 sebagai generator, yaitu basis yang pangkat-pangkatnya modulo p
        // dapat menghasilkan seluruh bilangan dari 1 sampai p - 1.
        // Pada modulus prima, pangkat terkecil yang menghasilkan sisa 1 harus membagi p - 1.
        // Karena p - 1 = 2q, pilihannya adalah 1, 2, q, atau 2q.
        // Jika e1^2 dan e1^q belum bersisa 1, pangkat terkecil tersebut harus 2q, yaitu p - 1.

        // Contoh, p = 23 dan q = 11:
        // -> 5^2 mod 23 = 2.
        // -> 5^11 mod 23 = 22.
        // Kedua hasil bukan 1, sehingga 5 dapat dipilih sebagai generator untuk modulus 23.
        BigInteger e1;

        do {
            // Mengambil e1 dari 2 sampai p - 2.
            e1 = RandomNumberGenerator.generateUniformRandomInteger(p.subtract(BigInteger.valueOf(3)), random).add(BigInteger.TWO);
        } while (ModularArithmetic.modularExponentiation(e1, BigInteger.TWO, p).equals(BigInteger.ONE) || ModularArithmetic.modularExponentiation(e1, q, p).equals(BigInteger.ONE));

        // 3. Memilih kunci privat d secara acak dari 2 sampai p - 2, atau 1 < d < p - 1.
        BigInteger d = RandomNumberGenerator.generateUniformRandomInteger(p.subtract(BigInteger.valueOf(3)), random).add(BigInteger.TWO);

        // 4. Menghitung komponen publik e2 dari e1 dan kunci privat d.
        BigInteger e2 = ModularArithmetic.modularExponentiation(e1, d, p);

        return new KeyPair(p, e1, e2, d);
    }
}
