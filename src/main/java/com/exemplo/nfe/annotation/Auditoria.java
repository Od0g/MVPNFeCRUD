package com.exemplo.nfe.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Anotação personalizada para marcar métodos que devem ser auditados.
 * Permite adicionar uma descrição da ação auditada.
 */
@Target(ElementType.METHOD) // A anotação pode ser usada em métodos
@Retention(RetentionPolicy.RUNTIME) // A anotação estará disponível em tempo de execução
public @interface Auditoria {
    String descricao() default ""; // Opcional: para adicionar uma descrição mais detalhada da ação
}
