import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.Arrays;

public class Encryption {
    // Satu byte memiliki 2^8 = 256 kemungkinan nilai.
    private static final BigInteger BYTE_BASE = BigInteger.valueOf(256);

    // Membangkitkan bilangan acak yang sulit ditebak menggunakan SecureRandom.
    private static final SecureRandom random = new SecureRandom();

    public static int calculatePlaintextChunkSize(BigInteger p) {
        // ElGamal mengenkripsi bilangan bulat P dalam interval 0 <= P < p.
        // Jika seluruh byte pesan dibaca sebagai satu bilangan, nilainya dapat mencapai atau melebihi p.
        // Karena itu, byte pesan dibagi menjadi beberapa potongan, yang disebut chunk.
        // Metode ini menentukan jumlah byte terbanyak per chunk agar setiap nilainya tetap kurang dari p.

        // Satu byte dapat menyatakan nilai 0 sampai 255. Jika k byte digabungkan,
        // nilai terbesarnya adalah 256^k - 1.
        // Agar nilai tersebut kurang dari p, ukuran chunk harus memenuhi 256^k <= p.

        // Contoh, p = 65537:
        // -> 2 byte dapat menyatakan nilai sampai 256^2 - 1 = 65535, yang masih kurang dari p.
        // -> 3 byte dapat menyatakan nilai sampai 256^3 - 1 = 16777215, yang melebihi p.
        // Jadi, ukuran chunk dipilih sebesar 2 byte.

        // 1. Memastikan p cukup besar untuk memuat seluruh kemungkinan nilai satu byte, yaitu 0 sampai 255.
        if (p == null || p.compareTo(BYTE_BASE) < 0) {
            throw new IllegalArgumentException("[Encryption.calculatePlaintextChunkSize.INVALID_P] p harus bernilai minimal 256 agar dapat memuat satu byte.");
        }

        // 2. Memulai perhitungan dari ukuran 0 byte. limit menyimpan nilai 256^chunkSize.
        int chunkSize = 0;
        BigInteger limit = BigInteger.ONE;

        // 3. Menambah ukuran satu byte selama 256^(chunkSize + 1) masih tidak melebihi p.
        while (limit.multiply(BYTE_BASE).compareTo(p) <= 0) {
            limit = limit.multiply(BYTE_BASE);
            chunkSize++;
        }

        return chunkSize;
    }

    public static BigInteger[] createPlaintextChunks(byte[] plaintextBytes, int chunkSize) {
        // Memotong deretan byte pesan menjadi beberapa chunk, lalu membaca setiap chunk sebagai bilangan bulat.
        // Setiap byte menempati satu posisi pada bilangan berbasis 256.
        // Contoh, dua byte bernilai 1 dan 2 dibaca sebagai 1 x 256 + 2 = 258.
        // Byte di sebelah kiri memiliki nilai posisi lebih besar, seperti digit kiri pada bilangan desimal.

        // 1. Memastikan deretan byte pesan tidak null.
        if (plaintextBytes == null) {
            throw new IllegalArgumentException("[Encryption.createPlaintextChunks.NULL_PLAINTEXT] Plaintext tidak boleh null.");
        }

        // 2. Memastikan setiap chunk dapat memuat setidaknya satu byte.
        if (chunkSize < 1) {
            throw new IllegalArgumentException("[Encryption.createPlaintextChunks.INVALID_CHUNK_SIZE] Ukuran chunk harus bernilai positif.");
        }

        // 3. Menghitung jumlah chunk. Pesan kosong menghasilkan 0 chunk.
        // Bagian terakhir tetap dihitung sebagai satu chunk meskipun jumlah bytenya kurang dari chunkSize.
        int chunkCount = plaintextBytes.length == 0
                ? 0
                : (plaintextBytes.length - 1) / chunkSize + 1;
        BigInteger[] plaintextChunks = new BigInteger[chunkCount];

        // 4. Mengambil byte untuk setiap chunk, kemudian mengubahnya menjadi BigInteger.
        for (int i = 0; i < plaintextChunks.length; i++) {
            // start adalah indeks byte pertama, sedangkan end adalah batas akhir dari pesan yang tidak ikut disalin.
            // Math.min memastikan batas pengambilan tidak melewati akhir pesan.
            int start = i * chunkSize;
            int end = Math.min(start + chunkSize, plaintextBytes.length);
            byte[] chunkBytes = Arrays.copyOfRange(plaintextBytes, start, end);

            // Angka 1 meminta BigInteger membaca byte sebagai bilangan non-negatif,
            // sehingga bit paling kiri tidak dipakai sebagai tanda bilangan negatif.
            plaintextChunks[i] = new BigInteger(1, chunkBytes);
        }

        return plaintextChunks;
    }

    public static BigInteger generateSecretRandomNumber(BigInteger p) {
        // Memilih bilangan acak rahasia r yang digunakan pada perpangkatan C1 dan C2.
        // Pengambilan r diulang untuk setiap chunk agar pesan yang sama dapat menghasilkan ciphertext berbeda.
        // Nilai r tidak dikirim sebagai bagian dari ciphertext.
        // Pada implementasi ini, r dipilih dari 2 sampai p - 2, atau 1 < r < p - 1.

        // 1. Memastikan p bernilai minimal 5.
        if (p == null || p.compareTo(BigInteger.valueOf(5)) < 0) {
            throw new IllegalArgumentException("[Encryption.generateSecretRandomNumber.INVALID_P] p harus bernilai minimal 5.");
        }

        // 2. Mengambil angka acak dari 0 sampai p - 4 menggunakan batas atas p - 3.
        // Penambahan 2 menggeser rentang tersebut menjadi 2 sampai p - 2.
        return RandomNumberGenerator.generateUniformRandomInteger(
                p.subtract(BigInteger.valueOf(3)), random
        ).add(BigInteger.TWO);
    }

    public static BigInteger[][] encrypt(byte[] plaintextBytes, BigInteger e1, BigInteger e2, BigInteger p) {
        // Mengenkripsi byte pesan menggunakan kunci publik penerima, yaitu (e1, e2, p).
        // Nilai e1 adalah basis perpangkatan, p adalah modulus prima,
        // dan e2 = e1^d mod p, dengan d sebagai kunci privat penerima.

        // Pesan dibagi menjadi chunk dan setiap chunk dibaca sebagai bilangan P yang kurang dari p.
        // Untuk setiap P, pengirim mengambil r secara acak, lalu menghitung:
        // C1 = e1^r mod p.
        // C2 = (e2^r x P) mod p.
        // Kedua angka tersebut disimpan sebagai pasangan {C1, C2}, satu pasangan untuk setiap chunk.

        // 1. Memastikan seluruh bagian kunci publik tidak null.
        if (e1 == null || e2 == null || p == null) {
            throw new IllegalArgumentException("[Encryption.encrypt.NULL_KEY_VALUE] e1, e2, dan p tidak boleh null.");
        }

        // 2. Memastikan e1 dan e2 berada dalam interval 0 < nilai < p.
        if (e1.signum() <= 0 || e1.compareTo(p) >= 0
                || e2.signum() <= 0 || e2.compareTo(p) >= 0) {
            throw new IllegalArgumentException("[Encryption.encrypt.INVALID_PUBLIC_KEY] e1 dan e2 harus berada pada interval 0 < nilai < p.");
        }

        // 3. Menentukan ukuran chunk, lalu membentuk bilangan pesan untuk setiap chunk.
        int chunkSize = calculatePlaintextChunkSize(p);
        BigInteger[] plaintextChunks = createPlaintextChunks(plaintextBytes, chunkSize);

        // 4. Menyiapkan satu baris untuk setiap chunk, dengan dua tempat untuk C1 dan C2.
        BigInteger[][] ciphertext = new BigInteger[plaintextChunks.length][2];

        // 5. Mengenkripsi setiap chunk dengan pengambilan r pada masing-masing perhitungan.
        for (int i = 0; i < plaintextChunks.length; i++) {
            BigInteger r = generateSecretRandomNumber(p);

            // Menghitung C1 = e1^r mod p.
            BigInteger c1 = ModularArithmetic.modularExponentiation(e1, r, p);

            // sharedSecret menyimpan hasil e2^r mod p, yaitu pengali untuk menyamarkan bilangan pesan P.
            BigInteger sharedSecret = ModularArithmetic.modularExponentiation(e2, r, p);
            BigInteger c2 = sharedSecret.multiply(plaintextChunks[i]).mod(p);

            // Kolom 0 menyimpan C1 dan kolom 1 menyimpan C2 untuk chunk ke-i.
            ciphertext[i][0] = c1;
            ciphertext[i][1] = c2;
        }

        return ciphertext;
    }
}
