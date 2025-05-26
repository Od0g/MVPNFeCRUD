// BackupService.java
package com.exemplo.nfe.service;

import org.apache.commons.io.FileUtils; // Importar FileUtils
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files; // Para criar diretórios
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import java.io.FileOutputStream;

@Service
public class BackupService {

    // Agendado para executar diariamente às 2 AM
    // Cron expression: segundo minuto hora dia-do-mes mes dia-da-semana
    @Scheduled(cron = "0 0 2 * * ?")
    public void realizarBackup() {
        System.out.println("Iniciando backup automático...");

        // Diretório de origem (onde os arquivos estão, ex: XMLs de NF-e)
        Path origemPath = Paths.get("uploads");
        File origemDir = origemPath.toFile();

        // Diretório de destino para o backup, com timestamp
        String dataBackup = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        Path destinoPath = Paths.get("backup", "nfe_" + dataBackup);
        File destinoDir = destinoPath.toFile();

        try {
            // Criar o diretório de destino se não existir
            if (!Files.exists(destinoPath)) {
                Files.createDirectories(destinoPath);
            }

            // Copiar o diretório de origem para o destino
            FileUtils.copyDirectory(origemDir, destinoDir);
            System.out.println("Backup de diretório realizado para: " + destinoPath);

            // Opcional: Compactar o diretório de backup
            String zipFileName = "backup/nfe_" + dataBackup + ".zip";
            compactarDiretorio(destinoPath, Paths.get(zipFileName));
            System.out.println("Backup compactado para: " + zipFileName);

            // Opcional: Excluir o diretório não compactado após a compactação
            FileUtils.deleteDirectory(destinoDir);
            System.out.println("Diretório de backup temporário excluído.");

            // Implementar upload para cloud aqui (AWS S3/MinIO)

        } catch (IOException e) {
            System.err.println("Erro ao realizar backup: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Compacta um diretório em um arquivo ZIP.
     * @param sourceDirPath Caminho do diretório a ser compactado.
     * @param zipFilePath Caminho do arquivo ZIP de destino.
     * @throws IOException Se ocorrer um erro de I/O.
     */
    private void compactarDiretorio(Path sourceDirPath, Path zipFilePath) throws IOException {
        try (ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(zipFilePath.toFile()))) {
            Files.walk(sourceDirPath)
                 .filter(path -> !Files.isDirectory(path)) // Ignorar diretórios
                 .forEach(path -> {
                     ZipEntry zipEntry = new ZipEntry(sourceDirPath.relativize(path).toString());
                     try {
                         zos.putNextEntry(zipEntry);
                         Files.copy(path, zos);
                         zos.closeEntry();
                     } catch (IOException e) {
                         System.err.println("Erro ao adicionar arquivo ao ZIP: " + path + " - " + e.getMessage());
                     }
                 });
        }
    }
}