# Проект Foodgram «Продуктовый помощник»

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Как запустить проект

#### Клонировать репозиторий и перейти в него в командной строке

```shell
git clone https://github.com/mariao-max/foodgram-project-react.git
cd foodgram-project-react/backend
```

#### Запустить проект

```shell
cd ../infra
docker-compose up -d --build
```

#### Подготовить базу данных и статику 

```shell
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend python manage.py csv
```

## Проект доступен по следующим ссылкам:

* http://yourfoodgram.ddns.net - главная страница

* http://yourfoodgram.ddns.net/admin/ - админ-панель

* http://yourfoodgram.ddns.net/api/ - апи для foodgram

Логин администратора - admin@mail.ru
Пароль администратора - admin

Автор бэкенда: Одринская Мария.