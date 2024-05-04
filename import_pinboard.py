import logging
from datetime import datetime

import requests
from tqdm import tqdm

from config import settings
from db import Bookmark, Tag, BookmarkTag, User, get_session

# Configure logging
logging.basicConfig(level=logging.INFO)


def import_pinboard_bookmarks():
    logging.info("Fetching bookmarks from Pinboard API.")
    response = requests.get(settings.pinboard_api_url)
    if response.status_code == 200:
        logging.info("Successfully fetched bookmarks.")
        bookmarks = response.json()
    else:
        logging.error(f"Failed to fetch bookmarks. Status code: {response.status_code}")
        return
    with get_session() as session:
        # get default user (username is mvv for now)
        user = session.query(User).filter_by(username='mvv').first()
        if not user:
            logging.error("Default user not found. Exiting.")
            return

        logging.info("Session started successfully.")
        # Fetch all bookmarks from Pinboard
        for bookmark in tqdm(bookmarks, desc="Importing bookmarks"):
            # Check if the bookmark already exists and update it if it does
            existing_bookmark = (
                session.query(Bookmark).filter_by(url=bookmark["href"]).first()
            )
            if existing_bookmark:
                existing_bookmark.title = bookmark["description"]
                existing_bookmark.description = bookmark["extended"]
                existing_bookmark.created_at = datetime.strptime(bookmark["time"], "%Y-%m-%dT%H:%M:%SZ")
                existing_bookmark.user_id = user.id  # Ensure user.id foreign key is added
                session.commit()
            else:
                # Create a new Bookmark instance for each new bookmark
                new_bookmark = Bookmark(
                    url=bookmark["href"],
                    title=bookmark["description"],
                    description=bookmark["extended"],
                    created_at=datetime.strptime(bookmark["time"], "%Y-%m-%dT%H:%M:%SZ"),
                    user_id=user.id  # Ensure user.id foreign key is added
                )
                session.add(new_bookmark)
                session.commit()
                existing_bookmark = new_bookmark

            # If the bookmark has tags, create new Tag instances or associate existing ones
            if bookmark["tags"]:
                tags = bookmark["tags"].split(" ")
                for tag_name in tags:
                    # Check if the tag already exists, create if it doesn't
                    tag = session.query(Tag).filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        session.add(tag)
                        session.commit()

                    # Check if the BookmarkTag association already exists, create if it doesn't
                    bookmark_tag = (
                        session.query(BookmarkTag)
                        .filter_by(bookmark_id=existing_bookmark.id, tag_id=tag.id)
                        .first()
                    )
                    if not bookmark_tag:
                        bookmark_tag = BookmarkTag(
                            bookmark_id=existing_bookmark.id, tag_id=tag.id
                        )
                        session.add(bookmark_tag)
                        session.commit()

        logging.info("Import completed successfully.")

if __name__ == "__main__":
    import_pinboard_bookmarks()