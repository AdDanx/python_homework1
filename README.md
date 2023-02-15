#Для запуска приложения необходимо доставить нужные пакеты из requirements.txt 
#Используется asgi - uvcorn внутри кода

После запуска база заполняется двумя items, двумя stores и одним sale

Запросы как в задании
GET /items/
GET /stores/
GET /stores/top
GET /items/top

POST /sales/

{
  "item_id": 1,
  "store_id": 1
}

