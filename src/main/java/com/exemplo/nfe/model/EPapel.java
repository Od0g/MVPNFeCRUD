package com.exemplo.nfe.model;

public enum EPapel {
    ADMIN,
    USUARIO, // Pode ser o papel padrão para usuários operacionais
    RELATORIOS_GERAR, // Adicionado para permissão de relatórios
    NFE_EXPORTAR,
    OPERACIONAL // Adicionado para clareza se você quiser um papel distinto
}
