# Instruccions per usar el Mapa de Calor

## Descripció

El mapa de calor compara les preferències de l'usuari (generades per la IA) amb cada zona de Los Ángeles, mostrant visualment les àrees més adequades segons les seves necessitats.

## Com usar

### 1. Generar Vector de Preferències

Al panel esquerre "AI Assistant":

1. Escriu una descripció de les teves necessitats (exemple: "Sóc estudiant, necessito una zona tranquil·la amb bon internet i a prop de universitats")
2. Fes clic a "Generate"
3. La IA generarà un vector de 11 valors que representa les teves preferències

### 2. Visualitzar el Mapa de Calor

1. Després de generar el vector, el mapa de calor es carrega automàticament
2. Al panel dret "Filtres", fes clic a "Mostrar Mapa de Calor"
3. El mapa mostrarà colors que indiquen la coincidència:
   - **Blau**: Baixa coincidència (30-40%)
   - **Cian**: Coincidència baixa-mitjana (40-50%)
   - **Verd**: Coincidència mitjana (50-60%)
   - **Groc-Verd**: Bona coincidència (60-70%)
   - **Groc**: Molt bona coincidència (70-80%)
   - **Taronja**: Coincidència excel·lent (80-90%)
   - **Vermell**: Coincidència perfecta (90-100%)

### 3. Explorar Resultats

- Fes clic en qualsevol àrea coloreada per veure el percentatge exacte de coincidència
- Les zones que no es mostren tenen menys del 30% de coincidència
- Pots activar/desactivar altres filtres per comparar

## Interpretació del Vector de Preferències

El vector té 11 components (índexs 0-10):
0. **Income** - Preu/nivell econòmic

1. **Crimes** - Seguretat (menor valor = més segur)
2. **Connectivity** - Connectivitat digital/internet
3. **Noise** - Contaminació acústica (major valor = menys soroll)
4. **Walkability** - Caminabilitat/ciutat de 15 minuts
5. **Accessibility** - Accessibilitat per a persones amb mobilitat reduïda
6. **Wellbeing** - Benestar general/espais verds/pet-friendly
7. **Mobility** - Transport públic/bici/mobilitat
8. **Education** - Centres educatius propers
9. **Community Vibe** - Ambient de la comunitat/comercios
10. **Health** - Centres mèdics/salut

## Mètodes de Càlcul

El sistema ofereix **5 mètodes diferents** per calcular la similitud entre les teves preferències i les zones de Los Ángeles. Pots canviar el mètode al desplegable "Mètode" ubicat a la cantonada inferior dreta del mapa.

### 1. 🎯 Coseno (Cosine Similarity) - **RECOMANAT**
- **Descripció**: Mesura l'angle entre dos vectors, ignorant magnituds
- **Avantatges**: Ràpid, estable i funciona bé per comparar patrons
- **Ús ideal**: Cerques generals, casos on importa més el "patró" de preferències que els valors exactes
- **Fórmula**: `similarity = dot(v1, v2) / (||v1|| * ||v2||)`
- **Rang**: 0 (vectors perpendiculars) a 1 (vectors paral·lels)

### 2. 📊 Maximum Likelihood (ML)
- **Descripció**: Basat en distribució gaussiana, assumeix que les dades segueixen una distribució normal
- **Avantatges**: Penalitza més les diferències grans, dóna resultats més "suaus"
- **Ús ideal**: Quan vols resultats més conservadors, penalitzant zones molt diferents
- **Mètode**: Calcula distància euclidiana normalitzada i aplica transformació gaussiana (σ=0.3)
- **Rang**: 0 (molt diferents) a 1 (idèntics)

### 3. 📏 Manhattan Distance
- **Descripció**: Suma de diferències absolutes en cada dimensió (distància L1)
- **Avantatges**: Més sensible a diferències individuals en cada categoria
- **Ús ideal**: Quan totes les dimensions són igualment importants
- **Fórmula**: `distance = Σ|v1[i] - v2[i]|`, després `similarity = 1 - distance/11`
- **Rang**: 0 (molt diferents) a 1 (idèntics)

### 4. ⚖️ Weighted Euclidean (Ponderat)
- **Descripció**: Distància euclidiana amb pesos personalitzats per dimensió
- **Avantatges**: Prioritza les dimensions més importants (crimes, accessibility, health, income)
- **Ús ideal**: Quan la seguretat, accessibilitat i salut són prioritàries
- **Pesos aplicats**:
  - 🔴 **Seguretat (Crimes)**: 1.5 (màxima prioritat)
  - 🟡 **Accessibilitat**: 1.3 (alta prioritat)
  - 🟡 **Income**: 1.2 (alta prioritat)
  - 🟡 **Salut (Health)**: 1.2 (alta prioritat)
  - 🟢 **Resta**: 0.8-1.1 (prioritat normal)
- **Rang**: 0 (molt diferents) a 1 (idèntics)

### 5. 📈 Pearson Correlation
- **Descripció**: Mesura correlació lineal entre vectors
- **Avantatges**: Detecta patrons similars fins i tot amb escalas diferents
- **Ús ideal**: Quan importa més la "tendència" que els valors absoluts
- **Fórmula**: Coeficient de correlació de Pearson, normalitzat de [-1,1] a [0,1]
- **Rang**: 0 (no correlacionats/oposats) a 1 (perfectament correlacionats)

### Comparació Ràpida

| Mètode | Velocitat | Precisió | Sensibilitat | Millor per |
|--------|-----------|----------|--------------|-----------|
| **Coseno** | ⚡⚡⚡ | ⭐⭐⭐ | Mitjana | Ús general |
| **ML** | ⚡⚡ | ⭐⭐⭐⭐ | Alta | Resultats conservadors |
| **Manhattan** | ⚡⚡⚡ | ⭐⭐⭐ | Alta | Balance dimensional |
| **Weighted** | ⚡⚡ | ⭐⭐⭐⭐⭐ | Molt alta | Prioritzar seguretat/salut |
| **Pearson** | ⚡⚡ | ⭐⭐⭐ | Baixa | Patrons similars |

### Quin mètode triar?

- **Família amb nens** → ⚖️ Weighted (prioritza seguretat i accessibilitat)
- **Estudiant/Jove professional** → 🎯 Coseno (balance general)
- **Cerca conservadora** → 📊 ML (resultats més estrictes)
- **Totes les categories igual d'importants** → 📏 Manhattan
- **Buscar zones amb patró similar** → 📈 Pearson

## Com canviar el mètode

1. Localitza el botó **"Mètode: [nom]"** a la cantonada inferior dreta del mapa
2. Fes clic per desplegar el menú
3. Selecciona un dels 5 mètodes disponibles
4. El mapa de calor es recalcularà automàticament

## Exemple d'ús

```
Prompt: "Busco un lloc tranquil, necessito bon internet per teletreballar, 
         tinc un gos i m'agradaria estar a prop de parcs. 
         Pressupost mitjà-alt."

Resultat esperat: 
- Zones amb alta connectivitat (connectivity)
- Baixa contaminació acústica (noise)
- Bona puntuació en wellbeing (espais verds)
- Preu mitjà-alt (income)

Mètode recomanat: Coseno o Weighted
```

## Notes Tècniques

- Tots els mètodes retornen valors normalitzats entre 0 i 1
- Es requereix un llindar mínim del 30% per mostrar una zona al mapa
- Cada cel·la del mapa representa una àrea de ~2.36 km² de Los Ángeles
- Els càlculs s'executen al backend (Python + NumPy) per màxima precisió
