import json
from pathlib import Path

from sqlmodel import Session

from app.core.config import settings
from app.db.database import create_db_and_tables, engine
from app.db.models import Place

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

def load_places() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        total_count = 0

        for data_file in DATA_DIR.glob("*.json"):
            print(f"Loading {data_file.name}...")

            with open(data_file, encoding="utf-8") as handle:
                payload = json.load(handle)

            items = payload.get("items", [])
            file_count = 0

            for item in items:
                if not item.get("contentid"):
                    continue

                place = Place(
                    contentid=item.get("contentid"),
                    contenttypeid=item.get("contenttypeid"),
                    title=item.get("title"),
                    addr1=item.get("addr1"),
                    addr2=item.get("addr2"),
                    areacode=item.get("areacode"),
                    cat1=item.get("cat1"),
                    cat2=item.get("cat2"),
                    cat3=item.get("cat3"),
                    mapx=float(item.get("mapx")) if item.get("mapx") else None,
                    mapy=float(item.get("mapy")) if item.get("mapy") else None,
                    zipcode=item.get("zipcode"),
                    tel=item.get("tel"),
                    firstimage=item.get("firstimage"),
                    firstimage2=item.get("firstimage2"),
                    createdtime=item.get("createdtime"),
                    modifiedtime=item.get("modifiedtime"),
                    mlevel=item.get("mlevel"),
                    cpyrhtDivCd=item.get("cpyrhtDivCd"),
                    sigungucode=item.get("sigungucode"),
                    lDongRegnCd=item.get("lDongRegnCd"),
                    lDongSignguCd=item.get("lDongSignguCd"),
                    lclsSystm1=item.get("lclsSystm1"),
                    lclsSystm2=item.get("lclsSystm2"),
                    lclsSystm3=item.get("lclsSystm3"),
                    region=payload.get("region"),
                    contentType=payload.get("contentType"),
                )

                session.merge(place)
                file_count += 1

            print(f"Imported {file_count} places from {data_file.name}")
            total_count += file_count

        session.commit()
        print(f"Finished. Total imported: {total_count}")


if __name__ == "__main__":
    load_places()
