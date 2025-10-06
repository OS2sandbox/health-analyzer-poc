## Roller i Mikro-Hackathonet

For at gøre det nemt og trygt for alle deltagere og arrangører, har vi herunder opdelt opgaverne i overskuelige roller.

---

### Arkitekten  
*Har sammensat den tekniske arkitektur og defineret komponenterne i løsningen.*

- Har designet den overordnede struktur og udvalgt de løskoblede komponenter i stacken ud fra strategisk fit  
- Hjælper deltagerne med at forstå hvordan komponenterne hænger sammen  
- Sikrer at løsningen er konsistent og følger de tekniske principper  
- Understøtter teams med afklaringer og teknisk retning undervejs

**Teknologier og erfaring:**

- Open source software stacks  
- GitOps, Evidence, Meltano, dbt  
- Containerization og orkestrering  

---

### Facilitatoren
*Holder styr på tid, energi og samarbejde – og sørger for at alle kommer med.*

- Planlægger og faciliterer hackathonets forløb  
- Hjælper teams med at finde hinanden og komme i gang  
- Skaber god stemning og sikrer at alle bliver hørt  
- Fjerner forhindringer og støtter fremdrift

**Erfaring og fokusområder:**

- Facilitering og mødeledelse  
- Tidsstyring og motivator
- Motivation og inklusion

---

### Platform-engineer  
*Ansvarlig for at få teknikken til at spille – fra kode til kørsel.*

- Opsætter automatiske kørsler i GitHub  
- Pakker kode i containere og sørger for at den kan køre stabilt  
- Publicerer løsningen  
- Hjælper med at løse tekniske problemer, hvis noget går galt undervejs

**Teknologier og erfaring:**

- GitHub Actions, YAML  
- Containerization (OCI Containerfiles, GitHub Container registry)  
- Deployment via GitHub Pages

---

### Data Pipeline-udvikler  
*Sammensætter datamotoren – fra indsamling til struktur.*

- Skriver kode og dokumentation  
- Opsætter dataværktøjer til at hente og transformere data  
- Konfigurerer forbindelser til datakilder  
- Sikrer at data er korrekt og giver mening

**Teknologier og erfaring:**

- Python, SQL, YAML, Markdown, SQLite, JSON  
- Meltano, Singer taps-targets  
- GitHub API  
- Evidence  
- evt. dbt

---

### Forretningsudvikleren (Præsentation og formidling)  
*Fortæller historien bag data – og gør den forståelig for alle.*

- Bruger Markdown og simple SQL-spørgsmål til at vise resultater  
- Visualiserer data og laver en fortælling, der giver mening for beslutningstagere  
- Fokuserer på det, der skaber værdi og forståelse

**Teknologier og erfaring:**

- Markdown  
- SQL (grundlæggende forespørgsler)  
- Visualisering og datastorytelling  
- Evidence-baseret præsentation

---

## Teknologier og dokumentation

Dette mikro-hackathon forudsætter, at deltagerne har praktisk erfaring med følgende værktøjer og teknologier. Herunder finder du links til den officielle dokumentation, som kan bruges til opslagsværk og forberedelse.

### Platform og automation

- [GitHub Actions](https://docs.github.com/en/actions) – CI/CD workflows med YAML
- [YAML](https://yaml.org/) – Konfigurationssprog til bl.a. GitHub Actions og Meltano
- [OCI Containerfile-specifikation](https://specs.opencontainers.org/image-spec/) – Standard for container image format

### Data pipeline og integration

- [Meltano](https://docs.meltano.com/) – Workflow-motor til ELT
- [Singer](https://www.singer.io/) – Specifikation for taps og targets
- [Singer tap-github (GitHub)](https://github.com/singer-io/tap-github) – Tap til GitHub API via Singer
- [Meltano tap-github (Meltano Hub)](https://hub.meltano.com/extractors/tap-github/) – Tap til GitHub API via Meltano
- [dbt](https://docs.getdbt.com/) – Datamodellering og transformationer
- [SQLite](https://sqlite.org/docs.html) – Letvægts database til lokal datalagring
- [GitHub REST API](https://docs.github.com/en/rest) – Dataudtræk og integration

### Dokumentation og præsentation

- [Markdown](https://www.markdownguide.org/) – Dokumentation og præsentation
- [Evidence](https://docs.evidence.dev/) – Data storytelling og visualisering
