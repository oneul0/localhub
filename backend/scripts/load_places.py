import json
from pathlib import Path

from sqlmodel import Session

from app.core.config import settings
from app.db.database import create_db_and_tables, engine
from app.db.models import Place

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "부산_관광지.json"


def load_places() -> None:
    create_db_and_tables()
    with open(DATA_FILE, encoding="utf-8") as handle:
        payload = json.load(handle)
    items = payload.get("items", [])
    with Session(engine) as session:
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
                import json
                from pathlib import Path
                from typing import Iterable, Tuple

                from sqlmodel import Session

                from app.core.config import settings
                from app.db.database import create_db_and_tables, engine
                from app.db.models import Place


                BASE_DIR = Path(__file__).resolve().parents[2]
                DATA_DIR = BASE_DIR / "data"


                def _place_from_item(payload: dict, item: dict) -> Place:
                    return Place(
                        contentid=item.get("contentid"),
                        contenttypeid=item.get("contenttypeid"),
                        title=item.get("title"),
                        addr1=item.get("addr1"),
                        addr2=item.get("addr2"),
                        areacode=item.get("areacode"),
                        cat1=item.get("cat1"),
                        cat2=item.get("cat2"),
                        cat3=item.get("cat3"),
                        mapx=_safe_float(item.get("mapx")),
                        mapy=_safe_float(item.get("mapy")),
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


                def _safe_float(value):
                    try:
                        return float(value) if value is not None and value != "" else None
                    except (TypeError, ValueError):
                        return None


                def _iter_json_files(data_dir: Path) -> Iterable[Path]:
                    if not data_dir.exists():
                        return []
                    return sorted(data_dir.glob("*.json"))


                def _process_file(session: Session, file_path: Path) -> Tuple[int, int]:
                    """Process a single JSON file and return (imported_count, skipped_count)."""
                    imported = 0
                    skipped = 0
                    try:
                        with open(file_path, encoding="utf-8") as handle:
                            payload = json.load(handle)
                    except Exception as exc:
                        print(f"Skipping {file_path.name}: failed to read JSON ({exc})")
                        return 0, 0

                    items = payload.get("items", []) if isinstance(payload, dict) else []

                    for item in items:
                        try:
                            if not item.get("contentid"):
                                skipped += 1
                                continue
                            place = _place_from_item(payload, item)
                            session.merge(place)
                            imported += 1
                        except Exception as exc:  # skip invalid records but continue
                            skipped += 1
                            print(f"  Skipping record {item.get('contentid') or '<no id>'}: {exc}")
                            continue

                    session.commit()
                    return imported, skipped


                def load_places() -> None:
                    create_db_and_tables()

                    files = _iter_json_files(DATA_DIR)
                    if not files:
                        print(f"No JSON files found in {DATA_DIR}")
                        return

                    total_imported = 0
                    total_skipped = 0

                    with Session(engine) as session:
                        for file_path in files:
                            print(f"Importing {file_path.name}...")
                            imported, skipped = _process_file(session, file_path)
                            print(f"Imported {imported} records from {file_path.name}")
                            total_imported += imported
                            total_skipped += skipped

                    print(f"Total imported records: {total_imported}")
                    if total_skipped:
                        print(f"Total skipped records: {total_skipped}")


                if __name__ == "__main__":
                    load_places()
