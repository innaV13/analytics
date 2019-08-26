Зависимости описаны в файле installations. 

Для работы методов 4 и 5 нужно создать методы в базе. Методы находятся в папке sql.

`
cd sql
psql -U analytics -d analytics -a -f citizens_birthdays.sql
psql -U analytics -d analytics -a -f towns_stat_percentile_age.sql
`

Для запуска приложения необходимо выполнить: 

`
cd analytics
python3 ./analytics.py
`
Для запуска тестов нужно выполнить:

`
cd analytics
python3 ./unittests.py
`