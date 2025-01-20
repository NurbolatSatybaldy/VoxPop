from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In-memory database (list) for comments
# Each comment is a dict with "text" and "category" keys
comments_db = []

@app.get("/", response_class=HTMLResponse)
def home():
    """
    Simple homepage (optional).
    Redirect or instruct users to go to /feed or /comments/new.
    """
    return """
    <html>
    <head><title>VoxPop</title></head>
    <body>
        <h1>Welcome to VoxPop!</h1>
        <p><a href="/feed">Go to Public Feed</a></p>
        <p><a href="/comments/new">Leave a Comment</a></p>
    </body>
    </html>
    """

@app.get("/comments/new", response_class=HTMLResponse)
def get_new_comment_form(request: Request):
    """
    GET route to display a form where user can enter comment text + category.
    """
    return templates.TemplateResponse("voxpop/new_comment.html", {"request": request})

@app.post("/comments/new")
def post_new_comment(text: str = Form(...), category: str = Form(...)):
    """
    POST route that receives form data:
    - text (string)
    - category (two options: 'positive' or 'negative')
    Then it adds the comment to our in-memory list, with the newest on top.
    """
    new_comment = {
        "text": text,
        "category": category
    }
    # Insert at the beginning (index 0) so the newest is on top
    comments_db.insert(0, new_comment)
    # Redirect to feed
    return RedirectResponse(url="/feed", status_code=303)

@app.get("/feed", response_class=HTMLResponse)
def public_feed(request: Request, page: int = Query(1, gt=0), page_size: int = 5):
    """
    Public feed showing comments in chronological order (newest first).
    Uses basic pagination:
      - 'page' query param to specify page number
      - 'page_size' query param to define how many items per page (default=5)
    """
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    # Slice the comments for this page
    paginated_comments = comments_db[start_index:end_index]

    # Calculate if there's a next page
    next_page = page + 1 if end_index < len(comments_db) else None
    prev_page = page - 1 if page > 1 else None

    return templates.TemplateResponse("voxpop/feed.html", {
        "request": request,
        "comments": paginated_comments,
        "current_page": page,
        "next_page": next_page,
        "prev_page": prev_page
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

