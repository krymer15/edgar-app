import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_SECRET")
DATABASE_ID = os.getenv("DATABASE_ID")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def post_summary_to_notion(ticker: str, company_name: str, summary: str, filing_date: str):
    import os
    import requests
    from integrations.notion.notion_writer import DATABASE_ID, NOTION_HEADERS

    title = f"{ticker.upper()} – 8-K Summary – {filing_date}"

    def chunk_text(text: str, max_len: int = 1900) -> list[str]:
        lines = []
        current = ""
        for line in text.splitlines():
            if not line.strip():
                continue
            if len(current) + len(line) + 1 > max_len:
                lines.append(current.strip())
                current = line
            else:
                current += "\n" + line
        if current:
            lines.append(current.strip())
        return lines

    children_blocks = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            }
        }
        for chunk in chunk_text(summary)
    ]


    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"type": "text", "text": {"content": title}}]
            },
            "Ticker": {
                "rich_text": [{"type": "text", "text": {"content": ticker.upper()}}]
            },
            "Date": {
                "date": {"start": filing_date}
            },
            "Summary": {
                "rich_text": [{"type": "text", "text": {"content": "Full signal below."}}]
            }
        },
        "children": children_blocks  # ✅ attach summary blocks here
    }

    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            json=payload,
            headers=NOTION_HEADERS
        )



        response.raise_for_status()
        print(f"✅ Posted {ticker.upper()} summary to Notion")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Failed to post {ticker.upper()} to Notion: {e}")
        print("🧾 Request Payload:")
        print(payload)
        print("🐛 Notion Response:")
        print(response.text)
