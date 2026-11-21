<!-- well-document · audit scorecard: G1:5 G2:5 G3:5 G4:5 G5:5 G6:5 · STATUS: PASS -->

[← Read Original in English](README.md)

# izko-gold-price-api

[![CI](https://github.com/AtaCanYmc/izko-gold-price-api/actions/workflows/ci.yml/badge.svg)](https://github.com/AtaCanYmc/izko-gold-price-api/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

İzmir Kuyumcular Odası (`izko.org.tr`) güncel altın ve döviz kurlarını Playwright tabanlı başsız Chromium ile kazıyan Flask REST API servisi ve Python paketi.

## İçindekiler

- [Sistem Mimarisi](#sistem-mimarisi)
- [PyPI Üzerinden Kurulum](#pypi-üzerinden-kurulum)
- [Hızlı Başlangıç: Docker](#hızlı-başlangıç-docker)
- [Yerel Geliştirme Kurulumu](#yerel-geliştirme-kurulumu)
- [Python Kütüphanesi Olarak Kullanım](#python-kütüphanesi-olarak-kullanım)
- [API Uç Noktaları](#api-uç-noktaları)
- [Yapılandırma](#yapılandırma)
- [PyPI Paketi Derleme ve Yayınlama](#pypi-paketi-derleme-ve-yayınlama)
- [Dizin Yapısı](#dizin-yapısı)
- [Test ve Doğrulama](#test-ve-doğrulama)
- [Katkı ve Güvenlik](#katkı-ve-güvenlik)
- [Lisans](#lisans)

## Sistem Mimarisi

Paket hem bir Python arayüzü (`izko_gold_price_api`) hem de bir Flask sunucu komut satırı girişi (`izko-gold-price-api`) sunar. `/izko/bundle` uç noktası veya `scrape()` fonksiyonu çağrıldığında [`scrape.py`](src/izko_gold_price_api/scrape.py) Playwright üzerinden başsız Chromium başlatır, `https://www.izko.org.tr/Home/GuncelKur` sayfasındaki `#ataLabel` DOM seçicisinin yüklenmesini bekler, tanımlı tüm etiket kimliklerini okur ve Türkçe ondalık biçimindeki sayıları IEEE 754 kayan noktalı (`float`) değerlere dönüştürür.

```mermaid
sequenceDiagram
    participant Client as HTTP Client / Python Caller
    participant Flask as Flask Server: izko_gold_price_api.app
    participant Scraper as Playwright Scraper: izko_gold_price_api.scrape
    participant IZKO as izko.org.tr/Home/GuncelKur

    Client->>Flask: GET /izko/bundle
    Flask->>Scraper: scrape()
    Scraper->>IZKO: page.goto(url)
    IZKO-->>Scraper: HTML + dynamic DOM labels
    Scraper->>Scraper: wait_for_selector(#ataLabel)
    Scraper->>Scraper: Extract inner_text and convert via to_float()
    Scraper-->>Flask: dict payload, HTTP 200
    Flask-->>Client: application/json
```

## PyPI Üzerinden Kurulum

Paketi kurun ve Playwright Chromium tarayıcı ikilisini indirin:

```bash
pip install izko-gold-price-api
playwright install chromium

# Start the Flask REST API server
izko-gold-price-api
```

## Hızlı Başlangıç: Docker

Servisi Chromium ve sistem bağımlılıkları önceden kurulmuş yalıtılmış bir konteyner içinde çalıştırın.

```bash
# 1. Clone the repository
git clone https://github.com/AtaCanYmc/izko-gold-price-api.git && cd izko-gold-price-api

# 2. Bind Flask to all container interfaces in config.json
python3 -c 'import json; p="src/izko_gold_price_api/config.json"; c=json.load(open(p)); c["api"]["host"]="0.0.0.0"; json.dump(c, open(p,"w"), indent=2)'

# 3. Build and start the container
make docker-build
make docker-run

# 4. Verify service metadata endpoint
curl -f http://localhost:5000/izko
```

## Yerel Geliştirme Kurulumu

Python 3.10 veya daha yeni bir sürüm ile macOS, Linux ya da Windows üzerinde paketi düzenlenebilir modda kurun.

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install package in editable mode and download Chromium binary
make install

# 3. Start the Flask server via CLI entry point
make run
```

## Python Kütüphanesi Olarak Kullanım

Python kodunuzda `scrape`, `to_float` fonksiyonlarını veya Flask `app` nesnesini doğrudan içe aktarın:

```python
from izko_gold_price_api import scrape, to_float

payload, status_code = scrape()
if status_code == 200:
    print(payload["priceList"]["GramAltin"])
```

## API Uç Noktaları

### `GET /izko`

[`config.json`](src/izko_gold_price_api/config.json) dosyasındaki etkin sunucu yapılandırmasını ve kayıtlı uç nokta yollarını döndürür.

```bash
curl -s http://127.0.0.1:5000/izko
```

Yanıt (`200 OK`):

```json
{
  "debug": true,
  "endpointList": {
    "base": "/izko",
    "bundle": "/izko/bundle"
  },
  "host": "127.0.0.1",
  "port": 5000,
  "rootMessage": "Welcome to izko API"
}
```

### `GET /izko/bundle`

Yapılandırılmış İZKO adresine canlı başsız Chromium sorgusu çalıştırır ve ayrıştırılmış kur listesini döndürür. Türkçe binlik ayırıcı `.` ve ondalık virgül `,` içeren sayısal metinler `float` tipine çevrilir. Saat bilgisi gibi sayısal olmayan değerler `str` olarak korunur.

```bash
curl -s http://127.0.0.1:5000/izko/bundle
```

Yanıt (`200 OK`):

```json
{
  "priceList": {
    "14Ayar": 2150.0,
    "18Ayar": 2580.0,
    "22Ayar": 3180.0,
    "Ceyrek": 5720.0,
    "Cumhuriyet": 23450.0,
    "Dolar": 34.25,
    "Euro": 37.1,
    "GramAltin": 3180.0,
    "PaketliHas": 3505.0,
    "Tarih": "14:30:00",
    "Yarim": 11440.0,
    "Ziynet": 22880.0
  },
  "url": "https://www.izko.org.tr/Home/GuncelKur"
}
```

## Yapılandırma

Varsayılan çalışma zamanı ayarları [`src/izko_gold_price_api/config.json`](src/izko_gold_price_api/config.json) dosyasındadır. Kurulu paketi değiştirmeden harici bir yapılandırma dosyası kullanmak için `IZKO_CONFIG_PATH` ortam değişkenini tanımlayın.

### Sunucu ve Kazıyıcı Parametreleri

| Anahtar Yolu | Tip | Varsayılan | Zorunlu | Açıklama |
| :--- | :--- | :--- | :---: | :--- |
| `url.izko` | String | `https://www.izko.org.tr/Home/GuncelKur` | Evet | Playwright tarafından kazınan hedef URL. |
| `url.timeout` | Integer | `10000` | Evet | Milisaniye cinsinden DOM seçici bekleme zaman aşımı. |
| `api.host` | String | `127.0.0.1` | Evet | Flask dinleme adresi. Docker içinde `0.0.0.0` yapılmalıdır. |
| `api.port` | Integer | `5000` | Evet | HTTP dinleme portu. |
| `api.debug` | Boolean | `true` | Evet | Flask hata ayıklama yeniden yükleyicisi. Üretimde `false` yapılmalıdır. |
| `api.rootMessage` | String | `Welcome to izko API` | Hayır | `/izko` uç noktasında döndürülen bilgilendirme metni. |

### DOM Seçici Eşlemesi (`label`)

| Çıktı Alanı | Hedef DOM Kimliği | Varlık Türü |
| :--- | :--- | :--- |
| `22Ayar` | `#yirmiikiLabel` | 22 Ayar altın fiyatı |
| `18Ayar` | `#onsekizLabel` | 18 Ayar altın fiyatı |
| `14Ayar` | `#ondortLabel` | 14 Ayar altın fiyatı |
| `GramAltin` | `#gramLabel` | 24 Ayar gram altın fiyatı |
| `Cumhuriyet` | `#ataLabel` | Cumhuriyet altını fiyatı ve sayfa yüklenme referansı |
| `Ceyrek` | `#yeniceyrekLabel` | Çeyrek altın fiyatı |
| `Yarim` | `#yeniyarimLabel` | Yarım altın fiyatı |
| `Ziynet` | `#yenitamLabel` | Tam Ziynet altın fiyatı |
| `PaketliHas` | `#ons` | Paketli has altın / ons göstergesi |
| `Dolar` | `#dolar` | USD/TRY döviz kuru |
| `Euro` | `#euro` | EUR/TRY döviz kuru |
| `Tarih` | `#clock` | Kaynak güncelleme saati |

## PyPI Paketi Derleme ve Yayınlama

Kaynak (`sdist`) ve tekerlek (`bdist_wheel`) dağıtımlarını `Makefile` veya PEP 517 araçlarıyla oluşturun:

```bash
make build
make publish
```

## Dizin Yapısı

```text
.
├── .github/
│   ├── CODEOWNERS
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── config.yaml
│   │   └── feature_request.yml
│   ├── PULL_REQUEST_TEMPLATE/
│   │   └── pull_request_template.md
│   ├── dependabot.yml
│   └── workflows/
│       └── ci.yml
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .markdownlint.json
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── README.tr.md
├── ROADMAP.md
├── SECURITY.md
├── pyproject.toml
├── requirements.txt
└── src/
    └── izko_gold_price_api/
        ├── __init__.py
        ├── app.py
        ├── config.json
        └── scrape.py
```

## Test ve Doğrulama

Pull request açmadan önce yapılandırma sözdizimini, Python bayt kodu derlemesini ve dokümantasyon bağlantılarını doğrulayın:

```bash
# Run syntax, config schema, and markdown link verification
make verify

# Verify Turkish decimal normalization logic (with virtualenv active)
python -c "from izko_gold_price_api import to_float; assert to_float('23.450,75') == 23450.75; assert to_float('14:30') == '14:30'"
```

## Katkı ve Güvenlik

- Katkı süreci ve commit kuralları [CONTRIBUTING.md](CONTRIBUTING.md) dosyasında açıklanmıştır.
- Planlanan teknik kilometre taşları [ROADMAP.md](ROADMAP.md) dosyasında izlenir.
- Güvenlik açığı bildirim adımları [SECURITY.md](SECURITY.md) dosyasında belirtilmiştir.

## Lisans

[MIT Lisansı](LICENSE) altında yayınlanmıştır.
