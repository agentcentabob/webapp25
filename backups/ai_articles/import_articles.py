# read DISCLAIMER.MD for use of ai in generating and importing articles
# this file and relevant article files must be moved to root for importing

import database_manager as dbh
import re


def import_articles_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = re.split(r'\n(?=\d+\|\d+\|)', content)

        success_count = 0
        error_count = 0

        for block_num, block in enumerate(blocks, 1):
            block = block.strip()

            if not block:
                continue

            try:
                last_pipe_idx = block.rfind('|')

                if last_pipe_idx == -1:
                    print(f"Block {block_num}: ERROR - "
                          f"No pipe found")
                    error_count += 1
                    continue

                header_part = block[:last_pipe_idx]
                url_part = block[last_pipe_idx+1:].strip()
                url_match = re.search(
                    r'https://[^\s\)\]]+', url_part)
                if url_match:
                    url_part = url_match.group(0)
                else:
                    url_part = url_part.strip('[]')

                header_split = header_part.split('|', 2)

                if len(header_split) < 3:
                    print(f"Block {block_num}: ERROR - "
                          f"Missing fields")
                    error_count += 1
                    continue

                user_id = int(header_split[0].strip())
                article_id = int(
                    header_split[1].strip())
                article_md = header_split[2].strip()

                if not url_part.startswith('https://'):
                    print(f"Block {block_num}: WARNING - "
                          f"Invalid URL")

                con = dbh.get_connection()
                cur = con.cursor()

                cur.execute(
                    "UPDATE articles SET "
                    "article_md = ?, article_icon = ? "
                    "WHERE user_ID = ? "
                    "AND article_ID = ?",
                    (article_md, url_part,
                     user_id, article_id)
                )

                rows_affected = cur.rowcount
                con.commit()
                con.close()

                if rows_affected > 0:
                    print(f"✓ User {user_id}, "
                          f"Article {article_id} - OK")
                    success_count += 1
                else:
                    print(f"✗ User {user_id}, "
                          f"Article {article_id} - "
                          f"Not found")
                    error_count += 1

            except ValueError as e:
                print(f"Block {block_num}: ERROR - "
                      f"Invalid format: {e}")
                error_count += 1
            except Exception as e:
                print(f"Block {block_num}: ERROR - {e}")
                error_count += 1

        print(f"\n{'='*50}")
        print(f"Import Complete!")
        print(f"Successfully updated: {success_count}")
        print(f"Errors: {error_count}")
        print(f"{'='*50}")

    except FileNotFoundError:
        print(f"ERROR: File '{filepath}' not found")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    filepath = 'articles_10.txt'
    import_articles_from_file(filepath)
