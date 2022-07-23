from http.client import NO_CONTENT
from random import randrange
from signal import raise_signal
from time import sleep, time
from typing import Optional
from xml.dom import NotFoundErr
from fastapi import Body, FastAPI, Response, status, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI()


my_posts = [
    {"id": 1, "title": "Bangladesh", "content": "Bangladesh is my motherland"},
    {"id": 2, "title": "Germany", "content": "This is where I want to go"},
    {"id": 3, "title": "Denmark", "content": "This is the second item on my list"}
]


class Post(BaseModel):
    # id: int = randrange(0, 100000)
    title: str
    content: str


while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi",
                                user="postgres", password="toor", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("connection to database was successfull!")
        break
    except Exception as error:
        print("Connection failed!!!")
        sleep(2)


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts;""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, response: Response):
    cursor.execute(
        """INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *""", (post.title, post.content))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):

    cursor.execute("""SELECT * FROM posts WHERE id=%s""", (str(id),))
    data = cursor.fetchone()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found.")
    #     response.status_code = status.HTTP_404_NOT_FOUND
    return {"data": data}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    post = cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    post = cursor.fetchone()
    conn.commit()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_200_OK)
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING *""",
                   (post.title, post.content, str(id),))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} was not found")

    return {"data": updated_post}
