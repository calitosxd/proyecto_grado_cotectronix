-- ============================================================================
-- TABLA DE USUARIOS Y ROLES UML — SISTEMA DE MONITOREO AMBIENTAL FASE 2
-- Semillero COTECTRONIX — COTECNOVA
-- Actores modelados: Administrador de BD, Investigador / Docente, Estudiante
-- ============================================================================

USE `invernadero_olap_fase2`;

-- 1. Crear tabla de usuarios del sistema
CREATE TABLE IF NOT EXISTS `seguridad_usuarios` (
    `id_usuario` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `nombre_completo` VARCHAR(100) NOT NULL,
    `password_hash` VARCHAR(128) NOT NULL,
    `salt` VARCHAR(64) NOT NULL,
    `rol` VARCHAR(50) NOT NULL COMMENT 'Administrador de BD, Investigador / Docente, Estudiante / Semillerista',
    `pregunta_seguridad` VARCHAR(255) NOT NULL COMMENT 'Pregunta privada conocida solo por el usuario',
    `respuesta_hash` VARCHAR(128) NOT NULL COMMENT 'Hash SHA-256 normalizado de la respuesta secreta',
    `respuesta_salt` VARCHAR(64) NOT NULL,
    `semillero` VARCHAR(100) DEFAULT 'COTECTRONIX',
    `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `ultimo_acceso` DATETIME NULL,
    `activo` TINYINT NOT NULL DEFAULT 1,
    INDEX `idx_usuario_username` (`username`),
    INDEX `idx_usuario_rol` (`rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Insertar usuarios iniciales precargados (Actores de los diagramas UML)
INSERT INTO `seguridad_usuarios` (
    `id_usuario`, `username`, `nombre_completo`, `password_hash`, `salt`, `rol`,
    `pregunta_seguridad`, `respuesta_hash`, `respuesta_salt`, `semillero`, `fecha_creacion`, `activo`
) VALUES 
(
    1,
    'admin',
    'Administrador de BD — COTECTRONIX',
    'd088b1cbb8740d3930c249f086d1c0d7dd151768f7c11169943891a2fae68f25',
    '627001eab7b27ffed61bc85b132a43d9',
    'Administrador de BD',
    '¿Cuál es el nombre del semillero de investigación?',
    '0640ec74aa56deb21674520aff1463d147bb8a3c3440e3eb6c795cdb95b0257b',
    '366eaea63154911166fdec0d754cf90b',
    'COTECTRONIX',
    NOW(),
    1
),
(
    2,
    'investigador',
    'Docente Investigador COTECNOVA',
    '41a34f19c2b2ac0894cb8864da680c44781fabb236fe47559a7d693bcdb4f0fa',
    '6aea6437fa5eaece68ace48fde3e20f7',
    'Investigador / Docente',
    '¿Cuál es la institución universitaria del proyecto?',
    '1ef83a894b0f8b45237869b345bf862c1698b6ce30c1acc5bb5e8c2bfcb8df8d',
    '35d8852165f82707793f9e7e7f4e3032',
    'COTECTRONIX',
    NOW(),
    1
),
(
    3,
    'estudiante',
    'Estudiante Semillerista',
    '8b05d67960a4f135cd9f2477de9714bdffe9ca66e0de0452094a993239639d8c',
    '5bdbb76255696c33e24b8b04254e68aa',
    'Estudiante / Semillerista',
    '¿Cuál es el nombre del semillero de investigación?',
    'e1edeb9e4bcdb43fe2f8800f2c6854a7dd76505f8e769988b99af29d38ff1db2',
    'b10133349dd28d6e2b4d6140a36c86ad',
    'COTECTRONIX',
    NOW(),
    1
)
ON DUPLICATE KEY UPDATE `username` = VALUES(`username`);
