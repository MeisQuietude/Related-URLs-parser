# Тестовое задание

### Описание
Реализовать сервис, который обходит произвольный сайт с глубиной до 2 и сохраняет `html`, `url` и `title` страницы в хранилище.

Примеры сайтов:

* `https://ria.ru`
* `http://www.vesti.ru`
* `http://echo.msk.ru`
* `http://tass.ru/ural` 
* `https://lenta.ru`
* и любой другой, на котором есть ссылки
    
Оптимизировать прогрузку по потреблению памяти и по времени. 
Замерить время выполнения и потребление памяти загрузки.

```
При depth=0 необходимо сохранить html, title, url исходного веб-сайта.
На каждом depth=i+1 качаем страницы ссылок с i страницы (то есть глубина 2 это - главная, ссылки на главной и ссылки на страницах ссылок с главной).
```


### CLI
* По урлу сайта и глубине обхода загружаются данные.
* По урлу сайта из хранилища можно получить `n` прогруженных страниц (`url` и `title`).
    
Пример:
```
spider.py load http://www.vesti.ru/ --depth 2
>> ok, execution time: 10s, peak memory usage: 100 Mb
spider.py get http://www.vesti.ru/ -n 2
>> http://www.vesti.ru/news/: "Вести.Ru: новости, видео и фото дня"
>> http://www.vestifinance.ru/: "Вести Экономика: Главные события российской и мировой экономики, деловые новости,  фондовый рынок"
```

### Требования
* Язык реализации `python3`
* Выбор хранилища произвольный (`PostgreSQL`/`Redis`/`ElasticSearch` и любой другой на ваш выбор) 
* Стек технологий произвольный
* Выбор библиотек произвольный
* Решение оформить как проект на любом git-сервисе
* Описать в `README.md` установку, запуск, python и другие зависимости для запуска
    
### Было бы большим плюсом
* Докеризовать сервис
* Написать тесты при помощи `pytest`/`unittest` и любой другой на ваш выбор
    
    
### Результат выполнения
* Ссылку на _публичный_ репозиторий с вашей реализацией необходимо отправить нашему HR или TeamLead, от которого вы получили ссылку на данный репозиторий.
* Сервис _должен_ успешно запускаться после выполнения.
* И проходить _все_ тесты (при их наличии).


> Если в процессе выполнения у вас возникнут какие-либо неразрешимые вопросы - создайте [соответствующий issue][link_create_issue] в данном репозитории. На вопросы касательно деталей реализации ("А лучше так и так?") - вероятнее всего вы получите ответ "Как вы посчитаете правильнее".

[link_create_issue]:https://github.com/avtocod/python-developer-test-task/issues/new