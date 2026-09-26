# Сборка страницы «Протоколы УИК»

Данные — [deg.zhizhin.xyz/shpilkin.html](https://deg.zhizhin.xyz/shpilkin.html).

```sh
./fetch.sh               # скачать исходные CSV в src/ (~44 МБ, в git не попадают)
python3 build_detail.py  # uik-protocols/detail/<округ>.json — полные протоколы для карточек
python3 build.py         # uik-protocols/index.html — страница; запускать после build_detail.py (берёт версию карточек)
```

`template.html` — исходник страницы; `build.py` подставляет данные вместо `/*DATA*/null`.
