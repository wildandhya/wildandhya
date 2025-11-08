#!/usr/bin/env python3
import feedparser
import pathlib
import re
from datetime import datetime

# Configuration
RSS_FEED_URL = "https://wildandhya.pages.dev/rss.xml"
README_PATH = pathlib.Path(__file__).parent / "README.md"
MAX_ITEMS = 5

def fetch_blog_posts():
    """Fetch and parse RSS feed, separate into posts and TILs"""
    feed = feedparser.parse(RSS_FEED_URL)
    posts = []
    tils = []

    for entry in feed.entries:
        # Parse date - handle both GMT and timezone formats
        try:
            # Try with timezone offset first
            pub_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            # Fallback to GMT format
            pub_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S GMT")
        formatted_date = pub_date.strftime("%b %d, %Y")

        # Get categories
        categories = [cat['term'] for cat in entry.get('tags', [])]

        item = {
            'title': entry.title,
            'link': entry.link,
            'date': formatted_date,
        }

        # Separate TIL from Posts based on category
        if categories and 'TIL' in categories:
            tils.append(item)
        else:
            posts.append(item)

    return posts[:MAX_ITEMS], tils[:MAX_ITEMS]

def update_readme(posts, tils):
    """Update README.md with latest blog posts and TILs"""
    readme_content = README_PATH.read_text(encoding='utf-8')

    # Extract existing section headers (to preserve custom emojis)
    posts_header_match = re.search(r'(##.*?Latest Blog Posts)', readme_content)
    tils_header_match = re.search(r'(##.*?Today I Learned \(TIL\))', readme_content)

    posts_header = posts_header_match.group(1) if posts_header_match else "## 📝 Latest Blog Posts"
    tils_header = tils_header_match.group(1) if tils_header_match else "## 💡 Today I Learned (TIL)"

    # Build posts section
    posts_section = f"{posts_header}\n\n"
    for post in posts:
        posts_section += f"- **[{post['title']}]({post['link']})** - *{post['date']}*\n"
    posts_section += f"\n[→ Read more posts](https://wildandhya.pages.dev)\n"

    # Build TILs section
    tils_section = f"{tils_header}\n\n"
    for til in tils:
        tils_section += f"- **[{til['title']}]({til['link']})** - *{til['date']}*\n"
    tils_section += f"\n[→ Explore all TILs](https://wildandhya.pages.dev)\n"

    # Replace posts section
    posts_start = "<!--START_SECTION:blog-->"
    posts_end = "<!--END_SECTION:blog-->"

    if posts_start in readme_content and posts_end in readme_content:
        pattern = f"{re.escape(posts_start)}.*?{re.escape(posts_end)}"
        new_content = f"{posts_start}\n{posts_section}\n{posts_end}"
        readme_content = re.sub(pattern, new_content, readme_content, flags=re.DOTALL)

    # Replace TILs section
    tils_start = "<!--START_SECTION:tils-->"
    tils_end = "<!--END_SECTION:tils-->"

    if tils_start in readme_content and tils_end in readme_content:
        pattern = f"{re.escape(tils_start)}.*?{re.escape(tils_end)}"
        new_content = f"{tils_start}\n{tils_section}\n{tils_end}"
        readme_content = re.sub(pattern, new_content, readme_content, flags=re.DOTALL)
    else:
        # Add TILs section after posts if it doesn't exist
        readme_content = readme_content.replace(
            posts_end,
            f"{posts_end}\n\n{tils_start}\n{tils_section}\n{tils_end}"
        )

    README_PATH.write_text(readme_content, encoding='utf-8')
    print(f"✅ README updated with {len(posts)} posts and {len(tils)} TILs")

def main():
    try:
        print("🔄 Fetching content from RSS feed...")
        posts, tils = fetch_blog_posts()

        if not posts and not tils:
            print("⚠️ No content found in RSS feed")
            return

        print(f"📚 Found {len(posts)} posts and {len(tils)} TILs")
        update_readme(posts, tils)

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
