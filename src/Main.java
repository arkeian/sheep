import java.io.IOException;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        // Menjalankan seluruh proses: membaca file, membentuk kunci, mengenkripsi, lalu mengembalikan pesan.
        // Lokasi file diberikan ketika program dijalankan, misalnya: java Main pesan.txt.

        // 1. Memastikan pengguna memberikan tepat satu lokasi file.
        if (args.length != 1) {
            System.out.println("[Main.main.INVALID_ARGUMENT_COUNT] Penggunaan: java Main <path-file-teks>");
            return;
        }

        try {
            // 2. Membaca seluruh byte file dan memeriksa apakah isinya dapat dibaca sebagai teks UTF-8.
            // Byte asli digunakan untuk enkripsi, sedangkan bentuk teksnya digunakan untuk tampilan.
            Path inputPath = Path.of(args[0]);
            byte[] plaintextBytes = Files.readAllBytes(inputPath);
            String plaintext = Decryption.decodeUtf8(plaintextBytes);

            // 3. Membentuk kunci, lalu menentukan jumlah byte per chunk berdasarkan modulus p.
            DHKeyGeneration.KeyPair keyPair = DHKeyGeneration.generateKeyPair();
            int chunkSize = Encryption.calculatePlaintextChunkSize(keyPair.p());

            // 4. Mengenkripsi byte pesan menggunakan kunci publik (e1, e2, p).
            // Hasilnya berupa pasangan {C1, C2} untuk setiap chunk.
            BigInteger[][] ciphertext = Encryption.encrypt(
                    plaintextBytes, keyPair.e1(), keyPair.e2(), keyPair.p()
            );

            // 5. Memulihkan pesan menggunakan kunci privat d.
            // Ukuran chunk dan panjang byte semula diperlukan untuk mengembalikan byte nol
            // di awal chunk serta panjang chunk terakhir.
            byte[] decryptedBytes = Decryption.decrypt(
                    ciphertext, keyPair.d(), keyPair.p(), chunkSize, plaintextBytes.length
            );
            String decryptedText = Decryption.decodeUtf8(decryptedBytes);

            // 6. Membandingkan seluruh byte hasil dekripsi dengan byte file semula.
            // Pemeriksaan ini juga mencakup byte nol yang mungkin tidak terlihat pada tampilan teks.
            if (!Arrays.equals(plaintextBytes, decryptedBytes)) {
                throw new IllegalStateException("[Main.main.DECRYPTION_MISMATCH] Hasil dekripsi tidak sama dengan isi file semula.");
            }

            // 7. Menampilkan parameter, kunci, pesan semula, ciphertext, dan hasil dekripsi.
            printResult(inputPath, plaintext, keyPair, chunkSize, ciphertext, decryptedText);
        } catch (IOException exception) {
            // Melaporkan kegagalan membaca file.
            System.err.println("[Main.main.FILE_READ_ERROR] File tidak dapat dibaca: " + exception.getMessage());
        } catch (IllegalArgumentException | IllegalStateException | ArithmeticException exception) {
            // Melaporkan data yang tidak sesuai atau kegagalan selama proses perhitungan.
            System.err.println("[Main.main.PROCESSING_ERROR] Program dihentikan: " + exception.getMessage());
        }
    }

    private static void printResult(Path inputPath, String plaintext, DHKeyGeneration.KeyPair keyPair, int chunkSize, BigInteger[][] ciphertext, String decryptedText) {
        // Menampilkan hasil seluruh tahap demonstrasi.
        // Nilai kunci turut ditampilkan agar parameter yang digunakan dapat diamati.
        System.out.println("File input       : " + inputPath.toAbsolutePath());
        System.out.println("Ukuran chunk     : " + chunkSize + " byte");
        System.out.println("Jumlah chunk     : " + ciphertext.length);
        System.out.println("p                : " + keyPair.p());
        System.out.println("e1               : " + keyPair.e1());
        System.out.println("e2               : " + keyPair.e2());
        System.out.println("d (kunci privat) : " + keyPair.d());
        System.out.println();
        System.out.println("Plaintext:");
        System.out.println(plaintext);
        System.out.println();
        System.out.println("Ciphertext (C1, C2):");

        // Satu baris menampilkan pasangan C1 dan C2 untuk satu chunk, sesuai urutan pesan.
        for (int i = 0; i < ciphertext.length; i++) {
            System.out.println((i + 1) + ". (" + ciphertext[i][0] + ", " + ciphertext[i][1] + ")");
        }

        System.out.println();
        System.out.println("Hasil dekripsi:");
        System.out.println(decryptedText);
    }
}
