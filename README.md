# Book Store API

Book store api written in django rest framework

### Installing

I keep the database updated with the newest additions and data, so it should be just cloning the repository and installing the requirements and you're good to go

Create venv

```bash
py -m venv env
# after activation the env
pip install -r requirements.txt
```

##### Start it using docker-compose

```bash
docker-compose up
```

##### Start it using manage.py

```bash
# run the server
python manage.py runserver localhost:5000
```

You can access to localhost:5000/admin/ url with this login data:

```
username : admin
password : admin
```

### Deployment

Be sure set DEBUG = False, is_test_data in BaseModel (which every model is derived from) is dependent on this setting, if you set DEBUG False, is_test_data will be False and the API won't show up data with is_test_data = False, so the initial data from this repository's database won't show up.

For Rest:
[Django Deployment Checklist](https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/)

### Features

- book, author, publisher, category endpoints return the appropriate serialized models,
- book endpoint has url parameter that makes it easy to filter
  - you can filter books by author, publisher,category, as well as order them via price, or search books via their names
- These endpoints are all paginated (Max 50 results per page) and will return a data in this structure:
  - for instance /api/author endpoint gives this json
  - ```json
    {
      "count": 15,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 3,
          "name": "Cornell Crowcombe",
          "about": "Nullam porttitor lacus at turpis. Donec posuere metus vitae ipsum. Aliquam non mauris.\r\n\r\nMorbi non lectus. Aliquam sit amet diam in magna bibendum imperdiet. Nullam orci pede, venenatis non, sodales sed, tincidunt eu, felis.\r\n\r\nFusce posuere felis sed lacus. Morbi sem mauris, laoreet ut, rhoncus aliquet, pulvinar sed, nisl. Nunc rhoncus dui vel sem.\r\n\r\nSed sagittis. Nam congue, risus semper porta volutpat, quam pede lobortis ligula, sit amet eleifend pede libero quis orci. Nullam molestie nibh in lectus.",
          "birth_date": null,
          "death_date": null,
          "author_image": "http://localhost:5000/media/placeholder_author.png"
        },
        {
          "id": 4,
          "name": "Yorgo Mebius",
          "about": "Fusce consequat. Nulla nisl. Nunc nisl.\r\n\r\nDuis bibendum, felis sed interdum venenatis, turpis enim blandit mi, in porttitor pede justo eu massa. Donec dapibus. Duis at velit eu est congue elementum.\r\n\r\nIn hac habitasse platea dictumst. Morbi vestibulum, velit id pretium iaculis, diam erat fermentum justo, nec condimentum neque sapien placerat ante. Nulla justo.\r\n\r\nAliquam quis turpis eget elit sodales scelerisque. Mauris sit amet eros. Suspendisse accumsan tortor quis turpis.\r\n\r\nSed ante. Vivamus tortor. Duis mattis egestas metus.",
          "birth_date": null,
          "death_date": null,
          "author_image": "http://localhost:5000/media/placeholder_author.png"
        }
      ]
    }
    ```
  ```

  ```
- These endpoints also can be accessed via their ids in the route,
  - /api/author/3/ would return a data like this:
    - ```json
      {
        "id": 3,
        "name": "Cornell Crowcombe",
        "about": "Nullam porttitor lacus at turpis. Donec posuere metus vitae ipsum. Aliquam non mauris.\r\n\r\nMorbi non lectus. Aliquam sit amet diam in magna bibendum imperdiet. Nullam orci pede, venenatis non, sodales sed, tincidunt eu, felis.\r\n\r\nFusce posuere felis sed lacus. Morbi sem mauris, laoreet ut, rhoncus aliquet, pulvinar sed, nisl. Nunc rhoncus dui vel sem.\r\n\r\nSed sagittis. Nam congue, risus semper porta volutpat, quam pede lobortis ligula, sit amet eleifend pede libero quis orci. Nullam molestie nibh in lectus.",
        "birth_date": null,
        "death_date": null,
        "author_image": "http://localhost:5000/media/placeholder_author.png"
      }
      ```
    ```

    ```

#### JWT Token Authorization

- Every POST/GET requests listed in here must have a header (except of course login):
  ```json
      "Authorization" : "JWT token"
  ```
- User Login/Registration

  - Login at : POST /login
  - Register at : POST /api/user

- Users can add/remove books to/from their Favorite
  - POST to Cart endpoint (/api/favorite/) with a book id in the database:
    ```py
    class FavoritesModel(BaseModel):
        user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        book = models.ForeignKey(BookModel, on_delete=models.CASCADE)

        @property

        def __str__(self):
            return f"Cart {self.user}'s Book {self.id} (Book {self.book})"
    ```
  - DELETE to Favorite endpoint:

### Models

Every model is derived from the same BaseModel (declared in LibraryManagementSystem/library/models.py)

```py
class BaseQuerySet(models.QuerySet):
    def delete(self):
        return super(BaseQuerySet, self).update(deleted_at=now())

    def hard_delete(self):
        return super(BaseQuerySet, self).delete()


class BaseManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.get_deleted = kwargs.pop('get_deleted', False)
        super(BaseManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.get_deleted:
            return BaseQuerySet(self.model).filter(is_test_data=settings.DEBUG)
        else:
            return BaseQuerySet(self.model).filter(deleted_at=None, is_test_data=settings.DEBUG)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class BaseModel(models.Model):

    objects = BaseManager()
    all_objects = BaseManager(get_deleted=True)

    is_test_data = models.BooleanField(default=settings.DEBUG)
    created_at = models.DateTimeField(default=now)
    modified_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User, related_name='%(class)s_createdby',
                                   null=True, blank=True, on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(User,
                            related_name='%(class)s_modifiedby', null=True, blank=True, on_delete=models.SET_NULL)
    deleted_by = models.ForeignKey(User,
                            related_name='%(class)s_deletedby', null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        abstract = True

    def delete(self, deleted_by_user=None):
        self.deleted_by = deleted_by_user
        self.deleted_at = now()
        self.save()

    def hard_delete(self):
        super(BaseModel, self).delete()
```

- Models with attributes is_test_data = 1 or deleted_at = 'some date' doesn't show up in the api views

  - Unless django settings.DEBUG is True, then the is_test_data = 1 shows up in the API views, this is here to make sure test datas don't show up in production
  - deleted_at flag is there to make sure no data is lost in the database

- With this implementation (Soft Deleting) you can call delete() method from anywhere without a worry of losing your data

#### Models for Frontend

##### Author

```py
class AuthorModel(BaseModel):
    name = models.CharField(max_length=100)
    about = models.TextField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    author_image = models.ImageField(default="placeholder_author.png")

    def __str__(self):
        return self.name
```

##### Publisher/Category

```py
class PublisherModel(BaseModel):
    name = models.CharField(max_length=100)
    descripton = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class CategoryModel(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
```

##### Book

```py
class BookModel(BaseModel):
    name = models.CharField(max_length=100)
    published_date = models.DateField(null=True, blank=True)
    book_cover = models.ImageField(default="placeholder_cover.png")
    description = models.TextField()
    # how many books that are currently in storage
    store_amount = models.IntegerField(default=1)
    # page count of the book, no need to specify it
    pages = models.IntegerField(null=True, blank=True)
    #ISBN doesn't exist for books that have been published before 1970
    ISBN = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    author = models.ForeignKey(AuthorModel, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(CategoryModel, on_delete=models.SET_NULL, null=True, blank=True)
    publisher = models.ForeignKey(PublisherModel, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def overall_rating(self):
        # get all the BookRatingModel from the database
        ratings = BookRatingModel.objects.all().filter(book=self.id)
        if len(ratings) > 0:
            return sum([x.rating for x in ratings]) / len(ratings)
        else:
            return 0

    def __str__(self):
        return self.name
```
