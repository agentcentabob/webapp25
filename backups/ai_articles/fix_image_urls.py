import database_manager as dbh
import re


def fix_article_images():
    try:
        con = dbh.get_connection()
        cur = con.cursor()

        cur.execute("SELECT user_ID, article_ID, "
                    "article_md FROM articles")
        articles = cur.fetchall()

        updated_count = 0

        for article in articles:
            user_id = article[0]
            article_id = article[1]
            article_md = article[2]

            if not article_md:
                continue

            original_md = article_md
            pattern = (r'!\[([^\]]+) - '
                       r'\(Image not '
                       r'available due to '
                       r'AI article '
                       r'generation '
                       r'limitations\)\]'
                       r'\(/static/images/'
                       r'DO_NOT_ADD_IMAGE\.png\)')
            replacement = (r'![\1 '
                           r'(Image not '
                           r'available due to '
                           r'AI article '
                           r'generation '
                           r'limitations)]'
                           r'(/static/images/'
                           r'DO_NOT_ADD_IMAGE.png)')

            updated_md = re.sub(
                pattern, replacement, article_md)

            if updated_md != original_md:
                cur.execute(
                    "UPDATE articles SET "
                    "article_md = ? WHERE "
                    "user_ID = ? AND "
                    "article_ID = ?",
                    (updated_md, user_id,
                     article_id))

                image_count = len(
                    re.findall(pattern,
                               original_md))
                print(f"✓ User {user_id}, "
                      f"Article {article_id} - "
                      f"Updated {image_count} "
                      f"images")
                updated_count += 1

        con.commit()
        con.close()

        print(f"\n{'='*50}")
        print(f"Fix Complete!")
        print(f"Articles updated: "
              f"{updated_count}")
        print(f"{'='*50}")

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    fix_article_images()
