-- =========================================================
--  Numi · Base de datos de los paneles (MySQL 8)
--  La comparten el panel administrativo y el panel docente.
--
--  No ejecutes este archivo a mano: lo usa database/init_db.py,
--  que primero crea la base y luego estas tablas.
-- =========================================================

-- Sedes educativas conectadas a Numi
CREATE TABLE instituciones (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  nombre     VARCHAR(120) NOT NULL UNIQUE,
  comuna     VARCHAR(60)  NOT NULL,
  sedes      TINYINT UNSIGNED NOT NULL DEFAULT 1,
  estado     ENUM('Activa', 'Inactiva') NOT NULL DEFAULT 'Activa',
  creada_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Personas que entran a los paneles (docentes y administradores).
-- Los estudiantes no entran a los paneles: están en la tabla `estudiantes`.
CREATE TABLE usuarios (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(60)  NOT NULL,
  apellido        VARCHAR(60)  NOT NULL,
  correo          VARCHAR(120) NOT NULL UNIQUE,
  password_hash   VARCHAR(255) NULL,  -- NULL hasta que un administrador activa la cuenta
  rol             ENUM('Docente', 'Administrador') NOT NULL,
  institucion_id  INT NULL,           -- NULL = administrador de todas las instituciones
  sede            VARCHAR(60) NOT NULL DEFAULT 'Sede principal',
  documento       VARCHAR(20) NULL,
  estado          ENUM('Activo', 'Pendiente', 'Inactivo') NOT NULL DEFAULT 'Pendiente',
  ultimo_acceso   DATETIME NULL,
  creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_usuarios_institucion FOREIGN KEY (institucion_id) REFERENCES instituciones (id)
);

-- Materias. `clave` es la misma que guarda la app en el progreso (matematicas, español, ...)
CREATE TABLE materias (
  clave         VARCHAR(20) PRIMARY KEY,
  nombre        VARCHAR(40) NOT NULL,  -- como lo muestra el panel administrativo
  nombre_corto  VARCHAR(20) NOT NULL,  -- como lo muestra el panel docente
  carpeta       VARCHAR(20) NOT NULL,  -- carpeta de recursos: actividades/<carpeta>
  orden         TINYINT UNSIGNED NOT NULL
);

-- Grupos de una institución, con su docente y su código para que los niños se unan
CREATE TABLE grupos (
  id                   INT AUTO_INCREMENT PRIMARY KEY,
  institucion_id       INT NOT NULL,
  grado                TINYINT UNSIGNED NOT NULL,
  letra                CHAR(1) NOT NULL,
  docente_id           INT NULL,
  codigo               VARCHAR(10) NOT NULL UNIQUE,
  codigo_vence         DATE NOT NULL,
  codigo_usos          INT NOT NULL DEFAULT 0,
  codigo_usos_max      INT NOT NULL DEFAULT 30,
  ia_activada          BOOLEAN NOT NULL DEFAULT TRUE,
  paquete_version      VARCHAR(20) NOT NULL DEFAULT '2.1',
  paquete_mb           INT NOT NULL DEFAULT 340,
  paquete_actualizado  DATE NOT NULL,
  UNIQUE KEY uq_grupo (institucion_id, grado, letra),
  CONSTRAINT fk_grupos_institucion FOREIGN KEY (institucion_id) REFERENCES instituciones (id),
  CONSTRAINT fk_grupos_docente FOREIGN KEY (docente_id) REFERENCES usuarios (id) ON DELETE SET NULL
);

-- Niños que usan la app. `uid` es el identificador de Firebase que usa la app.
CREATE TABLE estudiantes (
  id                     INT AUTO_INCREMENT PRIMARY KEY,
  uid                    VARCHAR(128) NOT NULL UNIQUE,
  nombre                 VARCHAR(60) NOT NULL,
  grupo_id               INT NULL,
  racha_dias             INT NOT NULL DEFAULT 0,
  version_app            VARCHAR(10) NULL,
  ultima_sincronizacion  DATETIME NULL,
  nota_docente           TEXT NULL,
  CONSTRAINT fk_estudiantes_grupo FOREIGN KEY (grupo_id) REFERENCES grupos (id) ON DELETE SET NULL
);

-- Catálogo de actividades. `nombre` es el mismo texto que guarda la app en progreso.actividad
CREATE TABLE actividades (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  slug            VARCHAR(80) NOT NULL UNIQUE,  -- identificador para las URL (los-numeros)
  nombre          VARCHAR(120) NOT NULL,
  materia         VARCHAR(20) NOT NULL,
  grado           TINYINT UNSIGNED NOT NULL,
  tipo            VARCHAR(40) NOT NULL,
  descripcion     VARCHAR(255) NOT NULL DEFAULT '',
  estado          ENUM('Publicada', 'Borrador', 'Desactivada') NOT NULL DEFAULT 'Borrador',
  eliminada       BOOLEAN NOT NULL DEFAULT FALSE,  -- se marca, no se borra: el historial la sigue nombrando
  creada_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizada_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_actividades_materia FOREIGN KEY (materia) REFERENCES materias (clave)
);

-- Imágenes y audios que usan las actividades
CREATE TABLE recursos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(120) NOT NULL,
  tipo            ENUM('Imagen', 'Audio') NOT NULL,
  carpeta         VARCHAR(60) NOT NULL,   -- p. ej. actividades/ciencias
  emoji           VARCHAR(8) NULL,        -- miniatura que muestra el panel
  archivo         VARCHAR(255) NULL,      -- ruta del archivo subido (carpeta uploads/)
  version_minima  VARCHAR(10) NULL,       -- NULL = funciona en todas las versiones de la app
  creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_recurso (carpeta, nombre)
);

-- Qué recursos usa cada actividad (relación muchos a muchos)
CREATE TABLE actividad_recurso (
  actividad_id  INT NOT NULL,
  recurso_id    INT NOT NULL,
  PRIMARY KEY (actividad_id, recurso_id),
  CONSTRAINT fk_ar_actividad FOREIGN KEY (actividad_id) REFERENCES actividades (id) ON DELETE CASCADE,
  CONSTRAINT fk_ar_recurso FOREIGN KEY (recurso_id) REFERENCES recursos (id) ON DELETE CASCADE
);

-- El docente activa o desactiva cada actividad para su grupo. Sin fila = activa.
CREATE TABLE grupo_actividad (
  grupo_id      INT NOT NULL,
  actividad_id  INT NOT NULL,
  activa        BOOLEAN NOT NULL,
  PRIMARY KEY (grupo_id, actividad_id),
  CONSTRAINT fk_ga_grupo FOREIGN KEY (grupo_id) REFERENCES grupos (id) ON DELETE CASCADE,
  CONSTRAINT fk_ga_actividad FOREIGN KEY (actividad_id) REFERENCES actividades (id) ON DELETE CASCADE
);

-- Progreso por actividad: misma forma que el progreso de la app (gana el mayor avance)
CREATE TABLE progreso (
  estudiante_id  INT NOT NULL,
  grado          TINYINT UNSIGNED NOT NULL,
  materia        VARCHAR(20) NOT NULL,
  actividad      VARCHAR(120) NOT NULL,
  porcentaje     DECIMAL(5, 2) NOT NULL DEFAULT 0,
  intentos       INT NOT NULL DEFAULT 0,
  ultima_vez     DATETIME NULL,
  PRIMARY KEY (estudiante_id, grado, materia, actividad),
  CONSTRAINT fk_progreso_estudiante FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id) ON DELETE CASCADE,
  CONSTRAINT fk_progreso_materia FOREIGN KEY (materia) REFERENCES materias (clave)
);

-- Resultados del banco de preguntas (evaluación)
CREATE TABLE evaluaciones (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  estudiante_id  INT NOT NULL,
  materia        VARCHAR(20) NOT NULL,
  correctas      TINYINT UNSIGNED NOT NULL,
  total          TINYINT UNSIGNED NOT NULL,
  fecha          DATETIME NOT NULL,
  CONSTRAINT fk_eval_estudiante FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id) ON DELETE CASCADE,
  CONSTRAINT fk_eval_materia FOREIGN KEY (materia) REFERENCES materias (clave)
);

-- Periodos académicos para los reportes del docente
CREATE TABLE periodos (
  clave   VARCHAR(10) PRIMARY KEY,
  nombre  VARCHAR(30) NOT NULL,
  desde   DATE NOT NULL,
  hasta   DATE NOT NULL,
  orden   TINYINT UNSIGNED NOT NULL
);

-- Cada cambio guardado sobre una actividad
CREATE TABLE historial (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  actividad_id      INT NULL,
  actividad_nombre  VARCHAR(120) NOT NULL,
  cambio            VARCHAR(255) NOT NULL,
  tipo              ENUM('Publicada', 'Editada', 'Borrador', 'Desactivada', 'Eliminada') NOT NULL,
  usuario_id        INT NULL,
  fecha             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_historial_actividad FOREIGN KEY (actividad_id) REFERENCES actividades (id) ON DELETE SET NULL,
  CONSTRAINT fk_historial_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE SET NULL
);

-- Estado de los servicios del backend de la app (lo actualiza Monitoreo técnico)
CREATE TABLE servicios (
  clave         VARCHAR(20) PRIMARY KEY,
  nombre        VARCHAR(60) NOT NULL,
  operativo     BOOLEAN NULL,     -- NULL = todavía no se ha revisado
  caido_desde   DATETIME NULL,
  revisado_en   DATETIME NULL
);

-- Registro de eventos técnicos
CREATE TABLE eventos (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  nivel    ENUM('Crítico', 'Alerta', 'Info') NOT NULL,
  mensaje  VARCHAR(255) NOT NULL,
  fecha    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Informes generados desde Monitoreo técnico (el archivo se guarda en la base)
CREATE TABLE informes (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  titulo     VARCHAR(120) NOT NULL,
  formato    ENUM('CSV', 'PDF') NOT NULL,
  contenido  LONGBLOB NOT NULL,
  creado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
