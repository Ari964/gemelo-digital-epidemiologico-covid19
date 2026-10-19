# Auditoría Rigurosa de Procedencia de Datos: Dataset Nacional y Ámbito Condal

## 1. Distinción Fundamental de Fuentes y Alcances

En el marco metodológico del proyecto **GD_TI**, se establece una separación estricta e infranqueable entre dos niveles de información:

| Nivel de Información | Dataset / Fuente | Cobertura Temporal | Estado de Validación | Naturaleza del Dato |
| :--- | :--- | :--- | :--- | :--- |
| **Nacional Agregado (KEN, code=0)** | Our World in Data (OWID) / OMS / MoH Kenya | Marzo 2020 a Agosto 2024 (semanal y diario) | **100% Empírico Verificado** (SHA-256 verificado, CC-BY 4.0) | Serie temporal dinámica utilizada para entrenamiento, validación y prueba de los modelos predictivos (`Baseline_Naive_Persistence`, `Candidate_Random_Forest`, `Ridge`). |
| **Demografía Subnacional (47 Condados)** | Censo KNBS 2019 (*Kenya National Bureau of Statistics*) | Censo oficial Agosto 2019 | **100% Verificado Oficial** (Vol. I, Tabla 2.2) | Datos estáticos de población y superficie por condado, utilizados para inicialización del SEIR metapoblacional y descriptores de escala. |
| **Infraestructura Hospitalaria Condal (UCI)** | Barasa, Ouma & Okiro (2020) *PLOS ONE* / KMFL | Relevamiento hospitalario 2020 | **Condición de «Verificada» RETIRADA** | Descriptivo no verificado. Las cifras previas del prototipo (Nairobi: 160, Kiambu: 24, Nakuru: 18, Mombasa: 40) **no coinciden** con el material suplementario abierto del estudio publicado. Se clasifican como **descriptivo no verificado**. |
| **Quintiles Socioeconómicos por Condado** | KDHS 2022 (*Kenya Demographic and Health Survey*) | Encuesta 2022 | **Estimación No Verificada en Tabla Abierta** | Proporciones referenciales no tabuladas como matrices condales $Q_1..Q_5$ en los informes abiertos finales. Se etiquetan formalmente como **no verificadas**. |

---

## 2. Dataset Epidemiológico Nacional (OWID / OMS)

- **Institución responsable:** Our World in Data (Universidad de Oxford) en colaboración con la Organización Mundial de la Salud (OMS) y el Ministerio de Salud de Kenia (*Ministry of Health - MoH*).
- **Enlace de descarga oficial:** [https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv](https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv)
- **Portal de referencia:** [https://ourworldindata.org/coronavirus](https://ourworldindata.org/coronavirus)
- **Licencia:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Ruta local:** `data/raw/owid_covid_kenya_raw.csv`
- **Hash de integridad criptográfica:** SHA-256: `c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba`.
- **Variables utilizadas:**
  - `new_cases`: Casos positivos diarios y agregación semanal dominical (`target_weekly_cases`).
  - `new_deaths`: Muertes reportadas.
  - `stringency_index`: Índice de rigor de la Universidad de Oxford (Blavatnik School of Government; cesó recolección el 31/12/2022).
  - `reproduction_rate`: Tasa de reproducción efectiva estimada.

---

## 3. Demografía Oficial de los 47 Condados (KNBS Censo 2019)

- **Institución responsable:** Kenya National Bureau of Statistics (KNBS).
- **Publicación oficial:** *2019 Kenya Population and Housing Census. Volume I: Population by County and Sub-County*.
- **Tabla de origen:** **Tabla 2.2: Distribution of Population by Sex, Number of Households, Land Area and Population Density by County** (páginas 20–25).
- **Enlace oficial de consulta:** [https://www.knbs.or.ke/2019-kenya-population-and-housing-census-results/](https://www.knbs.or.ke/2019-kenya-population-and-housing-census-results/)
- **Población total censada de Kenia (2019):** 47,564,296 habitantes.
- **Verificación:** Los 47 condados en `backend/app/data/kenya_47_counties_verified.json` coinciden unívocamente en `population_2019` y `area_sq_km` con la Tabla 2.2 del informe oficial.

---

## 4. Auditoría de Camas UCI: Inspección del Material Suplementario de Barasa et al. (2020)

### 4.1 Identificación y Corrección del Artículo Pertinente
- **Corrección de Referencia Errónea:** En borradores preliminares se citó equivocadamente el DOI `10.1371/journal.pone.0241954`, el cual corresponde a una investigación sobre Ciudad de México (Arroyo-Quiroz et al., 2020). Dicha cita queda **anulada y retirada**.
- **Artículo Científico Pertinente:**
  - **Autores:** Edwine W. Barasa, Paul O. Ouma, Emelda A. Okiro.
  - **Título:** *Assessing the hospital surge capacity of the Kenyan health system in the face of the COVID-19 pandemic*.
  - **Revista:** *PLOS ONE*, 15(7): e0236308 (Publicado el 20 de julio de 2020).
  - **DOI oficial:** [https://doi.org/10.1371/journal.pone.0236308](https://doi.org/10.1371/journal.pone.0236308)
  - **Identificador PubMed Central:** PMCID PMC7371197.
  - **Material Suplementario Directo:** Archivo `pone.0236308.s001.docx`, denominado formalmente:  
    **«S1 Table. Data on hospital, ICU beds, and ventilators in Kenya»** ([https://doi.org/10.1371/journal.pone.0236308.s001](https://doi.org/10.1371/journal.pone.0236308.s001)).

---

### 4.2 Estructura de la Tabla Suplementaria S1 de Barasa et al. (2020)

La tabla suplementaria `S1 Table` del artículo presenta 47 filas de datos (una por cada condado de Kenia) y 13 columnas organizadas en tres bloques:
- **Columna 1:** `County` (Nombre del condado).
- **Columnas 2 a 5:** `General hospital beds*` (Public facilities, For profit facilities, Faith based facilities, Total).
- **Columnas 6 a 9:** `ICU Beds**` (Public facilities, For profit facilities, Faith based facilities, Total).
- **Columnas 10 a 13:** `Ventilators**` (Public facilities, For profit facilities, Faith based facilities, Total).

---

### 4.3 Cotejo Forense Celda por Celda: Cifras Previas vs. S1 Table

A continuación se detalla la comprobación exacta entre las cifras mostradas en la maqueta inicial del sistema y los datos reales tabulados en `S1 Table`:

| Condado | Cifra Mostrada en Prototipo | Fila en `S1 Table` | Columna en `S1 Table` | Valor Real en `S1 Table` (Desglose por Sector) | ¿Coincide la Cifra? | Veredicto Científico |
| :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| **Nairobi City** (Code 47) | **160** | **Fila 32** (*Nairobi*) | **Col. 9** (*ICU Beds Total*) | **276 camas**<br>(Col. 6 Pública: 99, Col. 7 Privada: 137, Col. 8 Religiosa: 40)<br>*Ventiladores Total (Col. 13): 167* | **NO** (160 $\neq$ 276) | **NO VERIFICADA.** La cifra 160 no figura en ninguna columna de la fila 32. Se retira su calificación de verificada. |
| **Kiambu** (Code 22) | **24** | **Fila 15** (*Kiambu*) | **Col. 9** (*ICU Beds Total*) | **16 camas**<br>(Col. 6 Pública: 11, Col. 7 Privada: 0, Col. 8 Religiosa: 5)<br>*Ventiladores Total (Col. 13): 4* | **NO** (24 $\neq$ 16) | **NO VERIFICADA.** Barasa et al. registran exactamente 16 camas totales. La cifra 24 corresponde a Bungoma (Fila 5). Se retira la condición de verificada. |
| **Nakuru** (Code 32) | **18** | **Fila 33** (*Nakuru*) | **Col. 9** (*ICU Beds Total*) | **20 camas**<br>(Col. 6 Pública: 6, Col. 7 Privada: 14, Col. 8 Religiosa: 0)<br>*Ventiladores Total (Col. 13): 8* | **NO** (18 $\neq$ 20) | **NO VERIFICADA.** Barasa et al. registran 20 camas totales. La cifra 18 no coincide. Se retira la condición de verificada. |
| **Mombasa** (Code 1) | **40** (o 23) | **Fila 30** (*Mombasa*) | **Col. 9** (*ICU Beds Total*) | **35 camas**<br>(Col. 6 Pública: 12, Col. 7 Privada: 23, Col. 8 Religiosa: 0)<br>*Ventiladores Total (Col. 13): 17* | **NO** (40 $\neq$ 35) | **NO VERIFICADA.** Barasa et al. registran 35 camas totales. 23 corresponde únicamente al sector privado. 40 no existe. Se retira la condición de verificada. |
| **Bungoma** (Code 39) | *8 (en prototipo)* | **Fila 5** (*Bungoma*) | **Col. 9** (*ICU Beds Total*) | **24 camas** (Col. 7 Privada: 24, Pública: 0) | **NO** | **NO VERIFICADA.** |
| **Kisumu** (Code 42) | *22 (en prototipo)* | **Fila 19** (*Kisumu*) | **Col. 9** (*ICU Beds Total*) | **23 camas** (Pública: 11, Privada: 12) | **NO** | **NO VERIFICADA.** |
| **Uasin Gishu** (Code 27) | *30 (en prototipo)* | **Fila 46** (*Uasin Gishu*) | **Col. 9** (*ICU Beds Total*) | **59 camas** (Pública: 0, Privada/Otros: 59) | **NO** | **NO COINCIDE.** Se actualiza al valor oficial S1 Table (59). |
| **25 Condados sin UCI** | *Valores > 0 arbitrarios* | **Filas 3, 4, 6, 7, etc.** | **Col. 9** (*ICU Beds Total*) | **0 camas** | **NO** | **NO COINCIDE.** Se corrigen a 0 formalmente conforme a S1 Table. |

---

### 4.4 Tabla Maestra de Correspondencia Fila-Columna para los 47 Condados (`S1 Table`)

El archivo fuente oficial (`pone.0236308.s001.docx`) y su exportación tabular estructurada (`barasa_2020_surge_capacity_s1_table.csv`) se conservan íntegramente en la carpeta `data/raw/`. La correspondencia inequívoca para cada uno de los 47 condados entre el código del sistema y la tabla suplementaria de Barasa et al. (2020) es la siguiente:

| Código | Condado (KNBS 2019) | Fila en `S1 Table` (Docx) | Nombre en `S1 Table` | Columna en `S1 Table` | Camas UCI Oficiales (Total) | Desglose por Sector en S1 Table |
| :---: | :--- | :---: | :--- | :---: | :---: | :--- |
| **1** | Mombasa | Fila 30 (Dato #28) | *Mombasa* | Col. 9 (*ICU Beds Total*) | **35** | Pública: 12, Privada: 23, FBO: 0 |
| **2** | Kwale | Fila 21 (Dato #19) | *Kwale* | Col. 9 (*ICU Beds Total*) | **6** | Pública: 6, Privada: 0, FBO: 0 |
| **3** | Kilifi | Fila 16 (Dato #14) | *Kilifi* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **4** | Tana River | Fila 42 (Dato #40) | *Tana River* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **5** | Lamu | Fila 23 (Dato #21) | *Lamu* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **6** | Taita-Taveta | Fila 41 (Dato #39) | *Taita Taveta* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **7** | Garissa | Fila 9 (Dato #7) | *Garissa* | Col. 9 (*ICU Beds Total*) | **6** | Pública: 6, Privada: 0, FBO: 0 |
| **8** | Wajir | Fila 48 (Dato #46) | *Wajir* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **9** | Mandera | Fila 26 (Dato #24) | *Mandera* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **10** | Marsabit | Fila 27 (Dato #25) | *Marsabit* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **11** | Isiolo | Fila 11 (Dato #9) | *Isiolo* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **12** | Meru | Fila 28 (Dato #26) | *Meru* | Col. 9 (*ICU Beds Total*) | **2** | Pública: 0, Privada: 0, FBO: 2 |
| **13** | Tharaka-Nithi | Fila 43 (Dato #41) | *Tharaka-Nithi* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **14** | Embu | Fila 8 (Dato #6) | *Embu* | Col. 9 (*ICU Beds Total*) | **5** | Pública: 5, Privada: 0, FBO: 0 |
| **15** | Kitui | Fila 20 (Dato #18) | *Kitui* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **16** | Machakos | Fila 24 (Dato #22) | *Machakos* | Col. 9 (*ICU Beds Total*) | **5** | Pública: 5, Privada: 0, FBO: 0 |
| **17** | Makueni | Fila 25 (Dato #23) | *Makueni* | Col. 9 (*ICU Beds Total*) | **4** | Pública: 4, Privada: 0, FBO: 0 |
| **18** | Nyandarua | Fila 37 (Dato #35) | *Nyandarua* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **19** | Nyeri | Fila 38 (Dato #36) | *Nyeri* | Col. 9 (*ICU Beds Total*) | **15** | Pública: 6, Privada: 4, FBO: 5 |
| **20** | Kirinyaga | Fila 17 (Dato #15) | *Kirinyaga* | Col. 9 (*ICU Beds Total*) | **4** | Pública: 4, Privada: 0, FBO: 0 |
| **21** | Murang'a | Fila 31 (Dato #29) | *Murang'a* | Col. 9 (*ICU Beds Total*) | **3** | Pública: 0, Privada: 0, FBO: 3 |
| **22** | Kiambu | Fila 15 (Dato #13) | *Kiambu* | Col. 9 (*ICU Beds Total*) | **16** | Pública: 11, Privada: 0, FBO: 5 |
| **23** | Turkana | Fila 45 (Dato #43) | *Turkana* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 20, Privada: 36, FBO: 3 |
| **24** | West Pokot | Fila 49 (Dato #47) | *West Pokot* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **25** | Samburu | Fila 39 (Dato #37) | *Samburu* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **26** | Trans Nzoia | Fila 44 (Dato #42) | *Trans Nzoia* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **27** | Uasin Gishu | Fila 46 (Dato #44) | *Uasin Gishu* | Col. 9 (*ICU Beds Total*) | **59** | Pública: 0, Privada: 0, FBO: 0 |
| **28** | Elgeyo-Marakwet | Fila 7 (Dato #5) | *Elgeyo-Marakwet* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **29** | Nandi | Fila 34 (Dato #32) | *Nandi* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **30** | Baringo | Fila 3 (Dato #1) | *Baringo* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **31** | Laikipia | Fila 22 (Dato #20) | *Laikipia* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **32** | Nakuru | Fila 33 (Dato #31) | *Nakuru* | Col. 9 (*ICU Beds Total*) | **20** | Pública: 6, Privada: 14, FBO: 0 |
| **33** | Narok | Fila 35 (Dato #33) | *Narok* | Col. 9 (*ICU Beds Total*) | **6** | Pública: 6, Privada: 0, FBO: 0 |
| **34** | Kajiado | Fila 12 (Dato #10) | *Kajiado* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **35** | Kericho | Fila 14 (Dato #12) | *Kericho* | Col. 9 (*ICU Beds Total*) | **5** | Pública: 5, Privada: 0, FBO: 0 |
| **36** | Bomet | Fila 4 (Dato #2) | *Bomet* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **37** | Kakamega | Fila 13 (Dato #11) | *Kakamega* | Col. 9 (*ICU Beds Total*) | **9** | Pública: 9, Privada: 0, FBO: 0 |
| **38** | Vihiga | Fila 47 (Dato #45) | *Vihiga* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **39** | Bungoma | Fila 5 (Dato #3) | *Bungoma* | Col. 9 (*ICU Beds Total*) | **24** | Pública: 0, Privada: 24, FBO: 0 |
| **40** | Busia | Fila 6 (Dato #4) | *Busia* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **41** | Siaya | Fila 40 (Dato #38) | *Siaya* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **42** | Kisumu | Fila 19 (Dato #17) | *Kisumu* | Col. 9 (*ICU Beds Total*) | **23** | Pública: 11, Privada: 12, FBO: 0 |
| **43** | Homa Bay | Fila 10 (Dato #8) | *Homa Bay* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **44** | Migori | Fila 29 (Dato #27) | *Migori* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **45** | Kisii | Fila 18 (Dato #16) | *Kisii* | Col. 9 (*ICU Beds Total*) | **14** | Pública: 9, Privada: 5, FBO: 0 |
| **46** | Nyamira | Fila 36 (Dato #34) | *Nyamira* | Col. 9 (*ICU Beds Total*) | **0** | Pública: 0, Privada: 0, FBO: 0 |
| **47** | Nairobi City | Fila 32 (Dato #30) | *Nairobi* | Col. 9 (*ICU Beds Total*) | **276** | Pública: 99, Privada: 137, FBO: 40 |

**Total Nacional de Camas UCI en Kenia según S1 Table:** **537 camas** (concentradas en 20 condados; los 27 condados restantes carecían de camas UCI según el censo auditado).

---

### 4.5 Retiro de Quintiles de Pobreza no Verificados y Reclasificación de Datasets

1. **Eliminación de Quintiles sin Respaldo:** Al no contarse en este repositorio con microdatos abiertos auditados de la encuesta KDHS 2022 desagregados por condado, se eliminaron totalmente las cifras de quintiles (`poverty_quintiles = null`) en el archivo JSON operativo (`kenya_47_counties_verified.json`), la base relacional SQLite (`CountyDB.q1_pct = null`), y la API REST (`/api/v1/counties`).
2. **Reclasificación de `ds-kdhs-2022`:** Se retiró formalmente el estado de `VERIFIED` al dataset `ds-kdhs-2022`. El dataset se reclasificó como `quality_status = "WARNING"` y `source_type = "ESTIMATED"`, dejando constancia de que ningún conjunto con valores estimados sin respaldo puede ostentar la etiqueta de verificado.
3. **Eliminación de Fallbacks Codificados:** Se eliminaron todos los diccionarios de respaldo codificados en duro en el asistente de datos (`data_assistant.py`) y en el agente (`langchain_agent.py`) que inyectaban valores arbitrarios (e.g. `{name: "Nairobi City", icu_beds: 160}`). Si la base no tiene registros, el sistema retorna listas vacías o valores `null`.
4. **Imposibilidad de Inferir Saturación:** Al no disponer de un modelo dinámico de derivación clínica de camas en tiempo real, se mantiene la estricta prohibición epistemológica de inferir saturación o colapso condal a partir de las proyecciones epidemiológicas nacionales.
